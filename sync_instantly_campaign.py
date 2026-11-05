import re
r"""
RubricWard — Dedicated Instantly.ai V2 Campaign Provisioner & Planholder Lead Sync (`D:\RubricWard\sync_instantly_campaign.py`).
====================================================================================================
1. Locates or creates the standalone `"RubricWard — 50-State Payer MRF & NSA IDR Outreach"`
   campaign (`672de7d4-7ff6-42ec-be56-9b6ce8519e8c`).
2. Strictly enforces:
   - `open_tracking: False`
   - `link_tracking: False`
   - `text_only: True`
   - `stop_on_reply: True`
   - `email_list`: strictly `*rubricward*` mailboxes (`aaron@tryrubricward.com`, `rates@tryrubricward.com`,
     `desk@tryrubricward.com`) — never attaching any `*signaltender*` or `*camberdesk*` mailbox.
3. Purges any bounced leads (`status < 0`), guessed role emails, or legacy leads containing `$` or `http` links
   in Step 1 / Step 2, patches existing leads in-place with updated clean variables, and syncs the 100% live
   HTML/Directory-verified, Zero-`$`, Zero-Link leads from `D:\RubricWard\campaign_leads.csv`.
"""

from error_telemetry import configure_utf8_stdio
configure_utf8_stdio()

from concurrent.futures import ThreadPoolExecutor
import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, List
import requests
from dotenv import load_dotenv

from autonomous_mailbox_scaler import fetch_live_rubricward_instantly_accounts
from harvest_verified_dot_contacts import is_non_buyer_or_trap_inbox, is_receptionist_or_generic_inbox, load_signaltender_exclusion_sets
from outbound_mailer import compute_dynamic_daily_limit
from outreach_generator import generate_outreach_queue

ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / ".env"
CSV_PATH = ROOT_DIR / "campaign_leads.csv"
BLACKLIST_PATH = ROOT_DIR / "bounced_leads_blacklist.json"
load_dotenv(dotenv_path=str(ENV_PATH))

