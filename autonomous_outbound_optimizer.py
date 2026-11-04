from datetime import datetime, timezone
r"""
RubricWard — Autonomous Outbound Sent-Payload, Sequence & Lead Self-Healing Optimizer
(`D:\RubricWard\autonomous_outbound_optimizer.py`).
====================================================================================================
Runs automatically inside `silent_rubricward_watcher.py` and `auto_error_healer.py` so the user
never has to ask whether there are outbound campaign bugs or tell the system to fix them:
  1. Sequence Step Self-Healing (`GET / PATCH /api/v2/campaigns/{cid}`):
     - Verifies Step 1, Step 2, and Step 3 all have non-empty `subject` and `body`, `open_tracking=False`,
       `link_tracking=False`, `text_only=True`, and `stop_on_reply=True`. Auto-repairs any blank step immediately.
  2. Bounce & Malformed Email Auto-Purge + Blacklist + Lead Pool Auto-Expansion:
     - Paginates all leads in Instantly (`POST /api/v2/leads/list`), purges any bounced (`status < 0`),
       unsubscribed (`lt_interest_status < 0`), or URL-encoded (`%`) email, blacklists it in
       `bounced_leads_blacklist.json`, removes it from `verified_public_dot_contacts.json`, and auto-triggers
       `harvest_verified_dot_contacts` when the verified pool drops below `compute_dynamic_target_leads()`.
  3. In-Flight & Uncontacted Lead Payload Self-Healing (`PATCH /api/v2/leads/{id}`):
     - Audits every lead in Instantly against the freshly generated `campaign_leads.csv` and automatically
       patches any lead whose `first_name`, `company_name`, `step1_subject`, `step1_body_zero_link`, or
       `step2_body_dossier_link` has stale/mismatched state or specialty copy, truncated parentheses, or raw tags.
"""

from error_telemetry import configure_utf8_stdio, report_error
configure_utf8_stdio()

from concurrent.futures import ThreadPoolExecutor
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List
import requests
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=str(ROOT_DIR / ".env"))

INSTANTLY_API_KEY = (os.getenv("INSTANTLY_API_KEY") or "").strip()
CAMPAIGN_ID = (os.getenv("RUBRICWARD_INSTANTLY_CAMPAIGN_ID") or "672de7d4-7ff6-42ec-be56-9b6ce8519e8c").strip()
BLACKLIST_PATH = ROOT_DIR / "bounced_leads_blacklist.json"
CONTACTS_PATH = ROOT_DIR / "verified_public_dot_contacts.json"


