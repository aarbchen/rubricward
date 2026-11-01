"""
Refresh Branded Stripe Checkout Sessions for RubricWard & CamberDesk.
Ensures every checkout link across RubricWard (Option 01 Surgical Alabaster #F2F9F8 & Clinical Teal #0F766E
+ Split Shield & Ledger Logo) and CamberDesk (Warm Architectural Alabaster #FAF8F5 & Blueprint Navy #1E3A8A)
points to a live branded `https://checkout.stripe.com/c/pay/cs_live_...` session with per-brand
`branding_settings` (`display_name`, `icon`, `logo`, `background_color`, `button_color`) rather than
shared `buy.stripe.com` links.
"""

import json
import os
import re
import time
from pathlib import Path
from typing import Dict

import requests
from dotenv import load_dotenv

RUBRICWARD_DIR = Path(r"D:\RubricWard")
CAMBERDESK_DIR = Path(r"D:\CamberDesk")

RUBRICWARD_PRICES = {
    "tier1_monthly": ("price_1UX1DrCGhMI1Ijip9ii9DAJJ", "tier1", "monthly"),
    "tier1_annual":  ("price_1UX1DsCGhMI1IjipZTHNJCnb", "tier1", "annual"),
    "tier2_monthly": ("price_1UX1DtCGhMI1IjiplKs9mqqj", "tier2", "monthly"),
    "tier2_annual":  ("price_1UX1DuCGhMI1IjipvoX6LqRg", "tier2", "annual"),
    "tier3_monthly": ("price_1UX1DvCGhMI1IjipJermub29", "tier3", "monthly"),
    "tier3_annual":  ("price_1UX1DwCGhMI1Ijipt8YrWKjX", "tier3", "annual"),
    "tier4_monthly": ("price_1UX1DyCGhMI1IjipzoXYNULY", "tier4", "monthly"),
    "tier4_annual":  ("price_1UX1DyCGhMI1IjipyDtDW5iE", "tier4", "annual"),
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
    load_dotenv(RUBRICWARD_DIR / ".env")
    sk = (os.getenv("STRIPE_API_KEY") or "").strip()
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
            if int(d.get("expires_at") or 0) - now > 21600 and len(d.get("urls") or {}) == 8:
                rw_urls = d["urls"]
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
                json.dumps({"generated_at": now, "expires_at": expires_at, "urls": rw_urls}, indent=2),
                encoding="utf-8",
            )

    if not force_regenerate and cd_json_path.exists():
        try:
            d = json.loads(cd_json_path.read_text(encoding="utf-8"))
            if int(d.get("expires_at") or 0) - now > 21600 and len(d.get("urls") or {}) == 8:
                cd_urls = d["urls"]
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
                json.dumps({"generated_at": now, "expires_at": expires_at, "urls": cd_urls}, indent=2),
                encoding="utf-8",
            )

    return rw_urls, cd_urls


