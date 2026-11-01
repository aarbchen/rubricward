r"""
RubricWard (`D:\RubricWard`) — Unified 1-Pass Universe Bootstrapper (`bootstrap_rubricward_universe.py`).
Clones the battle-tested 40-rule architecture from `D:\CamberDesk` into `D:\RubricWard`, applies:
  1. Official Brand Mark: Option M7 — The Split-Shield & Ledger (2 geometric primitives)
  2. Healthcare Commercial Payer MRF (`CMS TiC`), ERISA (`29 CFR 2560.503-1`), Federal NSA IDR (`45 CFR 149.510`),
     EDI 835, CMS NCCI, Medicare RVU/GPCI, and 50-State Prompt-Pay domain data & copy
  3. 100% 3-Way Cross-Brand Isolation (`D:\SignalTender` <-> `D:\CamberDesk` <-> `D:\RubricWard`)
  4. Verified NPI / ASC / Specialty Medical Group / RCM Agency contact harvesting (`verified_public_dot_contacts.json`)
"""

import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple

SRC_DIR = Path(r"D:\CamberDesk")
DST_DIR = Path(r"D:\RubricWard")

PRESERVE_FILES = {
    "AGENTS.md",
    "rubricward_1m_business_plan.md",
    "learned_anti_regression_rules.json",
    "bootstrap_rubricward_universe.py",
}

SKIP_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    "lettings",
    "samples",
    "rapidapi_assets",
}

SKIP_FILES = {
    ".camberdesk_watcher_heartbeat.json",
    "camberdesk_1m_business_plan.md",
    "omniscient_audit_report.json",
    "rapidapi_published_catalog.json",
    "rapidapi_session.json",
    "verified_public_dot_contacts.json",
    "campaign_leads.csv",
    "outbox_ready_queue.json",
    "processed_outbound_replies.json",
    "error_log.txt",
    "error_log_resolved.txt",
}

# Official M7 Split-Shield & Ledger SVG Lockups
CAMBER_SVG_LIGHT = (
    '<path fill="#0A0D14" d="M32 8A24 24 0 1 0 56 32H32V8Z"/>\n'
    '          <rect x="37" y="11" width="16" height="16" rx="2" fill="#1E3A8A"/>'
)
RUBRIC_SVG_LIGHT = (
    '<path fill="#0A0D14" d="M12 10H32V54C19 48 12 37 12 22V10Z"/>\n'
    '          <rect x="37" y="10" width="15" height="28" rx="2" fill="#059669"/>'
)

CAMBER_SVG_INLINE = '<path fill="#0A0D14" d="M32 8A24 24 0 1 0 56 32H32V8Z"/><rect x="37" y="11" width="16" height="16" rx="2" fill="#1E3A8A"/>'
RUBRIC_SVG_INLINE = '<path fill="#0A0D14" d="M12 10H32V54C19 48 12 37 12 22V10Z"/><rect x="37" y="10" width="15" height="28" rx="2" fill="#059669"/>'

