r"""
Upgrades `D:\RubricWard` with:
  1. Option M7 (The Split-Shield & Ledger) inside `FAVICON_SVG_XML` and `_sample_logo_pixel()` in `build_camberdesk_site.py`
  2. 3-Way Cross-Brand Isolation (`D:\SignalTender` + `D:\CamberDesk` + `D:\RubricWard`) in `verify_camberdesk_integrity.py`,
     `sync_instantly_campaign.py`, and `.env`
  3. Dedicated Instantly V2 Campaign creation & verified NPI lead sync (`sync_instantly_campaign.py`)
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RW = Path(r"D:\RubricWard")


def update_site_builder_m7_logo() -> None:
    p = RW / "build_camberdesk_site.py"
    txt = p.read_text(encoding="utf-8")

    old_svg = '''FAVICON_SVG_XML = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <rect x="2" y="2" width="60" height="60" rx="14" fill="#FAF8F5" stroke="#0A0D14" stroke-width="3"/>
  <path fill="#0A0D14" d="M32 9A23 23 0 1 0 55 32H32V9Z"/>
  <rect x="36" y="11" width="16" height="16" rx="2.5" fill="#1E3A8A"/>
</svg>
"""'''
    new_svg = '''FAVICON_SVG_XML = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <rect x="2" y="2" width="60" height="60" rx="14" fill="#FAF8F5" stroke="#0A0D14" stroke-width="3"/>
  <path fill="#0A0D14" d="M12 10H32V54C19 48 12 37 12 22V10Z"/>
  <rect x="37" y="10" width="15" height="28" rx="2" fill="#059669"/>
