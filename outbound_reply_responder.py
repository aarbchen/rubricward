r"""
RubricWard — Autonomous Outbound Reply Classifier & "SEND ZIP" Auto-Responder (`D:\RubricWard\outbound_reply_responder.py`).
Polls for unread estimator replies (via Instantly.ai V2 `/api/v2/emails` with `email_type="received"`),
classifies each reply with `claude-sonnet-5-5` (after stripping quoted email history via `_strip_quoted_thread()`),
automatically answers specific estimator questions or `"SEND ZIP"` requests with the contractor's live DOT letting dossier,
the 1-Click 6-File OpenXML (.DOCX + .XLSX) Bid-Tab `.ZIP` download link, and self-serve Stripe Checkout links
(`Tier 1 $199/mo`, `Tier 2 $499/mo`, `Tier 3 $1,499/mo`), and permanently purges/archives any `UNSUBSCRIBE` requests.
"""

from error_telemetry import configure_utf8_stdio, report_error
configure_utf8_stdio()

import csv
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List
import requests
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=str(ROOT_DIR / ".env"))

INSTANTLY_API_KEY = (os.getenv("INSTANTLY_API_KEY") or "").strip()
RUBRICWARD_CAMPAIGN_ID = (os.getenv("RUBRICWARD_INSTANTLY_CAMPAIGN_ID") or "").strip()
ANTHROPIC_API_KEY = (os.getenv("ANTHROPIC_API_KEY") or "").strip()
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
RUBRICWARD_DISCORD_WEBHOOK_URL = (os.getenv("RUBRICWARD_DISCORD_WEBHOOK_URL") or "").strip()
SITE_BASE_URL = os.getenv("RUBRICWARD_SITE_URL", "https://rubricward.com").rstrip("/")
CSV_PATH = ROOT_DIR / "campaign_leads.csv"
MLOT_CSV_PATH = ROOT_DIR / "mlot_sniper_leads.csv"
PROCESSED_PATH = ROOT_DIR / "processed_outbound_replies.json"
ARCHIVE_PATH = ROOT_DIR / "completed_outreach_archive.json"

TIER1_STRIPE_URL = "https://buy.stripe.com/bJeaEWePg6FteFid6Q7wA0i"
TIER2_STRIPE_URL = "https://buy.stripe.com/8x28wOePgd3R68M3wg7wA0k"
TIER3_STRIPE_URL = "https://buy.stripe.com/28E00ibD46Ft2WAaYI7wA0m"
TIER4_STRIPE_URL = "https://buy.stripe.com/28E7sK9uWfbZ54I5Eo7wA0o"


def lookup_prospect_context(from_email: str) -> Dict[str, str]:
    clean_em = str(from_email or "").strip().lower()
    dom = clean_em.split("@", 1)[1] if "@" in clean_em else ""
    matched: Dict[str, str] = {}
    for csv_candidate in (CSV_PATH, MLOT_CSV_PATH):
        if csv_candidate.exists() and not matched:
            try:
                with open(csv_candidate, mode="r", encoding="utf-8", newline="") as f:
                    for row in csv.DictReader(f):
                        row_em = str(row.get("email") or "").strip().lower()
                        if row_em == clean_em or (dom and row_em.endswith("@" + dom)):
                            matched = dict(row)
                            break
            except Exception:
                pass
    res_state = matched.get("state") or "TX"
    res_pid = matched.get("project_id") or "TXDOT-CSJ-0015-13-412"
    raw_compiler = matched.get("compiler_url") or ""
    if not raw_compiler or "project_id=" not in raw_compiler or "api.rubricward.com" in raw_compiler:
        raw_compiler = f"https://rubricward.com/v1/camber-autopilot/compile-bid-package?project_id={res_pid}&state_code={res_state}&format=binary"
    return {
        "first_name": matched.get("first_name") or "Chief Estimator",
        "company_name": matched.get("company_name") or "your estimating team",
        "state": res_state,
        "project_id": res_pid,
        "project_title": matched.get("project_title") or "IH-35 Bridge Deck Replacement & Superpave Overlay",
        "dossier_url": matched.get("dossier_url") or f"{SITE_BASE_URL}/lettings/index.html",
        "compiler_url": raw_compiler,
    }


def _strip_quoted_thread(raw_text: str) -> str:
    """Strip quoted email history ('On ... wrote:', '> ...', '-----Original Message-----') before classifying."""
    lines: List[str] = []
    for ln in str(raw_text or "").splitlines():
        s = ln.strip()
        if s.startswith(">"):
            continue
        if s.lower().startswith("on ") and s.lower().endswith("wrote:"):
            break
        if s.startswith("-----Original Message-----") or s.startswith("From: "):
            break
        lines.append(ln)
    cleaned = "\n".join(lines).strip()
    return cleaned if cleaned else str(raw_text or "").strip()