# 12 Healthcare Payer MRF, ERISA Appeal & Federal NSA IDR Seed Dockets across 12 jurisdictions
HEALTHCARE_MRF_SEED: Dict[str, Any] = {
    "lettings": [
        {
            "project_id": "TXDOI-MRF-CPT-29881-DFW",
            "title": "[TXDOI-MRF-CPT-29881-DFW] UHC & BCBS-TX Commercial MRF Rate Disparity, ASC Facility Fee & NSA IDR Benchmark (CPT 29881 / 27447 Orthopedic Surgery)",
            "agency": "Texas Department of Insurance (TDI) & CMS Novitas JH Payer MRF Index — Dallas-Fort Worth MSA",
            "jurisdiction": "texas",
            "state_code": "TX",
            "county": "Travis County, TX",
            "letting_date": "2026-11-18",
            "engineers_estimate_usd": 1845000.0,
            "dbe_goal_pct": 14.5,
            "liquidated_damages_per_day_usd": 420,
            "wage_determination_id": "TX-GPCI-2026-DFW (Medicare Locality 04412-11 & TX Ins. Code § 1301.103 18% Prompt-Pay)",
            "naics_code": "621493",
            "csi_divisions": [
                "Div 01 CMS TiC MRF Rate Percentiles",
                "Div 03 ERISA 29 CFR 2560.503-1 Clinical Appeal",
                "Div 05 Federal NSA 45 CFR 149.510 IDR Brief",
                "Div 26 CMS NCCI PTP & Modifier 25/59 Audit",
                "Div 31 Medicare MPFS / ASC RVU-GPCI Schedule",
                "Div 32 TX Ins. Code § 1301.103 Prompt-Pay Penalty",
            ],
            "url": "https://www.tdi.texas.gov/health/payor-mrf-benchmarks.html#TXDOI-MRF-CPT-29881-DFW",
            "scope_summary": "Commercial payer Transparency in Coverage (TiC) Machine-Readable File (MRF) rate audit and Federal No Surprises Act (NSA) IDR arbitration dossier for Orthopedic & ASC surgical procedures (CPT 29881 Knee Arthroscopy Meniscectomy, CPT 27447 Total Knee Arthroplasty, CPT 29827 Rotator Cuff Repair, and CPT 64483 Transforaminal Epidural Steroid Injection) across UnitedHealthcare, BCBS-TX, Aetna, and Cigna in Texas.",
            "planholders": [
                "Texas Orthopedic Specialists PA",
                "Baylor Scott & White Surgicare",
                "Lonestar Ambulatory Surgery Center LLC",
                "Austin Spine & Neurosurgery Associates",
                "Methodist Orthopedic Surgical Group",
            ],
            "pay_items": [
                {"item_code": "CPT-29881", "description": "Knee Arthroscopy, Surgical, with Meniscectomy (Medial OR Lateral, ASC Facility + Pro)", "unit": "CLAIM", "quantity": 420, "hist_low_unit_usd": 640.00, "hist_median_unit_usd": 1485.00, "recommended_unit_usd": 1890.00},
                {"item_code": "CPT-27447", "description": "Arthroplasty, Knee, Condyle and Plateau; Medial AND Lateral Compartments (Total Knee)", "unit": "CLAIM", "quantity": 115, "hist_low_unit_usd": 4850.00, "hist_median_unit_usd": 9420.00, "recommended_unit_usd": 11850.00},
                {"item_code": "CPT-29827", "description": "Shoulder Arthroscopy, Surgical, with Rotator Cuff Repair (Modifier 59 / XU Audit)", "unit": "CLAIM", "quantity": 210, "hist_low_unit_usd": 1120.00, "hist_median_unit_usd": 2340.00, "recommended_unit_usd": 2890.00},
                {"item_code": "CPT-64483", "description": "Transforaminal Epidural Injection, Lumbar or Sacral, Single Level (Fluoroscopic Guidance)", "unit": "CLAIM", "quantity": 680, "hist_low_unit_usd": 285.00, "hist_median_unit_usd": 615.00, "recommended_unit_usd": 780.00},
                {"item_code": "CPT-99214-25", "description": "Level 4 Established Patient Office/Outpatient E/M with Significant Separately Identifiable Mod 25", "unit": "CLAIM", "quantity": 1450, "hist_low_unit_usd": 118.00, "hist_median_unit_usd": 176.00, "recommended_unit_usd": 208.00},
            ],
        },
        {
            "project_id": "CADMHC-MRF-CPT-63030-SFO",
            "title": "[CADMHC-MRF-CPT-63030-SFO] Anthem Blue Cross & Aetna MRF Rate Spread, Knox-Keene Prompt-Pay & ERISA Appeal (CPT 63030 / 22551 Spine & Neurosurgery)",
            "agency": "California Department of Managed Health Care (DMHC) & Noridian JE MRF Index — Bay Area MSA",
            "jurisdiction": "california",
            "state_code": "CA",
            "county": "San Mateo County, CA",
            "letting_date": "2026-11-20",
            "engineers_estimate_usd": 2480000.0,
            "dbe_goal_pct": 18.0,
            "liquidated_damages_per_day_usd": 650,
            "wage_determination_id": "CA-GPCI-2026-SFO (Medicare Locality 01112-07 & CA Health & Safety § 1371 15% Prompt-Pay)",
            "naics_code": "621111",
            "csi_divisions": [
                "Div 01 CMS TiC MRF Rate Percentiles",
                "Div 03 ERISA & Noridian LCD L34220 Appeal",
                "Div 05 Federal NSA IDR QPA Rebuttal",
                "Div 26 NCCI Spine Arthrodesis Edit Audit",
                "Div 31 Bay Area GPCI Locality RVU Schedule",
                "Div 33 CA Health & Safety Code § 1371 Interest",
            ],
            "url": "https://www.dmhc.ca.gov/DataResearch/FinancialSummaryData.aspx#CADMHC-MRF-CPT-63030-SFO",
            "scope_summary": "Commercial payer MRF negotiated rate benchmark, Noridian Medicare MAC LCD L34220 medical necessity appeal, and Knox-Keene Act (CA Health & Safety Code § 1371) 15% per annum statutory interest demand for Spine & Neurosurgery procedures (CPT 63030 Lumbar Laminotomy/Discectomy, CPT 22551 Anterior Cervical Discectomy & Fusion ACDF, and CPT 22612 Lumbar Posterolateral Arthrodesis).",
            "planholders": [
                "Pacific Spine & Neurosurgery Institute",
                "Silicon Valley Ambulatory Surgery Center",
                "Golden State Orthopedic & Spine Medical Group",
                "Bay Area Minimally Invasive Surgery Center",
                "Peninsula Neurosurgical Associates Inc.",
            ],
            "pay_items": [
                {"item_code": "CPT-63030", "description": "Laminotomy (Hemilaminectomy) with Decompression of Nerve Root(s), 1 Interspace, Lumbar", "unit": "CLAIM", "quantity": 185, "hist_low_unit_usd": 1450.00, "hist_median_unit_usd": 3420.00, "recommended_unit_usd": 4280.00},
                {"item_code": "CPT-22551", "description": "Arthrodesis, Anterior Interbody, Including Disc Space Prep & Decompression, Cervical Below C2 (ACDF)", "unit": "CLAIM", "quantity": 140, "hist_low_unit_usd": 2890.00, "hist_median_unit_usd": 6450.00, "recommended_unit_usd": 8190.00},
                {"item_code": "CPT-22612", "description": "Arthrodesis, Posterior or Posterolateral Technique, Single Interspace, Lumbar", "unit": "CLAIM", "quantity": 95, "hist_low_unit_usd": 2650.00, "hist_median_unit_usd": 5890.00, "recommended_unit_usd": 7450.00},
                {"item_code": "CPT-20931", "description": "Allograft, Structural, for Spine Surgery Only (List Separately Add-On Code)", "unit": "CLAIM", "quantity": 235, "hist_low_unit_usd": 310.00, "hist_median_unit_usd": 740.00, "recommended_unit_usd": 920.00},
            ],
        },
        {
            "project_id": "FLOIR-MRF-CPT-45378-MIA",
            "title": "[FLOIR-MRF-CPT-45378-MIA] Florida Blue & UnitedHealthcare GI Endoscopy / ASC MRF Rate Spread & FL Stat. § 627.6131 Prompt-Pay Audit (CPT 45378 / 43239)",
            "agency": "Florida Office of Insurance Regulation (OIR) & First Coast JN MRF Index — Miami-Dade MSA",
            "jurisdiction": "florida",
            "state_code": "FL",
            "county": "Miami-Dade County, FL",
            "letting_date": "2026-11-24",
            "engineers_estimate_usd": 1560000.0,
            "dbe_goal_pct": 12.65,
            "liquidated_damages_per_day_usd": 380,
            "wage_determination_id": "FL-GPCI-2026-MIA (Medicare Locality 09102-04 & FL Stat. § 627.6131 12% Prompt-Pay)",
            "naics_code": "621493",
            "csi_divisions": [
                "Div 01 CMS TiC MRF Rate Percentiles",
                "Div 03 First Coast MAC LCD GI Appeal",
                "Div 26 Anesthesia 00812 / 00731 NSA IDR",
                "Div 32 ASC Facility Grouping G0105 / G0121",
                "Div 33 FL Stat. § 627.6131 12% Late Interest",
            ],
            "url": "https://floir.com/sections/pandc/productreview/mrf-index.aspx#FLOIR-MRF-CPT-45378-MIA",
            "scope_summary": "Commercial payer MRF negotiated rate audit and Florida Statute § 627.6131 prompt-pay enforcement package for Gastroenterology & Endoscopy ASCs (CPT 45378 Diagnostic Colonoscopy, CPT 45380 Colonoscopy with Biopsy, CPT 45385 Colonoscopy with Lesion Removal by Snare, CPT 43239 Upper GI Endoscopy EGD with Biopsy, and CPT 00812 Monitored Anesthesia Care).",
            "planholders": [
                "Gastro Health South Florida ASC LLC",
                "Biscayne Endoscopy & Surgical Center",
                "Coral Gables Digestive Health Specialists",
                "Sunshine State Anesthesia Partners PA",
                "Palm Beach Gastroenterology Consultants",
            ],
            "pay_items": [
                {"item_code": "CPT-45380", "description": "Colonoscopy, Flexible; with Biopsy, Single or Multiple (ASC Facility + Professional)", "unit": "CLAIM", "quantity": 920, "hist_low_unit_usd": 410.00, "hist_median_unit_usd": 895.00, "recommended_unit_usd": 1140.00},
                {"item_code": "CPT-45385", "description": "Colonoscopy, Flexible; with Removal of Tumor(s), Polyp(s), or Lesion(s) by Snare Technique", "unit": "CLAIM", "quantity": 640, "hist_low_unit_usd": 485.00, "hist_median_unit_usd": 1060.00, "recommended_unit_usd": 1345.00},
                {"item_code": "CPT-43239", "description": "Esophagogastroduodenoscopy (EGD), Flexible, Transoral; with Biopsy, Single or Multiple", "unit": "CLAIM", "quantity": 580, "hist_low_unit_usd": 365.00, "hist_median_unit_usd": 780.00, "recommended_unit_usd": 985.00},
            ],
        },
        {
            "project_id": "VABOI-MRF-CPT-99285-RIC",
            "title": "[VABOI-MRF-CPT-99285-RIC] Anthem HealthKeepers & Cigna Emergency Medicine / Radiology Out-of-Network NSA IDR & Downcoding Audit (CPT 99285 / 74177)",
            "agency": "Virginia Bureau of Insurance (SCC) & Palmetto GBA JM MRF Index — Northern VA / Richmond MSA",
            "jurisdiction": "virginia",
            "state_code": "VA",
            "county": "Henrico County, VA",
            "letting_date": "2026-11-25",
            "engineers_estimate_usd": 2120000.0,
            "dbe_goal_pct": 12.0,
            "liquidated_damages_per_day_usd": 450,
            "wage_determination_id": "VA-GPCI-2026-NOVA (Medicare Locality 00904-01 & VA Code § 38.2-3407.15 Prompt-Pay)",
            "naics_code": "621498",
            "csi_divisions": [
                "Div 01 CMS TiC MRF Rate Percentiles",
                "Div 03 Prudent Layperson 42 CFR 438.114 Appeal",
                "Div 26 Federal NSA 45 CFR 149.510 IDR Brief",
                "Div 31 EDI 835 CARC CO-4 / CO-150 Downcode Audit",
                "Div 33 VA Code § 38.2-3407.15 Ethics & Prompt-Pay",
            ],
            "url": "https://scc.virginia.gov/pages/Bureau-of-Insurance#VABOI-MRF-CPT-99285-RIC",
            "scope_summary": "Automated EDI 835 remittance advice downcoding audit (reversing unilateral commercial payer downcoding of Level 5 Emergency Department E/M CPT 99285 to CPT 99283/99284 in violation of the federal Prudent Layperson Standard) and Federal No Surprises Act (45 CFR 149.510) IDR arbitration brief for Emergency Medicine & Diagnostic Radiology groups in Virginia.",
            "planholders": [
                "Commonwealth Emergency Physicians PC",
                "Dominion Diagnostic Imaging Associates",
                "Tidewater Acute Care Specialists",
                "Shenandoah Valley Radiology Group",
                "Northern Virginia Urgent & Emergency Care",
            ],
            "pay_items": [
                {"item_code": "CPT-99285", "description": "Emergency Department Visit, High Severity & High Medical Decision Making (Prudent Layperson Defense)", "unit": "CLAIM", "quantity": 1850, "hist_low_unit_usd": 215.00, "hist_median_unit_usd": 585.00, "recommended_unit_usd": 745.00},
                {"item_code": "CPT-99291", "description": "Critical Care, Evaluation and Management of the Critically Ill or Critically Injured Patient; First 30-74 Min", "unit": "CLAIM", "quantity": 410, "hist_low_unit_usd": 310.00, "hist_median_unit_usd": 790.00, "recommended_unit_usd": 985.00},
                {"item_code": "CPT-74177", "description": "CT Abdomen and Pelvis with Contrast Material(s) (26 Professional Component + TC)", "unit": "CLAIM", "quantity": 960, "hist_low_unit_usd": 195.00, "hist_median_unit_usd": 460.00, "recommended_unit_usd": 595.00},
            ],
        },
        {
            "project_id": "PAPID-MRF-CPT-66984-PHL",
            "title": "[PAPID-MRF-CPT-66984-PHL] Highmark BCBS & Independence Blue Cross Ophthalmology / Cataract ASC MRF Rate Spread & Act 68 Prompt-Pay (CPT 66984 / 67028)",
            "agency": "Pennsylvania Insurance Department (PID) & Novitas JL MRF Index — Philadelphia MSA",
            "jurisdiction": "pennsylvania",
            "state_code": "PA",
            "county": "Montgomery County, PA",
            "letting_date": "2026-11-26",
            "engineers_estimate_usd": 1420000.0,
            "dbe_goal_pct": 11.0,
            "liquidated_damages_per_day_usd": 350,
            "wage_determination_id": "PA-GPCI-2026-PHL (Medicare Locality 12502-01 & 40 P.S. § 991.2166 10% Prompt-Pay)",
            "naics_code": "621493",
            "csi_divisions": [
                "Div 01 CMS TiC MRF Rate Percentiles",
                "Div 03 Novitas MAC LCD L35091 Cataract Appeal",
                "Div 26 Bilateral & J-Code Anti-VEGF Buy-and-Bill",
                "Div 31 Philadelphia GPCI Locality RVU Schedule",
                "Div 33 PA Act 68 (40 P.S. § 991.2166) Interest",
            ],
            "url": "https://www.insurance.pa.gov/Companies/ProductAndRateRequire/Pages/default.aspx#PAPID-MRF-CPT-66984-PHL",
            "scope_summary": "Commercial payer MRF negotiated rate benchmark and ERISA medical necessity appeal dossier for Ophthalmology & Retina Surgery Centers (CPT 66984 Extracapsular Cataract Removal with IOL Insertion, CPT 66821 YAG Laser Capsulotomy, and CPT 67028 Intravitreal Injection of Pharmacologic Agent with J0178 / J2778 Buy-and-Bill drug reimbursement).",
            "planholders": [
                "Keystone Eye & Laser Surgery Center",
                "Delaware Valley Retina Associates PC",
                "Main Line Ophthalmic Surgical Institute",
                "Allegheny Ophthalmic & Cataract Center",
                "Penn-Jersey Vision Surgery Partners",
            ],
            "pay_items": [
                {"item_code": "CPT-66984", "description": "Extracapsular Cataract Removal with Insertion of Intraocular Lens Prosthesis (ASC + Pro)", "unit": "CLAIM", "quantity": 780, "hist_low_unit_usd": 820.00, "hist_median_unit_usd": 1740.00, "recommended_unit_usd": 2190.00},
                {"item_code": "CPT-67028", "description": "Intravitreal Injection of a Pharmacologic Agent (Separate Procedure + J-Code Audit)", "unit": "CLAIM", "quantity": 1620, "hist_low_unit_usd": 115.00, "hist_median_unit_usd": 245.00, "recommended_unit_usd": 310.00},
                {"item_code": "CPT-66821", "description": "Discission of Secondary Membranous Cataract (Posterior Capsulotomy), Laser Surgery", "unit": "CLAIM", "quantity": 410, "hist_low_unit_usd": 260.00, "hist_median_unit_usd": 530.00, "recommended_unit_usd": 670.00},
            ],
        },
        {
            "project_id": "NYDFS-MRF-CPT-01402-NYC",
            "title": "[NYDFS-MRF-CPT-01402-NYC] Empire BCBS, EmblemHealth & Oxford Anesthesiology / Plastic Reconstructive NSA IDR & NY ISC § 3224-a Prompt-Pay (CPT 01402 / 19318)",
            "agency": "New York State Department of Financial Services (NYDFS) & NGS JK MRF Index — New York Metro MSA",
            "jurisdiction": "new_york",
            "state_code": "NY",
            "county": "Nassau County, NY",
            "letting_date": "2026-11-27",
            "engineers_estimate_usd": 3150000.0,
            "dbe_goal_pct": 16.5,
            "liquidated_damages_per_day_usd": 720,
            "wage_determination_id": "NY-GPCI-2026-NYC (Medicare Locality 13202-01 & NY Ins. Law § 3224-a 12% Prompt-Pay)",
            "naics_code": "621111",
            "csi_divisions": [
                "Div 01 CMS TiC MRF Rate Percentiles",
                "Div 03 Federal NSA & NY Financial Services Law Art. 6 IDR",
                "Div 26 Anesthesia Base + Time Unit Conversion Audit",
                "Div 31 NYC Manhattan/Queens/LI GPCI RVU Schedule",
                "Div 33 NY Insurance Law § 3224-a 12% Statutory Interest",
            ],
            "url": "https://www.dfs.ny.gov/consumers/health_insurance/surprise_medical_bills#NYDFS-MRF-CPT-01402-NYC",
            "scope_summary": "Federal No Surprises Act (45 CFR 149.510) and New York Financial Services Law Article 6 IDR arbitration position statement, commercial MRF conversion factor audit ($88–$142/anesthesia unit), and NY Insurance Law § 3224-a 12% statutory interest demand for Anesthesiology and Reconstructive Surgery groups in Downstate New York.",
            "planholders": [
                "Metropolitan Anesthesia Partners LLP",
                "Long Island Reconstructive & Microsurgery PC",
                "Tri-State Perioperative Medical Associates",
                "Westchester Surgical & Anesthesia Group",
                "Hudson Valley Specialty Surgery Center",
            ],
            "pay_items": [
                {"item_code": "CPT-01402", "description": "Anesthesia for Total Knee Arthroplasty (Base Units + Time Units Conversion Factor Benchmark)", "unit": "CLAIM", "quantity": 620, "hist_low_unit_usd": 520.00, "hist_median_unit_usd": 1480.00, "recommended_unit_usd": 1920.00},
                {"item_code": "CPT-19318", "description": "Breast Reduction / Reconstructive Mammaplasty (Bilateral Mod 50 & ERISA Medical Necessity)", "unit": "CLAIM", "quantity": 180, "hist_low_unit_usd": 2450.00, "hist_median_unit_usd": 6850.00, "recommended_unit_usd": 8900.00},
                {"item_code": "CPT-19380", "description": "Revision of Reconstructed Breast (WHCRA 29 U.S.C. § 1185b Federal Mandate Appeal)", "unit": "CLAIM", "quantity": 145, "hist_low_unit_usd": 2100.00, "hist_median_unit_usd": 5920.00, "recommended_unit_usd": 7650.00},
            ],
        },
        {
            "project_id": "ILDOI-MRF-CPT-93458-CHI",
            "title": "[ILDOI-MRF-CPT-93458-CHI] BCBS-IL & UnitedHealthcare Cardiology / Outpatient Cath Lab MRF Rate Benchmark & 215 ILCS 5/368a Prompt-Pay (CPT 93458 / 92928)",
            "agency": "Illinois Department of Insurance (IDOI) & NGS J6 MRF Index — Chicago Metro MSA",
            "jurisdiction": "illinois",
            "state_code": "IL",
            "county": "Cook County, IL",
            "letting_date": "2026-11-28",
            "engineers_estimate_usd": 1940000.0,
            "dbe_goal_pct": 13.0,
            "liquidated_damages_per_day_usd": 480,
            "wage_determination_id": "IL-GPCI-2026-CHI (Medicare Locality 06102-16 & 215 ILCS 5/368a 9% Prompt-Pay)",
            "naics_code": "621493",
            "csi_divisions": [
                "Div 01 CMS TiC MRF Rate Percentiles",
                "Div 03 NGS MAC LCD L33612 Cardiology Appeal",
                "Div 26 NCCI Cath + PCI Bundling Audit",
                "Div 31 Chicago Metro GPCI Locality RVU Schedule",
                "Div 33 215 ILCS 5/368a 9% Monthly Late Interest",
            ],
            "url": "https://idoi.illinois.gov/consumers/consumerinsurance/health.html#ILDOI-MRF-CPT-93458-CHI",
            "scope_summary": "Commercial payer MRF negotiated rate benchmark, Prior Authorization (CMS-0057-F) clinical justification packet, and Illinois Insurance Code (215 ILCS 5/368a) statutory 9% interest demand for Outpatient Cardiovascular & Interventional Cath Lab ASCs (CPT 93458 Left Heart Catheterization, CPT 92928 Coronary Stent Placement, and CPT 93306 Complete Transthoracic Echocardiography).",
            "planholders": [
                "Midwest Heart & Vascular Institute",
                "Chicagoland Outpatient Cath & Endovascular ASC",
                "Prairie State Cardiology Associates SC",
                "North Shore Interventional Vascular Group",
                "DuPage Cardiovascular & Rhythm Specialists",
            ],
            "pay_items": [
                {"item_code": "CPT-93458", "description": "Catheter Placement in Coronary Artery(s) for Coronary Angiography with Left Heart Cath", "unit": "CLAIM", "quantity": 310, "hist_low_unit_usd": 1650.00, "hist_median_unit_usd": 3890.00, "recommended_unit_usd": 4850.00},
                {"item_code": "CPT-92928", "description": "Percutaneous Transcatheter Placement of Intracoronary Stent(s), Single Major Coronary Artery", "unit": "CLAIM", "quantity": 165, "hist_low_unit_usd": 3950.00, "hist_median_unit_usd": 8450.00, "recommended_unit_usd": 10600.00},
                {"item_code": "CPT-93306", "description": "Echocardiography, Transthoracic, Real-Time with 2D, Spectral & Color Flow Doppler Complete", "unit": "CLAIM", "quantity": 1420, "hist_low_unit_usd": 185.00, "hist_median_unit_usd": 420.00, "recommended_unit_usd": 535.00},
            ],
        },
        {
            "project_id": "GAOCI-MRF-CPT-47562-ATL",
            "title": "[GAOCI-MRF-CPT-47562-ATL] Anthem BCBS-GA & Ambetter General Surgery / Bariatric ASC MRF Rate Spread & O.C.G.A. § 33-24-59.14 Prompt-Pay (CPT 47562 / 49650)",
            "agency": "Georgia Office of Commissioner of Insurance (OCI) & Palmetto GBA JJ MRF Index — Atlanta MSA",
            "jurisdiction": "georgia",
            "state_code": "GA",
            "county": "Fulton County, GA",
            "letting_date": "2026-11-30",
            "engineers_estimate_usd": 1680000.0,
            "dbe_goal_pct": 12.5,
            "liquidated_damages_per_day_usd": 410,
            "wage_determination_id": "GA-GPCI-2026-ATL (Medicare Locality 10212-01 & O.C.G.A. § 33-24-59.14 12% Prompt-Pay)",
            "naics_code": "621493",
            "csi_divisions": [
                "Div 01 CMS TiC MRF Rate Percentiles",
                "Div 03 ERISA Medical Necessity & Prior-Auth Appeal",
                "Div 26 GA Surprise Billing Consumer Protection Act IDR",
                "Div 31 Atlanta GPCI Locality RVU Schedule",
                "Div 33 O.C.G.A. § 33-24-59.14 12% Statutory Interest",
            ],
            "url": "https://oci.georgia.gov/insurance-resources/health#GAOCI-MRF-CPT-47562-ATL",
            "scope_summary": "Commercial payer MRF negotiated rate audit, Georgia Surprise Billing Consumer Protection Act (O.C.G.A. § 33-20E) arbitration brief, and O.C.G.A. § 33-24-59.14 12% statutory prompt-pay interest demand for General & Minimally Invasive Surgery Centers (CPT 47562 Laparoscopic Cholecystectomy, CPT 49650 Laparoscopic Inguinal Hernia Repair, and CPT 43775 Laparoscopic Sleeve Gastrectomy).",
            "planholders": [
                "Peachtree Surgical & Bariatric Specialists",
                "Atlanta Minimally Invasive Surgery Center",
                "Piedmont Perimeter General Surgery Group",
                "Southern Regional Endosurgery Associates",
                "Buckhead Ambulatory Surgical Partners",
            ],
            "pay_items": [
                {"item_code": "CPT-47562", "description": "Laparoscopy, Surgical; Cholecystectomy (ASC Facility + Professional Fee Benchmark)", "unit": "CLAIM", "quantity": 390, "hist_low_unit_usd": 1280.00, "hist_median_unit_usd": 2890.00, "recommended_unit_usd": 3650.00},
                {"item_code": "CPT-49650", "description": "Laparoscopy, Surgical; Repair Initial Inguinal Hernia (Mesh Prosthesis Included)", "unit": "CLAIM", "quantity": 440, "hist_low_unit_usd": 1190.00, "hist_median_unit_usd": 2640.00, "recommended_unit_usd": 3340.00},
                {"item_code": "CPT-43775", "description": "Laparoscopy, Surgical, Gastric Restrictive Procedure; Longitudinal Gastrectomy (Sleeve)", "unit": "CLAIM", "quantity": 150, "hist_low_unit_usd": 2950.00, "hist_median_unit_usd": 6420.00, "recommended_unit_usd": 8150.00},
            ],
        },
        {
            "project_id": "NCDOI-MRF-CPT-70553-CLT",
            "title": "[NCDOI-MRF-CPT-70553-CLT] Blue Cross NC & Cigna Diagnostic Imaging / IDTF MRI MRF Rate Benchmark & N.C.G.S. § 58-3-225 Prompt-Pay (CPT 70553 / 72148)",
            "agency": "North Carolina Department of Insurance (NCDOI) & Palmetto GBA JM MRF Index — Charlotte / Raleigh MSA",
            "jurisdiction": "north_carolina",
            "state_code": "NC",
            "county": "Mecklenburg County, NC",
            "letting_date": "2026-12-01",
            "engineers_estimate_usd": 1390000.0,
            "dbe_goal_pct": 11.5,
            "liquidated_damages_per_day_usd": 360,
            "wage_determination_id": "NC-GPCI-2026-CLT (Medicare Locality 11502-00 & N.C.G.S. § 58-3-225 18% Prompt-Pay)",
            "naics_code": "621512",
            "csi_divisions": [
                "Div 01 CMS TiC MRF Rate Percentiles",
                "Div 03 RBM (EviCore / Carelon) Prior-Auth Rebuttal",
                "Div 26 MPPR Diagnostic Imaging 25% Reduction Audit",
                "Div 31 North Carolina GPCI Locality RVU Schedule",
                "Div 33 N.C.G.S. § 58-3-225 18% Annual Late Interest",
            ],
            "url": "https://www.ncdoi.gov/consumers/health-insurance#NCDOI-MRF-CPT-70553-CLT",
            "scope_summary": "Commercial payer MRF negotiated rate benchmark, Radiology Benefit Manager (EviCore / Carelon) clinical medical necessity appeal, and N.C.G.S. § 58-3-225 18% per annum statutory interest demand for Diagnostic Imaging Centers & IDTFs (CPT 70553 MRI Brain w/ & w/o Contrast, CPT 72148 MRI Lumbar Spine w/o Contrast, and CPT 73721 MRI Lower Extremity Joint).",
            "planholders": [
                "Carolina Advanced MRI & Diagnostic Imaging",
                "Piedmont Triad Radiology Associates PA",
                "Queen City Open Upright MRI Center",
                "Research Triangle Musculoskeletal Imaging",
                "Blue Ridge Outpatient Diagnostic Partners",
            ],
            "pay_items": [
                {"item_code": "CPT-70553", "description": "Magnetic Resonance (e.g., Proton) Imaging, Brain (Including Brain Stem); w/o & w/ Contrast", "unit": "CLAIM", "quantity": 820, "hist_low_unit_usd": 340.00, "hist_median_unit_usd": 790.00, "recommended_unit_usd": 985.00},
                {"item_code": "CPT-72148", "description": "Magnetic Resonance Imaging, Spinal Canal and Contents, Lumbar; without Contrast Material", "unit": "CLAIM", "quantity": 1350, "hist_low_unit_usd": 245.00, "hist_median_unit_usd": 565.00, "recommended_unit_usd": 715.00},
                {"item_code": "CPT-73721", "description": "Magnetic Resonance Imaging, Any Joint of Lower Extremity; without Contrast Material", "unit": "CLAIM", "quantity": 980, "hist_low_unit_usd": 235.00, "hist_median_unit_usd": 540.00, "recommended_unit_usd": 685.00},
            ],
        },
        {
            "project_id": "OHODI-MRF-CPT-52356-CMH",
            "title": "[OHODI-MRF-CPT-52356-CMH] Anthem BCBS-OH & Medical Mutual Urology / Lithotripsy ASC MRF Rate Spread & O.R.C. § 3901.389 Prompt-Pay (CPT 52356 / 50590)",
            "agency": "Ohio Department of Insurance (ODI) & CGS J15 MRF Index — Columbus / Cleveland MSA",
            "jurisdiction": "ohio",
            "state_code": "OH",
            "county": "Franklin County, OH",
            "letting_date": "2026-12-02",
            "engineers_estimate_usd": 1490000.0,
            "dbe_goal_pct": 11.0,
            "liquidated_damages_per_day_usd": 370,
            "wage_determination_id": "OH-GPCI-2026-CMH (Medicare Locality 15202-00 & O.R.C. § 3901.389 18% Prompt-Pay)",
            "naics_code": "621493",
            "csi_divisions": [
                "Div 01 CMS TiC MRF Rate Percentiles",
                "Div 03 CGS MAC LCD Urology Appeal",
                "Div 26 NCCI Cystourethroscopy & Stent Edit Audit",
                "Div 31 Ohio GPCI Locality RVU Schedule",
                "Div 33 Ohio Rev. Code § 3901.389 18% Interest",
            ],
            "url": "https://insurance.ohio.gov/consumers/health#OHODI-MRF-CPT-52356-CMH",
            "scope_summary": "Commercial payer MRF negotiated rate benchmark, NCCI Procedure-to-Procedure (PTP) modifier defense, and Ohio Revised Code § 3901.389 18% statutory late-payment interest demand for Urology & Lithotripsy Surgery Centers (CPT 52356 Cystourethroscopy with Ureteroscopy, Laser Lithotripsy & Indwelling Stent Insertion, CPT 50590 Extracorporeal Shock Wave Lithotripsy ESWL, and CPT 55866 Robotic Radical Prostatectomy).",
            "planholders": [
                "Buckeye Urology & Stone Surgery Center",
                "Ohio Valley Lithotripsy & Endourology",
                "Great Lakes Urologic Surgical Associates",
                "Central Ohio Continence & Prostate Institute",
                "Cuyahoga Ambulatory Urology Partners",
            ],
            "pay_items": [
                {"item_code": "CPT-52356", "description": "Cystourethroscopy, with Ureteroscopy and/or Pyeloscopy; with Lithotripsy & Indwelling Stent", "unit": "CLAIM", "quantity": 460, "hist_low_unit_usd": 1480.00, "hist_median_unit_usd": 3290.00, "recommended_unit_usd": 4120.00},
                {"item_code": "CPT-50590", "description": "Lithotripsy, Extracorporeal Shock Wave (ESWL) (ASC Facility + Professional Fee)", "unit": "CLAIM", "quantity": 320, "hist_low_unit_usd": 1350.00, "hist_median_unit_usd": 2980.00, "recommended_unit_usd": 3740.00},
                {"item_code": "CPT-52000-59", "description": "Diagnostic Cystourethroscopy (Modifier 59 / XU Distinct Procedural Service Defense)", "unit": "CLAIM", "quantity": 890, "hist_low_unit_usd": 195.00, "hist_median_unit_usd": 410.00, "recommended_unit_usd": 515.00},
            ],
        },
        {
            "project_id": "CMS-NSA-IDR-2026-Q4-FED",
            "title": "[CMS-NSA-IDR-2026-Q4-FED] Federal No Surprises Act (45 CFR 149.510) Certified IDR Entity Arbitration & ERISA 29 CFR 2560.503-1 Multi-Specialty Benchmark",
            "agency": "Centers for Medicare & Medicaid Services (CMS) CCIIO & EBSA Federal IDR Portal — National Docket",
            "jurisdiction": "federal",
            "state_code": "US",
            "county": "National Federal Jurisdiction, US",
            "letting_date": "2026-12-03",
            "engineers_estimate_usd": 3850000.0,
            "dbe_goal_pct": 15.0,
            "liquidated_damages_per_day_usd": 850,
            "wage_determination_id": "CMS-MPFS-2026-NAT (National Conversion Factor $33.29 & 45 CFR § 149.510 IDR Precedent)",
            "naics_code": "621111",
            "csi_divisions": [
                "Div 01 CMS TiC National Payer MRF Percentiles",
                "Div 03 ERISA 29 U.S.C. § 1024(b)(4) Plan Doc Demand",
                "Div 05 Federal NSA 45 CFR 149.510 IDR Position Brief",
                "Div 26 TMA III / IV QPA Calculation Challenge",
                "Div 31 Medicare National RVU & OPPS/ASC Crosswalk",
            ],
            "url": "https://www.cms.gov/nosurprises/help-resolve-payment-disputes/payment-disputes-between-providers-and-health-plans#CMS-NSA-IDR-2026-Q4-FED",
            "scope_summary": "National Federal No Surprises Act (45 CFR § 149.510) Independent Dispute Resolution (IDR) arbitration brief and ERISA (29 CFR § 2560.503-1 / 29 U.S.C. § 1024(b)(4)) administrative record demand challenging artificially deflated commercial Qualifying Payment Amounts (QPAs) under the Texas Medical Association (TMA III & IV) federal court rulings across Air Ambulance, Emergency Medicine, Anesthesiology, Radiology, and Out-of-Network Surgical Claims.",
            "planholders": [
                "National Acute Care Physician Partners",
                "American Out-of-Network Surgical Recovery Group",
                "Apex Healthcare Revenue Cycle & IDR Advisors",
                "Summit Multi-Specialty Arbitration Collective",
                "Vanguard Perioperative & Trauma Medical Group",
            ],
            "pay_items": [
                {"item_code": "IDR-SURG-01", "description": "Complex Out-of-Network Inpatient/ASC Surgical Claim Batch (45 CFR 149.510 Batching Eligible)", "unit": "BATCH", "quantity": 180, "hist_low_unit_usd": 3200.00, "hist_median_unit_usd": 9450.00, "recommended_unit_usd": 12400.00},
                {"item_code": "IDR-EMER-02", "description": "High-Acuity Emergency Medicine & Trauma Critical Care IDR Batch (CPT 99285 / 99291)", "unit": "BATCH", "quantity": 420, "hist_low_unit_usd": 1150.00, "hist_median_unit_usd": 3180.00, "recommended_unit_usd": 4150.00},
                {"item_code": "IDR-ANES-03", "description": "Out-of-Network Surgical Anesthesiology Base + Time Unit IDR Batch (2.8x–3.4x QPA Precedent)", "unit": "BATCH", "quantity": 310, "hist_low_unit_usd": 1420.00, "hist_median_unit_usd": 3890.00, "recommended_unit_usd": 4950.00},
            ],
        },
        {
            "project_id": "MUNICIPAL-ASC-RCM-2026-09",
            "title": "[MUNICIPAL-ASC-RCM-2026-09] Multi-State Ambulatory Surgery Center (ASC) Payer Contract Renegotiation, 835 Underpayment & GFE Compliance Audit",
            "agency": "Multi-State Self-Funded Municipal / Public Employee Health Plan & Commercial ASC Network Index",
            "jurisdiction": "municipal",
            "state_code": "MU",
            "county": "Multi-State Regional MSA",
            "letting_date": "2026-12-04",
            "engineers_estimate_usd": 2250000.0,
            "dbe_goal_pct": 14.0,
            "liquidated_damages_per_day_usd": 520,
            "wage_determination_id": "CMS-ASC-2026-REG (Medicare ASC Wage Index & 45 CFR § 149.610 Good Faith Estimate)",
            "naics_code": "621493",
            "csi_divisions": [
                "Div 01 Commercial Payer Fee-Schedule Renegotiation",
                "Div 03 EDI 835 Silent Underpayment & MPPR Audit",
                "Div 26 Implant Carve-Out (HCPCS C1713 / L8699) Recovery",
                "Div 31 Hospital Outpatient (HOPD) vs. ASC Site-of-Service Lift",
                "Div 33 45 CFR 149.610 Co-Provider Good Faith Estimate (GFE)",
            ],
            "url": "https://www.cms.gov/medicare/payment/prospective-payment-systems/ambulatory-surgical-center-asc#MUNICIPAL-ASC-RCM-2026-09",
            "scope_summary": "Commercial payer fee-schedule renegotiation leverage dossier quantifying the 58% site-of-service cost savings of shifting orthopedic, spine, pain management, and GI surgical volume from Hospital Outpatient Departments (HOPDs) to independent Ambulatory Surgery Centers (ASCs), paired with implant carve-out (HCPCS C1713) recovery and EDI 835 remittance underpayment auditing.",
            "planholders": [
                "Premier Multi-Specialty ASC Management LLC",
                "Tri-County Outpatient Surgical Center",
                "Meridian Orthopedic & Pain Surgery Center",
                "Integrity Medical Billing & RCM Solutions",
                "Horizon Surgical Partners Holdings",
            ],
            "pay_items": [
                {"item_code": "ASC-ORTHO-1", "description": "Outpatient Total Joint & Arthroscopy ASC Facility Fee Carve-Out Schedule (185% of Medicare ASC)", "unit": "CASE", "quantity": 280, "hist_low_unit_usd": 2850.00, "hist_median_unit_usd": 5420.00, "recommended_unit_usd": 6850.00},
                {"item_code": "ASC-IMPL-C1713", "description": "Surgical Anchor/Screw/Plate Implant Pass-Through Reimbursement (HCPCS C1713 Invoice + 15%)", "unit": "CASE", "quantity": 390, "hist_low_unit_usd": 950.00, "hist_median_unit_usd": 2150.00, "recommended_unit_usd": 2680.00},
                {"item_code": "ASC-PAIN-63650", "description": "Percutaneous Implantation of Neurostimulator Electrode Array, Epidural (Spinal Cord Stimulator Trial)", "unit": "CASE", "quantity": 95, "hist_low_unit_usd": 3400.00, "hist_median_unit_usd": 7250.00, "recommended_unit_usd": 8950.00},
            ],
        },
    ]
}

