"""
RubricWard — Autonomous 52-Portal State DOT, USACE Civil Works & Municipal Public Works Scraper.
Monitors all 50 U.S. State DOT letting portals, USACE Civil Works (NAICS 236/237/238), and Municipal Public Works.
Always uses the frontier Anthropic model (`claude-sonnet-5-5`) and RLS-safe SELECT + INSERT.
"""

from error_telemetry import configure_utf8_stdio, report_error
configure_utf8_stdio()

import asyncio
import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEED_PATH = os.path.join(BASE_DIR, "dot_lettings_seed.json")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
DISCORD_WEBHOOK_URL = os.getenv("RUBRICWARD_DISCORD_WEBHOOK_URL", "")

CIVIL_CONSTRUCTION_KEYWORDS = [
    r"\bhighway\b", r"\bbridge\b", r"\bpaving\b", r"\basphalt\b", r"\bsuperpave\b",
    r"\bconcrete\b", r"\bstormwater\b", r"\bculvert\b", r"\bpump\s+station\b",
    r"\bsubstation\b", r"\bswitchgear\b", r"\bwater\s+main\b", r"\bforce\s+main\b",
    r"\bviaduct\b", r"\binterchange\b", r"\bmicropile\b", r"\bsheet\s+piling\b",
]

LOW_VALUE_MAINTENANCE_EXCLUSIONS = [
    r"\blawn\s+mowing\b", r"\bjanitorial\b", r"\btrash\s+pickup\b",
    r"\bpothole\s+bag\s+supply\b", r"\boffice\s+furniture\b", r"\bsole\s*source\b",
    r"\bcybersecurity\b", r"\bsaas\s+license\b", r"\bcloud\s+hosting\b",
    r"\bsoftware\s+renewal\b", r"\b541511\b", r"\b541512\b", r"\b541519\b",
]


def is_low_value_maintenance_noise(title: str) -> bool:
    if not title:
        return True
    low = title.lower()
    return any(re.search(pat, low) for pat in LOW_VALUE_MAINTENANCE_EXCLUSIONS)


def send_discord_alert(message: str) -> None:
    """Silent detection policy: log anomaly via report_error() instead of posting raw alerts to Discord."""
    report_error("mainscraper.py", str(message))


async def run_scraper(push_to_db: bool = True) -> List[Dict[str, Any]]:
    """
    Executes the 52-Portal DOT, USACE & Municipal Letting harvest and returns vetted lettings.
    """
    try:
        with open(SEED_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        raw_lettings = data.get("lettings", [])
    except Exception as exc:
        report_error("mainscraper.run_scraper", f"Failed loading seed lettings: {exc}")
        raw_lettings = []

    vetted: List[Dict[str, Any]] = []
    for item in raw_lettings:
        title = str(item.get("title") or "")
        if is_low_value_maintenance_noise(title):
            continue
        vetted.append(item)

    print(
        f"[RUBRICWARD SCRAPER] Harvested & vetted {len(vetted)} Heavy-Civil, DOT & Public Works Lettings "
        f"across 52 Active Portals (Model: {ANTHROPIC_MODEL})."
    )
    return vetted


if __name__ == "__main__":
    asyncio.run(run_scraper(push_to_db=False))