def apply_rubricward_branded_urls(rw_urls: Dict[str, str]) -> None:
    old_to_tier = {
        "https://buy.stripe.com/bJeaEWePg6FteFid6Q7wA0i": "tier1_monthly",
        "https://buy.stripe.com/5kQcN46iK2pd68MfeY7wA0j": "tier1_annual",
        "https://buy.stripe.com/8x28wOePgd3R68M3wg7wA0k": "tier2_monthly",
        "https://buy.stripe.com/dRmdR8ePg4xl8gU8QA7wA0l": "tier2_annual",
        "https://buy.stripe.com/28E00ibD46Ft2WAaYI7wA0m": "tier3_monthly",
        "https://buy.stripe.com/bJecN46iKfbZ0OsfeY7wA0n": "tier3_annual",
        "https://buy.stripe.com/28E7sK9uWfbZ54I5Eo7wA0o": "tier4_monthly",
        "https://buy.stripe.com/5kQ14m6iK1l940EfeY7wA0p": "tier4_annual",
    }

    # 1. Update D:\RubricWard\build_rubricward_site.py
    site_py = RUBRICWARD_DIR / "build_rubricward_site.py"
    txt = site_py.read_text(encoding="utf-8")
    for old_url, tier_key in old_to_tier.items():
        txt = txt.replace(old_url, rw_urls[tier_key])

    # Also support replacing any previous cs_live_ URLs by tier key in RUBRICWARD_STRIPE_LINKS & catalog
    for tier_key, new_url in rw_urls.items():
        txt = re.sub(
            rf"({tier_key}:\s*')(https://checkout\.stripe\.com/c/pay/cs_live_[^']+)(')",
            lambda m, u=new_url: m.group(1) + u + m.group(3),
            txt,
        )
        txt = re.sub(
            rf"({tier_key}:\s*\{{[^}}]+stripeUrl:\s*')(https://checkout\.stripe\.com/c/pay/cs_live_[^']+)(')",
            lambda m, u=new_url: m.group(1) + u + m.group(3),
            txt,
        )

    # Make sure #stripe-link-tier1..4 and #checkout-modal-direct-stripe-link use info.stripeUrl (direct checkout.stripe.com session)
    txt = txt.replace(
        "if (sl1) sl1.setAttribute('href', 'https://rubricward.com/v1/billing/checkout?plan=tier1&billing=' + billParam);",
        "if (sl1) sl1.setAttribute('href', window.RUBRICWARD_STRIPE_LINKS[k1]);",
    )
    txt = txt.replace(
        "if (sl2) sl2.setAttribute('href', 'https://rubricward.com/v1/billing/checkout?plan=tier2&billing=' + billParam);",
        "if (sl2) sl2.setAttribute('href', window.RUBRICWARD_STRIPE_LINKS[k2]);",
    )
    txt = txt.replace(
        "if (sl3) sl3.setAttribute('href', 'https://rubricward.com/v1/billing/checkout?plan=tier3&billing=' + billParam);",
        "if (sl3) sl3.setAttribute('href', window.RUBRICWARD_STRIPE_LINKS[k3]);",
    )
    txt = txt.replace(
        "if (sl4) sl4.setAttribute('href', 'https://rubricward.com/v1/billing/checkout?plan=tier4&billing=' + billParam);",
        "if (sl4) sl4.setAttribute('href', window.RUBRICWARD_STRIPE_LINKS[k4]);",
    )
    txt = txt.replace(
        'href="https://rubricward.com/v1/billing/checkout?plan=tier1&amp;billing=monthly"',
        f'href="{rw_urls["tier1_monthly"]}"',
    )
    txt = txt.replace(
        'href="https://rubricward.com/v1/billing/checkout?plan=tier2&amp;billing=monthly"',
        f'href="{rw_urls["tier2_monthly"]}"',
    )
    txt = txt.replace(
        'href="https://rubricward.com/v1/billing/checkout?plan=tier3&amp;billing=monthly"',
        f'href="{rw_urls["tier3_monthly"]}"',
    )
    txt = txt.replace(
        'href="https://rubricward.com/v1/billing/checkout?plan=tier4&amp;billing=monthly"',
        f'href="{rw_urls["tier4_monthly"]}"',
    )
    txt = txt.replace(
        "const _brandedHref = 'https://rubricward.com/v1/billing/checkout?plan=' + (_parts[0] || 'tier2') + '&billing=' + (_parts[1] || 'monthly');",
        "const _brandedHref = info.stripeUrl || ('https://rubricward.com/v1/billing/checkout?plan=' + (_parts[0] || 'tier2') + '&billing=' + (_parts[1] || 'monthly'));",
    )
    txt = txt.replace(
        "const resp = await fetch('https://rubricward.com/v1/billing/create-checkout-session', {",
        "const resp = await fetch('https://b2b-contract-parser-api.onrender.com/v1/billing/create-checkout-session', {",
    )
    txt = txt.replace(
        "body: JSON.stringify({ plan, billing, email, tier, customer_email: email, company_name: company, state_dots: states })",
        "body: JSON.stringify({ brand: 'rubricward', plan, billing, email, tier, customer_email: email, company_name: company, state_dots: states })",
    )
    site_py.write_text(txt, encoding="utf-8")

    # 2. Update D:\RubricWard\build_cloudflare_edge_worker.py
    worker_py = RUBRICWARD_DIR / "build_cloudflare_edge_worker.py"
    wtxt = worker_py.read_text(encoding="utf-8")
    for old_url, tier_key in old_to_tier.items():
        wtxt = wtxt.replace(old_url, rw_urls[tier_key])
    for tier_key, new_url in rw_urls.items():
        wtxt = re.sub(
            rf"({tier_key}:\s*')(https://checkout\.stripe\.com/c/pay/cs_live_[^']+)(')",
            lambda m, u=new_url: m.group(1) + u + m.group(3),
            wtxt,
        )
    # Fix v1/billing/checkout/index.html inside build_cloudflare_edge_worker.py so it doesn't corrupt #fid... on checkout.stripe.com URLs
    wtxt = wtxt.replace(
        "const target = base + '?client_reference_id=rubricward_' + tierKey + '_' + billKey + (email ? '&prefilled_email=' + encodeURIComponent(email) : '');",
        "const target = base.startsWith('https://checkout.stripe.com/') ? base : (base + '?client_reference_id=rubricward_' + tierKey + '_' + billKey + (email ? '&prefilled_email=' + encodeURIComponent(email) : ''));",
    )
    # Style v1/billing/checkout/index.html with Option 01 Surgical Alabaster & Clinical Teal
    wtxt = wtxt.replace(
        '<body class="bg-[#FAF8F5] text-[#0A0D14] min-h-screen flex items-center justify-center p-6 font-sans">',
        '<body class="bg-[#F2F9F8] text-[#071C21] min-h-screen flex items-center justify-center p-6 font-sans">',
    )
    wtxt = wtxt.replace(
        '<div class="text-xs font-mono font-bold text-[#059669] uppercase tracking-wider">RUBRICWARD // SELF-SERVE STRIPE CHECKOUT</div>',
        '<div class="text-xs font-mono font-bold text-[#0F766E] uppercase tracking-wider">RUBRICWARD // SELF-SERVE STRIPE CHECKOUT</div>',
    )
    wtxt = wtxt.replace('?client_reference_id=rubricward_tier2_monthly"', '"')
    worker_py.write_text(wtxt, encoding="utf-8")

    # 3. Update D:\RubricWard\verify_rubricward_integrity.py so it verifies the branded checkout.stripe.com URLs
    ver_py = RUBRICWARD_DIR / "verify_rubricward_integrity.py"
    vtxt = ver_py.read_text(encoding="utf-8")
    for old_url, tier_key in old_to_tier.items():
        vtxt = vtxt.replace(old_url, rw_urls[tier_key])
    ver_py.write_text(vtxt, encoding="utf-8")
    print("[RUBRICWARD] Applied 8 branded checkout.stripe.com session URLs across build_rubricward_site.py, build_cloudflare_edge_worker.py, and verify_rubricward_integrity.py")


