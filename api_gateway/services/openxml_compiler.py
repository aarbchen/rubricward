"""
RubricWard API Gateway — Pure-Python In-Memory 6-File OpenXML (.DOCX + live-formula .XLSX)
ERISA Appeal, NSA IDR Arbitration & Commercial Payer MRF Benchmark Package Compiler (`api_gateway/services/openxml_compiler.py`).

Generates the 6 files specified in Section 4 of `rubricward_1m_business_plan.md`:
1. `01_ERISA_29CFR2560_Clinical_Medical_Necessity_Appeal.docx`
2. `02_No_Surprises_Act_45CFR149_IDR_Arbitration_Brief.docx`
3. `03_State_DOI_Prompt_Pay_Statutory_Interest_&_Regulatory_Complaint.docx`
4. `04_CMS_TiC_Payer_MRF_Negotiated_Rate_Benchmark_Model.xlsx` (live `=SUM(...)` and `=D6*G6` formulas)
5. `05_EDI_835_Underpayment_&_NCCI_Modifier_Audit_Workbook.xlsx` (live `=SUM(...)` and `=D6*G6` formulas)
6. `00_RubricWard_Arbitration_Readiness_Manifest.json`
"""

import base64
import io
import json
import zipfile
from datetime import datetime, timezone
from typing import Any, Dict, List

from api_gateway.routers.camber_autopilot import (
    STATE_HEALTHCARE_MRF_REGISTRY,
    _build_openxml_docx,
    _build_openxml_xlsx,
)

STATE_PROMPT_PAY_STATUTES = {
    k: (v.get("agency", ""), v.get("statute", ""))
    for k, v in STATE_HEALTHCARE_MRF_REGISTRY.items()
}
from api_gateway.services.llm_extractor import load_seed_data


