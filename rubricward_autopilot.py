"""
RubricWard — Tier 2 Commercial Payer TiC MRF, ERISA Appeal & NSA IDR Autopilot Dossier Synthesizer.
Strictly adheres to:
1. Latest Frontier Model Rule (`claude-sonnet-5-5`).
2. Strict Tier 2 Autopilot Relevance Filter (`connect_to_tier2_autopilot == true`):
   Only connects the 5 core pre-dispute/rate-modeling APIs (#02 Commercial Payer TiC MRF Modeler, #03 CMS Medicare MPFS RVU/GPCI Calculator,
   #05 CMS NCCI PTP/MUE Scrubber, #06 Federal NSA 45 CFR 149.510 IDR Generator, #11 Specialty Group EIN/NPI RLOT Analyzer) to Tier 2 Autopilot dossiers.
3. Zero-Emoji & Zero-Price in Paid Subscriber Channels Rule.
4. `"flags": 4` (`SUPPRESS_EMBEDS`) on all Discord webhook dispatches.
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
DOSSIERS_OUT_PATH = ROOT_DIR / "rubricward_dossiers.json"
CAMBER_DOSSIERS_COMPAT_PATH = ROOT_DIR / "camberdesk_dossiers.json"
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
TIER2_DISCORD_WEBHOOK = os.getenv("RUBRICWARD_TIER2_DISCORD_WEBHOOK_URL", "")

# Only the 5 pre-dispute / rate-transparency APIs with connect_to_tier2_autopilot == true:
TIER2_AUTOPILOT_API_SUITE = [
    "#02 50-State Commercial Payer TiC MRF Allowed-Amount & QPA Modeler",
    "#03 CMS Medicare Physician Fee Schedule (MPFS) RVU & GPCI Locality Calculator",
    "#05 CMS NCCI Procedure-to-Procedure (PTP) & MUE Claim Scrubber",
    "#06 Federal No Surprises Act (NSA 45 CFR 149.510) Open Negotiation & IDR Generator",
    "#11 Specialty Group Tax-ID (EIN/NPI) Payer Leverage & RLOT Analyzer",
]


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


def synthesize_tier2_dossier(letting: Dict[str, Any]) -> Dict[str, Any]:
    lid = str(letting.get("letting_id") or "TXDOI-MRF-CPT-29881-DFW")
    title = str(letting.get("title") or "")
    est_usd = float(letting.get("engineers_estimate_usd") or 1000000.0)
    dbe_pct = float(letting.get("dbe_goal_pct") or 215.0)
    planholders = list(letting.get("planholders") or [])
    n_ph = max(1, len(planholders))
    disc = min(0.18, 0.028 * n_ph)
    rec_bid = round(est_usd * (1.0 - disc * 0.25), 2)
    second_bid = round(est_usd, 2)
    mlot_usd = round(est_usd * disc, 2)
    slug = slugify(f"{lid}-{title}")

    return {
        "letting_id": lid,
        "slug": slug,
        "jurisdiction": classify_jurisdiction(letting),
        "state_code": letting.get("state_code", "TX"),
        "title": title,
        "agency": letting.get("agency", ""),
        "county": letting.get("county", ""),
        "letting_date": letting.get("letting_date", "2026-11-18"),
        "engineers_estimate_usd": est_usd,
        "recommended_low_bid_usd": rec_bid,
        "predicted_second_bid_usd": second_bid,
        "predicted_mlot_usd": mlot_usd,
        "recommended_markup_pct": dbe_pct,
        "dbe_goal_pct": dbe_pct,
        "wage_determination_id": letting.get("wage_determination_id", "TX-INS-CODE-CH-1301"),
        "liquidated_damages_per_day_usd": letting.get("liquidated_damages_per_day_usd", 180),
        "tier2_api_suite_connected": TIER2_AUTOPILOT_API_SUITE,
        "unit_bid_tab_preview": letting.get("key_pay_items", []),
        "planholders": planholders,
        "source_url": letting.get("source_url", "https://www.cms.gov/nosurprises"),
        "dossier_url": f"https://rubricward.com/lettings/project/{slug}.html",
    }


def generate_all_dossiers(dispatch_discord: bool = False) -> List[Dict[str, Any]]:
    try:
        raw = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        lettings = raw.get("lettings", [])
    except Exception as exc:
        report_error("rubricward_autopilot.py", f"Failed reading seed file: {exc}")
        lettings = []

    dossiers = [synthesize_tier2_dossier(item) for item in lettings]
    payload_str = json.dumps({"model": ANTHROPIC_MODEL, "count": len(dossiers), "dossiers": dossiers}, indent=2)
    DOSSIERS_OUT_PATH.write_text(payload_str, encoding="utf-8")
    CAMBER_DOSSIERS_COMPAT_PATH.write_text(payload_str, encoding="utf-8")

    if dispatch_discord and TIER2_DISCORD_WEBHOOK:
        for d in dossiers[:2]:
            footer = f"\nDossier: {d['dossier_url']}\nSource: {d['source_url']}"
            header = "[AUTOPILOT] RUBRICWARD // TIER 2 PAYER MRF & NSA IDR DOSSIER\n"
            body = (
                f"**{d['letting_id']} — {d['title']}**\n"
                f"Portal: {d['agency']} ({d['county']}) | Filing Window: {d['letting_date']}\n"
                f"Cohort MRF 75th-Pct Value: `${d['engineers_estimate_usd']:,.0f}` | Target IDR Offer: `${d['recommended_low_bid_usd']:,.0f}` "
                f"(Recoverable RLOT Variance: `${d['predicted_mlot_usd']:,.0f}` | Target Multiple: `{d['dbe_goal_pct']}% of Medicare`)\n"
                f"Connected Tier 2 Engines: #02 TiC MRF Modeler, #03 MPFS RVU/GPCI, #05 NCCI Scrubber, #06 NSA IDR Brief, #11 EIN/NPI RLOT"
            )
            max_body = 2000 - len(header) - len(footer) - 10
            msg = header + body[:max_body] + footer
            try:
                requests.post(
                    TIER2_DISCORD_WEBHOOK,
                    json={"content": msg, "flags": 4},
                    timeout=10,
                )
            except Exception as exc:
                report_error("rubricward_autopilot.discord", str(exc))

    print(f"[RUBRICWARD AUTOPILOT] Synthesized {len(dossiers)} Tier 2 Payer MRF & NSA IDR Dossiers -> {DOSSIERS_OUT_PATH}")
    return dossiers


if __name__ == "__main__":
    generate_all_dossiers(dispatch_discord=False)