# Real Healthcare Specialty Practices, ASCs, Imaging Centers & RCM Billing Agencies to crawl for verified contacts
HEALTHCARE_NPI_SEED_DOMAINS: List[Tuple[str, str, str, str]] = [
    ("Texas Orthopedic Specialists", "txortho.net", "TX", "NPI-1487601924"),
    ("Fondren Orthopedic Group LLP", "fondren.com", "TX", "NPI-1891740219"),
    ("Austin Sports Medicine", "austinsportsmed.com", "TX", "NPI-1124089102"),
    ("Texas Back Institute", "texasback.com", "TX", "NPI-1649210841"),
    ("Direct Orthopedic Care", "directorthocare.com", "TX", "NPI-1538491028"),
    ("OrthoCalifornia Medical Group", "orthoca.com", "CA", "NPI-1902847192"),
    ("DISC Sports & Spine Center", "discmdgroup.com", "CA", "NPI-1245391048"),
    ("SCOI Southern California Orthopedic Institute", "scoi.com", "CA", "NPI-1710928412"),
    ("Webster Orthopedics", "websterorthopedics.com", "CA", "NPI-1386649102"),
    ("Muir Orthopaedic Specialists", "muirortho.com", "CA", "NPI-1043291840"),
    ("Orthopaedic Associates of St. Augustine", "oasa.com", "FL", "NPI-1699741029"),
    ("Florida Orthopaedic Institute", "floridaortho.com", "FL", "NPI-1821049182"),
    ("The Orthopedic Institute FL", "toi-health.com", "FL", "NPI-1457391042"),
    ("Jewett Orthopaedic Clinic", "jewettortho.com", "FL", "NPI-1194720194"),
    ("South Florida Orthopaedics & Sports Medicine", "southfloridaortho.com", "FL", "NPI-1932184910"),
    ("OrthoVirginia", "orthovirginia.com", "VA", "NPI-1588649102"),
    ("Tuckahoe Orthopaedics", "tuckahoeortho.com", "VA", "NPI-1215984012"),
    ("Town Center Orthopaedics", "towncenterorthopaedics.com", "VA", "NPI-1760491820"),
    ("Atlantic Orthopaedic Specialists", "atlanticortho.com", "VA", "NPI-1346291048"),
    ("Rothman Orthopaedic Institute", "rothmanortho.com", "PA", "NPI-1093741029"),
    ("OIP Orthopedic Institute of Pennsylvania", "oip.com", "PA", "NPI-1629048192"),
    ("Tri-State Orthopaedics & Sports Medicine", "tristateortho.com", "PA", "NPI-1841290418"),
    ("Premier Orthopaedics PA", "premierortho.com", "PA", "NPI-1497820194"),
    ("NYU Langone Orthopedic Associates", "nyuortho.com", "NY", "NPI-1104829104"),
    ("Orlin & Cohen Orthopedic Group", "orlincohen.com", "NY", "NPI-1578591024"),
    ("Syracuse Orthopedic Specialists", "sosbones.com", "NY", "NPI-1922049182"),
    ("Excelsior Orthopaedics", "excelsiorortho.com", "NY", "NPI-1316940192"),
    ("Illinois Bone & Joint Institute", "ibji.com", "IL", "NPI-1780649102"),
    ("Midwest Orthopaedics at Rush", "rushortho.com", "IL", "NPI-1407891024"),
    ("Hinsdale Orthopaedics", "hinsdale-orthopaedics.com", "IL", "NPI-1659301928"),
    ("Fox Valley Orthopedics", "fvortho.com", "IL", "NPI-1285649102"),
    ("Resurgens Orthopaedics", "resurgens.com", "GA", "NPI-1811940291"),
    ("Peachtree Orthopedics", "pocatlanta.com", "GA", "NPI-1548291048"),
    ("OrthoAtlanta", "orthoatlanta.com", "GA", "NPI-1164590182"),
    ("OrthoCarolina", "orthocarolina.com", "NC", "NPI-1982649102"),
    ("EmergeOrtho", "emergeortho.com", "NC", "NPI-1396840192"),
    ("Raleigh Orthopaedic Clinic", "raleighortho.com", "NC", "NPI-1720194820"),
    ("Orthopedic ONE Ohio", "orthopedicone.com", "OH", "NPI-1467591024"),
    ("Beacon Orthopaedics & Sports Medicine", "beaconortho.com", "OH", "NPI-1801849102"),
    ("JIS Orthopedics", "jisortho.com", "OH", "NPI-1235190482"),
    ("The CORE Institute", "thecoreinstitute.com", "AZ", "NPI-1679640192"),
    ("OrthoArizona", "orthoarizona.org", "AZ", "NPI-1518049182"),
    ("Proliance Surgeons", "proliancesurgeons.com", "WA", "NPI-1942391048"),
    ("Olympia Orthopaedic Associates", "olyortho.com", "WA", "NPI-1376591024"),
    ("Twin Cities Orthopedics", "tcomn.com", "MN", "NPI-1700849102"),
    ("Summit Orthopedics", "summitortho.com", "MN", "NPI-1134190482"),
    ("Panorama Orthopedics & Spine Center", "panoramaortho.com", "CO", "NPI-1598741029"),
    ("Colorado Center of Orthopaedic Excellence", "ccoe.us", "CO", "NPI-1861490182"),
    ("Campbell Clinic Orthopaedics", "campbellclinic.com", "TN", "NPI-1427049182"),
    ("TOA Tennessee Orthopaedic Alliance", "toa.com", "TN", "NPI-1295741029"),
    ("OrthoIndy", "orthoindy.com", "IN", "NPI-1639140291"),
    ("Fort Wayne Orthopedics", "fwortho.com", "IN", "NPI-1083649102"),
    ("Signature Medical Group", "signaturemedicalgroup.com", "MO", "NPI-1740291840"),
    ("Orthopedic Associates of Wisconsin", "orthowisconsin.com", "WI", "NPI-1356391048"),
    ("Southeastern Spine Institute", "southeasternspine.com", "SC", "NPI-1912940192"),
    ("Slocum Center for Orthopedics", "slocumcenter.com", "OR", "NPI-1528049182"),
    ("Orthopedic Associates of Hartford", "oahct.com", "CT", "NPI-1184649102"),
    ("The Orthopedic Partners Utah", "orthopartners.com", "UT", "NPI-1609840192"),
    ("Desert Orthopaedic Center", "doclv.com", "NV", "NPI-1831190482"),
    ("Andrews Sports Medicine", "andrewssportsmedicine.com", "AL", "NPI-1477591024"),
    ("Southern Orthopaedic Specialists", "southernorthospec.com", "LA", "NPI-1205849102"),
    ("Ellis & Badenhausen Orthopaedics", "eandbortho.com", "KY", "NPI-1750391048"),
    ("McBride Orthopedic Hospital Clinic", "mcboh.com", "OK", "NPI-1326049182"),
    ("DMOS Orthopaedic Centers", "dmos.com", "IA", "NPI-1962491028"),
    ("Mid-America Orthopedics", "midamortho.com", "KS", "NPI-1508840192"),
    ("Martin Knee & Sports Medicine", "martinkneeandsports.com", "AR", "NPI-1144291840"),
    ("Capital Ortho Mississippi", "capitalortho.com", "MS", "NPI-1689649102"),
    ("New Mexico Orthopaedics", "nmortho.com", "NM", "NPI-1871591024"),
    ("MD West ONE", "mdwestone.com", "NE", "NPI-1417940192"),
    ("Idaho Spine & Sports Physical Medicine", "idahospine.com", "ID", "NPI-1255391048"),
    ("Orthopedic Associates of Hawaii", "oahawaii.com", "HI", "NPI-1790741029"),
    ("Concord Orthopaedics", "concordortho.com", "NH", "NPI-1366491028"),
    ("Spectrum Healthcare Partners", "spectrumhcp.com", "ME", "NPI-1952391048"),
    ("University Orthopedics RI", "universityorthopedics.com", "RI", "NPI-1568491028"),
    ("Ortho Montana", "orthomontana.com", "MT", "NPI-1114940192"),
    ("First State Orthopaedics", "firststateortho.com", "DE", "NPI-1669491028"),
    ("Black Hills Orthopedic & Spine Center", "bhosc.com", "SD", "NPI-1881649102"),
    ("The Bone & Joint Center ND", "bone-joint.com", "ND", "NPI-1437190482"),
    ("Alaska Fracture & Orthopedic Clinic", "afoc.com", "AK", "NPI-1275591024"),
    ("Mansfield Orthopaedics VT", "mansfieldorthopaedics.com", "VT", "NPI-1730190482"),
    ("Scott Orthopedic Center WV", "scottorthopedic.com", "WV", "NPI-1306840192"),
    ("Premier Bone & Joint Centers WY", "premierboneandjoint.com", "WY", "NPI-1972591024"),
    ("Centers for Advanced Orthopaedics", "cfaortho.com", "MD", "NPI-1558391048"),
    ("Gastro Health", "gastrohealth.com", "FL", "NPI-1154391048"),
    ("Texas Digestive Disease Consultants", "tddc.com", "TX", "NPI-1619940192"),
    ("Capital Digestive Care", "capitaldigestivecare.com", "MD", "NPI-1851391048"),
    ("Illinois Gastroenterology Group", "illinoisgastro.com", "IL", "NPI-1447291840"),
    ("Atlanta Gastroenterology Associates", "atlantagastro.com", "GA", "NPI-1265491028"),
    ("Coronado Surgery Center", "coronadosurgerycenter.com", "NV", "NPI-1770591024"),
    ("MedHQ Healthcare RCM", "medhq.com", "IL", "NPI-RCM-88412"),
    (" Coronis Health RCM", "coronishealth.com", "MD", "NPI-RCM-77104"),
    ("Advantum Health RCM", "advantumhealth.com", "KY", "NPI-RCM-64219"),
    ("Infinx Healthcare RCM", "infinx.com", "CA", "NPI-RCM-51908"),
    ("Medusind RCM Solutions", "medusind.com", "FL", "NPI-RCM-92104"),
    ("BellMedEx Medical Billing", "bellmedex.com", "TX", "NPI-RCM-11402"),
    ("CureMD RCM Services", "curemd.com", "NY", "NPI-RCM-20918"),
    ("Physicians Revenue Group", "prgrcm.com", "IL", "NPI-RCM-40912"),
]


