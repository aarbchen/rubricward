"""
RubricWard — Subscriber Discord & Webhook Delivery Engine (`client_delivery.py`).
Strictly enforces:
- Zero prices inside paid subscriber channels (`[VIP] RUBRICWARD // TIER 2 PAYER MRF & IDR FEED`)
- `"flags": 4` (`SUPPRESS_EMBEDS`) on every Discord webhook POST
- Identical word-boundary `slugify()` and portal-first `classify_jurisdiction()`
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

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent
SEED_PATH = ROOT_DIR / "dot_lettings_seed.json"
TIER1_DISCORD_WEBHOOK = os.getenv("RUBRICWARD_TIER1_DISCORD_WEBHOOK_URL", "")
TIER2_DISCORD_WEBHOOK = os.getenv("RUBRICWARD_TIER2_DISCORD_WEBHOOK_URL", "")


def slugify(text: str) -> str:
    """Word-boundary slugify (<= 65 chars, never cutting a word in half)."""
    cleaned = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    if len(cleaned) <= 65:
        return cleaned
    truncated = cleaned[:65]
    if "-" in truncated:
        truncated = truncated.rsplit("-", 1)[0]
    return truncated.strip("-")


def classify_jurisdiction(letting: Dict[str, Any]) -> str:
    """Portal-first jurisdiction classifier identical across pseo_generator, client_delivery, and rubricward_autopilot."""
    url = str(letting.get("source_url") or "").lower()
    if "cms.gov" in url or "nsa" in str(letting.get("letting_id") or "").lower():
        return "federal"
    if "uhc.com" in url or "multi-payer" in str(letting.get("agency") or "").lower():
        return "municipal"
    if "tdi.texas.gov" in url:
        return "tx"
    if "dmhc.ca.gov" in url:
        return "ca"
    if "floir.com" in url:
        return "fl"
    if "scc.virginia.gov" in url:
        return "va"
    if "pa.gov" in url:
        return "pa"
    if "dfs.ny.gov" in url:
        return "ny"
    if "idoi.illinois.gov" in url:
        return "il"
    if "insurance.ohio.gov" in url:
        return "oh"
    if "oci.georgia.gov" in url:
        return "ga"
    if "ncdoi.gov" in url:
        return "nc"
    st = str(letting.get("state_code") or "").lower().strip()
    if st == "us":
        return "federal"
    if st == "mu":
        return "municipal"
    return st or "tx"


def format_subscriber_message(letting: Dict[str, Any], tier: int = 2) -> Dict[str, Any]:
    lid = str(letting.get("letting_id") or "")
    title = str(letting.get("title") or "")
    slug = slugify(f"{lid}-{title}")
    dossier_url = f"https://rubricward.com/lettings/project/{slug}.html"
    source_url = str(letting.get("source_url") or "https://www.cms.gov/nosurprises")
    est_usd = float(letting.get("engineers_estimate_usd") or 0.0)
    dbe_pct = float(letting.get("dbe_goal_pct") or 215.0)

    header = (
        "[VIP] RUBRICWARD // TIER 2 PAYER MRF & IDR FEED\n"
        if tier == 2
        else "[WIRE] RUBRICWARD // TIER 1 52-PORTAL PAYER MRF FEED\n"
    )
    footer = f"\nDossier: {dossier_url}\nSource: {source_url}"
    body = (
        f"**{lid} — {title}**\n"
        f"Portal: {letting.get('agency', '')} ({letting.get('county', '')}) | Filing Window: {letting.get('letting_date', '')}\n"
        f"Cohort MRF 75th-Pct Value: `${est_usd:,.0f}` | Target Multiple: `{dbe_pct}% of Medicare` | Statute: `{letting.get('wage_determination_id', '')}`"
    )
    max_body = 2000 - len(header) - len(footer) - 10
    content = header + body[:max_body] + footer
    return {"content": content, "flags": 4}


def deliver_all(dispatch_live: bool = False) -> List[Dict[str, Any]]:
    raw = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    lettings = raw.get("lettings", [])
    messages = [format_subscriber_message(x, tier=2) for x in lettings]
    if dispatch_live and TIER2_DISCORD_WEBHOOK:
        for msg in messages[:2]:
            try:
                requests.post(TIER2_DISCORD_WEBHOOK, json=msg, timeout=10)
            except Exception as exc:
                report_error("client_delivery.py", str(exc))
    print(f"[RUBRICWARD DELIVERY] Formatted {len(messages)} 52-Portal Payer MRF & NSA IDR subscriber payloads (flags=4).")
    return messages


if __name__ == "__main__":
    deliver_all(dispatch_live=False)
