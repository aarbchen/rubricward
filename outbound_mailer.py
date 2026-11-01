r"""
RubricWard — Built-In Zero-Cost Outbound Drip Sender, Auto-Ramp Scheduler & Welcome Dossier Mailer
(`D:\RubricWard\outbound_mailer.py`).
Dispatches personalized, state-matched 2-step DOT Planholder, 2nd-Place MLOT & DBE ITB sequences from
`campaign_leads.csv` with:
  1. Automatic Post-Warmup Volume Ramp (`compute_dynamic_daily_limit()`):
     - Scales automatically by live RubricWard Instantly mailbox count (`*rubricward*`).
  2. Strict Google DNS MX Verification (`verify_email_domain_mx()`):
     - Blocks any domain without a valid live MX record before staging or sending.
"""

from error_telemetry import configure_utf8_stdio, report_error
configure_utf8_stdio()

import argparse
import csv
from datetime import datetime, timezone, date
import json
import math
import os
from typing import Any, Dict, List, Optional, Tuple
import requests
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

CAMPAIGN_CSV_PATH = os.path.join(BASE_DIR, "campaign_leads.csv")
SENT_LOG_PATH = os.path.join(BASE_DIR, "sent_outreach_log.json")
OUTBOX_QUEUE_PATH = os.path.join(BASE_DIR, "outbox_ready_queue.json")
MX_CACHE_PATH = os.path.join(BASE_DIR, "dns_mx_cache.json")

OUTBOUND_LAUNCH_DATE_STR = (os.getenv("OUTBOUND_LAUNCH_DATE") or "2026-11-02").strip()
INSTANTLY_API_KEY = (os.getenv("INSTANTLY_API_KEY") or "").strip()

_MX_CACHE: Optional[Dict[str, bool]] = None


def verify_email_domain_mx(email: str) -> bool:
    """
    Verifies via Google DNS-over-HTTPS (`https://dns.google/resolve?type=MX`) that the recipient's
    domain has a valid, non-null, non-parked MX record so zero synthetic/dead domains ever bounce.
    """
    global _MX_CACHE
    if _MX_CACHE is None:
        _MX_CACHE = {}
        if os.path.exists(MX_CACHE_PATH):
            try:
                with open(MX_CACHE_PATH, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        _MX_CACHE.update({k: bool(v) for k, v in loaded.items()})
            except Exception:
                pass

    clean = str(email or "").strip().lower()
    if "@" not in clean:
        return False
    dom = clean.split("@", 1)[1].strip()
    if not dom or "." not in dom or dom.endswith(".example.com"):
        return False
    if dom in _MX_CACHE:
        return _MX_CACHE[dom]

    valid = False
    parked_mx_tokens = ("parklogic", "sedoparking", "above.com", "bodis", "eftydns", "parkingcrew", "localhost")
    try:
        import re as _re
        import subprocess as _sp
        out = _sp.check_output(
            ["nslookup", "-type=mx", dom],
            stderr=_sp.STDOUT,
            timeout=4,
            text=True,
        )
        for m in _re.finditer(r"mail exchanger\s*=\s*(?:\d+\s+)?([^\s\r\n]+)", out, _re.I):
            mx_h = m.group(1).rstrip(".").lower()
            if mx_h and mx_h != "." and "0.0.0.0" not in mx_h and "(root)" not in mx_h and not any(pk in mx_h for pk in parked_mx_tokens):
                valid = True
                break
    except Exception:
        valid = False

    _MX_CACHE[dom] = valid
    try:
        with open(MX_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(_MX_CACHE, f, indent=2)
    except Exception:
        pass
    return valid


def is_instantly_account_warmed(acct: Dict[str, Any], min_score: int = 85) -> bool:
    if not isinstance(acct, dict) or int(acct.get("status") or 0) != 1:
        return False
    score = int(acct.get("stat_warmup_score") or 0)
    return score >= min_score


def _detect_live_rubricward_mailbox_count(fallback: int = 3) -> int:
    if not INSTANTLY_API_KEY:
        return fallback
    try:
        r = requests.get(
            "https://api.instantly.ai/api/v2/accounts?limit=100",
            headers={"Authorization": f"Bearer {INSTANTLY_API_KEY}"},
            timeout=6,
        )
        if r.status_code == 200:
            items = (r.json() or {}).get("items") or []
            cd_items = [
                x for x in items
                if "rubricward" in str(x.get("email") or "").lower()
                and is_instantly_account_warmed(x)
            ]
            if cd_items:
                return len(cd_items)
    except Exception:
        pass
    return fallback


def compute_dynamic_daily_limit(now_utc: Optional[datetime] = None) -> Tuple[int, int, str]:
    override = (os.getenv("OUTBOUND_DAILY_LIMIT_OVERRIDE") or "").strip()
    if override.isdigit() and int(override) > 0:
        d_cap = int(override)
        return d_cap, max(1, math.ceil(d_cap / 4)), f"Manual Override ({d_cap}/day)"

    mb_raw = (os.getenv("OUTBOUND_MAILBOX_COUNT") or "3").strip()
    env_mb_count = max(1, int(mb_raw)) if mb_raw.isdigit() else 3
    mailbox_count = _detect_live_rubricward_mailbox_count(fallback=env_mb_count)
    scale_factor = mailbox_count / 2.0

    now_dt = now_utc or datetime.now(timezone.utc)
    today_d = now_dt.date()
    try:
        launch_d = date.fromisoformat(OUTBOUND_LAUNCH_DATE_STR)
    except Exception:
        launch_d = date(2026, 11, 2)

    days_since_launch = (today_d - launch_d).days
    if days_since_launch <= 2:
        d_cap = max(15, mailbox_count * 5)
        c_cap = max(1, math.ceil(d_cap / 4))
        return d_cap, c_cap, f"Ramp Phase 1 ({d_cap}/day | {c_cap}/cron across {mailbox_count} mailboxes)"
    if days_since_launch <= 6:
        d_cap = max(30, mailbox_count * 10)
        c_cap = max(1, math.ceil(d_cap / 4))
        return d_cap, c_cap, f"Ramp Phase 2 ({d_cap}/day | {c_cap}/cron across {mailbox_count} mailboxes)"
    if days_since_launch <= 13:
        d_cap = max(60, mailbox_count * 20)
        c_cap = max(1, math.ceil(d_cap / 4))
        return d_cap, c_cap, f"Ramp Phase 3 ({d_cap}/day | {c_cap}/cron across {mailbox_count} mailboxes)"
    d_cap = max(90, mailbox_count * 30)
    c_cap = max(1, math.ceil(d_cap / 4))
    return d_cap, c_cap, f"Full Warmed Cadence ({d_cap}/day | {c_cap}/cron across {mailbox_count} mailboxes)"


if __name__ == "__main__":
    d_cap, c_cap, label = compute_dynamic_daily_limit()
    print(json.dumps({"daily_cap": d_cap, "per_cron_cap": c_cap, "phase": label}, indent=2))