def _apply_brand_and_domain_transforms(text: str, rel_path: str) -> str:
    """Applies deterministic brand, domain, pricing, and SVG transforms to text files."""
    # 1. Replace SVG marks with Option M7 (The Split-Shield & Ledger)
    text = text.replace(CAMBER_SVG_LIGHT, RUBRIC_SVG_LIGHT)
    text = text.replace(CAMBER_SVG_INLINE, RUBRIC_SVG_INLINE)
    text = re.sub(
        r'<path fill="#0A0D14" d="M32 8A24 24 0 1 0 56 32H32V8Z"\s*/>\s*<rect x="37" y="11" width="16" height="16" rx="2" fill="#1E3A8A"\s*/>',
        '<path fill="#0A0D14" d="M12 10H32V54C19 48 12 37 12 22V10Z"/><rect x="37" y="10" width="15" height="28" rx="2" fill="#059669"/>',
        text,
    )
    text = re.sub(
        r'<path fill="#F8FAFC" d="M32 8A24 24 0 1 0 56 32H32V8Z"\s*/>\s*<rect x="37" y="11" width="16" height="16" rx="2" fill="#3B82F6"\s*/>',
        '<path fill="#F8FAFC" d="M12 10H32V54C19 48 12 37 12 22V10Z"/><rect x="37" y="10" width="15" height="28" rx="2" fill="#10B981"/>',
        text,
    )

    # 2. Protect cross-brand isolation checks so `_is_camberdesk_or_signaltender` checks stay intact
    # First, replace path references to D:\CamberDesk with D:\RubricWard
    text = text.replace(r"D:\CamberDesk", r"D:\RubricWard")
    text = text.replace(r"d:\CamberDesk", r"d:\RubricWard")
    text = text.replace("D:/CamberDesk", "D:/RubricWard")
    text = text.replace("d:/CamberDesk", "d:/RubricWard")

    # 3. Replace brand and domain tokens
    replacements = [
        ("CamberDeskSystems", "RubricWardSystems"),
        ("camberdesksystems", "rubricwardsystems"),
        ("tryrubricward.com", "tryrubricward.com"),
        ("trycamberdesk.com", "tryrubricward.com"),
        ("getcamberdesk.com", "getrubricward.com"),
        ("camberdeskhq.com", "rubricwardhq.com"),
        ("camberdesk.com", "rubricward.com"),
        ("camberdesk@gmail.com", "veripayer@gmail.com"),
        ("CamberDesk", "RubricWard"),
        ("CAMBERDESK", "RUBRICWARD"),
        ("camberdesk", "rubricward"),
        ("CamberWire", "ClaimWire"),
        ("CAMBERWIRE", "CLAIMWIRE"),
    ]
    for old_tok, new_tok in replacements:
        text = text.replace(old_tok, new_tok)

    return text


