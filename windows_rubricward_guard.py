r"""
RubricWard — OS-Level Windows Process Guard (`windows_rubricward_guard.py`).

Ensures `silent_rubricward_watcher.py` is always running in the background:
1. Inspects `.rubricward_watcher_heartbeat.json` for a live PID (`OpenProcess`) and fresh timestamp (< 40 min old).
2. If the watcher process is missing or stalled, spawns a detached background process (`CREATE_NO_WINDOW`).
3. If the nighttime + user-away window is active (`omniscient_auditor.is_nighttime_and_user_away()`), triggers a 3-Pillar `omniscient_auditor.py` check.
"""

from error_telemetry import configure_utf8_stdio

configure_utf8_stdio()

import ctypes
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RUBRICWARD_DIR = Path(__file__).resolve().parent
HEARTBEAT_PATH = RUBRICWARD_DIR / ".rubricward_watcher_heartbeat.json"
WATCHER_SCRIPT = RUBRICWARD_DIR / "silent_rubricward_watcher.py"
PYTHON_EXE = sys.executable


def _is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
        if not handle:
            return False
        exit_code = ctypes.c_ulong(0)
        STILL_ACTIVE = 259
        ok = ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
        ctypes.windll.kernel32.CloseHandle(handle)
        return bool(ok and exit_code.value == STILL_ACTIVE)
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def ensure_watcher_alive() -> dict:
    alive = False
    current_pid = 0

    if HEARTBEAT_PATH.exists():
        try:
            hb = json.loads(HEARTBEAT_PATH.read_text(encoding="utf-8"))
            current_pid = int(hb.get("pid") or 0)
            if _is_pid_running(current_pid):
                alive = True
        except Exception:
            pass

    if alive:
        return {"status": "already_running", "pid": current_pid}

    creationflags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW
    proc = subprocess.Popen(
        [PYTHON_EXE, str(WATCHER_SCRIPT)],
        cwd=str(RUBRICWARD_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    now_iso = datetime.now(timezone.utc).isoformat()
    try:
        HEARTBEAT_PATH.write_text(
            json.dumps({"pid": proc.pid, "updated_at": now_iso, "cycle": 0, "spawned_by": "windows_rubricward_guard"}, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass
    return {"status": "respawned", "pid": proc.pid}


if __name__ == "__main__":
    res = ensure_watcher_alive()
    print(f"[RUBRICWARD PROCESS GUARD] Watcher status: {res}")
