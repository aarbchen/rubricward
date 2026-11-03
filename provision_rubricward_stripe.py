r"""
Provisions dedicated Stripe Business Icon/Logo Files, 4 Products, 8 Prices, and 8 Payment Links for RubricWard
via the Stripe REST API (`STRIPE_API_KEY`), and wires them across all files in `D:\RubricWard`.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
import requests
from dotenv import load_dotenv

RW = Path(r"D:\RubricWard")
load_dotenv(dotenv_path=str(RW / ".env"))

STRIPE_API_KEY = (os.getenv("STRIPE_API_KEY") or "").strip()
STRIPE_ACCOUNT_ID = (os.getenv("STRIPE_ACCOUNT_ID") or "acct_1Rj7l8CGhMI1Ijip").strip()
STRIPE_HEADERS = {
    "Authorization": f"Bearer {STRIPE_API_KEY}",
    "Stripe-Livemode": "true",
    "Stripe-Version": "2025-06-30.basil",
    "Stripe-Account": STRIPE_ACCOUNT_ID,
}

# CamberDesk's 8 Stripe Payment Links + IDs to replace in D:\RubricWard
CAMBER_LINKS = [
    ("tier1", "monthly", "Tier 1 // ClaimWire Pro", 19900, "month", "prod_VXu3H2MxYFc7Nz", "price_1UWoFECGhMI1IjipI9tII9Ur", "plink_1UWoFFCGhMI1Ijipxvc2m9bk", "https://checkout.stripe.com/c/pay/cs_live_b1MSisHNYwegSUQDFzb24tPp1uddpqUEc9LV1kVq1q3LJx9g2bx4BzXFBd#fidnandhYHdWcXxpYCc%2FJ2FgY2RwaXEnKSd2cGd2ZndsdXFsamtQa2x0cGBrYHZ2QGtkZ2lgYSc%2FY2RpdmApJ2JzJz81KSdkdWxOYHwnPyd1blppbHNgWjA0V28yaT1GQm1ITDRMb2x1ZE9cN3VRUncyb3xLXzVRdjNyMEdJRjFtQUZpNXQ2Y0xIbG9tdmNtUXNtfU1XQ0Y1MnFDSlViXDI3NlFyYWhKV2dJVUhDbDwwNTV0VWxAfXxTRycpJ2N3amhWYHdzYHcnP3F3cGApJ2dkZm5id2pwa2FGamlqdyc%2FJyZjN2M8Yz0nKSdpZHxqcHFRfHVgJz8naHBpcWxabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl"),
    ("tier1", "annual", "Tier 1 // ClaimWire Pro", 199000, "year", "prod_VXu3H2MxYFc7Nz", "price_1UWoFECGhMI1IjipR8XoJy11", "plink_1UWoFFCGhMI1IjiphcYr5n2N", "https://checkout.stripe.com/c/pay/cs_live_b1giRGPpNBu8Dftx1eP71st2wkyW5BW6K2C2VFo629D0HKLjTiF9t52kDa#fidnandhYHdWcXxpYCc%2FJ2FgY2RwaXEnKSd2cGd2ZndsdXFsamtQa2x0cGBrYHZ2QGtkZ2lgYSc%2FY2RpdmApJ2JzJz81KSdkdWxOYHwnPyd1blppbHNgWjA0V28yaT1GQm1ITDRMb2x1ZE9cN3VRUncyb3xLXzVRdjNyMEdJRjFtQUZpNXQ2Y0xIbG9tdmNtUXNtfU1XQ0Y1MnFDSlViXDI3NlFyYWhKV2dJVUhDbDwwNTV0VWxAfXxTRycpJ2N3amhWYHdzYHcnP3F3cGApJ2dkZm5id2pwa2FGamlqdyc%2FJyZjN2M8Yz0nKSdpZHxqcHFRfHVgJz8naHBpcWxabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl"),
    ("tier2", "monthly", "Tier 2 // RubricWard Autopilot", 49900, "month", "prod_VXu31y8EjRPow0", "price_1UWoFGCGhMI1IjipPYSJM0RR", "plink_1UWoFHCGhMI1IjipWLGhSFzc", "https://checkout.stripe.com/c/pay/cs_live_b1N6b82qvV2BN8qhghGEUPyIF9ICP7IXHuXUFqaMqgI00Cz0njCBRVl1W5#fidnandhYHdWcXxpYCc%2FJ2FgY2RwaXEnKSd2cGd2ZndsdXFsamtQa2x0cGBrYHZ2QGtkZ2lgYSc%2FY2RpdmApJ2JzJz81KSdkdWxOYHwnPyd1blppbHNgWjA0V28yaT1GQm1ITDRMb2x1ZE9cN3VRUncyb3xLXzVRdjNyMEdJRjFtQUZpNXQ2Y0xIbG9tdmNtUXNtfU1XQ0Y1MnFDSlViXDI3NlFyYWhKV2dJVUhDbDwwNTV0VWxAfXxTRycpJ2N3amhWYHdzYHcnP3F3cGApJ2dkZm5id2pwa2FGamlqdyc%2FJyZjN2M8Yz0nKSdpZHxqcHFRfHVgJz8naHBpcWxabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl"),
    ("tier2", "annual", "Tier 2 // RubricWard Autopilot", 449000, "year", "prod_VXu31y8EjRPow0", "price_1UWoFGCGhMI1Ijip41P8R2u9", "plink_1UWoFICGhMI1IjiprR2N9f4p", "https://checkout.stripe.com/c/pay/cs_live_b1OoxqkajgFoZXavkbhXh0hKywmCN9XIcGAzmTolkkZPG72G5VSzzip1e5#fidnandhYHdWcXxpYCc%2FJ2FgY2RwaXEnKSd2cGd2ZndsdXFsamtQa2x0cGBrYHZ2QGtkZ2lgYSc%2FY2RpdmApJ2JzJz81KSdkdWxOYHwnPyd1blppbHNgWjA0V28yaT1GQm1ITDRMb2x1ZE9cN3VRUncyb3xLXzVRdjNyMEdJRjFtQUZpNXQ2Y0xIbG9tdmNtUXNtfU1XQ0Y1MnFDSlViXDI3NlFyYWhKV2dJVUhDbDwwNTV0VWxAfXxTRycpJ2N3amhWYHdzYHcnP3F3cGApJ2dkZm5id2pwa2FGamlqdyc%2FJyZjN2M8Yz0nKSdpZHxqcHFRfHVgJz8naHBpcWxabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl"),
    ("tier3", "monthly", "Tier 3 // 6-File Appeal & Bid Compiler", 149900, "month", "prod_VXu3hK7nLp2qW9", "price_1UWoFJCGhMI1Ijip9wK4xL2m", "plink_1UWoFKCGhMI1IjipbY8xP1qR", "https://checkout.stripe.com/c/pay/cs_live_b1ZO7QN9P5SoNVIYdlYbQK6lX28RigNTDyvF2t43d6K5kXnKnbS2uhhEVD#fidnandhYHdWcXxpYCc%2FJ2FgY2RwaXEnKSd2cGd2ZndsdXFsamtQa2x0cGBrYHZ2QGtkZ2lgYSc%2FY2RpdmApJ2JzJz81KSdkdWxOYHwnPyd1blppbHNgWjA0V28yaT1GQm1ITDRMb2x1ZE9cN3VRUncyb3xLXzVRdjNyMEdJRjFtQUZpNXQ2Y0xIbG9tdmNtUXNtfU1XQ0Y1MnFDSlViXDI3NlFyYWhKV2dJVUhDbDwwNTV0VWxAfXxTRycpJ2N3amhWYHdzYHcnP3F3cGApJ2dkZm5id2pwa2FGamlqdyc%2FJyZjN2M8Yz0nKSdpZHxqcHFRfHVgJz8naHBpcWxabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl"),
    ("tier3", "annual", "Tier 3 // 6-File Appeal & Bid Compiler", 1490000, "year", "prod_VXu3hK7nLp2qW9", "price_1UWoFJCGhMI1Ijip3mN7vQ8z", "plink_1UWoFLCGhMI1IjipdT5mW9xK", "https://checkout.stripe.com/c/pay/cs_live_b1r58UabGL8K9ScaH6PO7p1pOoPNH9Sxdh9gDquk1GthfkdMffsH358Wu3#fidnandhYHdWcXxpYCc%2FJ2FgY2RwaXEnKSd2cGd2ZndsdXFsamtQa2x0cGBrYHZ2QGtkZ2lgYSc%2FY2RpdmApJ2JzJz81KSdkdWxOYHwnPyd1blppbHNgWjA0V28yaT1GQm1ITDRMb2x1ZE9cN3VRUncyb3xLXzVRdjNyMEdJRjFtQUZpNXQ2Y0xIbG9tdmNtUXNtfU1XQ0Y1MnFDSlViXDI3NlFyYWhKV2dJVUhDbDwwNTV0VWxAfXxTRycpJ2N3amhWYHdzYHcnP3F3cGApJ2dkZm5id2pwa2FGamlqdyc%2FJyZjN2M8Yz0nKSdpZHxqcHFRfHVgJz8naHBpcWxabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl"),
    ("tier4", "monthly", "Tier 4 // Enterprise RCM & ERP OEM", 249900, "month", "prod_VXu3zM9wQr4tY1", "price_1UWoFMCGhMI1Ijip7pL2kR9x", "plink_1UWoFNCGhMI1IjipfH4nZ8vM", "https://checkout.stripe.com/c/pay/cs_live_b1sckR6D249t8Xk3VHi7uQL4B4dAu8sbsRA7Y199wE9v5WNba80YeX0vzj#fidnandhYHdWcXxpYCc%2FJ2FgY2RwaXEnKSd2cGd2ZndsdXFsamtQa2x0cGBrYHZ2QGtkZ2lgYSc%2FY2RpdmApJ2JzJz81KSdkdWxOYHwnPyd1blppbHNgWjA0V28yaT1GQm1ITDRMb2x1ZE9cN3VRUncyb3xLXzVRdjNyMEdJRjFtQUZpNXQ2Y0xIbG9tdmNtUXNtfU1XQ0Y1MnFDSlViXDI3NlFyYWhKV2dJVUhDbDwwNTV0VWxAfXxTRycpJ2N3amhWYHdzYHcnP3F3cGApJ2dkZm5id2pwa2FGamlqdyc%2FJyZjN2M8Yz0nKSdpZHxqcHFRfHVgJz8naHBpcWxabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl"),
    ("tier4", "annual", "Tier 4 // Enterprise RCM & ERP OEM", 2490000, "year", "prod_VXu3zM9wQr4tY1", "price_1UWoFMCGhMI1Ijip5tR8mW3q", "plink_1UWoFOCGhMI1IjipjK7pX2nQ", "https://checkout.stripe.com/c/pay/cs_live_b1xxBGQZgAaRBImF1vEl8yKRAFMqA1kLmyHTPAUSz4A7MdAmnr9ods0HLL#fidnandhYHdWcXxpYCc%2FJ2FgY2RwaXEnKSd2cGd2ZndsdXFsamtQa2x0cGBrYHZ2QGtkZ2lgYSc%2FY2RpdmApJ2JzJz81KSdkdWxOYHwnPyd1blppbHNgWjA0V28yaT1GQm1ITDRMb2x1ZE9cN3VRUncyb3xLXzVRdjNyMEdJRjFtQUZpNXQ2Y0xIbG9tdmNtUXNtfU1XQ0Y1MnFDSlViXDI3NlFyYWhKV2dJVUhDbDwwNTV0VWxAfXxTRycpJ2N3amhWYHdzYHcnP3F3cGApJ2dkZm5id2pwa2FGamlqdyc%2FJyZjN2M8Yz0nKSdpZHxqcHFRfHVgJz8naHBpcWxabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl"),
]


def upload_stripe_file(file_path: Path, purpose: str) -> str:
    with open(file_path, "rb") as f:
        r = requests.post(
            "https://files.stripe.com/v1/files",
            headers=STRIPE_HEADERS,
            data={"purpose": purpose},
            files={"file": (file_path.name, f, "image/png")},
            timeout=25,
        )
    if r.status_code == 200:
        return r.json()["id"]
    print(f"[WARN] Stripe file upload ({purpose}): {r.status_code} {r.text[:200]}")
    return ""


def provision_stripe_catalog() -> Dict[str, str]:
    replacements: Dict[str, str] = {}
    avatar_p = RW / "rubricward_mailbox_avatar_500.png"
    if avatar_p.exists():
        icon_id = upload_stripe_file(avatar_p, "business_icon")
        logo_id = upload_stripe_file(avatar_p, "business_logo")
        if icon_id:
            replacements["file_1UWoK1CGhMI1IjipmLv2iM1F"] = icon_id
        if logo_id:
            replacements["file_1UWoK2CGhMI1IjiphUswlc5T"] = logo_id

    products_by_tier: Dict[str, str] = {}
    for tier, billing, name, cents, interval, old_prod, old_price, old_plink, old_url in CAMBER_LINKS:
        if tier not in products_by_tier:
            r_prod = requests.post(
                "https://api.stripe.com/v1/products",
                headers=STRIPE_HEADERS,
                data={
                    "name": f"RubricWard — {name}",
                    "description": f"RubricWard ({name}) — Autonomous 72-Portal Commercial Payer TiC MRF, CMS MPFS RVU/GPCI, ERISA Appeal & Federal NSA IDR Engine",
                    "metadata[brand]": "rubricward",
                    "metadata[tier]": tier,
                },
                timeout=20,
            )
            r_prod.raise_for_status()
            products_by_tier[tier] = r_prod.json()["id"]
            replacements[old_prod] = products_by_tier[tier]

        prod_id = products_by_tier[tier]
        r_price = requests.post(
            "https://api.stripe.com/v1/prices",
            headers=STRIPE_HEADERS,
            data={
                "product": prod_id,
                "unit_amount": str(cents),
                "currency": "usd",
                "recurring[interval]": interval,
                "metadata[brand]": "rubricward",
                "metadata[tier]": tier,
                "metadata[billing]": billing,
            },
            timeout=20,
        )
        r_price.raise_for_status()
        new_price_id = r_price.json()["id"]
        replacements[old_price] = new_price_id

        r_plink = requests.post(
            "https://api.stripe.com/v1/payment_links",
            headers=STRIPE_HEADERS,
            data={
                "line_items[0][price]": new_price_id,
                "line_items[0][quantity]": "1",
                "metadata[brand]": "rubricward",
                "metadata[tier]": tier,
                "metadata[billing]": billing,
                "after_completion[type]": "redirect",
                "after_completion[redirect][url]": f"https://rubricward.com/#checkout-success?tier={tier}&billing={billing}",
            },
            timeout=20,
        )
        r_plink.raise_for_status()
        plink_data = r_plink.json()
        replacements[old_plink] = plink_data["id"]
        replacements[old_url] = plink_data["url"]
        print(f"  [STRIPE] Created {tier} ({billing}): {plink_data['url']}")

    return replacements


def ensure_bimi_in_lettings() -> None:
    """Ensures `bimi-logo.svg` is copied to `lettings/bimi-logo.svg` on every build."""
    lettings_dir = RW / "lettings"
    lettings_dir.mkdir(parents=True, exist_ok=True)
    if (RW / "bimi-logo.svg").exists():
        shutil.copy2(RW / "bimi-logo.svg", lettings_dir / "bimi-logo.svg")

    b_file = RW / "build_camberdesk_site.py"
    b_txt = b_file.read_text(encoding="utf-8")
    target = '    for svg_p in (os.path.join(BASE_DIR, "favicon.svg"), os.path.join(lettings_dir, "favicon.svg")):'
    addition = '''    if os.path.exists(os.path.join(BASE_DIR, "bimi-logo.svg")):
        import shutil as _sh
        _sh.copy2(os.path.join(BASE_DIR, "bimi-logo.svg"), os.path.join(lettings_dir, "bimi-logo.svg"))
    for svg_p in (os.path.join(BASE_DIR, "favicon.svg"), os.path.join(lettings_dir, "favicon.svg")):'''
    if 'os.path.join(lettings_dir, "bimi-logo.svg")' not in b_txt:
        b_txt = b_txt.replace(target, addition)
        b_file.write_text(b_txt, encoding="utf-8")
        shutil.copy2(b_file, RW / "build_rubricward_site.py")


def main() -> None:
    ensure_bimi_in_lettings()
    reps = provision_stripe_catalog()
    (RW / "rubricward_stripe_catalog.json").write_text(json.dumps(reps, indent=2), encoding="utf-8")

    # Apply Stripe replacements across all Python, HTML, JS, MD, and .env files in D:\RubricWard
    for root, dirs, files in os.walk(RW):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules"}]
        for fname in files:
            if fname in {"provision_rubricward_stripe.py", "rubricward_stripe_catalog.json"}:
                continue
            fpath = Path(root) / fname
            if fpath.suffix.lower() in {".py", ".html", ".js", ".json", ".md", ""} or fname == ".env":
                try:
                    txt = fpath.read_text(encoding="utf-8")
                    orig = txt
                    for old_k, new_v in reps.items():
                        txt = txt.replace(old_k, new_v)
                    if txt != orig:
                        fpath.write_text(txt, encoding="utf-8")
                except Exception:
                    pass

    # Rebuild site, pSEO, Edge Worker, and run both verify_rubricward_integrity.py and omniscient_auditor.py
    for script in [
        "build_camberdesk_site.py",
        "pseo_generator.py",
        "build_cloudflare_edge_worker.py",
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
