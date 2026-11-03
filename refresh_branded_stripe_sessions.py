"""
Refresh Branded Stripe Checkout Sessions for RubricWard & CamberDesk (RULE-026).
Ensures every checkout link across RubricWard (Surgical Alabaster #F2F9F8 & Clinical Teal #0F766E)
and CamberDesk (Warm Architectural Alabaster #FAF8F5 & Blueprint Navy #1E3A8A) points to a live
branded `https://checkout.stripe.com/c/pay/cs_live_...` session with per-brand `branding_settings`
(`display_name`, `icon`, `logo`, `background_color`, `button_color`) and neutral parent merchant profile.
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict

import requests
from dotenv import load_dotenv

RUBRICWARD_DIR = Path(r"D:\RubricWard")
CAMBERDESK_DIR = Path(r"D:\CamberDesk")

RUBRICWARD_PRICES = {
    "tier1_monthly": ("price_1UXZSgCGhMI1IjipKtizXJYQ", "tier1", "monthly"),
    "tier1_annual":  ("price_1UXZSiCGhMI1Ijip3Pb4u9WW", "tier1", "annual"),
    "tier2_monthly": ("price_1UXZSkCGhMI1IjiplZtv2IfA", "tier2", "monthly"),
    "tier2_annual":  ("price_1UXZSmCGhMI1IjipWjvgLddS", "tier2", "annual"),
    "tier3_monthly": ("price_1UX1DvCGhMI1IjipJermub29", "tier3", "monthly"),
    "tier3_annual":  ("price_1UXZSqCGhMI1Ijip81RHV6JM", "tier3", "annual"),
    "tier4_monthly": ("price_1UXZSsCGhMI1Ijip2gKfcjte", "tier4", "monthly"),
    "tier4_annual":  ("price_1UXZSvCGhMI1IjipK7SYyQeZ", "tier4", "annual"),
}

CAMBERDESK_PRICES = {
    "tier1_monthly": ("price_1UWoFECGhMI1IjipI9tII9Ur", "tier1", "monthly"),
    "tier1_annual":  ("price_1UWoFECGhMI1IjipR8XoJy11", "tier1", "annual"),
    "tier2_monthly": ("price_1UWoFGCGhMI1IjipPYSJM0RR", "tier2", "monthly"),
    "tier2_annual":  ("price_1UWoFGCGhMI1IjiprXT3gMMp", "tier2", "annual"),
    "tier3_monthly": ("price_1UWoFICGhMI1IjipnZvSjWov", "tier3", "monthly"),
    "tier3_annual":  ("price_1UWoFICGhMI1IjipwNQWLjYY", "tier3", "annual"),
    "tier4_monthly": ("price_1UWoFKCGhMI1IjipGswJ1cUG", "tier4", "monthly"),
    "tier4_annual":  ("price_1UWoFKCGhMI1IjipI2wrHkwd", "tier4", "annual"),
}


def generate_or_load_sessions(force_regenerate: bool = False) -> tuple[Dict[str, str], Dict[str, str]]:
    load_dotenv(RUBRICWARD_DIR / ".env", override=True)
    sk = (os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY") or "").strip()
    acct = (os.getenv("STRIPE_ACCOUNT_ID") or "acct_1Rj7l8CGhMI1Ijip").strip()
    headers = {
        "Authorization": f"Bearer {sk}",
        "Stripe-Livemode": "true",
        "Stripe-Version": "2025-06-30.basil",
        "Stripe-Account": acct,
    }

    rw_json_path = RUBRICWARD_DIR / "stripe_branded_sessions.json"
    cd_json_path = CAMBERDESK_DIR / "stripe_branded_sessions.json"

    now = int(time.time())
    rw_urls: Dict[str, str] = {}
    cd_urls: Dict[str, str] = {}

    if not force_regenerate and rw_json_path.exists():
        try:
            d = json.loads(rw_json_path.read_text(encoding="utf-8"))
            u_map = d.get("urls") or d.get("sessions") or {}
            if int(d.get("expires_at") or 0) - now > 21600 and len(u_map) == 8:
                rw_urls = u_map
        except Exception:
            pass

    if not rw_urls and sk:
        expires_at = now + 86000
        for key, (price_id, plan, billing) in RUBRICWARD_PRICES.items():
            data = {
                "mode": "subscription",
                "line_items[0][price]": price_id,
                "line_items[0][quantity]": "1",
                "success_url": f"https://rubricward.com/?checkout=success&plan={plan}#account",
                "cancel_url": "https://rubricward.com/#checkout",
                "client_reference_id": f"rubricward_{key}",
                "allow_promotion_codes": "true",
                "expires_at": str(expires_at),
                "metadata[brand]": "rubricward",
                "metadata[plan]": plan,
                "metadata[billing]": billing,
                "subscription_data[metadata][brand]": "rubricward",
                "subscription_data[metadata][plan]": plan,
                "subscription_data[metadata][billing]": billing,
                "branding_settings[display_name]": "RubricWard",
                "branding_settings[background_color]": "#F2F9F8",
                "branding_settings[button_color]": "#0F766E",
                "branding_settings[border_style]": "rounded",
                "branding_settings[icon][type]": "file",
                "branding_settings[icon][file]": "file_1UX603CGhMI1Ijip32ZgFajz",
                "branding_settings[logo][type]": "file",
                "branding_settings[logo][file]": "file_1UX604CGhMI1IjipCqf3PdAQ",
            }
            r = requests.post("https://api.stripe.com/v1/checkout/sessions", headers=headers, data=data, timeout=20)
            if r.status_code == 200:
                rw_urls[key] = r.json()["url"]
        if len(rw_urls) == 8:
            rw_json_path.write_text(
                json.dumps({"brand": "rubricward", "generated_at": now, "expires_at": expires_at, "urls": rw_urls, "sessions": rw_urls}, indent=2),
                encoding="utf-8",
            )

    if not force_regenerate and cd_json_path.exists():
        try:
            d = json.loads(cd_json_path.read_text(encoding="utf-8"))
            u_map = d.get("urls") or d.get("sessions") or {}
            if int(d.get("expires_at") or 0) - now > 21600 and len(u_map) == 8:
                cd_urls = u_map
        except Exception:
            pass

    if not cd_urls and sk:
        expires_at = now + 86000
        for key, (price_id, plan, billing) in CAMBERDESK_PRICES.items():
            data = {
                "mode": "subscription",
                "line_items[0][price]": price_id,
                "line_items[0][quantity]": "1",
                "success_url": f"https://camberdesk.com/?checkout=success&plan={plan}#account",
                "cancel_url": "https://camberdesk.com/#checkout",
                "client_reference_id": f"camberdesk_{key}",
                "allow_promotion_codes": "true",
                "expires_at": str(expires_at),
                "metadata[brand]": "camberdesk",
                "metadata[plan]": plan,
                "metadata[billing]": billing,
                "subscription_data[metadata][brand]": "camberdesk",
                "subscription_data[metadata][plan]": plan,
                "subscription_data[metadata][billing]": billing,
                "branding_settings[display_name]": "CamberDesk",
                "branding_settings[background_color]": "#FAF8F5",
                "branding_settings[button_color]": "#1E3A8A",
                "branding_settings[border_style]": "rounded",
                "branding_settings[icon][type]": "file",
                "branding_settings[icon][file]": "file_1UWoK1CGhMI1IjipmLv2iM1F",
                "branding_settings[logo][type]": "file",
                "branding_settings[logo][file]": "file_1UWoK2CGhMI1IjiphUswlc5T",
            }
            r = requests.post("https://api.stripe.com/v1/checkout/sessions", headers=headers, data=data, timeout=20)
            if r.status_code == 200:
                cd_urls[key] = r.json()["url"]
        if len(cd_urls) == 8:
            cd_json_path.write_text(
                json.dumps({"brand": "camberdesk", "generated_at": now, "expires_at": expires_at, "urls": cd_urls, "sessions": cd_urls}, indent=2),
                encoding="utf-8",
            )

    return rw_urls, cd_urls


def apply_branded_urls_to_repo(repo_dir: Path, brand: str, urls: Dict[str, str]) -> None:
    site_py_name = "build_rubricward_site.py" if brand == "rubricward" else "build_camberdesk_site.py"
    site_py = repo_dir / site_py_name
    if not site_py.exists():
        return
    site_txt = site_py.read_text(encoding="utf-8")
    old_map: Dict[str, str] = {}
    for k in urls:
        m = re.search(rf"{k}\s*:\s*'(https://checkout\.stripe\.com/c/pay/cs_live_[^']+)'", site_txt)
        if m:
            old_map[k] = m.group(1)

    for rel in (site_py_name, "build_cloudflare_edge_worker.py", "api_gateway/routers/billing_webhook.py", "outbound_reply_responder.py"):
        fp = repo_dir / rel
        if not fp.exists():
            continue
        txt = fp.read_text(encoding="utf-8")
        for k, old_u in old_map.items():
            txt = txt.replace(old_u, urls[k])
        for tkey, new_u in urls.items():
            txt = re.sub(
                rf"({tkey}[\"']?\s*:\s*[\"'])(https://checkout\.stripe\.com/c/pay/cs_live_[^\s\"']+)([\"'])",
                lambda m, u=new_u: m.group(1) + u + m.group(3),
                txt,
            )
            txt = re.sub(
                rf"({tkey}\s*:\s*\{{[^}}]+stripeUrl:\s*')(https://checkout\.stripe\.com/c/pay/cs_live_[^']+)(')",
                lambda m, u=new_u: m.group(1) + u + m.group(3),
                txt,
            )
        if rel == site_py_name:
            txt = txt.replace(
                "if (d && d.checkout_url && directLinkEl) directLinkEl.setAttribute('href', d.checkout_url);",
                "if (d && d.checkout_url && d.checkout_url.indexOf('checkout.stripe.com/c/pay/cs_live_') !== -1 && directLinkEl) directLinkEl.setAttribute('href', d.checkout_url);",
            )
            txt = txt.replace(
                "if (data && data.checkout_url) {\n            resolvedCheckoutUrl = data.checkout_url;\n          }",
                "if (data && data.checkout_url && data.checkout_url.indexOf('checkout.stripe.com/c/pay/cs_live_') !== -1) {\n            resolvedCheckoutUrl = data.checkout_url;\n          }",
            )
        fp.write_text(txt, encoding="utf-8")

    subprocess.run([sys.executable, str(site_py)], cwd=str(repo_dir), check=False)


def apply_rubricward_branded_urls(urls: Dict[str, str]) -> None:
    apply_branded_urls_to_repo(RUBRICWARD_DIR, "rubricward", urls)


def apply_camberdesk_branded_urls(urls: Dict[str, str]) -> None:
    apply_branded_urls_to_repo(CAMBERDESK_DIR, "camberdesk", urls)


if __name__ == "__main__":
    rw, cd = generate_or_load_sessions(force_regenerate=("--force" in sys.argv))
    if rw:
        apply_rubricward_branded_urls(rw)
    if cd:
        apply_camberdesk_branded_urls(cd)