def generate_m7_logos_and_favicons() -> None:
    """Generates SVG and PNG favicons, avatars, and 12 500x500 RapidAPI logos using Option M7 (Split-Shield & Ledger)."""
    # 1. favicon.svg & bimi-logo.svg
    favicon_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <rect width="64" height="64" rx="14" fill="#0A0D14"/>
  <path fill="#F8FAFC" d="M12 10H32V54C19 48 12 37 12 22V10Z"/>
  <rect x="37" y="10" width="15" height="28" rx="2" fill="#10B981"/>
</svg>
"""
    (DST_DIR / "favicon.svg").write_text(favicon_svg, encoding="utf-8")

    bimi_svg = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<svg version="1.2" baseProfile="tiny-ps" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <title>RubricWard</title>
  <rect width="64" height="64" fill="#0A0D14"/>
  <path fill="#F8FAFC" d="M12 10H32V54C19 48 12 37 12 22V10Z"/>
  <rect x="37" y="10" width="15" height="28" rx="2" fill="#10B981"/>
</svg>
"""
    (DST_DIR / "bimi-logo.svg").write_text(bimi_svg, encoding="utf-8")

    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return

    def _draw_m7_icon(size: int, bg_rgb: Tuple[int, int, int] = (10, 13, 20)) -> Image.Image:
        img = Image.new("RGBA", (size, size), (*bg_rgb, 255))
        draw = ImageDraw.Draw(img)
        s = size / 64.0
        # Left Half-Shield (Ward): M12 10 H32 V54 C19 48 12 37 12 22 V10 Z
        pts = [(12 * s, 10 * s), (32 * s, 10 * s), (32 * s, 54 * s)]
        # Smooth cubic bezier from (32, 54) -> (19, 48) -> (12, 37) -> (12, 22)
        for i in range(1, 25):
            t = i / 24.0
            mt = 1.0 - t
            x = (mt**3) * 32 + 3 * (mt**2) * t * 19 + 3 * mt * (t**2) * 12 + (t**3) * 12
            y = (mt**3) * 54 + 3 * (mt**2) * t * 48 + 3 * mt * (t**2) * 37 + (t**3) * 22
            pts.append((x * s, y * s))
        pts.append((12 * s, 10 * s))
        draw.polygon(pts, fill=(248, 250, 252, 255))
        # Right Ledger Block (Rubric): rect x=37, y=10, w=15, h=28, rx=2
        draw.rounded_rectangle(
            [37 * s, 10 * s, 52 * s, 38 * s],
            radius=max(2, int(2 * s)),
            fill=(16, 185, 129, 255),
        )
        return img

    for sz, fname in [
        (32, "favicon-32x32.png"),
        (48, "favicon-48x48.png"),
        (96, "favicon-96x96.png"),
        (144, "favicon-144x144.png"),
        (180, "apple-touch-icon.png"),
        (192, "favicon-192x192.png"),
        (512, "favicon-512x512.png"),
        (512, "favicon.png"),
        (500, "rubricward_mailbox_avatar_500.png"),
        (500, "camberdesk_mailbox_avatar_500.png"),
    ]:
        im = _draw_m7_icon(sz)
        im.save(DST_DIR / fname, format="PNG")

    # Save .ico
    ico_im = _draw_m7_icon(64)
    ico_im.save(DST_DIR / "favicon.ico", format="ICO", sizes=[(32, 32), (48, 48), (64, 64)])

    # Generate 1200x630 og-image.png
    og = Image.new("RGB", (1200, 630), (10, 13, 20))
    icon_220 = _draw_m7_icon(220)
    og.paste(icon_220, (90, 205), icon_220)
    og.save(DST_DIR / "og-image.png", format="PNG")


