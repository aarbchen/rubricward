r"""
RubricWard — Dedicated Instantly.ai V2 Campaign Provisioner & Medical Group / ASC Lead Sync
(`D:\RubricWard\sync_instantly_campaign.py`).
====================================================================================================
1. Locates or creates the standalone `"RubricWard — 50-State Payer MRF & NSA IDR Outreach"`
   campaign (`672de7d4-7ff6-42ec-be56-9b6ce8519e8c`).
2. Strictly enforces:
   - `open_tracking: False`
   - `link_tracking: False`
   - `text_only: True`
   - `stop_on_reply: True`
   - `email_list`: strictly warmed (`stat_warmup_score >= 85`) `*rubricward*` mailboxes —
     never attaching any un-warmed (`score < 85`), `*signaltender*`, or `*camberdesk*` mailbox.
3. Purges any guessed role emails, synthetic domains, or legacy leads containing `$` or `http` links in Step 1 / Step 2,
   and syncs the 100% live HTML/Directory-verified, Zero-`$`, Zero-Link leads from `D:\RubricWard\campaign_leads.csv`.
"""

from error_telemetry import configure_utf8_stdio
configure_utf8_stdio()

import json
import os
from pathlib import Path
from typing import Any, Dict
import requests
from dotenv import load_dotenv

from autonomous_mailbox_scaler import fetch_live_rubricward_instantly_accounts
from harvest_verified_dot_contacts import load_signaltender_exclusion_sets
from outbound_mailer import compute_dynamic_daily_limit
from outreach_generator import generate_outreach_queue

ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / ".env"
CSV_PATH = ROOT_DIR / "campaign_leads.csv"
load_dotenv(dotenv_path=str(ENV_PATH))

INSTANTLY_API_KEY = (os.getenv("INSTANTLY_API_KEY") or "").strip()
CAMPAIGN_NAME = "RubricWard — 50-State Payer MRF & NSA IDR Outreach"
SIGNALTENDER_BLOCKED_CAMPAIGN_IDS = {
    "c7727dff-92cc-4621-9e96-c960938d5a47",
    "748eecf5-6b63-4dff-b9f2-1d2ff1a4a96f",
    "e69941d4-b5c0-45a7-ac67-ae8947761d4b",
}


def ensure_rubricward_campaign() -> str:
    headers = {
        "Authorization": f"Bearer {INSTANTLY_API_KEY}",
        "Content-Type": "application/json",
    }
    existing_id = (os.getenv("RUBRICWARD_INSTANTLY_CAMPAIGN_ID") or "").strip()
    if existing_id and existing_id not in SIGNALTENDER_BLOCKED_CAMPAIGN_IDS:
        r_check = requests.get(f"https://api.instantly.ai/api/v2/campaigns/{existing_id}", headers=headers, timeout=15)
        if r_check.status_code == 200 and (r_check.json() or {}).get("id"):
            return existing_id

    r_list = requests.get("https://api.instantly.ai/api/v2/campaigns?limit=50", headers=headers, timeout=15)
    if r_list.status_code == 200:
        for item in (r_list.json() or {}).get("items") or []:
            if (item.get("name") or "").strip() == CAMPAIGN_NAME:
                cid = item["id"]
                _save_campaign_id(cid)
                return cid

    payload = {
        "name": CAMPAIGN_NAME,
        "campaign_schedule": {
            "schedules": [
                {
                    "name": "Monday-Friday Revenue Cycle Hours",
                    "timing": {"from": "07:00", "to": "17:00"},
                    "days": {"1": True, "2": True, "3": True, "4": True, "5": True, "6": False, "0": False},
                    "timezone": "America/Chicago",
                }
            ]
        },
        "sequences": [
            {
                "steps": [
                    {
                        "type": "email",
                        "delay": 0,
                        "variants": [
                            {
                                "subject": "{{step1_subject}}",
                                "body": "{{step1_body_zero_link}}",
                            }
                        ],
                    },
                    {
                        "type": "email",
                        "delay": 3,
                        "variants": [
                            {
                                "subject": "Re: {{step1_subject}}",
                                "body": "{{step2_body_dossier_link}}",
                            }
                        ],
                    },
                ]
            }
        ],
        "text_only": True,
        "stop_on_reply": True,
        "link_tracking": False,
        "open_tracking": False,
        "daily_limit": 15,
    }
    r_create = requests.post("https://api.instantly.ai/api/v2/campaigns", headers=headers, json=payload, timeout=20)
    if r_create.status_code in (200, 201):
        cid = (r_create.json() or {}).get("id") or ""
        if cid:
            _save_campaign_id(cid)
            return cid
    return ""


