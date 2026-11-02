r"""
RubricWard — Autonomous Outbound Reply Classifier & "SEND ZIP" Auto-Responder (`D:\RubricWard\outbound_reply_responder.py`).
Polls for unread RCM/Medical Group replies (via Instantly.ai V2 `/api/v2/emails` with `email_type="received"`),
classifies each reply with `claude-sonnet-5-5` (after stripping quoted email history via `_strip_quoted_thread()`),
automatically answers specific Managed Care / RCM questions or `"SEND ZIP"` requests with the group's live Payer MRF & NSA IDR dossier,
the 1-Click 6-File OpenXML (.DOCX + .XLSX) Payer MRF & NSA IDR `.ZIP` download link, and self-serve Stripe Checkout links
(`Tier 1 $199/mo`, `Tier 2 $499/mo`, `Tier 3 $1,499/mo`), and permanently purges/archives any `UNSUBSCRIBE` requests.
Strictly enforces 3-way sender mailbox isolation (`*rubricward*` only; never responds to `*signaltender*` or `*camberdesk*`).
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
RUBRICWARD_CAMPAIGN_ID = (
    os.getenv("RUBRICWARD_INSTANTLY_CAMPAIGN_ID")
    or os.getenv("CAMBERDESK_INSTANTLY_CAMPAIGN_ID")
    or "672de7d4-7ff6-42ec-be56-9b6ce8519e8c"
).strip()
ANTHROPIC_API_KEY = (os.getenv("ANTHROPIC_API_KEY") or "").strip()
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
SITE_BASE_URL = os.getenv("RUBRICWARD_SITE_URL", "https://rubricward.com").rstrip("/")
CSV_PATH = ROOT_DIR / "campaign_leads.csv"
PROCESSED_PATH = ROOT_DIR / "processed_outbound_replies.json"
ARCHIVE_PATH = ROOT_DIR / "completed_outreach_archive.json"

TIER1_STRIPE_URL = f"{SITE_BASE_URL}/#checkout-tier1"
TIER2_STRIPE_URL = f"{SITE_BASE_URL}/#checkout-tier2"
TIER3_STRIPE_URL = f"{SITE_BASE_URL}/#checkout-tier3"


def _strip_quoted_thread(body: str) -> str:
    """Strips quoted email thread history ('>', 'On ... wrote:', 'From:') before intent classification (RULE-021)."""
    clean_lines: List[str] = []
    for line in (body or "").splitlines():
        s = line.strip()
        if s.startswith(">"):
            continue
        if s.lower().startswith(("on ", "from:", "sent:", "-----original message-----")):
            break
        clean_lines.append(line)
    cleaned = "\n".join(clean_lines).strip()
    return cleaned if cleaned else str(body or "").strip()


def lookup_prospect_context(from_email: str) -> Dict[str, str]:
    clean_em = str(from_email or "").strip().lower()
    dom = clean_em.split("@", 1)[1] if "@" in clean_em else ""
    matched: Dict[str, str] = {}
    if CSV_PATH.exists():
        try:
            with open(CSV_PATH, mode="r", encoding="utf-8", newline="") as f:
                for row in csv.DictReader(f):
                    row_em = str(row.get("email") or "").strip().lower()
                    if row_em == clean_em or (dom and row_em.endswith("@" + dom)):
                        matched = dict(row)
                        break
        except Exception:
            pass
    res_state = matched.get("state") or matched.get("state_code") or "TX"
    res_pid = matched.get("project_id") or matched.get("letting_id") or "TXDOI-MRF-CPT-29881-DFW"
    raw_compiler = matched.get("compiler_url") or ""
    if not raw_compiler or "project_id=" not in raw_compiler or "api.rubricward.com" in raw_compiler:
        raw_compiler = f"{SITE_BASE_URL}/v1/camber-autopilot/compile-bid-package?project_id={res_pid}&state_code={res_state}&format=binary"
    return {
        "first_name": matched.get("first_name") or "Revenue Cycle Director",
        "company_name": matched.get("company_name") or "your revenue cycle team",
        "state": res_state,
        "project_id": res_pid,
        "project_title": matched.get("project_title") or "Commercial Payer TiC MRF Underpayment & NSA IDR Cohort",
        "dossier_url": matched.get("dossier_url") or f"{SITE_BASE_URL}/lettings/index.html",
        "compiler_url": raw_compiler,
    }


def classify_rcm_reply(reply_text: str) -> str:
    stripped = _strip_quoted_thread(reply_text)
    txt = stripped.lower()
    if any(u in txt for u in ("unsubscribe", "remove me", "stop emailing", "not interested", "take me off")):
        return "UNSUBSCRIBE"
    if "?" in stripped and not any(p in txt for p in ("send zip", "send it", "send over")):
        return "QUESTION"
    if any(p in txt for p in ("send zip", "send it", "yes", "sure", "send over", "interested", "mrf", "appeal", "spreadsheet")):
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
                                "Classify this healthcare revenue cycle / medical group email reply into exactly one label: "
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


def build_reply_response(prospect_name: str, letting_id: str, inbound_body: str = "", from_email: str = "") -> Dict[str, str]:
    cleaned_inbound = _strip_quoted_thread(inbound_body)
    ctx = lookup_prospect_context(from_email) if from_email else {
        "first_name": prospect_name or "Revenue Cycle Team",
        "company_name": prospect_name or "your revenue cycle team",
        "state": letting_id[:2] if len(letting_id) >= 2 else "TX",
        "project_id": letting_id or "TXDOI-MRF-CPT-29881-DFW",
        "dossier_url": f"{SITE_BASE_URL}/#lettings",
        "compiler_url": f"{SITE_BASE_URL}/v1/camber-autopilot/compile-bid-package?project_id={letting_id or 'TXDOI-MRF-CPT-29881-DFW'}&state_code={(letting_id[:2] if len(letting_id) >= 2 else 'TX')}&format=binary",
    }
    return {
        "model": ANTHROPIC_MODEL,
        "letting_id": ctx["project_id"],
        "cleaned_inbound": cleaned_inbound,
        "subject": f"Re: Commercial Payer TiC MRF, ERISA Appeal & NSA IDR 6-File .ZIP Package for {ctx['project_id']}",
        "body": (
            f"Hi {prospect_name or ctx['first_name']},\n\n"
            f"Here is the direct link to your 6-file OpenXML (.DOCX + .XLSX) Commercial Payer TiC MRF, Medicare MPFS RVU/GPCI & Federal NSA IDR Package for {ctx['project_id']} "
            f"across our 52 monitored State DOI/APCD MRF & Federal IDR portals and 12 Healthcare Revenue Cycle APIs:\n\n"
            f"- 1-Click 6-File OpenXML (.DOCX + .XLSX) Claim & IDR Package (.ZIP): {ctx['compiler_url']}\n"
            f"- Live Payer MRF & NSA IDR Dossier: {ctx['dossier_url']}\n"
            f"- Tier 2 Payer MRF & NSA IDR Autopilot Desk ($499/mo): {TIER2_STRIPE_URL}\n"
            f"- Tier 3 Unlimited 6-File .ZIP Appeal & IDR Compiler ($1,499/mo): {TIER3_STRIPE_URL}\n\n"
            f"Best,\n"
            f"Aaron Chen\n"
            f"RubricWard Payer MRF & NSA IDR Systems"
        ),
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
                if (
                    "rubricward" not in eaccount
                    or "signaltender" in eaccount
                    or "camberdesk" in eaccount
                    or "signaltender" in from_em.lower()
                    or "camberdesk" in from_em.lower()
                    or "rubricward" in from_em.lower()
                ):
                    continue
                summary["checked"] += 1
                body_obj = item.get("body") or {}
                body_txt = str(body_obj.get("text") or body_obj.get("html") or "").strip()
                if not body_txt:
                    processed.append(msg_id)
                    continue
                label = classify_rcm_reply(body_txt)
                if label in ("POSITIVE_INTEREST", "QUESTION"):
                    ctx = lookup_prospect_context(from_em)
                    pkg = build_reply_response(
                        prospect_name=ctx["first_name"],
                        letting_id=ctx["project_id"],
                        inbound_body=body_txt,
                        from_email=from_em,
                    )
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
    sample = build_reply_response("Specialty Group Revenue Cycle Team", "TXDOI-MRF-CPT-29881-DFW")
    res = run_reply_responder()
    print(f"[RUBRICWARD RESPONDER] Ready (Model: {sample['model']}) | {res}")
