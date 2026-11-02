"""
RubricWard API Gateway — Strict Pydantic V2 Request & Response Schemas (`api_gateway/schemas/claim_schemas.py`).
Covers all 12 Commercial Payer TiC MRF, Medicare MPFS RVU/GPCI, ERISA 29 CFR 2560.503-1 Appeal,
and Federal No Surprises Act (NSA 45 CFR 149.510) IDR Arbitration Endpoints + 3 Claim-Autopilot Moats.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PayerMrfBenchmarkRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cpt_code: str = Field(default="29881", description="5-digit CPT or HCPCS procedure code")
    payer_name: str = Field(default="UnitedHealthcare Choice Plus", description="Commercial health insurer name")
    state_code: str = Field(default="TX", min_length=2, max_length=2, description="Two-letter state postal code")
    msa_or_zip: str = Field(default="Dallas-Fort Worth-Arlington, TX (75201)", description="Geographic MSA or 5-digit ZIP")
    place_of_service: str = Field(default="24 - Ambulatory Surgical Center (ASC)", description="CMS Place of Service (24 ASC, 11 Office, 21 Inpatient, 22 Outpatient)")
    units: int = Field(default=1, ge=1, le=100, description="Billed service units")


class NsaIdrArbitrationRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    claim_id: str = Field(default="NSA-IDR-2026-TX-29881", description="Provider claim or IDR dispute reference ID")
    cpt_code: str = Field(default="29881", description="Disputed out-of-network CPT/HCPCS code")
    payer_name: str = Field(default="UnitedHealthcare", description="Commercial insurer or self-funded ERISA TPA")
    state_code: str = Field(default="TX", min_length=2, max_length=2, description="Two-letter state where service was rendered")
    payer_qpa_usd: float = Field(default=1420.00, ge=0.0, description="Payer disclosed Qualifying Payment Amount (QPA) in USD")
    provider_final_offer_usd: float = Field(default=3840.00, ge=0.0, description="Provider proposed IDR Final Offer in USD")
    provider_npi: str = Field(default="1093779706", description="10-digit billing/rendering provider NPI")
    patient_acuity_notes: str = Field(
        default="Complex bilateral arthroscopic meniscectomy with synovectomy in high-BMI patient requiring 45% extended operative duration.",
        description="Clinical complexity, comorbidity, and acuity justification under 45 CFR 149.510(c)(4)(iii)",
    )


class ErisaMedicalNecessityRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    claim_id: str = Field(default="ERISA-2026-L34979-64483", description="Denied claim reference number")
    denied_cpt_code: str = Field(default="64483", description="Denied CPT/HCPCS code")
    icd10_codes: List[str] = Field(default_factory=lambda: ["M54.16", "M51.16"], description="Primary and secondary ICD-10-CM diagnosis codes")
    carc_denial_code: str = Field(default="CO-50", description="HIPAA X12 835 CARC/RARC denial reason code")
    payer_policy_id: str = Field(default="CMS LCD L34979 / UHC CPB 0722", description="Cited payer Clinical Policy Bulletin or Medicare LCD/NCD")
    clinical_chart_excerpt: str = Field(
        default="Patient completed 8 weeks of supervised physical therapy and NSAID regimen without relief; lumbar MRI confirms L4-L5 foraminal stenosis with concordant radiculopathy.",
        description="De-identified clinical progress note and diagnostic imaging summary",
    )


class Era835LineItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cpt_code: str = Field(default="29881")
    modifier: Optional[str] = Field(default=None)
    billed_usd: float = Field(default=6200.00)
    contracted_or_mrf_median_usd: float = Field(default=3480.00)
    paid_usd: float = Field(default=1620.00)
    carc_code: str = Field(default="CO-45")


class Era835AuditRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    practice_name: str = Field(default="Texas Orthopedic Associates & ASC")
    payer_name: str = Field(default="BlueCross BlueShield")
    state_code: str = Field(default="TX")
    remittance_lines: List[Era835LineItem] = Field(default_factory=list)


class NcciClaimPair(BaseModel):
    model_config = ConfigDict(extra="ignore")
    column1_cpt: str = Field(default="29881", description="Primary procedure CPT code")
    column2_cpt: str = Field(default="29877", description="Secondary procedure CPT code")
    modifier_appended: str = Field(default="59", description="Modifier appended (25, 59, XE, XS, XP, XU)")
    distinct_compartment_documented: bool = Field(default=True, description="Whether operative note documents separate anatomical compartment/session")


class NcciModifierAuditRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    claim_id: str = Field(default="NCCI-2026-ASC-0091")
    place_of_service: str = Field(default="24 - ASC")
    code_pairs: List[NcciClaimPair] = Field(default_factory=list)


class RvuGpciLineRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cpt_code: str = Field(default="63030")
    work_rvu: float = Field(default=13.18)
    pe_rvu: float = Field(default=11.42)
    mp_rvu: float = Field(default=2.85)
    units: int = Field(default=1)


class RvuGpciScheduleRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    state_code: str = Field(default="TX")
    mac_locality: str = Field(default="04412-18 Dallas/Houston TX")
    facility_setting: str = Field(default="Non-Facility / ASC")
    work_gpci: float = Field(default=1.018)
    pe_gpci: float = Field(default=1.012)
    mp_gpci: float = Field(default=1.145)
    commercial_target_pct_of_medicare: float = Field(default=185.0)
    procedures: List[RvuGpciLineRequest] = Field(default_factory=list)


class PromptPayDemandRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    claim_id: str = Field(default="PP-2026-TX-1301")
    state_code: str = Field(default="TX")
    payer_name: str = Field(default="Aetna Commercial PPO")
    plan_funding_type: str = Field(default="Fully Insured Commercial Plan")
    unpaid_clean_claim_principal_usd: float = Field(default=14850.00)
    days_since_clean_claim_submission: int = Field(default=68, ge=1)


class PriorAuthPacketRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    procedure_cpt: str = Field(default="22612", description="Target CPT code requiring Prior Authorization")
    diagnosis_icd10: str = Field(default="M43.16", description="Primary ICD-10 diagnosis code")
    payer_name: str = Field(default="Cigna Healthcare")
    conservative_therapy_weeks: int = Field(default=8)
    imaging_summary: str = Field(default="Flexion-extension radiographs and lumbar MRI demonstrating Grade II spondylolisthesis at L4-L5 with dynamic instability.")


class OigUpcodingAuditRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    provider_npi: str = Field(default="1093779706")
    specialty: str = Field(default="Orthopedic Surgery / Pain Management")
    em_level_distribution: Dict[str, float] = Field(
        default_factory=lambda: {"99212": 0.05, "99213": 0.34, "99214": 0.46, "99215": 0.15}
    )
    modifier_25_attach_rate_pct: float = Field(default=28.4)


class PayerRenegotiationRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    practice_name: str = Field(default="Lone Star Orthopedic & Spine Center")
    provider_npi: str = Field(default="1093779706")
    state_code: str = Field(default="TX")
    payer_name: str = Field(default="UnitedHealthcare")
    top_cpt_code: str = Field(default="29881")
    annual_cpt_volume: int = Field(default=420, ge=1)
    current_contracted_rate_usd: float = Field(default=1840.00, ge=0.0)
    peer_75th_percentile_mrf_rate_usd: float = Field(default=3190.00, ge=0.0)


class GoodFaithEstimateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    patient_status: str = Field(default="Uninsured / Self-Pay (45 CFR 149.610)")
    primary_cpt_code: str = Field(default="29881")
    primary_diagnosis_icd10: str = Field(default="M23.211")
    surgeon_fee_usd: float = Field(default=2150.00)
    facility_asc_fee_usd: float = Field(default=3450.00)
    anesthesia_fee_usd: float = Field(default=780.00)


class CompileAppealPackageRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: Optional[str] = Field(default="TXDOI-MRF-CPT-29881-DFW", description="Case/Cohort ID or Claim ID")
    claim_id: Optional[str] = Field(default=None, description="Optional alias for project_id")
    project_title: Optional[str] = Field(
        default="Commercial Payer TiC MRF Rate-Disparity, ERISA 29 CFR 2560.503-1 Appeal & Federal NSA IDR Dossier",
        description="Cohort or case title",
    )
    state_code: str = Field(default="TX", description="Two-letter state code or US / MU")
    provider_name: str = Field(default="Multi-Specialty Surgical Group & ASC LLC", description="Billing provider organization name")
    provider_npi: str = Field(default="1093779706", description="10-digit billing NPI")
    payer_name: str = Field(default="UnitedHealthcare Choice Plus", description="Target commercial payer")


class IdrRcmClearinghouseRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    state_code: str = Field(default="TX")
    specialty_focus: str = Field(default="Orthopedic / Spine ASC & Out-of-Network Emergency Medicine")
    disputed_ar_backlog_usd: float = Field(default=485000.00)
    target_dispute_types: List[str] = Field(
        default_factory=lambda: [
            "Federal NSA 45 CFR 149.510 IDR Arbitration",
            "ERISA 29 CFR 2560.503-1 Level-1/Level-2 Appeals",
            "Commercial Payer TiC MRF Contract Renegotiation",
        ]
    )