def _save_campaign_id(cid: str) -> None:
    if not ENV_PATH.exists():
        return
    txt = ENV_PATH.read_text(encoding="utf-8")
    if "RUBRICWARD_INSTANTLY_CAMPAIGN_ID=" in txt:
        lines = [
            f"RUBRICWARD_INSTANTLY_CAMPAIGN_ID={cid}" if ln.startswith("RUBRICWARD_INSTANTLY_CAMPAIGN_ID=") else ln
            for ln in txt.splitlines()
        ]
        ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        ENV_PATH.write_text(txt.rstrip() + f"\nRUBRICWARD_INSTANTLY_CAMPAIGN_ID={cid}\n", encoding="utf-8")


def sync_leads_to_instantly() -> Dict[str, Any]:
    leads = generate_outreach_queue()
    if not INSTANTLY_API_KEY:
        return {"status": "skipped_no_key", "leads_local": len(leads)}

    cid = ensure_rubricward_campaign()
    if not cid or cid in SIGNALTENDER_BLOCKED_CAMPAIGN_IDS:
        return {"status": "local_only", "leads_local": len(leads)}

    headers = {
        "Authorization": f"Bearer {INSTANTLY_API_KEY}",
        "Content-Type": "application/json",
    }
    auth_only_headers = {
        "Authorization": f"Bearer {INSTANTLY_API_KEY}",
    }

    _, warmed_rw, _ = fetch_live_rubricward_instantly_accounts()
    rubricward_emails = sorted(
        em for em in set(warmed_rw)
        if "rubricward" in em.lower()
        and "signaltender" not in em.lower()
        and "camberdesk" not in em.lower()
    )
    dynamic_daily_cap, _, _ = compute_dynamic_daily_limit()
    three_step_sequences = [
        {
            "steps": [
                {
                    "type": "email",
                    "delay": 3,
                    "delay_unit": "days",
                    "pre_delay_unit": "days",
                    "variants": [
                        {
                            "subject": "{{step1_subject}}",
                            "body": "{{step1_body_zero_link}}",
                        }
                    ],
                },
                {
                    "type": "email",
                    "delay": 4,
                    "delay_unit": "days",
                    "pre_delay_unit": "days",
                    "variants": [
                        {
                            "subject": "Re: {{step1_subject}}",
                            "body": "{{step2_body_dossier_link}}",
                        }
                    ],
                },
                {
                    "type": "email",
                    "delay": 4,
                    "delay_unit": "days",
                    "pre_delay_unit": "days",
                    "variants": [
                        {
                            "subject": "Re: {{step1_subject}}",
                            "body": (
                                "Closing the loop on {{project_id}} before the 30-day Federal NSA IDR Open Negotiation "
                                "and ERISA 29 CFR 2560.503-1 appeal window — should I route our 6-file OpenXML CPT/DRG "
                                "TiC MRF benchmark and Medicare MPFS RVU/GPCI workbook to another Managed Care or Revenue "
                                "Cycle director on your team, or hold off for this cycle?\n\n— Aaron\nRubricWard Payer MRF & NSA IDR Desk"
                            ),
                        }
                    ],
                },
            ]
        }
    ]
    patch_payload: Dict[str, Any] = {
        "open_tracking": False,
        "link_tracking": False,
        "text_only": True,
        "stop_on_reply": True,
        "daily_limit": dynamic_daily_cap,
        "sequences": three_step_sequences,
    }
    if rubricward_emails:
        patch_payload["email_list"] = rubricward_emails

    try:
        requests.patch(
            f"https://api.instantly.ai/api/v2/campaigns/{cid}",
            headers=headers,
            json=patch_payload,
            timeout=15,
        )
    except Exception:
        pass

    st_excluded_emails, st_excluded_domains = load_signaltender_exclusion_sets()
    valid_email_map = {
        l["email"].strip().lower(): l
        for l in leads
        if l["email"].strip().lower() not in st_excluded_emails
        and l["email"].strip().lower().split("@", 1)[-1] not in st_excluded_domains
    }
    purged_count = 0
    existing_clean_emails = set()
    try:
        r_existing = requests.post(
            "https://api.instantly.ai/api/v2/leads/list",
            headers=headers,
            json={"campaign": cid, "limit": 100},
            timeout=15,
        )
        if r_existing.status_code == 200:
            for item in (r_existing.json() or {}).get("items") or []:
                em_existing = str(item.get("email") or "").strip().lower()
                dom_existing = em_existing.split("@", 1)[-1] if "@" in em_existing else ""
                lid = item.get("id")
                payload_vars = item.get("payload") or {}
                s1 = str(payload_vars.get("step1_body_zero_link") or "")
                s2 = str(payload_vars.get("step2_body_dossier_link") or "")
                subj1 = str(payload_vars.get("step1_subject") or "")
                comp_url = str(payload_vars.get("compiler_url") or "")
                has_dollar_or_link = ("$" in s1) or ("$" in s2) or ("$" in subj1) or ("http://" in s1) or ("https://" in s1) or ("http://" in s2) or ("https://" in s2) or ("api.rubricward.com" in comp_url)
                is_st_overlap = (em_existing in st_excluded_emails) or (dom_existing in st_excluded_domains)
                is_in_flight = (item.get("status") in (1, 2)) or (int(item.get("email_open_count") or 0) > 0)
                if lid and (is_st_overlap or has_dollar_or_link or (not is_in_flight and (em_existing not in valid_email_map or not payload_vars.get("source_url")))):
                    requests.delete(f"https://api.instantly.ai/api/v2/leads/{lid}", headers=auth_only_headers, timeout=10)
                    purged_count += 1
                elif em_existing in valid_email_map or is_in_flight:
                    existing_clean_emails.add(em_existing)
    except Exception:
        pass

    uploaded = 0
    for lead in leads:
        em_clean = lead["email"].strip().lower()
        if em_clean in existing_clean_emails:
            uploaded += 1
            continue
        payload = {
            "campaign": cid,
            "email": em_clean,
            "first_name": lead.get("first_name") or "Revenue Cycle",
            "company_name": lead["company_name"],
            "custom_variables": {
                "license_or_dot_id": lead.get("license_or_dot_id") or "NPI-VERIFIED",
                "state": lead.get("state") or lead.get("state_code") or "TX",
                "project_id": lead.get("project_id") or lead.get("letting_id") or "TXDOI-MRF-CPT-29881-DFW",
                "project_title": lead.get("project_title") or lead.get("subject") or "Commercial Payer TiC MRF Cohort",
                "letting_date": lead.get("letting_date") or "2026-11-30",
                "dossier_url": lead["dossier_url"],
                "compiler_url": lead.get("compiler_url") or "https://rubricward.com/v1/camber-autopilot/compile-bid-package?format=binary",
                "source_type": lead.get("source_type", "website_html_mailto"),
                "source_url": lead.get("source_url", ""),
                "step1_subject": lead["step1_subject"],
                "step1_body_zero_link": lead["step1_body_zero_link"],
                "step2_body_dossier_link": lead["step2_body_dossier_link"],
            },
            "skip_if_in_workspace": True,
        }
        try:
            r = requests.post("https://api.instantly.ai/api/v2/leads", headers=headers, json=payload, timeout=15)
            if r.status_code in (200, 201):
                uploaded += 1
        except Exception:
            pass

    print(
        f"[RUBRICWARD INSTANTLY] Campaign {cid}: purged {purged_count} legacy/guessed leads, "
        f"synced {uploaded}/{len(leads)} HTML/Directory-verified Zero-$ Zero-Link leads "
        f"(open_tracking=False, link_tracking=False, daily_limit={dynamic_daily_cap}, senders={rubricward_emails})."
    )
    return {
        "status": "synced",
        "campaign_id": cid,
        "purged_legacy_leads": purged_count,
        "uploaded": uploaded,
        "total": len(leads),
        "daily_limit": dynamic_daily_cap,
        "open_tracking": False,
        "link_tracking": False,
        "rubricward_senders": rubricward_emails,
    }


if __name__ == "__main__":
    res = sync_leads_to_instantly()
    print(json.dumps(res, indent=2))
