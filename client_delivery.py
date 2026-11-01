r"""
RubricWard — Subscriber Letting & Preconstruction Dossier Delivery Engine (`D:\RubricWard\client_delivery.py`).
Formats and dispatches high-value 50-State DOT, USACE & Municipal construction lettings and
6-File OpenXML (.DOCX + .XLSX) Bid-Tab Dossiers to paid subscribers (with `flags: 4` SUPPRESS_EMBEDS
and reserved footer links so URLs are never truncated).
"""

from error_telemetry import configure_utf8_stdio, report_error
configure_utf8_stdio()

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List
import requests
from dotenv import load_dotenv

from rubricward_autopilot import slugify

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=str(ROOT_DIR / ".env"))

SITE_BASE_URL = os.getenv("RUBRICWARD_SITE_URL", "https://rubricward.com").rstrip("/")
API_BASE_URL = os.getenv("RUBRICWARD_API_BASE_URL", "https://rubricward.com").rstrip("/")
DOSSIERS_PATH = ROOT_DIR / "rubricward_dossiers.json"


def format_dossier_dispatch(dossier: Dict[str, Any]) -> str:
    pid = str(dossier.get("project_id") or "TXDOT-CSJ-0015-13-412")
    raw_title = str(dossier.get("title") or "IH-35 Bridge Deck Replacement")
    clean_title = re.sub(r"^\[[^\]]+\]\s*", "", raw_title)
    agency = str(dossier.get("agency") or "TxDOT")
    county = str(dossier.get("county") or "Travis County, TX")
    state_code = str(dossier.get("state_code") or "TX")
    est_usd = float(dossier.get("engineers_estimate_usd") or 18450000.0)
    letting_date = str(dossier.get("letting_date") or "2026-11-18")
    dbe_pct = float(dossier.get("dbe_goal_pct") or 11.5)
    wage_id = str(dossier.get("wage_determination_id") or "TX20260028")
    slug = str(dossier.get("slug") or slugify(clean_title))

    dossier_url = f"{SITE_BASE_URL}/lettings/project/{slug}.html"
    zip_url = f"{API_BASE_URL}/v1/camber-autopilot/compile-bid-package?project_id={pid}&state_code={state_code}&format=binary"
    source_url = str(dossier.get("url") or dossier_url)

    footer = (
        f"\n**Dossier:** <{dossier_url}>\n"
        f"**6-File .ZIP Package:** <{zip_url}>\n"
        f"**Source:** <{source_url}>"
    )
    header = (
        "**[AUTOPILOT] RUBRICWARD // PRECONSTRUCTION & BID-TAB DOSSIER**\n"
        f"**Project:** `{pid}` — {clean_title[:110]}\n"
        f"**Owner:** {agency} ({county}) | **Letting:** `{letting_date}`\n"
        f"**Engineer's Est:** `${est_usd:,.0f}` | **DBE Goal:** `{dbe_pct:.1f}%` | **Davis-Bacon:** `{wage_id}`\n"
    )
    scope = str(dossier.get("scope_summary") or "")[:600]
    narrative = f"**Scope & Pay-Item Highlights:** {scope}\n"

    max_body = 1950 - len(header) - len(footer)
    return header + narrative[:max_body] + footer


def run_subscriber_delivery(send_live_webhook: bool = False) -> Dict[str, Any]:
    if not DOSSIERS_PATH.exists():
        return {"status": "no_dossiers", "count": 0}
    data = json.loads(DOSSIERS_PATH.read_text(encoding="utf-8"))
    if isinstance(data, list):
        dossiers = data
    elif isinstance(data, dict) and "dossiers" in data:
        dossiers = data["dossiers"]
    elif isinstance(data, dict):
        dossiers = list(data.values())
    else:
        dossiers = []

    formatted_messages: List[str] = []
    for d in dossiers[:12]:
        msg = format_dossier_dispatch(d)
        assert len(msg) <= 2000, f"Message exceeded 2000 chars ({len(msg)})"
        formatted_messages.append(msg)

    webhook_url = (os.getenv("RUBRICWARD_DISCORD_WEBHOOK_URL") or "").strip()
    signaltender_webhook_ids = (
        "1555743443802918993",
        "1560070981563715644",
        "1561230679860056117",
        "1563916225862574080",
        "1563916236126036068",
    )
    if any(wid in webhook_url for wid in signaltender_webhook_ids):
        webhook_url = ""
    sent = 0
    if send_live_webhook and webhook_url:
        for msg in formatted_messages[:3]:
            try:
                resp = requests.post(webhook_url, json={"content": msg, "flags": 4}, timeout=12)
                if resp.status_code in (200, 204):
                    sent += 1
            except Exception as exc:
                report_error("client_delivery.py", f"Webhook delivery error: {exc}")

    print(f"[RUBRICWARD DELIVERY] Prepared {len(formatted_messages)} executive letting dispatches (sent={sent}).")
    return {"status": "ready", "prepared": len(formatted_messages), "sent": sent}


if __name__ == "__main__":
    run_subscriber_delivery(send_live_webhook=False)