def apply_camberdesk_branded_urls(cd_urls: Dict[str, str]) -> None:
    old_to_tier = {
        "https://buy.stripe.com/28E00icH8gg32WAb2I7wA0i": "tier1_monthly",
        "https://buy.stripe.com/bJebJ0cH81l968M1o87wA0j": "tier1_annual",
        "https://buy.stripe.com/28E4gybD4fbZap22sc7wA0k": "tier2_monthly",
        "https://buy.stripe.com/aFa6oGdLcaVJcxa8QA7wA0l": "tier2_annual",
        "https://buy.stripe.com/3cI8wOdLcfbZ9kYgj27wA0m": "tier3_monthly",
        "https://buy.stripe.com/7sY00i9uWd3R1Swb2I7wA0n": "tier3_annual",
        "https://buy.stripe.com/aFa9AS0Yqgg3fJm3wg7wA0o": "tier4_monthly",
        "https://buy.stripe.com/14A00i5eG8NB68M7Mw7wA0p": "tier4_annual",
    }

    for target_file in ("build_camberdesk_site.py", "build_cloudflare_edge_worker.py", "verify_camberdesk_integrity.py"):
        fpath = CAMBERDESK_DIR / target_file
        if not fpath.exists():
            continue
        txt = fpath.read_text(encoding="utf-8")
        for old_url, tier_key in old_to_tier.items():
            txt = txt.replace(old_url, cd_urls[tier_key])
        for tier_key, new_url in cd_urls.items():
            txt = re.sub(
                rf"({tier_key}:\s*')(https://checkout\.stripe\.com/c/pay/cs_live_[^']+)(')",
                lambda m, u=new_url: m.group(1) + u + m.group(3),
                txt,
            )
            txt = re.sub(
                rf"({tier_key}:\s*\{{[^}}]+stripeUrl:\s*')(https://checkout\.stripe\.com/c/pay/cs_live_[^']+)(')",
                lambda m, u=new_url: m.group(1) + u + m.group(3),
                txt,
            )
        if target_file == "build_camberdesk_site.py":
            txt = txt.replace(
                "if (sl1) sl1.setAttribute('href', 'https://camberdesk.com/v1/billing/checkout?plan=tier1&billing=' + billParam);",
                "if (sl1) sl1.setAttribute('href', window.CAMBERDESK_STRIPE_LINKS[k1]);",
            )
            txt = txt.replace(
                "if (sl2) sl2.setAttribute('href', 'https://camberdesk.com/v1/billing/checkout?plan=tier2&billing=' + billParam);",
                "if (sl2) sl2.setAttribute('href', window.CAMBERDESK_STRIPE_LINKS[k2]);",
            )
            txt = txt.replace(
                "if (sl3) sl3.setAttribute('href', 'https://camberdesk.com/v1/billing/checkout?plan=tier3&billing=' + billParam);",
                "if (sl3) sl3.setAttribute('href', window.CAMBERDESK_STRIPE_LINKS[k3]);",
            )
            txt = txt.replace(
                "if (sl4) sl4.setAttribute('href', 'https://camberdesk.com/v1/billing/checkout?plan=tier4&billing=' + billParam);",
                "if (sl4) sl4.setAttribute('href', window.CAMBERDESK_STRIPE_LINKS[k4]);",
            )
            txt = txt.replace(
                'href="https://camberdesk.com/v1/billing/checkout?plan=tier1&amp;billing=monthly"',
                f'href="{cd_urls["tier1_monthly"]}"',
            )
            txt = txt.replace(
                'href="https://camberdesk.com/v1/billing/checkout?plan=tier2&amp;billing=monthly"',
                f'href="{cd_urls["tier2_monthly"]}"',
            )
            txt = txt.replace(
                'href="https://camberdesk.com/v1/billing/checkout?plan=tier3&amp;billing=monthly"',
                f'href="{cd_urls["tier3_monthly"]}"',
            )
            txt = txt.replace(
                'href="https://camberdesk.com/v1/billing/checkout?plan=tier4&amp;billing=monthly"',
                f'href="{cd_urls["tier4_monthly"]}"',
            )
            txt = txt.replace(
                "const _brandedHref = 'https://camberdesk.com/v1/billing/checkout?plan=' + (_parts[0] || 'tier2') + '&billing=' + (_parts[1] || 'monthly');",
                "const _brandedHref = info.stripeUrl || ('https://camberdesk.com/v1/billing/checkout?plan=' + (_parts[0] || 'tier2') + '&billing=' + (_parts[1] || 'monthly'));",
            )
            txt = txt.replace(
                "const resp = await fetch('https://camberdesk.com/v1/billing/create-checkout-session', {",
                "const resp = await fetch('https://b2b-contract-parser-api.onrender.com/v1/billing/create-checkout-session', {",
            )
            txt = txt.replace(
                "body: JSON.stringify({ plan, billing, email, tier, customer_email: email, company_name: company, state_dots: states })",
                "body: JSON.stringify({ brand: 'camberdesk', plan, billing, email, tier, customer_email: email, company_name: company, state_dots: states })",
            )
        if target_file == "build_cloudflare_edge_worker.py":
            txt = txt.replace(
                "const target = base + '?client_reference_id=camberdesk_' + tierKey + '_' + billKey + (email ? '&prefilled_email=' + encodeURIComponent(email) : '');",
                "const target = base.startsWith('https://checkout.stripe.com/') ? base : (base + '?client_reference_id=camberdesk_' + tierKey + '_' + billKey + (email ? '&prefilled_email=' + encodeURIComponent(email) : ''));",
            )
            txt = txt.replace("?client_reference_id=camberdesk_tier2_monthly\"", "\"")
        fpath.write_text(txt, encoding="utf-8")
    print("[CAMBERDESK] Applied 8 branded checkout.stripe.com session URLs across build_camberdesk_site.py, build_cloudflare_edge_worker.py, and verify_camberdesk_integrity.py")


if __name__ == "__main__":
    rw, cd = generate_or_load_sessions(force_regenerate=False)
    apply_rubricward_branded_urls(rw)
    apply_camberdesk_branded_urls(cd)
