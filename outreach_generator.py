r"""
RubricWard — Autonomous Planholder, Post-Letting MLOT & DBE/MEP Contractor Outbound Generator
(`D:\RubricWard\outreach_generator.py`).
====================================================================================================
Enforces three non-negotiable deliverability rules across all 3 outbound engines:
  1. ZERO Guessed Role Prefixes (`estimating@`, `bids@`, `civilbids@`):
     - Every single email in `campaign_leads.csv` and `outbox_ready_queue.json` comes strictly from
       `D:\RubricWard\verified_public_dot_contacts.json`, harvested directly from live contractor website
       HTML (`mailto:` / page text) or public Federal/State Civil & DOT engineering award directories
       with the exact `source_url` recorded.
  2. ZERO-Link, ZERO-`$` Conversational Rule in BOTH Step 1 and Step 2:
     - Formats all figures as `USD 18,450,000` and `USD 135.00/TON` (zero `$` characters).
     - Contains zero `http://` or `https://` links in `step1_subject`, `step1_body_zero_link`, and
       `step2_body_dossier_link` (`dossier_url` and `compiler_url` are sent only by `outbound_reply_responder.py`
       after the estimator replies `"SEND ZIP"`).
  3. Live DNS `MX` Verification (`verify_email_domain_mx()`) on every recipient domain.
"""

from error_telemetry import configure_utf8_stdio, report_error
configure_utf8_stdio()

import csv
import json
import os
import re
from typing import Any, Dict, List

from api_gateway.services.llm_extractor import load_seed_data
from rubricward_autopilot import slugify
from harvest_verified_dot_contacts import load_signaltender_exclusion_sets
from mlot_sniper_generator import (
    _sanitize_zero_dollar_zero_link,
    build_mlot_and_runner_up_leads,
    load_verified_dot_contacts,
)
from outbound_mailer import verify_email_domain_mx

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "campaign_leads.csv")
QUEUE_PATH = os.path.join(BASE_DIR, "outbox_ready_queue.json")
SITE_BASE_URL = os.getenv("RUBRICWARD_SITE_URL", "https://rubricward.com").rstrip("/")
API_BASE_URL = os.getenv("RUBRICWARD_API_BASE_URL", "https://rubricward.com").rstrip("/")