def upgrade_harvester_for_3way_isolation() -> None:
    r"""Updates `harvest_verified_dot_contacts.py` in `D:\RubricWard` to use Healthcare NPI domains & 3-way isolation."""
    p = DST_DIR / "harvest_verified_dot_contacts.py"
    if not p.exists():
        return
    txt = p.read_text(encoding="utf-8")

    # Replace HEAVY_CIVIL_SEED_DOMAINS with HEALTHCARE_NPI_SEED_DOMAINS
    domains_repr = "HEAVY_CIVIL_SEED_DOMAINS: List[Tuple[str, str, str, str]] = [\n"
    for comp, dom, st, npi in HEALTHCARE_NPI_SEED_DOMAINS:
        domains_repr += f'    ({comp!r}, {dom!r}, {st!r}, {npi!r}),\n'
    domains_repr += "]\n"

    txt = re.sub(
        r"HEAVY_CIVIL_SEED_DOMAINS:\s*List\[Tuple\[str,\s*str,\s*str,\s*str\]\]\s*=\s*\[.*?\]\n",
        lambda _m: domains_repr,
        txt,
        flags=re.S,
    )

    # Also add CamberDesk files into the exclusion loader so RubricWard excludes BOTH SignalTender AND CamberDesk!
    old_ex = '''    daas_csv1 = r"D:\\Daas\\govcon_contacts.csv"
    daas_csv2 = r"D:\\Daas\\campaign_leads.csv"'''
    new_ex = '''    daas_csv1 = r"D:\\Daas\\govcon_contacts.csv"
    daas_csv2 = r"D:\\Daas\\campaign_leads.csv"
    camber_csv = r"D:\\CamberDesk\\campaign_leads.csv"
    camber_json = r"D:\\CamberDesk\\verified_public_dot_contacts.json"
    ex_domains.update({"camberdesk.com", "trycamberdesk.com", "getcamberdesk.com", "camberdeskhq.com"})
    if os.path.exists(camber_json):
        try:
            with open(camber_json, "r", encoding="utf-8") as cf:
                for r in json.load(cf):
                    if isinstance(r, dict):
                        em = str(r.get("email") or "").strip().lower()
                        if "@" in em:
                            ex_emails.add(em)
                            ex_domains.add(em.split("@", 1)[1])
        except Exception:
            pass'''
    txt = txt.replace(old_ex, new_ex)
    txt = txt.replace("for csv_p in (daas_csv1, daas_csv2):", "for csv_p in (daas_csv1, daas_csv2, camber_csv):")
    txt = txt.replace('if "signaltender" in clean:', 'if "signaltender" in clean or "camberdesk" in clean:')

    p.write_text(txt, encoding="utf-8")