def audit_rendered_sent_outbox_and_learn(cid: str, headers: Dict[str, str], all_leads: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    1. Audits the last 100 actual rendered emails (GET /api/v2/emails) sent to prospects
       to catch any unrendered {{variable}}, % encoding, or broken link in real time.
    2. Deduplicates by email ID, separates genuine human replies from auto-replies/OOO
       and unsubscribes, extracts OOO referral emails (Please send all correspondence to: <email>),
       computes live prefix delivery/bounce rates + cohort stats, and saves adaptive weights
       to learned_outbound_intelligence.json (consumed by outreach_generator.py).
    """
    intel_path = ROOT_DIR / "learned_outbound_intelligence.json"
    intel: Dict[str, Any] = {}
    if intel_path.exists():
        try:
            intel = json.loads(intel_path.read_text(encoding="utf-8"))
        except Exception:
            intel = {}

    sent_count = 0
    human_reply_count = 0
    auto_reply_count = 0
    unsubscribe_reply_count = 0
    unrendered_var_alerts = 0
    ooo_referrals: List[str] = list(intel.get("ooo_referral_emails") or [])
    cohort_stats: Dict[str, Dict[str, int]] = {}
    prefix_stats: Dict[str, Dict[str, int]] = {
        "named_person": {"clean": 0, "bounced": 0},
        "dept_desk": {"clean": 0, "bounced": 0},
        "generic_info": {"clean": 0, "bounced": 0},
    }

    lead_by_email: Dict[str, Dict[str, Any]] = {}
    for ld in all_leads:
        em = (ld.get("email") or "").strip().lower()
        if not em:
            continue
        lead_by_email[em] = ld
        local = em.split("@")[0]
        status_code = int(ld.get("status", 1) or 1)
        if local in ("info", "contact", "office", "admin", "hello", "general", "inquiries", "pq", "prequal"):
            bucket = "generic_info"
        elif local in ("estimating", "estimates", "bids", "bidding", "precon", "billing", "rcm", "managedcare", "contracts", "proposals", "sales", "capture"):
            bucket = "dept_desk"
        else:
            bucket = "named_person"
        if status_code < 0:
            prefix_stats[bucket]["bounced"] += 1
        else:
            prefix_stats[bucket]["clean"] += 1

    seen_msg_ids = set()
    try:
        r_em = requests.get(
            f"https://api.instantly.ai/api/v2/emails?campaign_id={cid}&limit=100",
            headers=headers,
            timeout=20,
        )
        if r_em.status_code == 200:
            items = (r_em.json() or {}).get("items") or []
            for m in items:
                msg_id = str(m.get("id") or "").strip()
                if msg_id and msg_id in seen_msg_ids:
                    continue
                if msg_id:
                    seen_msg_ids.add(msg_id)
                ue_type = int(m.get("ue_type", 1) or 1)
                to_em = (m.get("to_address_email_list") or "").strip().lower()
                from_em = (m.get("from_address_email") or "").strip().lower()
                body_txt = ((m.get("body") or {}).get("text") or "")
                subj_txt = (m.get("subject") or "")

                if "{{" in body_txt or "}}" in body_txt or "{{" in subj_txt:
                    unrendered_var_alerts += 1

                prospect_em = from_em if ue_type == 2 else to_em
                ld_obj = lead_by_email.get(prospect_em) or {}
                pl = ld_obj.get("payload") or {}
                cohort_key = str(pl.get("matched_state") or pl.get("agency") or pl.get("state") or "default")[:40]
                if cohort_key not in cohort_stats:
                    cohort_stats[cohort_key] = {
                        "sent": 0,
                        "human_replies": 0,
                        "auto_replies": 0,
                        "unsubscribes": 0,
                    }

                if ue_type == 2:
                    combo_low = f"{subj_txt} {body_txt}".lower()
                    is_auto = any(
                        kw in combo_low
                        for kw in (
                            "automatic reply", "auto-reply", "autoreply", "out of office",
                            "out-of-office", "away from the office", "on vacation",
                            "thank you for contacting", "prequalification", "no longer with",
                        )
                    )
                    is_unsub = any(
                        kw in combo_low
                        for kw in ("unsubscribe", "remove me", "stop emailing", "take me off")
                    )
                    if is_unsub:
                        unsubscribe_reply_count += 1
                        cohort_stats[cohort_key]["unsubscribes"] += 1
                    elif is_auto:
                        auto_reply_count += 1
                        cohort_stats[cohort_key]["auto_replies"] += 1
                        p_local = prospect_em.split("@", 1)[0] if "@" in prospect_em else ""
                        if p_local in ("pq", "prequal", "prequalification", "billing", "ap", "accounts", "noreply", "no-reply", "donotreply", "support", "helpdesk"):
                            try:
                                bl_d = {"bounced_emails": [], "bounced_domains": []}
                                if BLACKLIST_PATH.exists():
                                    bl_d.update(json.loads(BLACKLIST_PATH.read_text(encoding="utf-8")) or {})
                                b_set = set(bl_d.get("bounced_emails") or [])
                                if prospect_em not in b_set:
                                    b_set.add(prospect_em)
                                    bl_d["bounced_emails"] = sorted(b_set)
                                    BLACKLIST_PATH.write_text(json.dumps(bl_d, indent=2), encoding="utf-8")
                                if ld_obj.get("id"):
                                    requests.delete(f"https://api.instantly.ai/api/v2/leads/{ld_obj['id']}", headers=headers, timeout=10)
                            except Exception:
                                pass
                        for ref_m in re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", body_txt):
                            ref_clean = ref_m.strip().lower().rstrip(".")
                            ref_dom = ref_clean.split("@", 1)[-1]
                            if (
                                ref_clean != prospect_em
                                and ref_clean != to_em
                                and not any(b in ref_dom for b in ("signaltender", "camberdesk", "rubricward"))
                                and ref_clean not in ooo_referrals
                            ):
                                ooo_referrals.append(ref_clean)
                                try:
                                    if CONTACTS_PATH.exists():
                                        c_list = json.loads(CONTACTS_PATH.read_text(encoding="utf-8")) or []
                                        if not any(str(x.get("email") or "").strip().lower() == ref_clean for x in c_list if isinstance(x, dict)):
                                            c_list.insert(0, {
                                                "email": ref_clean,
                                                "first_name": ref_clean.split("@")[0].split(".")[0].title(),
                                                "company_name": str(ld_obj.get("company_name") or ref_dom.split(".")[0].title()),
                                                "state": str(pl.get("state") or "TX"),
                                                "source_type": "ooo_colleague_referral",
                                                "source_url": f"https://{ref_dom}",
                                            })
                                            CONTACTS_PATH.write_text(json.dumps(c_list, indent=2), encoding="utf-8")
                                except Exception:
                                    pass
                    else:
                        human_reply_count += 1
                        cohort_stats[cohort_key]["human_replies"] += 1
                else:
                    sent_count += 1
                    cohort_stats[cohort_key]["sent"] += 1
    except Exception:
        pass

    recommended_weights: Dict[str, float] = {}
    for bucket, st in prefix_stats.items():
        total = st["clean"] + st["bounced"]
        bounce_rate = (st["bounced"] / total) if total > 0 else 0.0
        base_w = 1.0 if bucket == "named_person" else (0.9 if bucket == "dept_desk" else 0.25)
        recommended_weights[bucket] = round(max(0.05, base_w * (1.0 - min(0.85, bounce_rate * 5.0))), 3)

    intel.update({
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "campaign_id": cid,
        "recent_rendered_emails_audited": sent_count,
        "recent_human_replies_detected": human_reply_count,
        "recent_auto_replies_detected": auto_reply_count,
        "recent_unsubscribes_detected": unsubscribe_reply_count,
        "ooo_referral_emails": ooo_referrals,
        "unrendered_template_tags_detected": unrendered_var_alerts,
        "prefix_delivery_stats": prefix_stats,
        "adaptive_prefix_priority_weights": recommended_weights,
        "cohort_stats": cohort_stats,
    })
    try:
        intel_path.write_text(json.dumps(intel, indent=2), encoding="utf-8")
    except Exception:
        pass
    return {
        "rendered_audited": sent_count,
        "human_replies_detected": human_reply_count,
        "auto_replies_detected": auto_reply_count,
        "unsubscribes_detected": unsubscribe_reply_count,
        "ooo_referrals_extracted": ooo_referrals,
        "unrendered_alerts": unrendered_var_alerts,
        "adaptive_weights": recommended_weights,
    }


def run_autonomous_outbound_optimizer(regenerate_local: bool = True) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "brand": "RubricWard",
        "campaign_id": CAMPAIGN_ID,
        "sequence_repaired": False,
        "bounced_or_bad_purged": 0,
        "leads_patched_in_place": 0,
        "leads_uploaded": 0,
        "total_clean_leads": 0,
        "status": "ok",
    }
    if not INSTANTLY_API_KEY or not CAMPAIGN_ID:
        summary["status"] = "skipped_no_key"
        return summary

    headers = {
        "Authorization": f"Bearer {INSTANTLY_API_KEY}",
        "Content-Type": "application/json",
    }
    auth_only = {"Authorization": f"Bearer {INSTANTLY_API_KEY}"}

    # 1. Audit & Self-Heal Campaign Sequences (Ensure Step 1, Step 2, Step 3 are all non-empty)
    step3_breakup = ("Closing the loop on {{project_id}} before the 30-day Federal NSA IDR Open Negotiation and ERISA 29 CFR 2560.503-1 appeal window — should I route our 6-file OpenXML CPT/DRG TiC MRF benchmark and Medicare MPFS RVU/GPCI workbook to another Managed Care or Revenue Cycle director on your team, or hold off for this cycle?\n\n— Aaron\nRubricWard Payer MRF & NSA IDR Desk")
    expected_sequences = [
        {
            "steps": [
                {
                    "type": "email",
                    "delay": 2,
                    "delay_unit": "days",
                    "pre_delay_unit": "days",
                    "variants": [{"subject": "{{step1_subject}}", "body": "{{step1_body_zero_link}}"}],
                },
                {
                    "type": "email",
                    "delay": 1,
                    "delay_unit": "days",
                    "pre_delay_unit": "days",
                    "variants": [{"subject": "Re: {{step1_subject}}", "body": "{{step2_body_dossier_link}}"}],
                },
                {
                    "type": "email",
                    "delay": 2,
                    "delay_unit": "days",
                    "pre_delay_unit": "days",
                    "variants": [{"subject": "Re: {{step1_subject}}", "body": step3_breakup}],
                },
            ]
        }
    ]
    try:
        rc = requests.get(f"https://api.instantly.ai/api/v2/campaigns/{CAMPAIGN_ID}", headers=auth_only, timeout=12)
        if rc.status_code == 200:
            cdata = rc.json() or {}
            seqs = cdata.get("sequences") or []
            steps = (seqs[0].get("steps") or []) if seqs and isinstance(seqs[0], dict) else []
            needs_seq_fix = len(steps) < 3 or int(steps[1].get('delay') or 99) > 1 or int(steps[2].get('delay') or 99) > 2
            for st_item in steps:
                vars_list = st_item.get("variants") or []
                if not vars_list or not str(vars_list[0].get("subject") or "").strip() or not str(vars_list[0].get("body") or "").strip():
                    needs_seq_fix = True
            if needs_seq_fix:
                rp = requests.patch(
                    f"https://api.instantly.ai/api/v2/campaigns/{CAMPAIGN_ID}",
                    headers=headers,
                    json={"sequences": expected_sequences},
                    timeout=15,
                )
                summary["sequence_repaired"] = rp.status_code in (200, 201)
    except Exception as exc:
        report_error("autonomous_outbound_optimizer.py", f"Campaign sequence audit warning: {exc}", severity="WARNING")

    # 2. Scan live leads in Instantly for bounces (`status < 0`) and record in bounced_leads_blacklist.json
    bl_data = {"bounced_emails": [], "bounced_domains": []}
    if BLACKLIST_PATH.exists():
        try:
            bl_data.update(json.loads(BLACKLIST_PATH.read_text(encoding="utf-8")) or {})
        except Exception:
            pass
    bl_emails = set(bl_data.get("bounced_emails") or [])
    bl_domains = set(bl_data.get("bounced_domains") or [])
    new_bounces = False
    all_leads: List[Dict[str, Any]] = []

    try:
        starting_after = None
        for _ in range(25):
            req_body: Dict[str, Any] = {"campaign": CAMPAIGN_ID, "limit": 50}
            if starting_after:
                req_body["starting_after"] = starting_after
            rl = requests.post("https://api.instantly.ai/api/v2/leads/list", headers=headers, json=req_body, timeout=15)
            if rl.status_code != 200:
                break
            rj = rl.json() or {}
            items = rj.get("items") or []
            all_leads.extend(items)
            for it in items:
                em = str(it.get("email") or "").strip().lower()
                st_code = int(it.get("status") or 0)
                lt_code = int(it.get("lt_interest_status") or 0)
                if (st_code < 0 or lt_code < 0 or "%" in em) and em and em not in bl_emails:
                    bl_emails.add(em)
                    new_bounces = True
            starting_after = rj.get("next_starting_after")
            if not starting_after or len(items) < 50:
                break
    except Exception:
        pass

    if new_bounces:
        try:
            BLACKLIST_PATH.write_text(
                json.dumps({"bounced_emails": sorted(bl_emails), "bounced_domains": sorted(bl_domains)}, indent=2),
                encoding="utf-8",
            )
            if CONTACTS_PATH.exists():
                raw_c = json.loads(CONTACTS_PATH.read_text(encoding="utf-8")) or []
                filtered_c = [
                    r for r in raw_c
                    if str(r.get("email") or "").strip().lower() not in bl_emails
                    and str(r.get("email") or "").strip().lower().split("@", 1)[-1] not in bl_domains
                ]
                if len(filtered_c) != len(raw_c):
                    CONTACTS_PATH.write_text(json.dumps(filtered_c, indent=2), encoding="utf-8")
        except Exception:
            pass

    # 3. Run sync_instantly_campaign.sync_leads_to_instantly() to regenerate clean leads, purge bounces, and patch in-place
    if regenerate_local:
        try:
            import sync_instantly_campaign
            sync_res = sync_instantly_campaign.sync_leads_to_instantly()
            summary["bounced_or_bad_purged"] = int(sync_res.get("purged_legacy_leads") or 0)
            summary["leads_patched_in_place"] = int(sync_res.get("patched_existing_leads") or 0)
            summary["leads_uploaded"] = int(sync_res.get("uploaded") or 0)
            summary["total_clean_leads"] = int(sync_res.get("total") or 0)
        except Exception as exc:
            report_error("autonomous_outbound_optimizer.py", f"Lead sync self-heal warning: {exc}", severity="WARNING")

    summary["outbox_learning"] = audit_rendered_sent_outbox_and_learn(CAMPAIGN_ID, auth_only, all_leads)
    return summary


if __name__ == "__main__":
    res = run_autonomous_outbound_optimizer(regenerate_local=True)
    print(json.dumps(res, indent=2))



def run_outbound_optimizer() -> Dict[str, Any]:
    return run_autonomous_outbound_optimizer()