def generate_outreach_queue() -> List[Dict[str, Any]]:
    # Clear stale negative MX entries before running fresh nslookup MX checks
    mx_cache_file = os.path.join(BASE_DIR, "dns_mx_cache.json")
    if os.path.exists(mx_cache_file):
        try:
            with open(mx_cache_file, "r", encoding="utf-8") as f:
                c = json.load(f)
            if isinstance(c, dict):
                cleaned_c = {k: v for k, v in c.items() if v is True}
                with open(mx_cache_file, "w", encoding="utf-8") as f:
                    json.dump(cleaned_c, f, indent=2)
        except Exception:
            pass

    seed = load_seed_data()
    lettings = seed.get("lettings", [])
    verified_contacts = load_verified_dot_contacts()
    st_excluded_emails, st_excluded_domains = load_signaltender_exclusion_sets()

    seen_emails = set()
    leads: List[Dict[str, Any]] = []

    def _add_lead(contact: Dict[str, str], matched_let: Dict[str, Any]) -> None:
        clean_em = str(contact.get("email") or "").strip().lower()
        dom = clean_em.split("@", 1)[1] if "@" in clean_em else ""
        source_url = str(contact.get("source_url") or "").strip()
        source_type = str(contact.get("source_type") or "website_html_mailto").strip()
        if not clean_em or not source_url or clean_em in seen_emails:
            return
        if clean_em in st_excluded_emails or dom in st_excluded_domains:
            return
        if not verify_email_domain_mx(clean_em):
            return
        seen_emails.add(clean_em)

        company = str(contact.get("company_name") or "your estimating team").strip()
        raw_fn = str(contact.get("first_name") or "Estimating").strip()
        dot_id = str(contact.get("license_or_dot_id") or "DOT-PREQ").strip()
        state = str(contact.get("state") or matched_let.get("state_code") or "TX").strip()

        pid = str(matched_let.get("project_id") or "TXDOT-CSJ-0015-13-412")
        clean_title = re.sub(r"^\[[^\]]+\]\s*", "", str(matched_let.get("title") or "IH-35 Bridge & Superpave Letting"))
        agency = str(matched_let.get("agency") or "TxDOT")
        county = str(matched_let.get("county") or "Travis County, TX")
        letting_date = str(matched_let.get("letting_date") or "2026-11-18")
        est_usd = float(matched_let.get("engineers_estimate_usd") or 18450000.0)
        wage_id = str(matched_let.get("wage_determination_id") or f"{state}20260028 (Heavy & Highway)")
        pay_items = matched_let.get("pay_items") or []
        top_item_str = "key unit pay items"
        if pay_items:
            pi = pay_items[0]
            top_item_str = (
                f"Item {pi.get('item_code')} ({pi.get('description')[:42]}) at "
                f"USD {float(pi.get('hist_median_unit_usd') or 135.0):,.2f}/{pi.get('unit', 'UNIT')} median"
            )

        slug = slugify(clean_title)
        dossier_url = f"{SITE_BASE_URL}/lettings/project/{slug}.html"
        compiler_url = f"{API_BASE_URL}/v1/camber-autopilot/compile-bid-package?project_id={pid}&state_code={state}&format=binary"
        clean_fname = raw_fn.split(".")[0].capitalize() if "." in raw_fn else raw_fn.capitalize()
        greeting_name = (
            f"{company} team"
            if clean_fname.lower() in ("estimating", "capture", "bids", "info", "contact", "office", "sales")
            else clean_fname
        )

        step1_subject = _sanitize_zero_dollar_zero_link(
            f"{pid} unit bid tabs & Davis-Bacon rates ({county})"
        )
        step1_body = _sanitize_zero_dollar_zero_link(
            f"Hi {greeting_name},\n\n"
            f"Noticed {company}'s civil & infrastructure work in {state} while indexing {agency} letting {pid} "
            f"({clean_title[:72]} — USD {est_usd:,.0f} Engineer's Estimate opening {letting_date} in {county}).\n\n"
            f"We already pulled the 36-month historical DOT unit-price bid tabulations across the confirmed planholders "
            f"(benchmarking {top_item_str}) and mapped {wage_id} prevailing wage fringes + CSI Divisions 00-48 submittals into a 6-file Word/Excel takeoff package.\n\n"
            f"Is {company} pricing {pid} (or sub-quoting a trade division on it) this week? Reply 'SEND ZIP' and I will send the 6-file .DOCX + .XLSX bid-tab package over.\n\n"
            f"Best,\nAaron Chen\nRubricWard Preconstruction & DOT Systems"
        )

        step2_body = _sanitize_zero_dollar_zero_link(
            f"Hi {greeting_name} — quick follow-up in case {company}'s estimating desk is locking in unit prices for {pid} ({county}).\n\n"
            f"We already compiled the 36-month historical DOT unit-bid spread ({top_item_str}), {wage_id} Davis-Bacon WH-347 wage fringes, "
            f"and the 6-File OpenXML (.DOCX + .XLSX) Takeoff Package for {pid}.\n\n"
            f"Want me to reply with the 6-file .ZIP takeoff package and Excel unit bid-tab sheet for {pid}, or should I hold off?\n\n"
            f"Best,\nAaron Chen\nRubricWard Preconstruction & DOT Systems"
        )

        leads.append({
            "email": clean_em,
            "first_name": clean_fname,
            "company_name": company,
            "license_or_dot_id": dot_id,
            "state": state,
            "project_id": pid,
            "project_title": clean_title,
            "letting_date": letting_date,
            "dossier_url": dossier_url,
            "compiler_url": compiler_url,
            "source_type": source_type,
            "source_url": source_url,
            "step1_subject": step1_subject,
            "step1_body_zero_link": step1_body,
            "step2_body_dossier_link": step2_body,
        })

    # 1. Engine 1 & Engine 3: First half of verified HTML-scraped & DOT directory contacts
    planholder_slice = verified_contacts[: max(1, len(verified_contacts) // 2)]
    for idx, contact in enumerate(planholder_slice):
        st = str(contact.get("state") or "TX")
        matched_let = next(
            (l for l in lettings if l.get("state_code") == st),
            lettings[idx % len(lettings)] if lettings else {},
        )
        _add_lead(contact=contact, matched_let=matched_let)

    # 2. Engine 2: Post-Letting 2nd-Place Runner-Up & Margin Left on Table (MLOT) Sniper Loop
    for mlot_lead in build_mlot_and_runner_up_leads(verified_contacts=verified_contacts):
        em = mlot_lead["email"].strip().lower()
        dom = em.split("@", 1)[1] if "@" in em else ""
        if em in st_excluded_emails or dom in st_excluded_domains:
            continue
        if em not in seen_emails and mlot_lead.get("source_url") and verify_email_domain_mx(em):
            seen_emails.add(em)
            leads.append(mlot_lead)

    fieldnames = [
        "email", "first_name", "company_name", "license_or_dot_id", "state",
        "project_id", "project_title", "letting_date", "dossier_url", "compiler_url",
        "source_type", "source_url",
        "step1_subject", "step1_body_zero_link", "step2_body_dossier_link",
    ]
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)

    with open(QUEUE_PATH, "w", encoding="utf-8") as fh:
        json.dump({"count": len(leads), "outbox_queue": leads}, fh, indent=2)

    print(
        f"[RUBRICWARD OUTBOUND] Generated {len(leads)} 100% HTML/Directory-Verified, Zero-$, Zero-Link outreach leads "
        f"-> {CSV_PATH} & {QUEUE_PATH}"
    )
    return leads


if __name__ == "__main__":
    generate_outreach_queue()