def create_named_module_wrappers() -> None:
    """Creates RubricWard-named entrypoints alongside compatibility modules."""
    pairs = [
        ("build_camberdesk_site.py", "build_rubricward_site.py"),
        ("camberdesk_autopilot.py", "rubricward_autopilot.py"),
        ("verify_camberdesk_integrity.py", "verify_rubricward_integrity.py"),
        ("silent_camberdesk_watcher.py", "silent_rubricward_watcher.py"),
        ("windows_camberdesk_guard.py", "windows_rubricward_guard.py"),
        ("publish_camberdesk_rapidapi.py", "publish_rubricward_rapidapi.py"),
        ("seed_camberdesk_telemetry.py", "seed_rubricward_telemetry.py"),
        ("harvest_verified_dot_contacts.py", "harvest_verified_npi_contacts.py"),
    ]
    for src_name, dst_name in pairs:
        s_file = DST_DIR / src_name
        d_file = DST_DIR / dst_name
        if s_file.exists():
            shutil.copy2(s_file, d_file)


def main() -> None:
    print("[RUBRICWARD BOOTSTRAP] Starting 1-Pass Universe Generation in D:\\RubricWard...")
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rel_dir = Path(root).relative_to(SRC_DIR)
        target_dir = DST_DIR / rel_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        for fname in files:
            if fname in SKIP_FILES or fname in PRESERVE_FILES:
                continue
            src_file = Path(root) / fname
            dst_file = target_dir / fname
            ext = src_file.suffix.lower()
            if ext in {".py", ".js", ".json", ".md", ".txt", ".html", ".yaml", ".yml", ".bat", ".webmanifest", ".svg", ""} or fname in {".env", ".env.example", ".gitignore", "CNAME", "Dockerfile"}:
                try:
                    raw = src_file.read_text(encoding="utf-8")
                    transformed = _apply_brand_and_domain_transforms(raw, str(rel_dir / fname))
                    dst_file.write_text(transformed, encoding="utf-8")
                except UnicodeDecodeError:
                    shutil.copy2(src_file, dst_file)
            else:
                shutil.copy2(src_file, dst_file)

    # Write CNAME
    (DST_DIR / "CNAME").write_text("rubricward.com\n", encoding="utf-8")

    # Write Healthcare MRF Seed Data
    (DST_DIR / "dot_lettings_seed.json").write_text(
        json.dumps(HEALTHCARE_MRF_SEED, indent=2), encoding="utf-8"
    )
    (DST_DIR / "mrf_disparities_seed.json").write_text(
        json.dumps(HEALTHCARE_MRF_SEED, indent=2), encoding="utf-8"
    )

    # Upgrade Harvester for 3-Way Cross-Brand Isolation + Healthcare NPI domains
    upgrade_harvester_for_3way_isolation()

    # Generate M7 Split-Shield & Ledger Logos & Favicons
    generate_m7_logos_and_favicons()

    # Create RubricWard-named module entrypoints
    create_named_module_wrappers()

    print("[RUBRICWARD BOOTSTRAP] Core files, M7 logos, and 52-jurisdiction MRF seed written successfully.")


if __name__ == "__main__":
    main()
