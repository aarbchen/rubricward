r"""
RubricWard — Silent 24/7 Autopilot, Self-Healing, RapidAPI Keepalive & Outbound Reply Watcher (`D:\RubricWard\silent_rubricward_watcher.py`).
Runs silently in the background (`IsDaemon=True`):
  1. Prevents Windows Sleep/Standby (`SetThreadExecutionState`).
  2. Rolls the `RubricWardSystems` (`12422060`) RapidAPI Studio session cookie every 15 minutes via GraphQL.
  3. Runs `outbound_reply_responder.py`, `autonomous_mailbox_scaler.py`, `autonomous_outbound_optimizer.py`, and
     `auto_error_healer.py --clear-resolved` every 15 minutes in fresh subprocesses so code updates take effect immediately.
  4. If `auto_error_healer.py` detects any unhealed error (`returncode != 0`), emits `[WAKEUP_AGENT: SELF_HEALING_REQUIRED]`
     and exits (`0`) to immediately wake the AI coding agent in Antigravity to fix the root cause without waiting for user input.
"""

from error_telemetry import configure_utf8_stdio
configure_utf8_stdio()

import ctypes
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime

import omniscient_auditor
import publish_rubricward_rapidapi

ROOT_DIR = Path(__file__).resolve().parent
HEARTBEAT_PATH = ROOT_DIR / ".rubricward_watcher_heartbeat.json"
CHECK_INTERVAL_SECONDS = 900  # 15 minutes


def prevent_windows_sleep() -> None:
    if os.name != "nt":
        return
    try:
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_AWAYMODE_REQUIRED = 0x00000040
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
        return bool(((res.get("data") or {}).get("api") or {}).get("id"))
    except Exception:
        return False


def main() -> int:
    prevent_windows_sleep()
    python_exe = sys.executable
    no_win_flag = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    print(
        "[*] RubricWard Silent 24/7 Autopilot & Self-Healing Watcher active in background "
        "(15m Subprocess Error Healer + Outbound Optimizer + Reply Responder + RapidAPI Keepalive).",
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

        # 2. Every 15m cycle: run reply responder, mailbox scaler, outbound optimizer, and error healer in fresh subprocesses
        for script_args, t_out in (
            (["outbound_reply_responder.py"], 180),
            (["autonomous_mailbox_scaler.py"], 180),
            (["autonomous_outbound_optimizer.py"], 240),
        ):
            try:
                subprocess.run(
                    [python_exe, str(ROOT_DIR / script_args[0]), *script_args[1:]],
                    cwd=str(ROOT_DIR),
                    capture_output=True,
                    text=True,
                    timeout=t_out,
                    creationflags=no_win_flag,
                )
            except Exception:
                pass

        try:
            healer_res = subprocess.run(
                [python_exe, str(ROOT_DIR / "auto_error_healer.py"), "--clear-resolved"],
                cwd=str(ROOT_DIR),
                capture_output=True,
                text=True,
                timeout=240,
                creationflags=no_win_flag,
            )
            if healer_res.returncode != 0:
                tail_out = (healer_res.stdout or "")[-1500:] + "\n" + (healer_res.stderr or "")[-800:]
                print(
                    "\n[WAKEUP_AGENT: SELF_HEALING_REQUIRED]\n"
                    f"RubricWard auto_error_healer.py detected unhealed issue(s) (exit={healer_res.returncode}):\n"
                    f"{tail_out}\n"
                    "Please diagnose and fix the reported RubricWard issue immediately, codify a prevention rule, "
                    "and restart silent_rubricward_watcher.py.",
                    flush=True,
                )
                return 0
        except Exception:
            pass

        # 3. Run 3-Pillar Omniscient Auditor at most ONCE per calendar night (gated to Nighttime & User-Away)
        try:
            night_allowed, _ = omniscient_auditor.is_nighttime_and_user_away(min_idle_seconds=900)
            today_night_key = datetime.now().astimezone().strftime("%Y-%m-%d")
            if night_allowed and globals().get("_LAST_OMNISCIENT_AUDIT_DATE") != today_night_key:
                globals()["_LAST_OMNISCIENT_AUDIT_DATE"] = today_night_key
                subprocess.run(
                    [python_exe, str(ROOT_DIR / "omniscient_auditor.py"), "--mode", "full", "--force-now", "--auto-deploy"],
                    cwd=str(ROOT_DIR),
                    capture_output=True,
                    text=True,
                    timeout=900,
                    creationflags=no_win_flag,
                )
        except Exception:
            pass

        # 4. Every 16 cycles (~4 hours), refresh RapidAPI 100% Service Level telemetry across all 12 APIs
        if cycle % 16 == 0 and cycle > 0:
            try:
                subprocess.run(
                    [python_exe, str(ROOT_DIR / "seed_rubricward_telemetry.py")],
                    cwd=str(ROOT_DIR),
                    capture_output=True,
                    text=True,
                    timeout=300,
                    creationflags=no_win_flag,
                )
            except Exception:
                pass

        # 5. Every 48 cycles (~12 hours), refresh 24h branded Stripe Checkout sessions for RubricWard & CamberDesk
        if cycle % 48 == 0 and cycle > 0:
            try:
                subprocess.run(
                    [python_exe, str(ROOT_DIR / "refresh_branded_stripe_sessions.py"), "--force"],
                    cwd=str(ROOT_DIR),
                    capture_output=True,
                    text=True,
                    timeout=90,
                    creationflags=no_win_flag,
                )
            except Exception:
                pass

        # 6. Every 24 cycles (~6 hours), refresh 52-Portal Payer MRF Cohorts, pSEO pages, and Instantly lead queue
        if cycle % 24 == 0 and cycle > 0:
            for sc_name in (
                "mainscraper.py",
                "rubricward_autopilot.py",
                "pseo_generator.py",
                "harvest_verified_dot_contacts.py",
                "outreach_generator.py",
                "sync_instantly_campaign.py",
                "outbound_mailer.py",
            ):
                try:
                    subprocess.run(
                        [python_exe, str(ROOT_DIR / sc_name)],
                        cwd=str(ROOT_DIR),
                        capture_output=True,
                        text=True,
                        timeout=300,
                        creationflags=no_win_flag,
                    )
                except Exception:
                    pass

        cycle += 1
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    sys.exit(main())
