r"""
RubricWard (`D:\RubricWard`) — Full Pipeline Builder & Verifier (`run_full_build.py`).
"""

import shutil
import subprocess
import sys
from pathlib import Path

RW = Path(r"D:\RubricWard")


def main() -> None:
    # 1. Fix raw docstring in bootstrap_rubricward_universe.py
    b_file = RW / "bootstrap_rubricward_universe.py"
    b_txt = b_file.read_text(encoding="utf-8").replace('"""Updates', 'r"""Updates')
    b_file.write_text(b_txt, encoding="utf-8")

    # 2. Update generate_rapidapi_kit.py to render Option M7 (Split-Shield & Ledger) & use https://rubricward.com
    g_file = RW / "generate_rapidapi_kit.py"
    g_txt = g_file.read_text(encoding="utf-8")
    g_txt = g_txt.replace("https://api.rubricward.com", "https://rubricward.com")
    g_txt = g_txt.replace(
        "if dist <= radius and not (dx > 0 and dy < 0):",
        "if 94 <= x <= 250 and 78 <= y <= 422 and (y <= 172 or x >= 94.0 + 156.0 * (((y - 172.0) / 250.0) ** 1.85)):",
    )
    g_file.write_text(g_txt, encoding="utf-8")

    # 3. Run pipeline scripts in order
    scripts = [
        "harvest_verified_dot_contacts.py",
        "pseo_generator.py",
        "build_camberdesk_site.py",
        "camberdesk_autopilot.py",
        "outreach_generator.py",
        "generate_rapidapi_kit.py",
        "build_cloudflare_edge_worker.py",
    ]
    for script in scripts:
        print(f"\n=== RUNNING {script} ===", flush=True)
        res = subprocess.run([sys.executable, str(RW / script)], cwd=str(RW))
        if res.returncode != 0:
            print(f"[ERROR] {script} exited with code {res.returncode}")
            sys.exit(res.returncode)

    # Sync named wrappers
    for s_name, d_name in [
        ("build_camberdesk_site.py", "build_rubricward_site.py"),
        ("camberdesk_autopilot.py", "rubricward_autopilot.py"),
        ("verify_camberdesk_integrity.py", "verify_rubricward_integrity.py"),
        ("silent_camberdesk_watcher.py", "silent_rubricward_watcher.py"),
        ("windows_camberdesk_guard.py", "windows_rubricward_guard.py"),
        ("publish_camberdesk_rapidapi.py", "publish_rubricward_rapidapi.py"),
        ("seed_camberdesk_telemetry.py", "seed_rubricward_telemetry.py"),
        ("harvest_verified_dot_contacts.py", "harvest_verified_npi_contacts.py"),
    ]:
        if (RW / s_name).exists():
            shutil.copy2(RW / s_name, RW / d_name)

    print("\n=== RUNNING verify_rubricward_integrity.py ===", flush=True)
    res_v = subprocess.run([sys.executable, str(RW / "verify_rubricward_integrity.py")], cwd=str(RW))
    sys.exit(res_v.returncode)


if __name__ == "__main__":
    main()