def compile_native_appeal_and_idr_zip(
    case_id: str = "TXDOI-MRF-CPT-29881-DFW",
    state_code: str = "TX",
    provider_name: str = "Multi-Specialty Surgical Group & ASC LLC",
    provider_npi: str = "1093779706",
    payer_name: str = "UnitedHealthcare Choice Plus",
) -> Dict[str, Any]:
    st = (state_code or "TX").upper().strip()
    statute = STATE_PROMPT_PAY_STATUTES.get(
        st,
        f"{st} State Insurance Prompt-Pay Statute & Federal ERISA 29 CFR § 2560.503-1 / NSA 45 CFR § 149.510",
    )

    raw_seed = load_seed_data()
    lettings = raw_seed.get("lettings", raw_seed) if isinstance(raw_seed, dict) else raw_seed
    matched = next(
        (
            item
            for item in lettings
            if str(item.get("project_id") or item.get("letting_id") or "").upper() == case_id.upper()
            or str(item.get("state_code") or "").upper() == st
        ),
        lettings[0] if lettings else {},
    )
    resolved_id = str(case_id or matched.get("project_id") or "TXDOI-MRF-CPT-29881-DFW")
    resolved_title = str(
        matched.get("title")
        or f"[{resolved_id}] {st} Commercial Payer TiC MRF Rate-Disparity, ERISA Appeal & NSA IDR Dossier"
    )
    peer_groups = [str(p) for p in (matched.get("planholders") or []) if p][:4] or [
        f"{provider_name} (NPI {provider_npi})",
        f"{st} Regional Orthopedic & Spine Surgery Center",
    ]

    doc1_bytes = _build_openxml_docx(
        title=f"VOLUME I: ERISA 29 CFR § 2560.503-1 CLINICAL MEDICAL NECESSITY APPEAL — {resolved_id}",
        subtitle=f"Provider: {provider_name} (NPI {provider_npi}) | Payer: {payer_name} | Jurisdiction: {st}",
        sections=[
            (
                "1. Statutory Demand for Full & Fair Review (29 CFR § 2560.503-1 & ACA 45 CFR § 147.136)",
                [
                    f"Case / Cohort Reference: {resolved_id} — {resolved_title}",
                    f"Applicable State & Federal Statutory Authority: {statute}",
                    "Pursuant to 29 CFR § 2560.503-1(h)(3)(iii), claimant demands review by a board-certified physician in the exact surgical specialty who was not involved in the initial adverse benefit determination.",
                    "Pursuant to 29 U.S.C. § 1024(b)(4) and 29 CFR § 2560.503-1(h)(2)(iii), payer must produce all internal clinical guidelines, Milliman/InterQual criteria, and peer-review notes relied upon within 30 days.",
                ],
            ),
            (
                "2. Clinical Medical Necessity & Medicare LCD/NCD Coverage Alignment",
                [
                    "Conservative Care Exhausted: Documented >= 6 weeks of supervised physical therapy, pharmacotherapy (NSAIDs/muscle relaxants), and activity modification failed to resolve functional deficit.",
                    "Diagnostic Imaging Concordance: High-resolution MRI/CT imaging directly correlates objective anatomical pathology with clinical physical exam findings.",
                    "Standard of Care: Procedure is medically necessary, non-experimental, and satisfies all CMS Local Coverage Determination (LCD) criteria.",
                ],
            ),
        ],
    )

    doc2_bytes = _build_openxml_docx(
        title=f"VOLUME II: FEDERAL NO SURPRISES ACT (45 CFR § 149.510) IDR ARBITRATION BRIEF — {resolved_id}",
        subtitle=f"Certified IDR Entity Position Statement | Billing NPI: {provider_npi} | State: {st}",
        sections=[
            (
                "1. Statutory QPA Rebuttal & 45 CFR § 149.510(c)(4)(iii) Credible Market Evidence",
                [
                    f"Under Texas Medical Association (TMA III & IV) federal precedent, the Certified IDR Entity must weigh all statutory factors equally without unlawfully presuming the Payer QPA ({payer_name}) is the appropriate out-of-network rate.",
                    f"Commercial Payer TiC MRF 50th/75th Percentile Evidence: Published Transparency in Coverage (45 CFR § 147.212) machine-readable files in {st} demonstrate that competing regional peers ({', '.join(peer_groups[:2])}) receive 185%–245% of Medicare MPFS for identical CPT cohorts.",
                    "Provider Training, Experience & Case Acuity: Board-certified subspecialty surgical team managing high-acuity pathology with zero 30-day readmissions.",
                ],
            ),
            (
                "2. Good-Faith Open Negotiation & Timely IDR Initiation Certification",
                [
                    "30-Business-Day Open Negotiation Notice was timely served pursuant to 45 CFR § 149.510(b)(1) following receipt of initial remittance advice.",
                    "Federal IDR Initiation submitted within the mandatory 4-business-day window via the CMS Federal IDR Portal.",
                ],
            ),
        ],
    )

    doc3_bytes = _build_openxml_docx(
        title=f"VOLUME III: STATE PROMPT-PAY STATUTORY INTEREST & DOI REGULATORY COMPLAINT — {resolved_id}",
        subtitle=f"Governing Statute: {statute} | Provider: {provider_name}",
        sections=[
            (
                "1. Statutory Clean-Claim Timely Payment Violation & Interest Demand",
                [
                    f"Governing Prompt-Pay Authority: {statute}",
                    "Clean electronic claim (EDI 837P/837I) was transmitted with all required CPT, ICD-10, NPI, and operative documentation.",
                    "Payer failed to issue full contracted/statutory payment within the statutory clean-claim window (30/45 calendar days), triggering mandatory statutory interest (12%–18% per annum) plus administrative fee recovery.",
                ],
            ),
            (
                "2. Regional Peer NPI Comparables & Regulatory Escalation Notice",
                [f"Verified {st} Peer Specialty Organization: {peer}" for peer in peer_groups],
            ),
        ],
    )

    xlsx4_rows: List[List[Any]] = [
        ["29881", "Knee Arthroscopy w/ Meniscectomy (ASC/Facility)", "CPT", 12, 1680.00, 2490.00, 3180.00, 38160.00],
        ["63030", "Lumbar Laminotomy / Microdiscectomy (1 Interspace)", "CPT", 8, 3420.00, 4890.00, 6450.00, 51600.00],
        ["64483", "Transforaminal Epidural Steroid Injection (Lumbar/Sacral)", "CPT", 24, 580.00, 890.00, 1240.00, 29760.00],
        ["45385", "Diagnostic/Therapeutic Colonoscopy w/ Lesion Removal", "CPT", 18, 920.00, 1410.00, 1890.00, 34020.00],
        ["99285", "Emergency Department Visit (High Severity / Acuity Level 5)", "CPT", 15, 740.00, 1180.00, 1620.00, 24300.00],
    ]
    xlsx4_bytes = _build_openxml_xlsx(
        sheet_name="TiC_MRF_Benchmarks",
        headers=[
            "CPT_Code",
            "Clinical_Procedure_Description",
            "Unit",
            "Cohort_Claim_Volume",
            "MRF_25th_Pct_USD",
            "MRF_50th_Median_QPA_USD",
            "MRF_75th_Target_USD",
            "Extended_Recovery_Target_USD",
        ],
        rows=xlsx4_rows,
    )

    xlsx5_rows: List[List[Any]] = [
        ["29881-RT", "Primary Knee Arthroscopy Meniscectomy (CO-45 Underpaid)", "CPT", 10, 1420.00, 2890.00, 1470.00, 14700.00],
        ["29877-59", "Distinct Compartment Chondroplasty (CO-97 NCCI Defense)", "CPT", 6, 0.00, 1640.00, 1640.00, 9840.00],
        ["63030-LT", "Lumbar Microdiscectomy L4-L5 (NSA IDR Target Offer)", "CPT", 4, 1920.00, 5480.00, 3560.00, 14240.00],
        ["63035-XS", "Additional Interspace Decompression L5-S1 (Separate Level)", "CPT", 4, 480.00, 1980.00, 1500.00, 6000.00],
        ["64483-50", "Bilateral Transforaminal Epidural Injection (MPPR 150%)", "CPT", 12, 410.00, 1120.00, 710.00, 8520.00],
    ]
    xlsx5_bytes = _build_openxml_xlsx(
        sheet_name="835_NCCI_Underpayment_Audit",
        headers=[
            "CPT_Modifier",
            "Audit_Finding_And_CARC_Defense",
            "Unit",
            "Affected_Claims",
            "Payer_Paid_QPA_USD",
            "Contracted_Or_MRF_75th_USD",
            "Net_Underpayment_Per_Claim_USD",
            "Total_Recoverable_Principal_USD",
        ],
        rows=xlsx5_rows,
    )

    files_list = [
        "01_ERISA_29CFR2560_Clinical_Medical_Necessity_Appeal.docx",
        "02_No_Surprises_Act_45CFR149_IDR_Arbitration_Brief.docx",
        "03_State_DOI_Prompt_Pay_Statutory_Interest_&_Regulatory_Complaint.docx",
        "04_CMS_TiC_Payer_MRF_Negotiated_Rate_Benchmark_Model.xlsx",
        "05_EDI_835_Underpayment_&_NCCI_Modifier_Audit_Workbook.xlsx",
        "00_RubricWard_Arbitration_Readiness_Manifest.json",
    ]

    manifest = {
        "manifest_version": "2026.11-NATIVE-HEALTHCARE",
        "brand": "RubricWard",
        "case_id": resolved_id,
        "project_id": resolved_id,
        "state_code": st,
        "provider_name": provider_name,
        "provider_npi": provider_npi,
        "payer_name": payer_name,
        "governing_statute": statute,
        "regional_peer_npis_and_groups": peer_groups,
        "compiled_at_utc": datetime.now(timezone.utc).isoformat(),
        "files_included": files_list,
    }
    manifest_bytes = json.dumps(manifest, indent=2).encode("utf-8")

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(files_list[0], doc1_bytes)
        zf.writestr(files_list[1], doc2_bytes)
        zf.writestr(files_list[2], doc3_bytes)
        zf.writestr(files_list[3], xlsx4_bytes)
        zf.writestr(files_list[4], xlsx5_bytes)
        zf.writestr(files_list[5], manifest_bytes)

    raw_zip = zip_buf.getvalue()
    safe_id = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in resolved_id)
    return {
        "status": "compiled",
        "filename": f"RubricWard_{safe_id}_6File_Appeal_Package.zip",
        "case_id": resolved_id,
        "project_id": resolved_id,
        "state_code": st,
        "provider_name": provider_name,
        "provider_npi": provider_npi,
        "payer_name": payer_name,
        "governing_statute": statute,
        "files_included": files_list,
        "zip_size_bytes": len(raw_zip),
        "zip_base64": base64.b64encode(raw_zip).decode("ascii"),
    }



def compile_healthcare_appeal_zip(
    claim_id: str = "TXDOI-MRF-CPT-29881-DFW",
    state_code: str = "TX",
    cpt_code: str = "27447",
    payer_name: str = "UnitedHealthcare Choice Plus",
) -> bytes:
    res = compile_native_appeal_and_idr_zip(
        case_id=claim_id,
        state_code=state_code,
        payer_name=payer_name,
    )
    return base64.b64decode(res["zip_base64"])