def classify_estimator_reply(reply_text: str) -> str:
    stripped = _strip_quoted_thread(reply_text)
    txt = stripped.lower()
    if any(u in txt for u in ("unsubscribe", "remove me", "stop emailing", "not interested", "take me off")):
        return "UNSUBSCRIBE"
    if "?" in stripped and not any(p in txt for p in ("send zip", "send it", "send over")):
        return "QUESTION"
    if any(p in txt for p in ("send zip", "send it", "yes", "sure", "send over", "interested", "bid tab", "spreadsheet")):
        return "POSITIVE_INTEREST"

    if ANTHROPIC_API_KEY and txt:
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": ANTHROPIC_MODEL,
                    "max_tokens": 30,
                    "messages": [
                        {
                            "role": "user",
                            "content": (
                                "Classify this construction estimator email reply into exactly one label: "
                                "POSITIVE_INTEREST, QUESTION, or UNSUBSCRIBE.\n\n"
                                f"Reply: {stripped[:500]}"
                            ),
                        }
                    ],
                },
                timeout=15,
            )
            if resp.status_code == 200:
                out = ((resp.json().get("content") or [{}])[0].get("text") or "").upper()
                if "UNSUBSCRIBE" in out:
                    return "UNSUBSCRIBE"
                if "QUESTION" in out:
                    return "QUESTION"
        except Exception:
            pass
    return "POSITIVE_INTEREST"


def build_zip_fulfillment_reply(from_email: str, reply_text: str = "", label: str = "POSITIVE_INTEREST") -> Dict[str, str]:
    ctx = lookup_prospect_context(from_email)
    custom_answer_block = ""
    stripped_q = _strip_quoted_thread(reply_text)
    if label == "QUESTION" and stripped_q and ANTHROPIC_API_KEY:
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": ANTHROPIC_MODEL,
                    "max_tokens": 220,
                    "system": (
                        "You are Aaron at the RubricWard Preconstruction & DOT Desk. "
                        "Directly answer the estimator's question in 2-3 concise plain-text sentences (no markdown asterisks or hashtags). "
                        "Facts: RubricWard monitors all 50 U.S. State DOT portals + Federal USACE Civil Works + Municipal Public Works (52 portals total), "
                        "benchmarks 36 months of historical winning unit-price bid tabulations (1.42M+ pay items), calculates county-specific Davis-Bacon WH-347 wages, "
                        "and compiles 6-File OpenXML (.DOCX + .XLSX with live =ROUND(D6*G6,2) and =SUM() Excel formulas) bid packages compatible with HCSS HeavyBid, Procore, and Excel."
                    ),
                    "messages": [{"role": "user", "content": f"Estimator question: {stripped_q[:500]}"}],
                },
                timeout=15,
            )
            if resp.status_code == 200:
                ans = ((resp.json().get("content") or [{}])[0].get("text") or "").strip().replace("**", "")
                if len(ans) >= 15:
                    custom_answer_block = f"{ans}\n\n"
        except Exception:
            pass

    body = (
        f"Hi {ctx['first_name']},\n\n"
        f"{custom_answer_block}"
        f"Here is the pre-shredded DOT Bid-Tab & Preconstruction package for {ctx['project_id']} ({ctx['project_title']}):\n\n"
        f"1. 1-Click 6-File OpenXML (.DOCX + .XLSX) Bid-Tab & Takeoff Package (.ZIP):\n"
        f"   {ctx['compiler_url']}\n"
        f"   (Includes Vol I CSI Spec & Submittal Matrix .docx, Vol II DOT Historical Unit-Price Bid Tabulation .xlsx with live =SUM() formulas, "
        f"Vol III Davis-Bacon WH-347 Fringe Model .xlsx, Vol IV 49 CFR 26 DBE & BABA Audit .docx, and Vol V AIA G702/G703 SOV .docx)\n\n"
        f"2. Interactive Letting Dossier & Competitor Spread Preview:\n"
        f"   {ctx['dossier_url']}\n\n"
        f"If you want automated 50-State DOT planholder alerts, 36-month historical unit bid tabulations, and unlimited 6-File .ZIP compilations across all upcoming lettings:\n"
        f"- Tier 1 // ClaimWire Pro ($199/mo): {TIER1_STRIPE_URL}\n"
        f"- Tier 2 // RubricWard Autopilot ($499/mo — Recommended): {TIER2_STRIPE_URL}\n"
        f"- Tier 3 // Unlimited 6-File .ZIP Takeoff Compiler ($1,499/mo): {TIER3_STRIPE_URL}\n\n"
        f"Best,\n"
        f"Aaron // RubricWard Preconstruction & DOT Systems\n"
        f"{SITE_BASE_URL}"
    )
    return {
        "to_email": from_email,
        "project_id": ctx["project_id"],
        "subject": f"Re: {ctx['project_id']} unit bid tabs & 6-File .ZIP Takeoff Package",
        "body": body,
    }