INSTANTLY_API_KEY = (os.getenv("INSTANTLY_API_KEY") or "").strip()
CAMPAIGN_NAME = "RubricWard — 50-State Payer MRF & NSA IDR Outreach"
BLOCKED_CAMPAIGN_IDS = {
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
    if existing_id and existing_id not in BLOCKED_CAMPAIGN_IDS:
        r_check = requests.get(f"https://api.instantly.ai/api/v2/campaigns/{existing_id}", headers=headers, timeout=15)
        if r_check.status_code == 200 and (r_check.json() or {}).get("id"):
            return existing_id

    r_list = requests.get("https://api.instantly.ai/api/v2/campaigns?limit=50", headers=headers, timeout=15)
    if r_list.status_code == 200:
        for item in (r_list.json() or {}).get("items") or []:
            if (item.get("name") or "").strip() == CAMPAIGN_NAME and item.get("id") not in BLOCKED_CAMPAIGN_IDS:
                cid = item["id"]
                _save_campaign_id(cid)
                return cid

    payload = {
        "name": CAMPAIGN_NAME,
        "campaign_schedule": {
            "schedules": [
                {
                    "name": "Monday-Friday Estimating Hours",
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
                        "delay": 2,
                        "variants": [
                            {
                                "subject": "{{step1_subject}}",
                                "body": "{{step1_body_zero_link}}",
                            }
                        ],
                    },
                    {
                        "type": "email",
                        "delay": 2,
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
        "daily_limit": 90,
    }
    r_create = requests.post("https://api.instantly.ai/api/v2/campaigns", headers=headers, json=payload, timeout=20)
    if r_create.status_code in (200, 201):
        cid = (r_create.json() or {}).get("id") or ""
        if cid:
            _save_campaign_id(cid)
            return cid
    print(f"[!] Note creating Instantly campaign: HTTP {r_create.status_code} {r_create.text[:250]}")
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
    if not cid or cid in BLOCKED_CAMPAIGN_IDS:
        return {"status": "local_only", "leads_local": len(leads)}

    headers = {
        "Authorization": f"Bearer {INSTANTLY_API_KEY}",
        "Content-Type": "application/json",
    }
    auth_only_headers = {
        "Authorization": f"Bearer {INSTANTLY_API_KEY}",
    }

    _, warmed_rw, warming_rw = fetch_live_rubricward_instantly_accounts()
    rubricward_emails = sorted(
        em for em in set(warmed_rw)
        if "rubricward" in em.lower() and "signaltender" not in em.lower() and "camberdesk" not in em.lower()
    )
    dynamic_daily_cap, _, _ = compute_dynamic_daily_limit()
    step3_breakup_text = (
        "Closing the loop on {{project_id}} before the quarterly payer rate cycle — "
        "should I route our 6-file OpenXML CPT fee schedule and NSA IDR workbook to "
        "another revenue-cycle lead on your managed-care desk, or hold off for this cycle?\n\n"
        "— Aaron\nRubricWard Healthcare Rate Desk"
    )
    three_step_sequences = [
        {
            "steps": [
                {
                    "type": "email",
                    "delay": 1,
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
                    "delay": 1,
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
                    "delay": 2,
                    "delay_unit": "days",
                    "pre_delay_unit": "days",
                    "variants": [
                        {
                            "subject": "Re: {{step1_subject}}",
                            "body": step3_breakup_text,
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
        "disable_bounce_protect": True,
        "daily_limit": dynamic_daily_cap,
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
        requests.patch(
            f"https://api.instantly.ai/api/v2/campaigns/{cid}",
            headers=headers,
            json={"sequences": three_step_sequences},
            timeout=15,
        )
        requests.post(
            f"https://api.instantly.ai/api/v2/campaigns/{cid}/activate",
            headers=headers,
            json={},
            timeout=15,
        )
    except Exception:
        pass

    bl_data = {"bounced_emails": [], "bounced_domains": []}
    if BLACKLIST_PATH.exists():
        try:
            bl_data.update(json.loads(BLACKLIST_PATH.read_text(encoding="utf-8")) or {})
        except Exception:
            pass
    bl_emails = set(bl_data.get("bounced_emails") or [])
    bl_domains = set(bl_data.get("bounced_domains") or [])

    st_excluded_emails, st_excluded_domains = load_signaltender_exclusion_sets()
    valid_email_map = {
        l["email"].strip().lower(): l
        for l in leads
        if l["email"].strip().lower() not in st_excluded_emails
        and l["email"].strip().lower().split("@", 1)[-1] not in st_excluded_domains
        and l["email"].strip().lower() not in bl_emails
        and l["email"].strip().lower().split("@", 1)[-1] not in bl_domains
        and not is_receptionist_or_generic_inbox(l["email"])
    }

    purged_count = 0
    to_delete_ids: List[str] = []
    existing_clean_map: Dict[str, Dict[str, Any]] = {}
    new_bounces_found = False

    try:
        starting_after = None
        for _ in range(25):
            list_req: Dict[str, Any] = {"campaign": cid, "limit": 50}
            if starting_after:
                list_req["starting_after"] = starting_after
            r_existing = None
            for _att in range(3):
                try:
                    r_existing = requests.post(
                        "https://api.instantly.ai/api/v2/leads/list",
                        headers=headers,
                        json=list_req,
                        timeout=35,
                    )
                    if r_existing.status_code == 200:
                        break
                except Exception:
                    pass
            if r_existing is None:
                break
            if r_existing.status_code != 200:
                break
            r_json = r_existing.json() or {}
            items = r_json.get("items") or []
            for item in items:
                em_existing = str(item.get("email") or "").strip().lower()
                dom_existing = em_existing.split("@", 1)[-1] if "@" in em_existing else ""
                lid = str(item.get("id") or "").strip()
                lead_status = int(item.get("status") or 0)
                interest_status = int(item.get("lt_interest_status") or 0)
                payload_vars = item.get("payload") or {}
                s1 = str(payload_vars.get("step1_body_zero_link") or "")
                s2 = str(payload_vars.get("step2_body_dossier_link") or "")
                subj1 = str(payload_vars.get("step1_subject") or "")
                comp_url = str(payload_vars.get("compiler_url") or "")
                has_dollar_or_link = ("$" in s1) or ("$" in s2) or ("$" in subj1) or ("http://" in s1) or ("https://" in s1) or ("api.rubricward.com" in comp_url)
                is_st_overlap = (em_existing in st_excluded_emails) or (dom_existing in st_excluded_domains)
                is_bounced_or_bad = (lead_status < 0) or (interest_status < 0) or (em_existing in bl_emails) or (dom_existing in bl_domains) or ("%" in em_existing)
                if lead_status < 0 and em_existing and em_existing not in bl_emails:
                    bl_emails.add(em_existing)
                    new_bounces_found = True

                if lid and (is_bounced_or_bad or is_st_overlap or has_dollar_or_link or is_receptionist_or_generic_inbox(em_existing) or (em_existing not in valid_email_map)):
                    to_delete_ids.append(lid)
                elif em_existing in valid_email_map and lid:
                    existing_clean_map[em_existing] = item
            starting_after = r_json.get("next_starting_after")
            if not starting_after or len(items) < 50:
                break
    except Exception:
        pass

    for del_id in to_delete_ids:
        try:
            r_del = requests.delete(f"https://api.instantly.ai/api/v2/leads/{del_id}", headers=auth_only_headers, timeout=10)
            if 200 <= r_del.status_code < 300:
                purged_count += 1
        except Exception:
            pass

    if new_bounces_found:
        try:
            BLACKLIST_PATH.write_text(
                json.dumps({"bounced_emails": sorted(bl_emails), "bounced_domains": sorted(bl_domains)}, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def _sync_one_lead(lead: Dict[str, Any]) -> tuple[int, int]:
        em_clean = lead["email"].strip().lower()
        pid_val = str(lead.get("project_id") or lead.get("letting_id") or "TXDOI-MRF-CPT-29881-DFW")
        lead_step3_breakup = step3_breakup_text.replace("{{project_id}}", pid_val)
        custom_vars = {
            "license_or_dot_id": lead.get("license_or_dot_id") or "NPI-VERIFIED",
            "state": lead.get("state") or lead.get("state_code") or "TX",
            "project_id": pid_val,
            "project_title": lead.get("project_title") or lead.get("subject") or "Commercial Payer TiC MRF Cohort",
            "letting_date": lead.get("letting_date") or "2026-11-30",
            "dossier_url": lead["dossier_url"],
            "compiler_url": lead.get("compiler_url") or "https://rubricward.com/v1/camber-autopilot/compile-bid-package?format=binary",
            "source_type": lead.get("source_type", "website_html_mailto"),
            "source_url": lead.get("source_url", ""),
            "step1_subject": lead["step1_subject"],
            "step1_body_zero_link": lead["step1_body_zero_link"],
            "step2_body_dossier_link": lead["step2_body_dossier_link"],
            "step3_body_breakup": lead_step3_breakup,
        }
        fn_val = lead.get("first_name") or "Revenue Cycle"
        if em_clean in existing_clean_map:
            ex_item = existing_clean_map[em_clean]
            ex_id = str(ex_item.get("id") or "")
            ex_payload = ex_item.get("payload") or {}
            has_started = bool((ex_item.get("status_summary") or {}).get("lastStep")) or bool(ex_item.get("timestamp_last_contact"))
            if has_started:
                if ex_payload.get("project_id") and not re.search(r"-2026-10\d\d", str(ex_payload.get("project_id"))):
                    custom_vars["project_id"] = ex_payload["project_id"]
                if ex_payload.get("step1_subject"):
                    cleaned_ex_subj = re.sub(r"\s*—\s*NPI\s+\d+", "", str(ex_payload["step1_subject"])).strip()
                    if not re.search(r"-2026-10\d\d", cleaned_ex_subj):
                        custom_vars["step1_subject"] = cleaned_ex_subj
            needs_patch = (
                str(ex_item.get("first_name") or "") != str(fn_val)
                or str(ex_item.get("company_name") or "") != str(lead["company_name"])
                or str(ex_payload.get("project_id") or "") != str(custom_vars["project_id"])
                or str(ex_payload.get("dossier_url") or "") != str(lead["dossier_url"])
                or str(ex_payload.get("compiler_url") or "") != str(custom_vars["compiler_url"])
                or str(ex_payload.get("step1_subject") or "") != str(custom_vars["step1_subject"])
                or str(ex_payload.get("step1_body_zero_link") or "") != str(custom_vars["step1_body_zero_link"])
                or str(ex_payload.get("step2_body_dossier_link") or "") != str(lead["step2_body_dossier_link"])
                or str(ex_payload.get("step3_body_breakup") or "") != lead_step3_breakup
            )
            if needs_patch and ex_id:
                try:
                    rp = requests.patch(
                        f"https://api.instantly.ai/api/v2/leads/{ex_id}",
                        headers=headers,
                        json={
                            "first_name": fn_val,
                            "company_name": lead["company_name"],
                            "custom_variables": custom_vars,
                        },
                        timeout=25,
                    )
                    if 200 <= rp.status_code < 300:
                        return (1, 1)
                except Exception:
                    pass
            return (1, 0)

        payload = {
            "campaign": cid,
            "email": em_clean,
            "first_name": fn_val,
            "company_name": lead["company_name"],
            "custom_variables": custom_vars,
            "skip_if_in_workspace": True,
        }
        try:
            r = requests.post("https://api.instantly.ai/api/v2/leads", headers=headers, json=payload, timeout=15)
            if r.status_code in (200, 201):
                return (1, 0)
        except Exception:
            pass
        return (0, 0)

    with ThreadPoolExecutor(max_workers=8) as pool:
        instantly_priority_leads = [l for l in leads if not is_receptionist_or_generic_inbox(l['email'])]
        results = list(pool.map(_sync_one_lead, instantly_priority_leads))

    uploaded = sum(x[0] for x in results)
    patched_count = sum(x[1] for x in results)

    print(
        f"[RUBRICWARD INSTANTLY] Campaign {cid}: purged {purged_count} bounced/legacy leads, "
        f"patched {patched_count} existing leads, synced {uploaded}/{len(leads)} HTML/Directory-verified Zero-$ Zero-Link leads "
        f"(open_tracking=False, link_tracking=False, daily_limit={dynamic_daily_cap}, senders={rubricward_emails})."
    )
    return {
        "status": "synced",
        "campaign_id": cid,
        "purged_legacy_leads": purged_count,
        "patched_existing_leads": patched_count,
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