</svg>
"""'''
    txt = txt.replace(old_svg, new_svg)

    old_sample = '''    # Blueprint Navy upper-right quadrant block (with slight rounded corner rx=2.5)
    if 36.0 <= nx <= 52.0 and 11.0 <= ny <= 27.0:
        bx = max(abs(nx - 44.0) - 5.5, 0.0)
        by = max(abs(ny - 19.0) - 5.5, 0.0)
        if math.hypot(bx, by) <= 2.5:
            return navy

    # Obsidian Ink 270-degree compass sector
    dx = nx - 32.0
    dy = ny - 32.0
    if math.hypot(dx, dy) <= 23.0 and not (dx > 0 and dy < 0):
        return obsidian
    return vellum'''

    new_sample = '''    emerald = (5, 150, 105, 255)
    # Option M7 Right Vertical Rubric Ledger block (x in 37..52, y in 10..38, rx=2.0)
    if 37.0 <= nx <= 52.0 and 10.0 <= ny <= 38.0:
        bx = max(abs(nx - 44.5) - 5.5, 0.0)
        by = max(abs(ny - 24.0) - 12.0, 0.0)
        if math.hypot(bx, by) <= 2.0:
            return emerald

    # Option M7 Left Half-Shield (Ward: x in 12..32, y in 10..54)
    if 12.0 <= nx <= 32.0 and 10.0 <= ny <= 54.0:
        if ny <= 22.0:
            return obsidian
        norm_y = (ny - 22.0) / 32.0
        min_x = 12.0 + 20.0 * (norm_y ** 1.85)
        if nx >= min_x:
            return obsidian
    return vellum'''

    assert old_sample in txt, "Could not locate old_sample in build_camberdesk_site.py"
    txt = txt.replace(old_sample, new_sample)
    p.write_text(txt, encoding="utf-8")
    shutil.copy2(p, RW / "build_rubricward_site.py")


def update_env_and_instantly_isolation() -> None:
    env_p = RW / ".env"
    if env_p.exists():
        env_txt = env_p.read_text(encoding="utf-8")
        # Clear CamberDesk's Instantly campaign ID so RubricWard creates its own isolated campaign
        env_txt = re.sub(r"RUBRICWARD_INSTANTLY_CAMPAIGN_ID=.*", "RUBRICWARD_INSTANTLY_CAMPAIGN_ID=", env_txt)
        env_txt = re.sub(r"CAMBERDESK_INSTANTLY_CAMPAIGN_ID=.*", "RUBRICWARD_INSTANTLY_CAMPAIGN_ID=", env_txt)
        env_txt = re.sub(r"RAPIDAPI_EMAIL=.*", "RAPIDAPI_EMAIL=veripayer@gmail.com", env_txt)
        env_txt = re.sub(r"RUBRICWARD_EMAIL=.*", "RUBRICWARD_EMAIL=veripayer@gmail.com", env_txt)
        env_txt = re.sub(r"RAPIDAPI_USERNAME=.*", "RAPIDAPI_USERNAME=RubricWardSystems", env_txt)
        env_txt = re.sub(r"RAPIDAPI_DISPLAY_NAME=.*", "RAPIDAPI_DISPLAY_NAME=RubricWard Systems", env_txt)
        env_p.write_text(env_txt, encoding="utf-8")

    # Update sync_instantly_campaign.py so CamberDesk's campaign ID is blocked and RubricWard uses its own campaign name
    sync_p = RW / "sync_instantly_campaign.py"
    if sync_p.exists():
        s_txt = sync_p.read_text(encoding="utf-8")
        s_txt = s_txt.replace(
            'CAMPAIGN_NAME = "RubricWard — 50-State DOT Planholder & Unit Bid-Tab Outreach"',
            'CAMPAIGN_NAME = "RubricWard — 50-State Payer MRF & NSA IDR Outreach"',
        )
        s_txt = s_txt.replace(
            '"748eecf5-6b63-4dff-b9f2-1d2ff1a4a96f",',
            '"748eecf5-6b63-4dff-b9f2-1d2ff1a4a96f",\n    "e69941d4-b5c0-45a7-ac67-ae8947761d4b",',
        )
        s_txt = s_txt.replace(
            "if existing_id:",
            "if existing_id and existing_id not in SIGNALTENDER_BLOCKED_CAMPAIGN_IDS:",
        )
        sync_p.write_text(s_txt, encoding="utf-8")

    # Also update verify_camberdesk_integrity.py to enforce 3-way zero overlap against BOTH D:\Daas AND D:\CamberDesk
    ver_p = RW / "verify_camberdesk_integrity.py"
    if ver_p.exists():
        v_txt = ver_p.read_text(encoding="utf-8")
        old_loop = '    for st_csv_name in ("govcon_contacts.csv", "campaign_leads.csv"):'
        new_loop = '''    camber_csv_p = r"D:\\CamberDesk\\campaign_leads.csv"
    if os.path.exists(camber_csv_p):
        try:
            with open(camber_csv_p, "r", encoding="utf-8-sig", newline="") as cf:
                for r in csv.DictReader(cf):
                    em = str(r.get("Email") or r.get("email") or "").strip().lower()
                    if "@" in em:
                        st_emails.add(em)
                        st_domains.add(em.split("@", 1)[1])
        except Exception:
            pass
    for st_csv_name in ("govcon_contacts.csv", "campaign_leads.csv"):'''
        if "D:\\\\CamberDesk\\\\campaign_leads.csv" not in v_txt:
            v_txt = v_txt.replace(old_loop, new_loop)
            ver_p.write_text(v_txt, encoding="utf-8")
            shutil.copy2(ver_p, RW / "verify_rubricward_integrity.py")


def main() -> None:
    update_site_builder_m7_logo()
    update_env_and_instantly_isolation()

    for script in [
        "build_camberdesk_site.py",
        "pseo_generator.py",
        "build_cloudflare_edge_worker.py",
        "sync_instantly_campaign.py",
        "verify_rubricward_integrity.py",
        "omniscient_auditor.py",
    ]:
        print(f"\n=== RUNNING {script} ===", flush=True)
        cmd = [sys.executable, str(RW / script)]
        if script == "omniscient_auditor.py":
            cmd.append("--force-now")
        res = subprocess.run(cmd, cwd=str(RW))
        if res.returncode != 0:
            print(f"[ERROR] {script} exited with {res.returncode}")
            sys.exit(res.returncode)


if __name__ == "__main__":
    main()