def _archive_and_purge_unsubscribed_lead(from_email: str) -> None:
    clean_unsub = str(from_email or "").strip().lower()
    if not clean_unsub or "@" not in clean_unsub:
        return
    try:
        archived: List[str] = []
        if ARCHIVE_PATH.exists():
            raw = json.loads(ARCHIVE_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                archived = [str(x).strip().lower() for x in raw if x]
        if clean_unsub not in archived:
            archived.append(clean_unsub)
            ARCHIVE_PATH.write_text(json.dumps(sorted(set(archived)), indent=2), encoding="utf-8")
    except Exception:
        pass

    if INSTANTLY_API_KEY and RUBRICWARD_CAMPAIGN_ID:
        try:
            headers = {"Authorization": f"Bearer {INSTANTLY_API_KEY}", "Content-Type": "application/json"}
            l_resp = requests.post(
                "https://api.instantly.ai/api/v2/leads/list",
                headers=headers,
                json={"campaign": RUBRICWARD_CAMPAIGN_ID, "search": clean_unsub, "limit": 20},
                timeout=10,
            )
            if l_resp.status_code == 200:
                for l_it in (l_resp.json().get("items") or []):
                    if str(l_it.get("email") or "").strip().lower() == clean_unsub and l_it.get("id"):
                        requests.delete(
                            f"https://api.instantly.ai/api/v2/leads/{l_it['id']}",
                            headers={"Authorization": f"Bearer {INSTANTLY_API_KEY}"},
                            timeout=10,
                        )
        except Exception:
            pass


def run_reply_responder() -> Dict[str, Any]:
    processed: List[str] = []
    if PROCESSED_PATH.exists():
        try:
            processed = json.loads(PROCESSED_PATH.read_text(encoding="utf-8"))
        except Exception:
            processed = []

    summary = {"checked": 0, "replied": 0, "unsubscribed": 0, "model": ANTHROPIC_MODEL}
    if not INSTANTLY_API_KEY or not RUBRICWARD_CAMPAIGN_ID:
        return summary

    try:
        r = None
        for attempt in range(3):
            try:
                r = requests.get(
                    "https://api.instantly.ai/api/v2/emails",
                    headers={"Authorization": f"Bearer {INSTANTLY_API_KEY}"},
                    params={"campaign_id": RUBRICWARD_CAMPAIGN_ID, "email_type": "received", "limit": 50},
                    timeout=20,
                )
                break
            except requests.exceptions.RequestException:
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))

        if r is not None and r.status_code == 200:
            items = (r.json() or {}).get("items") or []
            for item in items:
                msg_id = str(item.get("id") or "")
                if not msg_id or msg_id in processed or item.get("ue_type") != 2:
                    continue
                eaccount = str(item.get("eaccount") or "").strip().lower()
                from_em = str(item.get("from_address_email") or item.get("lead") or "").strip()
                if "rubricward" not in eaccount or "signaltender" in eaccount or "signaltender" in from_em.lower() or "rubricward" in from_em.lower():
                    continue
                summary["checked"] += 1
                body_obj = item.get("body") or {}
                body_txt = str(body_obj.get("text") or body_obj.get("html") or "").strip()
                if not body_txt:
                    processed.append(msg_id)
                    continue
                label = classify_estimator_reply(body_txt)
                if label in ("POSITIVE_INTEREST", "QUESTION"):
                    pkg = build_zip_fulfillment_reply(from_em, reply_text=body_txt, label=label)
                    r_send = requests.post(
                        "https://api.instantly.ai/api/v2/emails/reply",
                        headers={"Authorization": f"Bearer {INSTANTLY_API_KEY}", "Content-Type": "application/json"},
                        json={
                            "reply_to_uuid": msg_id,
                            "eaccount": item.get("eaccount"),
                            "subject": pkg["subject"],
                            "body": {"text": pkg["body"]},
                        },
                        timeout=15,
                    )
                    if 200 <= r_send.status_code < 300:
                        summary["replied"] += 1
                else:
                    summary["unsubscribed"] += 1
                    _archive_and_purge_unsubscribed_lead(from_em)
                processed.append(msg_id)
            PROCESSED_PATH.write_text(json.dumps(processed[-500:], indent=2), encoding="utf-8")
    except Exception as exc:
        report_error("outbound_reply_responder.py", f"Reply polling note: {exc}")

    return summary


if __name__ == "__main__":
    res = run_reply_responder()
    print(f"[RUBRICWARD REPLY RESPONDER] {res}")
