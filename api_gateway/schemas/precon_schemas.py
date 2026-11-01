"""
RubricWard API Gateway — Strict Pydantic V2 Request & Response Schemas
for all 12 Construction / 50-State DOT Microservices + 6-File .ZIP Compiler.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    status: str = Field(default="healthy", description="Service health status.")
    service: str = Field(default="rubricward-api-gateway", description="Microservice identifier.")
    version: str = Field(default="1.0.0", description="API Gateway semantic version.")
    model: str = Field(default="claude-sonnet-5-5", description="Active frontier LLM model.")
    portals_monitored: int = Field(default=52, description="Active State DOT, USACE & Municipal portals.")
    endpoints_live: int = Field(default=12, description="Total live construction preconstruction endpoints.")


# API #01: CSI MasterFormat Divisions 00-48 Spec & Submittal Shredder
class CsiSpecShredRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    spec_text: str = Field(
        default="SECTION 01 10 00 SUMMARY: Contractor shall replace 4 prestressed bridge spans and place 68,000 tons of Item 341 Superpave HMA. Liquidated damages are $4,200 per calendar day. Submit mix design under Division 03 and shop drawings under Division 05 within 21 days of NTP.",
        min_length=10,
        max_length=50000,
        description="Raw text from Project Manual, Special Provisions, or CSI MasterFormat Divisions 00-48 specification.",
    )
    project_id: str = Field(
        default="TXDOT-CSJ-0015-13-412",
        min_length=2,
        max_length=120,
        description="DOT CSJ, Contract ID, or Project Number.",
    )
    target_trade: str = Field(
        default="Heavy Civil / Highway & Bridge",
        min_length=2,
        max_length=120,
        description="Primary trade focus (e.g., 'Heavy Civil / Highway & Bridge', 'Div 26 Electrical', 'Div 03 Concrete').",
    )


# API #02: 50-State DOT Historical Item Bid Tabulation & Spread Modeler
class DotBidTabRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    state_code: str = Field(
        default="TX",
        min_length=2,
        max_length=10,
        description="Two-letter U.S. state postal code (e.g., 'TX', 'CA', 'FL', 'VA', 'PA', 'NY') or 'US' for USACE.",
    )
    pay_item_description: str = Field(
        default="Dense-Graded Hot-Mix Asphalt (Superpave SP-C PG 76-22)",
        min_length=3,
        max_length=300,
        description="DOT Pay Item code and description (e.g., '341-6008 Superpave HMA', 'Class A Structural Concrete').",
    )
    unit: str = Field(
        default="TON",
        min_length=1,
        max_length=20,
        description="Pay item unit of measure ('TON', 'LF', 'CY', 'SY', 'LB', 'EA', 'LS').",
    )
    quantity: float = Field(
        default=68000.0,
        ge=1.0,
        le=100000000.0,
        description="Estimated project takeoff quantity for this pay item.",
    )


# API #03: Davis-Bacon & State Prevailing Wage Fringe Calculator
class PrevailingWageRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    state_code: str = Field(default="TX", min_length=2, max_length=10, description="Two-letter U.S. state code.")
    county: str = Field(default="Travis County", min_length=2, max_length=120, description="Project county name.")
    construction_type: str = Field(
        default="Highway",
        min_length=3,
        max_length=40,
        description="Davis-Bacon WDOL construction type: 'Highway', 'Heavy', 'Building', or 'Residential'.",
    )
    crew_classifications: List[str] = Field(
        default=["Operating Engineer (Paver / Crane)", "Cement Mason / Concrete Finisher", "Ironworker (Reinforcing & Structural)", "Electrician (Traffic Signal & ITS)", "Laborer (Heavy & Highway)"],
        description="Trade classifications to price under 29 CFR Part 5 and Form WH-347.",
    )
    estimated_crew_hours: int = Field(
        default=14500,
        ge=40,
        le=5000000,
        description="Total estimated man-hours across the project schedule.",
    )


# API #05: Build America, Buy America (BABA / 23 CFR 635.410) Material Auditor
class BabaComplianceRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="USACE-W912EP-27-B-0004", min_length=2, max_length=120, description="Project or Contract ID.")
    bom_items: List[str] = Field(
        default=[
            "ASTM A572 Gr 50 Steel Sheet Piling PZ-35 ($7,797,000 — Melted & Poured in Indiana, USA)",
            "Epoxy-Coated Reinforcing Bar Grade 60 ($1,450,000 — Melted & Manufactured in Texas, USA)",
            "13.8kV Medium-Voltage Switchgear & VFD Lineup ($3,290,000 — Assembled in North Carolina, 68% US component cost)",
            "Specialty Submersible Fiber Optic Splice Closures ($85,000 — Imported German housing, De Minimis <5% candidate)",
        ],
        description="Bill of Materials (BOM) line items with dollar values and country of melt/manufacture.",
    )
    funding_agency: str = Field(default="FHWA / USACE Infrastructure", min_length=2, max_length=140, description="Federal or state funding agency.")


# API #06: DOT DBE (49 CFR Part 26) Subcontractor & Good Faith Effort Generator
class DbeGoodFaithRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="TXDOT-CSJ-0015-13-412", min_length=2, max_length=120, description="DOT Project ID.")
    total_bid_amount_usd: float = Field(default=17850000.0, ge=10000.0, le=5000000000.0, description="Total prime contract bid amount in USD.")
    dbe_goal_pct: float = Field(default=11.5, ge=0.0, le=50.0, description="Mandatory contract DBE participation goal percentage.")
    proposed_dbe_commitments: List[Dict[str, Any]] = Field(
        default=[
            {"sub_name": "Apex Civil & Utility Constructors LLC", "role": "Subcontractor (100% Credit)", "scope": "36-Inch RCP Storm Drain & Excavation", "quote_usd": 1480000.0},
            {"sub_name": "Vanguard Traffic Signal & ITS Inc.", "role": "Subcontractor (100% Credit)", "scope": "ITS Fiber Conduit & High-Mast Illumination", "quote_usd": 695000.0},
        ],
        description="List of proposed certified DBE subcontractors or regular dealers (60% credit under 49 CFR 26.55).",
    )


# API #07: AIA G702 / G703 Schedule of Values (SOV) & Retainage Billing Generator
class AiaPayAppRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="TXDOT-CSJ-0015-13-412", min_length=2, max_length=120, description="Project number.")
    contractor_name: str = Field(default="Webber Civil Constructors LLC", min_length=2, max_length=180, description="Prime or Subcontractor name.")
    contract_sum_usd: float = Field(default=17850000.0, ge=1000.0, le=5000000000.0, description="Original Contract Sum in USD.")
    retainage_pct: float = Field(default=5.0, ge=0.0, le=20.0, description="Contract retainage percentage (typically 5% or 10%).")
    application_number: int = Field(default=1, ge=1, le=240, description="Progress billing application number.")


# API #08: Miller Act (40 U.S.C. 3131) & Surety Bond Capacity Underwriter
class SuretyBondAuditRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    contractor_name: str = Field(default="Apex Civil & Utility Constructors LLC", min_length=2, max_length=180, description="Contractor legal name.")
    current_assets_usd: float = Field(default=4850000.0, ge=0.0, description="Total current assets on CPA balance sheet (USD).")
    current_liabilities_usd: float = Field(default=2150000.0, ge=0.0, description="Total current liabilities on CPA balance sheet (USD).")
    net_worth_equity_usd: float = Field(default=4200000.0, ge=0.0, description="Total tangible net worth / stockholders equity (USD).")
    uncompleted_wip_backlog_usd: float = Field(default=16500000.0, ge=0.0, description="Current uncompleted cost-to-complete WIP backlog (USD).")
    target_project_bid_usd: float = Field(default=12400000.0, ge=10000.0, description="Target project bid amount requiring 100% Performance & Payment Bonds.")


# API #09: Construction RFI, Differing Site Conditions & AIA G701 Change Order
class RfiChangeOrderRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="CALTRANS-04-2Q7404", min_length=2, max_length=120, description="Project ID.")
    issue_summary: str = Field(
        default="Encountered uncharted 48-inch abandoned cast-iron brine main and serpentine rock formation at Bent 4 micropile elevation -38.0 ft (Soil Boring B-12 showed medium stiff clay to -65.0 ft).",
        min_length=10,
        max_length=10000,
        description="Description of the plan discrepancy, conflict, or Type I/II differing site condition.",
    )
    direct_cost_impact_usd: float = Field(default=184500.0, ge=0.0, description="Estimated direct labor, equipment standby, and material cost impact (USD).")
    critical_path_delay_days: int = Field(default=14, ge=0, le=1000, description="Estimated Critical Path Method (CPM) schedule impact in calendar days.")


# API #10: OSHA 29 CFR 1926, USACE EM 385-1-1 AHA & Insurance EMR Auditor
class OshaEmrAuditRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="USACE-W912EP-27-B-0004", min_length=2, max_length=120, description="Project ID.")
    high_hazard_activities: List[str] = Field(
        default=["Deep Cofferdam Excavation > 20 ft (29 CFR 1926 Subpart P)", "Crawler Crane Steel Sheet Pile Driving Near 13.8kV Lines (Subpart CC)", "Bridge Deck Hydrodemolition & Silica Dust Control (1926.1153)"],
        description="List of high-hazard construction activities requiring Activity Hazard Analysis (AHA).",
    )
    contractor_emr_current: float = Field(default=0.78, ge=0.3, le=2.5, description="Contractor current NCCI Experience Modification Rate (EMR).")


# API #11: DOT Planholder List, Competitor Bid Behavior & MLOT Analyzer
class PlanholderSpreadRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="TXDOT-CSJ-0015-13-412", min_length=2, max_length=120, description="DOT Project ID.")
    engineers_estimate_usd: float = Field(default=18450000.0, ge=10000.0, description="Official DOT Engineer's Estimate in USD.")
    planholders: List[str] = Field(
        default=["Webber LLC", "Granite Construction Inc.", "Jordan Foster Construction LLC", "Lone Star Paving Co.", "Capital Excavation Company"],
        description="List of contractors on the official DOT planholder list.",
    )


# API #12: Trade Subcontractor Invitation to Bid (ITB), Scope Gap & AIA A401
class SubcontractorItbRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="TXDOT-CSJ-0015-13-412", min_length=2, max_length=120, description="Project ID.")
    trade_package: str = Field(default="Division 26 — Roadway ITS Fiber Duct Bank, High-Mast Illumination & 480V Switchgear", min_length=3, max_length=240, description="Target subcontractor trade package.")
    prime_contractor: str = Field(default="Webber Civil Constructors LLC", min_length=2, max_length=180, description="Issuing General Contractor / Heavy-Civil Prime.")
    bid_due_date: str = Field(default="2026-11-18", min_length=4, max_length=40, description="Subcontractor quote deadline.")


# Master Moat #1: 6-File OpenXML Bid-Tab, Prevailing-Wage & AIA Pay-App .ZIP Compiler
class CompileBidPackageRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    project_id: str = Field(default="TXDOT-CSJ-0015-13-412", max_length=120, description="Target DOT CSJ, USACE Solicitation ID, or Project Number.")
    project_title: str = Field(default="IH-35 Corridor Bridge Deck Replacement, Superpave HMA Overlay & ITS Fiber Duct Bank", max_length=300, description="Project title.")
    agency: str = Field(default="Texas Department of Transportation (TxDOT) — Austin District", max_length=200, description="Issuing DOT or public works agency.")
    state_code: str = Field(default="TX", max_length=10, description="Two-letter U.S. state code.")
    county: str = Field(default="Travis County, TX", max_length=120, description="Project county.")
    contractor_name: str = Field(default="Apex Civil & Utility Constructors LLC", max_length=180, description="Bidding Prime or Subcontractor legal name.")
    license_or_dot_id: str = Field(default="TXDOT-PREQUAL-88412", max_length=100, description="State Contractor License or DOT Prequalification ID.")
    dbe_status: str = Field(default="DOT Certified Prime / 11.5% DBE Participation Committed", max_length=140, description="DBE/MBE/WBE or Prime status.")
    target_markup_pct: float = Field(default=8.5, ge=1.0, le=35.0, description="Target overhead & profit markup percentage.")
    spec_text: str = Field(default="", max_length=50000, description="Optional raw specification or special provisions text.")


# Master Moat #3: Two-Sided 49 CFR Part 26 Prime-to-DBE / Subcontractor Clearinghouse
class DbeClearinghouseRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    company_name: str = Field(default="Apex Civil & Utility Constructors LLC", max_length=180, description="Contractor legal entity name.")
    estimating_email: str = Field(default="estimating@apexcivilconstructors.com", max_length=254, description="Chief Estimator or Bid Desk email.")
    license_or_dot_id: str = Field(default="TXDOT-PREQUAL-88412", max_length=100, description="Contractor license or DOT vendor ID.")
    dbe_status: str = Field(default="DOT Certified DBE (49 CFR Part 26)", max_length=120, description="DBE, MBE, WBE, DVBE, SBE, or Heavy-Civil Prime.")
    role_requested: str = Field(default="Prime Seeking Certified DBE Subcontractor Quotes", max_length=140, description="Clearinghouse role.")
    trade_division: str = Field(default="Div 31/33 Underground Utilities & Storm Drainage", max_length=160, description="CSI division or DOT work class.")
    project_id: str = Field(default="TXDOT-CSJ-0015-13-412", max_length=120, description="Target DOT or municipal project ID.")
    state_code: str = Field(default="TX", max_length=10, description="Two-letter U.S. state code.")
    proposed_dbe_share_pct: float = Field(default=12.5, ge=1.0, le=100.0, description="Proposed DBE subcontract participation percentage.")

