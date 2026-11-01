"""
RubricWard API Gateway — Strict Pydantic V2 Request & Response Schemas
for all 12 Commercial Payer TiC MRF, Medicare RVU/GPCI, ERISA Appeal & NSA IDR Microservices
+ 6-File OpenXML .ZIP Claim/IDR Package Compiler.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    status: str = Field(default="healthy", description="Service health status.")
    service: str = Field(default="rubricward-api-gateway", description="Microservice identifier.")
    version: str = Field(default="1.0.0", description="API Gateway semantic version.")
    model: str = Field(default="claude-sonnet-5-5", description="Active frontier LLM model.")
    portals_monitored: int = Field(default=52, description="Active State DOI/APCD MRF, CMS Federal IDR & Commercial Payer portals.")
    endpoints_live: int = Field(default=12, description="Total live commercial payer MRF, ERISA appeal & NSA IDR endpoints.")


# API #01: Commercial Payer Clinical Policy Bulletin (CPB), LCD/NCD & Prior-Auth Shredder
class CsiSpecShredRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    spec_text: str = Field(
        default="COMMERCIAL PAYER CLINICAL POLICY BULLETIN (CPB-0742): Lumbar Laminotomy (CPT 63030) and Arthroscopic Meniscectomy (CPT 29881) require 6 weeks of documented supervised physical therapy, NSAID trial, and MRI confirming nerve root compression. Timely filing window is 90 calendar days; ERISA internal appeal deadline is 180 calendar days under 29 CFR 2560.503-1.",
        min_length=10,
        max_length=50000,
        description="Raw text from Commercial Payer Clinical Policy Bulletin (CPB), Medicare LCD/NCD, or Adverse Benefit Determination letter.",
    )
    project_id: str = Field(
        default="TXDOI-MRF-CPT-29881-DFW",
        min_length=2,
        max_length=120,
        description="Claim Cohort ID, Payer Policy Number, or NSA IDR Case Reference.",
    )
    target_trade: str = Field(
        default="Orthopedic Surgery & Ambulatory Surgery Center (ASC)",
        min_length=2,
        max_length=120,
        description="Clinical specialty focus (e.g., 'Orthopedic Surgery & ASC', 'Neurosurgery / Spine', 'Gastroenterology', 'Emergency Medicine').",
    )


# API #02: 50-State Commercial Payer TiC MRF Allowed-Amount & QPA Percent-of-Medicare Modeler
class DotBidTabRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    state_code: str = Field(
        default="TX",
        min_length=2,
        max_length=10,
        description="Two-letter U.S. state postal code (e.g., 'TX', 'CA', 'FL', 'VA', 'PA', 'NY') or 'US' for Federal IDR.",
    )
    pay_item_description: str = Field(
        default="CPT 29881 — Arthroscopy, Knee, Surgical; with Meniscectomy (Medial OR Lateral) — ASC Facility & Professional",
        min_length=3,
        max_length=300,
        description="CPT, HCPCS, APC, or MS-DRG procedure code and clinical description.",
    )
    unit: str = Field(
        default="CLAIM",
        min_length=1,
        max_length=20,
        description="Billing unit of measure ('CLAIM', 'CASE', 'UNIT', 'RVU', 'DRG').",
    )
    quantity: float = Field(
        default=420.0,
        ge=1.0,
        le=100000000.0,
        description="Annual or disputed cohort claim volume for this CPT/DRG procedure.",
    )


# API #03: CMS Medicare Physician Fee Schedule (MPFS) RVU, GPCI Locality & ASC Payment Calculator
class PrevailingWageRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    state_code: str = Field(default="TX", min_length=2, max_length=10, description="Two-letter U.S. state code.")
    county: str = Field(default="Dallas / Tarrant County (DFW Locality)", min_length=2, max_length=120, description="CMS Medicare GPCI locality or county name.")
    construction_type: str = Field(
        default="ASC / Outpatient Facility",
        min_length=3,
        max_length=40,
        description="Place of Service setting: 'ASC / Outpatient Facility', 'HOPD (POS 22)', 'Inpatient (POS 21)', or 'Office Non-Facility (POS 11)'.",
    )
    crew_classifications: List[str] = Field(
        default=[
            "CPT 29881 — Knee Arthroscopy & Meniscectomy (Work RVU 7.03)",
            "CPT 27447 — Total Knee Arthroplasty (Work RVU 20.72)",
            "CPT 63030 — Lumbar Hemilaminectomy / Microdiscectomy (Work RVU 13.18)",
            "CPT 45380 — Diagnostic Colonoscopy with Biopsy (Work RVU 3.56)",
            "CPT 99285 — Level-5 Emergency Department Visit (Work RVU 4.00)",
        ],
        description="CPT/HCPCS procedure codes to price under CMS MPFS RVU, GPCI locality indices, and Commercial % of Medicare.",
    )
    estimated_crew_hours: int = Field(
        default=1250,
        ge=1,
        le=5000000,
        description="Total annual claim encounters across the specialty cohort.",
    )


# API #05: CMS NCCI Procedure-to-Procedure (PTP) Unbundling, MUE & Modifier 25/59 Claim Scrubber
class BabaComplianceRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="TXDOI-MRF-CPT-29881-DFW", min_length=2, max_length=120, description="Claim Cohort or Encounter ID.")
    bom_items: List[str] = Field(
        default=[
            "CPT 29881 — Arthroscopic Medial Meniscectomy ($1,985 Allowed — Primary Procedure Column 1)",
            "CPT 29877 — Arthroscopic Debridement/Chondroplasty ($840 Billed — Bundled into 29881 unless separate compartment with Modifier -59/-XS)",
            "CPT 99214-25 — E/M Established Patient Visit Same-Day ($185 Allowed — Distinct preoperative decision for surgery)",
            "HCPCS J7325 — Hyaluronan Intra-Articular Visco-Supplementation ($620 — Verify MUE Bilateral Unit Limit & Prior-Auth)",
        ],
        description="Claim line items (CPT/HCPCS + modifiers) to scrub against CMS NCCI PTP edits and Medically Unlikely Edits (MUEs).",
    )
    funding_agency: str = Field(default="CMS NCCI / Commercial Payer Claims Editing Engine", min_length=2, max_length=140, description="Governing coding edit standard or commercial payer.")


# API #06: Federal No Surprises Act (NSA 45 CFR 149.510) Open Negotiation & IDR Position Brief Generator
class DbeGoodFaithRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="CMS-NSA-IDR-CPT-63047-NAT", min_length=2, max_length=120, description="NSA IDR Dispute Case ID.")
    total_bid_amount_usd: float = Field(default=1420000.0, ge=100.0, le=5000000000.0, description="Total target 75th-percentile commercial MRF arbitration offer across disputed claim cohort (USD).")
    dbe_goal_pct: float = Field(default=215.0, ge=0.0, le=500.0, description="Target commercial reimbursement as a percentage of CMS Medicare fee schedule (e.g., 215.0%).")
    proposed_dbe_commitments: List[Dict[str, Any]] = Field(
        default=[
            {"sub_name": "Texas Orthopedic & Spine Surgical Associates PLLC", "role": "Out-of-Network Surgical Group (IDR Initiating Party)", "scope": "CPT 29881 / 63030 Emergent & Facility-Based Surgical Claims", "quote_usd": 895000.0},
            {"sub_name": "Lone Star Ambulatory Surgery Center LLC", "role": "Out-of-Network Facility / ASC Co-Claimant", "scope": "ASC Facility Fee Cohort & Implant Pass-Through Recovery", "quote_usd": 525000.0},
        ],
        description="Disputed provider/facility claim cohorts and target NSA IDR arbitration offers under 45 CFR 149.510.",
    )


# API #07: HIPAA X12 835 Electronic Remittance Advice (ERA) CARC/RARC Underpayment & Zero-Pay Auditor
class AiaPayAppRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="TXDOI-MRF-CPT-29881-DFW", min_length=2, max_length=120, description="Remittance Audit Batch ID.")
    contractor_name: str = Field(default="Texas Orthopedic & Spine Surgical Associates PLLC", min_length=2, max_length=180, description="Billing Provider Group or ASC legal name.")
    contract_sum_usd: float = Field(default=1840000.0, ge=100.0, le=5000000000.0, description="Total contracted expected allowed amount across the remittance batch (USD).")
    retainage_pct: float = Field(default=18.5, ge=0.0, le=90.0, description="Observed payer CARC-45/97 underpayment & wrongful denial hair-cut percentage.")
    application_number: int = Field(default=1, ge=1, le=240, description="ERA Remittance Audit Cycle Number.")


# API #08: 50-State Prompt-Pay Statute Interest Penalty & Clean-Claim Timely-Filing Calculator
class SuretyBondAuditRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    contractor_name: str = Field(default="Texas Orthopedic & Spine Surgical Associates PLLC", min_length=2, max_length=180, description="Provider Group or Hospital legal name.")
    current_assets_usd: float = Field(default=2450000.0, ge=0.0, description="Total clean claims aged > 45 calendar days past electronic 837 submission (USD).")
    current_liabilities_usd: float = Field(default=620000.0, ge=0.0, description="Partial payer interim remittances received to date (USD).")
    net_worth_equity_usd: float = Field(default=1830000.0, ge=0.0, description="Net overdue principal balance subject to statutory prompt-pay interest (USD).")
    uncompleted_wip_backlog_usd: float = Field(default=940000.0, ge=0.0, description="Claims pending ERISA Level-1/Level-2 medical necessity appeal (USD).")
    target_project_bid_usd: float = Field(default=1830000.0, ge=100.0, description="Target principal + statutory prompt-pay penalty demand amount (USD).")


# API #09: ERISA 29 CFR 2560.503-1 Level-1 & Level-2 Medical Necessity Appeal Drafter
class RfiChangeOrderRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="CADMHC-MRF-CPT-63030-SFO", min_length=2, max_length=120, description="Denied Claim or Cohort ID.")
    issue_summary: str = Field(
        default="Payer issued CARC 50 (Non-Covered / Not Medically Necessary) denial on CPT 63030 Lumbar Microdiscectomy despite MRI confirming L4-L5 extruded disc herniation with radiculopathy and 8 weeks of failed conservative physical therapy and epidural steroid injection.",
        min_length=10,
        max_length=10000,
        description="Clinical summary of the CARC/RARC denial and documented objective medical necessity evidence.",
    )
    direct_cost_impact_usd: float = Field(default=68500.0, ge=0.0, description="Disputed principal claim allowed amount under commercial MRF 75th percentile (USD).")
    critical_path_delay_days: int = Field(default=74, ge=0, le=1000, description="Calendar days elapsed since clean-claim submission for statutory interest calculation.")


# API #10: MS-DRG / APR-DRG Inpatient Clinical Validation & DRG Downcode Defense
class OshaEmrAuditRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="NYDFS-MRF-CPT-27447-NYC", min_length=2, max_length=120, description="Inpatient DRG Audit Batch ID.")
    high_hazard_activities: List[str] = Field(
        default=[
            "MS-DRG 871 Septicemia w/ MCC Downgraded to DRG 872 (Sepsis-3 SOFA Score >= 2 & Lactate 3.4 mmol/L Documented)",
            "Secondary MCC E43 Unspecified Severe Protein-Calorie Malnutrition (ASPEN Clinical Criteria Met)",
            "Secondary MCC J96.01 Acute Hypoxemic Respiratory Failure Requiring High-Flow Nasal Cannula (P/F Ratio < 250)",
        ],
        description="List of inpatient MS-DRG / APR-DRG clinical validation denials or CC/MCC downcodes to defend.",
    )
    contractor_emr_current: float = Field(default=0.94, ge=0.1, le=5.0, description="Hospital Case Mix Index (CMI) or clean-claim clinical validation pass ratio.")


# API #11: Regional Specialty Group Tax-ID (EIN/NPI) Payer Leverage & Revenue Left on Table (RLOT) Analyzer
class PlanholderSpreadRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="TXDOI-MRF-CPT-29881-DFW", min_length=2, max_length=120, description="Regional Market MRF Cohort ID.")
    engineers_estimate_usd: float = Field(default=2450000.0, ge=1000.0, description="Annual cohort commercial revenue at 75th-percentile regional MRF benchmark (USD).")
    planholders: List[str] = Field(
        default=[
            "Texas Orthopedic Associates (EIN Verified TiC MRF — 238% of Medicare)",
            "Baylor Scott & White Orthopedic Spine Group (EIN Verified TiC MRF — 265% of Medicare)",
            "UT Southwestern Clinical Faculty Group (EIN Verified TiC MRF — 274% of Medicare)",
            "OrthoLoneStar PLLC (EIN Verified TiC MRF — 224% of Medicare)",
            "DFW Sports Medicine & ASC Partners (EIN Verified TiC MRF — 198% of Medicare)",
        ],
        description="List of regional peer provider groups and health systems in the same MSA from CMS TiC MRF files.",
    )


# API #12: Managed Care Payer Contract Redline & Rate-Escalator Term Sheet Generator
class SubcontractorItbRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="TXDOI-MRF-CPT-29881-DFW", min_length=2, max_length=120, description="Managed Care Contract Negotiation ID.")
    trade_package: str = Field(default="Commercial PPO / HMO & Self-Funded ASO Fee Schedule Addendum (Orthopedic & ASC Carve-Out)", min_length=3, max_length=240, description="Target payer contract line of business and specialty schedule.")
    prime_contractor: str = Field(default="UnitedHealthcare / Optum Commercial Network", min_length=2, max_length=180, description="Counterparty Commercial Payer / Network.")
    bid_due_date: str = Field(default="2026-11-30", min_length=4, max_length=40, description="Contract renewal or termination notice deadline.")


# Master Moat #1: 6-File OpenXML Commercial Payer MRF, ERISA Appeal & NSA IDR .ZIP Compiler
class CompileBidPackageRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="TXDOI-MRF-CPT-29881-DFW", max_length=120, description="Target Claim Cohort ID, Payer MRF Case ID, or NSA IDR Dispute Reference.")
    project_title: str = Field(default="UHC / BlueCross TX Commercial MRF Underpayment & NSA IDR Cohort — CPT 29881 / 27447 Orthopedic & ASC", max_length=300, description="Claim cohort or payer dispute title.")
    agency: str = Field(default="Texas Department of Insurance (TDI Ch. 1301) & Commercial Payer TiC MRF", max_length=200, description="Governing State DOI, Federal NSA IDR, or Commercial Payer MRF portal.")
    state_code: str = Field(default="TX", max_length=10, description="Two-letter U.S. state code.")
    county: str = Field(default="Dallas / Tarrant / Travis MSA, TX", max_length=120, description="CMS Medicare GPCI locality / MSA.")
    contractor_name: str = Field(default="Apex Orthopedic & Spine Surgical Associates PLLC", max_length=180, description="Billing Provider Group, ASC, or Health System legal name.")
    license_or_dot_id: str = Field(default="NPI-1841290482 / EIN-75-2948102", max_length=100, description="Type-2 Organizational NPI and Federal Tax ID (EIN).")
    dbe_status: str = Field(default="Independent Physician Group & ASC (NSA IDR & ERISA 29 CFR 2560.503-1 Eligible)", max_length=140, description="Provider network/arbitration posture.")
    target_markup_pct: float = Field(default=215.0, ge=1.0, le=500.0, description="Target commercial reimbursement multiple (% of Medicare or target uplift %).")
    spec_text: str = Field(default="", max_length=50000, description="Optional raw EOB/835 CARC denial text or payer Clinical Policy Bulletin excerpt.")


# Master Moat #3: Two-Sided Provider Group / ASC Payer-Rate & NSA IDR Benchmark Network
class DbeClearinghouseRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    company_name: str = Field(default="Apex Orthopedic & Spine Surgical Associates PLLC", max_length=180, description="Provider Group, ASC, or RCM Billing Firm legal name.")
    estimating_email: str = Field(default="rcm@apexorthospine.com", max_length=254, description="VP of Revenue Cycle, Managed Care Director, or Practice Administrator email.")
    license_or_dot_id: str = Field(default="NPI-1841290482", max_length=100, description="Organizational Type-2 NPI or Tax ID prefix.")
    dbe_status: str = Field(default="Independent Specialty Group / ASC (Commercial MRF & NSA IDR Cohort)", max_length=120, description="Provider entity classification.")
    role_requested: str = Field(default="Provider Group Seeking Peer EIN/NPI Commercial MRF Benchmarks & IDR Arbitrator Win Rates", max_length=140, description="Clearinghouse benchmarking role.")
    trade_division: str = Field(default="Orthopedic Surgery, Neurosurgery/Spine & Ambulatory Surgery Center (CPT 20000-69999)", max_length=160, description="Clinical specialty and CPT/DRG series.")
    project_id: str = Field(default="TXDOI-MRF-CPT-29881-DFW", max_length=120, description="Target State DOI / Commercial Payer MRF Cohort ID.")
    state_code: str = Field(default="TX", max_length=10, description="Two-letter U.S. state code.")
    proposed_dbe_share_pct: float = Field(default=215.0, ge=1.0, le=500.0, description="Target commercial allowed-amount multiple (% of Medicare).")
