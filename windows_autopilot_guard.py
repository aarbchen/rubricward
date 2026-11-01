r"""
RubricWard — OS-Level Windows Task Scheduler Watchdog (`D:\RubricWard\windows_autopilot_guard.py`).
===================================================================================================
Runs independently of VS Code via Windows Task Scheduler (`\RubricWard_Autopilot_Guard`)
every 30 minutes and at Windows logon.

Responsibilities:
  1. Verifies whether `silent_rubricward_watcher.py` is actively running by checking
     `.rubricward_watcher_heartbeat.json` and verifying the Windows PID.
  2. Polls `outbound_reply_responder.run_reply_responder()` 24/7 so estimators replying
     "SEND ZIP" on Monday–Friday always receive their 6-File OpenXML (.DOCX + .XLSX) Bid Package
     and live dossier link even if VS Code is closed or reset.
  3. Respawns `silent_rubricward_watcher.py` via `CREATE_NO_WINDOW` whenever it is not running.
"""

from error_telemetry import configure_utf8_stdio, report_error
configure_utf8_stdio()

import ctypes
import json
import os
import subprocess
import sys
import time
from dotenv import load_dotenv

import auto_error_healer
import outbound_reply_responder
import publish_rubricward_rapidapi

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

HEARTBEAT_PATH = os.path.join(BASE_DIR, ".rubricward_watcher_heartbeat.json")
MAX_HEARTBEAT_AGE_SECONDS = 2100  # 35 minutes


def is_pid_running_windows(pid: int) -> bool:
    """Return True if a Windows process with the given PID is currently alive."""
    if pid <= 0:
        return False
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
    if not handle:
        return False
    try:
        exit_code = ctypes.c_ulong()
        if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return exit_code.value == STILL_ACTIVE
        return True
    finally:
        kernel32.CloseHandle(handle)


def is_watcher_alive() -> tuple[bool, str]:
    """Check whether `silent_rubricward_watcher.py` is alive via heartbeat file + Windows PID."""
    if not os.path.exists(HEARTBEAT_PATH):
        return False, "No heartbeat file (.rubricward_watcher_heartbeat.json)"
    try:
        with open(HEARTBEAT_PATH, "r", encoding="utf-8") as f:
            hb = json.load(f)
        pid = int(hb.get("pid") or 0)
        ts = float(hb.get("timestamp") or 0)
        if not is_pid_running_windows(pid):
            return False, f"Watcher PID {pid} is no longer running"
        if ts > 0 and (time.time() - ts) > MAX_HEARTBEAT_AGE_SECONDS:
            return False, f"Watcher heartbeat is stale ({int(time.time() - ts)}s old, PID {pid})"
        return True, f"PID {pid} active"
    except Exception as exc:
        return False, f"Heartbeat check error: {exc}"


def main() -> int:
    # 1. Keep RapidAPI session alive
    try:
        s = publish_rubricward_rapidapi.load_session()
        publish_rubricward_rapidapi.gql(
            s,
            'query { api(id: "api_11b4a89a-3b9c-4f59-9029-8f0da73bd8bc") { id visibility } }',
        )
    except Exception:
        pass

    # 2. Poll outbound replies 24/7 even if VS Code is closed or reset
    try:
        outbound_reply_responder.run_reply_responder()
    except Exception:
        pass

    python_exe = r"D:\Daas\daas_env\Scripts\python.exe"
    if not os.path.exists(python_exe):
        python_exe = sys.executable
    no_win_flag = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0

    alive, detail = is_watcher_alive()
    if not alive:
        try:
            watcher_script = os.path.join(BASE_DIR, "silent_rubricward_watcher.py")
            proc = subprocess.Popen([python_exe, watcher_script], cwd=BASE_DIR, creationflags=no_win_flag)
            print(f"[*] Respawned silent_rubricward_watcher.py (PID {proc.pid})", flush=True)
        except Exception as exc:
            report_error("windows_autopilot_guard.py", f"Failed to respawn silent_rubricward_watcher.py: {exc}")

    if alive:
        print(f"[+] RubricWard Watcher alive: {detail}", flush=True)
        return 0

    try:
        auto_error_healer.run_healer(clear_resolved=True, run_smoke=False)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        report_error("windows_autopilot_guard.py", f"Watchdog exception: {exc}")
        sys.exit(1)

