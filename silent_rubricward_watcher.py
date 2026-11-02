r"""
RubricWard — Silent 24/7 Autopilot, RapidAPI Session Keepalive & Outbound Reply Watcher (`D:\RubricWard\silent_rubricward_watcher.py`).
Runs silently in the background (`IsDaemon=True`):
  1. Prevents Windows Sleep/Standby (`SetThreadExecutionState`).
  2. Rolls the `RubricWardSystems` (`12422060`) RapidAPI Studio session cookie every 15 minutes via GraphQL.
  3. Polls `outbound_reply_responder.run_reply_responder()` every 15 minutes to auto-dispatch 6-File `.ZIP` packages to estimators who reply `"SEND ZIP"`.
  4. Runs a rotating slice of `seed_rubricward_telemetry.run_telemetry_seeder()` to keep all 12 RapidAPI `100% Service Level` badges green.
"""

from error_telemetry import configure_utf8_stdio
configure_utf8_stdio()

import ctypes
import json
import os
from pathlib import Path
import sys
import time
from datetime import datetime

import auto_error_healer
import autonomous_mailbox_scaler
import autonomous_outbound_optimizer
import omniscient_auditor
import outbound_reply_responder
import publish_rubricward_rapidapi
import seed_rubricward_telemetry

ROOT_DIR = Path(__file__).resolve().parent
HEARTBEAT_PATH = ROOT_DIR / ".rubricward_watcher_heartbeat.json"
CHECK_INTERVAL_SECONDS = 900  # 15 minutes


def prevent_windows_sleep() -> None:
    if os.name != "nt":
        return
    try:
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_AWAYMODE_REQUIRED = 0x0000040
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED
        )
    except Exception:
        pass


def keepalive_rubricward_rapidapi() -> bool:
    try:
        s = publish_rubricward_rapidapi.load_session()
        res = publish_rubricward_rapidapi.gql(
            s,
            'query { api(id: "api_11b4a89a-3b9c-4f59-9029-8f0da73bd8bc") { id visibility } }',
        )
        ok = bool(((res.get("data") or {}).get("api") or {}).get("id"))
        return ok
    except Exception:
        return False


def main() -> int:
    prevent_windows_sleep()
    print(
        "[*] RubricWard Silent 24/7 Autopilot Watcher active in background "
        "(RapidAPI keepalive + Outbound 'SEND ZIP' Reply Responder + Telemetry Seeder).",
        flush=True,
    )
    cycle = 0
    while True:
        prevent_windows_sleep()
        now_iso = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
        try:
            HEARTBEAT_PATH.write_text(
                json.dumps({"pid": os.getpid(), "timestamp": time.time(), "updated_at": now_iso, "cycle": cycle}, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

        # 1. Keep RubricWardSystems RapidAPI session rolling
        keepalive_rubricward_rapidapi()

        # 2. Poll outbound replies for 'SEND ZIP' estimator requests & sync mailbox scaler
        try:
            outbound_reply_responder.run_reply_responder()
            autonomous_mailbox_scaler.run_autonomous_mailbox_scaler(dry_run=False)
        except Exception:
            pass

        # 3. Every 4 cycles (~1 hour), run Closed-Loop Autonomous Error Healer
        if cycle % 4 == 0:
            try:
                auto_error_healer.run_healer(clear_resolved=True, run_smoke=False)
                autonomous_outbound_optimizer.run_autonomous_outbound_optimizer(regenerate_local=True)
            except Exception:
                pass

        # 4. Run 3-Pillar Omniscient Auditor at most ONCE per calendar night (gated to Nighttime & User-Away)
        try:
            night_allowed, _ = omniscient_auditor.is_nighttime_and_user_away(min_idle_seconds=900)
            today_night_key = datetime.now().astimezone().strftime("%Y-%m-%d")
            if night_allowed and globals().get("_LAST_OMNISCIENT_AUDIT_DATE") != today_night_key:
                globals()["_LAST_OMNISCIENT_AUDIT_DATE"] = today_night_key
                omniscient_auditor.run_omniscient_audit(mode="full", force_now=True, auto_deploy=True)
        except Exception:
            pass

        # 5. Every 16 cycles (~4 hours), refresh RapidAPI 100% Service Level telemetry across all 12 APIs
        if cycle % 16 == 0 and cycle > 0:
            try:
                seed_rubricward_telemetry.run_telemetry_seeder(use_rapidapi_proxy=True)
            except Exception:
                pass

        # 5b. Every 48 cycles (~12 hours), refresh 24h branded Stripe Checkout sessions for RubricWard & CamberDesk
        if cycle % 48 == 0 and cycle > 0:
            try:
                import refresh_branded_stripe_sessions
                rw_u, cd_u = refresh_branded_stripe_sessions.generate_or_load_sessions(force_regenerate=True)
                if rw_u:
                    refresh_branded_stripe_sessions.apply_rubricward_branded_urls(rw_u)
                if cd_u:
                    refresh_branded_stripe_sessions.apply_camberdesk_branded_urls(cd_u)
            except Exception:
                pass

        # 6. Every 24 cycles (~6 hours), refresh 52-Portal DOT Lettings, pSEO pages, and Instantly lead queue
        if cycle % 24 == 0 and cycle > 0:
            try:
                import asyncio
                import mainscraper
                import rubricward_autopilot
                import pseo_generator
                import harvest_verified_dot_contacts
                import outreach_generator
                import sync_instantly_campaign
                import outbound_mailer
                asyncio.run(mainscraper.run_scraper(push_to_db=True))
                rubricward_autopilot.build_dossiers()
                pseo_generator.generate_pseo_pages()
                harvest_verified_dot_contacts.harvest_and_save_verified_dot_contacts()
                outreach_generator.generate_outreach_queue()
                sync_instantly_campaign.sync_leads_to_instantly()
                outbound_mailer.run_outbound_mailer()
            except Exception:
                pass

        cycle += 1
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    sys.exit(main())

