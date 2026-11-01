r"""
RubricWard RapidAPI Studio Listing Kit Generator (D:\RubricWard\generate_rapidapi_kit.py)
Generates all 3 RapidAPI Studio Listing Assets for each of the 12 RubricWard Preconstruction APIs:
1. OpenAPI 3.0.3 JSON specification (`rapidapi_assets/rapidapi_apiXX_openapi.json`)
2. 500x500 PNG API Logo (`rapidapi_assets/apiXX_logo.png`) featuring Symbol #07 (Compass Quadrant Lock) on Warm Vellum (#FAF8F5)
3. Full Markdown Long Description / README (`rapidapi_assets/rapidapi_apiXX_readme.md`)
"""

import json
import math
import struct
import zlib
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = ROOT_DIR / "rapidapi_assets"

RUBRICWARD_RAPIDAPI_CATALOG: List[Dict[str, Any]] = [
    {
        "num": "01",
        "slug": "csi-masterformat-spec-shredder",
        "title": "CSI MasterFormat Divisions 00-48 Spec & Submittal Shredder API",
        "short_description": "Shred raw Construction Project Manuals into CSI MasterFormat Divisions 00-48 tables, submittal logs, liquidated damages, and retainage rules.",
        "category": "Business",
        "method": "POST",
        "route": "/v1/shred/csi-masterformat",
        "operation_name": "Shred CSI MasterFormat Specification",
        "operation_id": "shredCsiMasterformatSpec",
        "accent_rgb": (30, 58, 138),  # Blueprint Navy #1E3A8A
        "sample_request": {
            "project_name": "TxDOT IH-45 Corridor Mill & Superpave Overlay",
            "solicitation_number": "CSJ-0912-72-614",
            "state_code": "TX",
            "specification_text": "SECTION 01 11 00 SUMMARY OF WORK: Liquidated damages of $2,500/calendar day apply beyond 240 calendar days. Retainage 5%. SECTION 03 30 00 CAST-IN-PLACE CONCRETE: Submit mix design and mill certs. SECTION 32 12 16 ASPHALT PAVING: TxDOT Item 3076 Superpave D-GR-B 18,500 Tons.",
        },
        "request_properties": {
            "project_name": {"type": "string", "description": "Project title or letting name.", "default": "TxDOT IH-45 Mill & Overlay"},
            "solicitation_number": {"type": "string", "description": "Official DOT CSJ, USACE, or Municipal solicitation ID.", "default": "CSJ-0912-72-614"},
            "state_code": {"type": "string", "description": "Two-letter U.S. state postal code.", "default": "TX"},
            "specification_text": {"type": "string", "description": "Unstructured Project Manual or CSI specification text to shred.", "minLength": 20},
        },
        "required_fields": ["specification_text"],
    },
    {
        "num": "02",
        "slug": "dot-unit-bid-tab-modeler",
        "title": "50-State DOT Historical Item Bid Tabulation & Spread Modeler API",
        "short_description": "Model 50-State DOT historical unit-price bid tabulations ($/Ton, $/LF, $/CY), low/median/high bidder spreads, and recommended unit bid prices.",
        "category": "Data",
        "method": "POST",
        "route": "/v1/model/dot-unit-bid-tabs",
        "operation_name": "Model DOT Historical Unit Bid Tabulations",
        "operation_id": "modelDotUnitBidTabs",
        "accent_rgb": (4, 120, 87),  # Surveyor Forest #047857
        "sample_request": {
            "state_code": "TX",
            "dot_agency": "TxDOT",
            "letting_quarter": "2026-Q4",
            "pay_items": [
                {"item_code": "3076-6001", "description": "Dense-Graded Hot-Mix Asphalt (Superpave)", "unit": "TON", "quantity": 18500},
                {"item_code": "0464-6008", "description": "Reinforced Concrete Pipe (Class III 36-Inch)", "unit": "LF", "quantity": 2400},
            ],
        },
        "request_properties": {
            "state_code": {"type": "string", "description": "Two-letter U.S. state postal code (e.g., TX, CA, FL, PA).", "default": "TX"},
            "dot_agency": {"type": "string", "description": "State DOT agency identifier (e.g., TxDOT, Caltrans, FDOT, PennDOT).", "default": "TxDOT"},
            "letting_quarter": {"type": "string", "description": "Target letting quarter for inflation adjustment.", "default": "2026-Q4"},
            "pay_items": {"type": "array", "description": "Array of DOT pay items with item_code, description, unit, and quantity.", "items": {"type": "object"}},
        },
        "required_fields": ["state_code", "pay_items"],
    },
    {
        "num": "03",
        "slug": "davis-bacon-prevailing-wage-calculator",
        "title": "Davis-Bacon 29 CFR 5 & State Prevailing Wage Fringe Calculator API",
        "short_description": "Calculate federal Davis-Bacon (29 CFR Part 5) and State Little Davis-Bacon prevailing wage base rates, fringe burdens, and WH-347 payroll costs.",
        "category": "Finance",
        "method": "POST",
        "route": "/v1/calculate/davis-bacon-prevailing-wage",
        "operation_name": "Calculate Davis-Bacon Prevailing Wage & Fringe Burden",
        "operation_id": "calculateDavisBaconPrevailingWage",
        "accent_rgb": (30, 58, 138),
        "sample_request": {
            "state_code": "TX",
            "county_name": "Harris County",
            "construction_type": "Highway",
            "crew_classifications": [
                {"trade": "Power Equipment Operator (Asphalt Paver / Roller)", "estimated_hours": 1450},
                {"trade": "Cement Mason / Concrete Finisher", "estimated_hours": 980},
            ],
        },
        "request_properties": {
            "state_code": {"type": "string", "description": "Two-letter U.S. state code.", "default": "TX"},
            "county_name": {"type": "string", "description": "Project county name for wage determination lookup.", "default": "Harris County"},
            "construction_type": {"type": "string", "description": "Davis-Bacon construction category (Highway, Heavy, Building, Residential).", "default": "Highway"},
            "crew_classifications": {"type": "array", "description": "List of labor trade classifications and estimated hours.", "items": {"type": "object"}},
        },
        "required_fields": ["state_code", "county_name", "crew_classifications"],
    },
    {
        "num": "04",
        "slug": "live-dot-construction-lettings-feed",
        "title": "52-Portal Live State DOT Lettings, USACE & Public Works Feed API",
        "short_description": "Stream AI-vetted heavy-civil, highway, bridge, water/sewer, and commercial construction lettings across all 50 State DOTs, USACE, and Municipal portals.",
        "category": "Data",
        "method": "GET",
        "route": "/v1/lettings/live",
        "operation_name": "Get Live 50-State DOT & Public Works Lettings",
        "operation_id": "getLiveDotLettings",
        "accent_rgb": (4, 120, 87),
        "sample_request": {"state": "ALL", "limit": 10},
        "request_properties": {
            "state": {"type": "string", "description": "Filter by two-letter state postal code (e.g., TX, CA, FL) or ALL.", "default": "ALL"},
            "limit": {"type": "integer", "description": "Maximum number of lettings to return (1-50).", "default": 10},
        },
        "required_fields": [],
    },
    {
        "num": "05",
        "slug": "baba-buy-america-material-auditor",
        "title": "Build America Buy America BABA & 23 CFR 635.410 Material Auditor API",
        "short_description": "Audit construction Bills of Materials against Build America, Buy America (BABA) and FHWA 23 CFR 635.410 domestic iron, steel, and manufactured product rules.",
        "category": "Business",
        "method": "POST",
        "route": "/v1/audit/baba-buy-america",
        "operation_name": "Audit BABA & Buy America Material Compliance",
        "operation_id": "auditBabaBuyAmerica",
        "accent_rgb": (30, 58, 138),
        "sample_request": {
            "project_name": "PennDOT I-81 Composite Bridge Deck Replacement",
            "funding_agency": "FHWA / DOT",
            "bom_items": [
                {"material_name": "ASTM A709 Grade 50W Structural Steel Plate Girders", "category": "Iron/Steel", "country_of_melt_and_pour": "US", "domestic_cost_pct": 100.0, "extended_cost_usd": 1420000},
                {"material_name": "Elastomeric Bridge Bearing Pads", "category": "Construction Material", "country_of_melt_and_pour": "US", "domestic_cost_pct": 92.0, "extended_cost_usd": 84000},
            ],
        },
        "request_properties": {
            "project_name": {"type": "string", "description": "Infrastructure project title.", "default": "PennDOT I-81 Bridge Replacement"},
            "funding_agency": {"type": "string", "description": "Federal funding agency (FHWA, FTA, EPA SRF, USACE).", "default": "FHWA / DOT"},
            "bom_items": {"type": "array", "description": "Bill of Materials items with category, origin, domestic_cost_pct, and extended_cost_usd.", "items": {"type": "object"}},
        },
        "required_fields": ["project_name", "bom_items"],
    },
    {
        "num": "06",
        "slug": "dot-dbe-good-faith-effort-generator",
        "title": "DOT DBE 49 CFR Part 26 Subcontractor & Good Faith Effort Generator API",
        "short_description": "Calculate certified DBE/MBE/WBE participation credit (100% subcontractor vs. 60% regular dealer) and generate audit-proof 49 CFR Part 26 Good Faith Effort logs.",
        "category": "Business",
        "method": "POST",
        "route": "/v1/generate/dbe-good-faith-effort",
        "operation_name": "Generate DOT DBE Participation & Good Faith Effort Log",
        "operation_id": "generateDbeGoodFaithEffort",
        "accent_rgb": (4, 120, 87),
        "sample_request": {
            "project_name": "FDOT SR-826 Palmetto Expressway Interchange Reconstruction",
            "total_base_bid_usd": 14850000,
            "dbe_goal_percent": 11.5,
            "proposed_dbe_commitments": [
                {"firm_name": "Sunshine Barricade & MOT LLC", "certification": "FDOT DBE", "role": "Subcontractor", "work_scope": "Maintenance of Traffic & Pavement Markings", "quote_amount_usd": 1180000},
                {"firm_name": "Gulfstream Aggregate Supply Inc.", "certification": "FDOT DBE", "role": "Regular Dealer", "work_scope": "Limestone Base & Pipe Bedding", "quote_amount_usd": 920000},
            ],
        },
        "request_properties": {
            "project_name": {"type": "string", "description": "DOT or municipal project name.", "default": "FDOT SR-826 Reconstruction"},
            "total_base_bid_usd": {"type": "number", "description": "Total prime contractor base bid in USD.", "default": 14850000},
            "dbe_goal_percent": {"type": "number", "description": "Mandatory DBE goal percentage (e.g., 11.5).", "default": 11.5},
            "proposed_dbe_commitments": {"type": "array", "description": "List of DBE firms, role (Subcontractor/Regular Dealer), and quote_amount_usd.", "items": {"type": "object"}},
        },
        "required_fields": ["project_name", "total_base_bid_usd", "dbe_goal_percent", "proposed_dbe_commitments"],
    },
    {
        "num": "07",
        "slug": "aia-g702-g703-pay-app-generator",
        "title": "AIA G702 G703 Schedule of Values SOV & Retainage Billing Generator API",
        "short_description": "Convert construction bid items into a balanced, front-load-compliant AIA G702 Application for Payment and G703 Continuation Sheet with retainage math.",
        "category": "Finance",
        "method": "POST",
        "route": "/v1/generate/aia-g702-g703-pay-app",
        "operation_name": "Generate AIA G702 & G703 Schedule of Values Pay App",
        "operation_id": "generateAiaG702G703PayApp",
        "accent_rgb": (30, 58, 138),
        "sample_request": {
            "project_name": "City of Austin Walnut Creek WWTP Digester Rehab",
            "application_number": 4,
            "retainage_pct": 5.0,
            "sov_lines": [
                {"item_no": "01", "description": "Mobilization, Bonds & Submittals", "scheduled_value_usd": 380000, "prev_completed_usd": 380000, "this_period_usd": 0, "stored_materials_usd": 0},
                {"item_no": "02", "description": "Cast-in-Place Structural Digester Wall Rehab", "scheduled_value_usd": 1950000, "prev_completed_usd": 820000, "this_period_usd": 465000, "stored_materials_usd": 115000},
            ],
        },
        "request_properties": {
            "project_name": {"type": "string", "description": "Construction contract title.", "default": "Walnut Creek WWTP Rehab"},
            "application_number": {"type": "integer", "description": "Monthly progress pay application number.", "default": 4},
            "retainage_pct": {"type": "number", "description": "Contract retainage withhold percentage.", "default": 5.0},
            "sov_lines": {"type": "array", "description": "Schedule of Values line items with scheduled_value_usd, prev_completed_usd, this_period_usd, stored_materials_usd.", "items": {"type": "object"}},
        },
        "required_fields": ["project_name", "sov_lines"],
    },
    {
        "num": "08",
        "slug": "surety-miller-act-bond-underwriter",
        "title": "Miller Act 40 USC 3131 & Surety Bond Capacity Underwriter API",
        "short_description": "Underwrite contractor working capital, net worth, and WIP backlog to calculate Single/Aggregate Surety Bond limits and sliding-scale bond premiums.",
        "category": "Finance",
        "method": "POST",
        "route": "/v1/audit/surety-miller-act-bond",
        "operation_name": "Underwrite Miller Act Surety Bond Capacity & Premium",
        "operation_id": "auditSuretyMillerActBond",
        "accent_rgb": (4, 120, 87),
        "sample_request": {
            "contractor_name": "Lone Star Heavy Civil Constructors Inc.",
            "current_assets_usd": 6400000,
            "current_liabilities_usd": 2950000,
            "tangible_net_worth_usd": 5100000,
            "uncompleted_wip_backlog_usd": 19500000,
            "target_project_bid_usd": 11200000,
        },
        "request_properties": {
            "contractor_name": {"type": "string", "description": "Legal name of construction contractor.", "default": "Lone Star Heavy Civil Constructors Inc."},
            "current_assets_usd": {"type": "number", "description": "CPA-reviewed current assets in USD.", "default": 6400000},
            "current_liabilities_usd": {"type": "number", "description": "Current liabilities in USD.", "default": 2950000},
            "tangible_net_worth_usd": {"type": "number", "description": "Tangible net worth (equity) in USD.", "default": 5100000},
            "uncompleted_wip_backlog_usd": {"type": "number", "description": "Current uncompleted Work-in-Progress (WIP) backlog in USD.", "default": 19500000},
            "target_project_bid_usd": {"type": "number", "description": "New project contract value requiring 100% Performance & Payment Bonds.", "default": 11200000},
        },
        "required_fields": ["contractor_name", "current_assets_usd", "current_liabilities_usd", "tangible_net_worth_usd", "target_project_bid_usd"],
    },
    {
        "num": "09",
        "slug": "construction-rfi-change-order-generator",
        "title": "Construction RFI Differing Site Conditions & AIA G701 Change Order API",
        "short_description": "Analyze plan discrepancies or Differing Site Conditions (FAR 52.236-2), calculate Critical Path Time-Impact float consumption, and draft AIA G701 Change Orders.",
        "category": "Business",
        "method": "POST",
        "route": "/v1/generate/rfi-change-order-claim",
        "operation_name": "Generate Construction RFI & AIA G701 Change Order Claim",
        "operation_id": "generateRfiChangeOrderClaim",
        "accent_rgb": (30, 58, 138),
        "sample_request": {
            "project_name": "USACE Norfolk District Floodwall Sector Gate Monolith",
            "contract_clause_reference": "FAR 52.236-2 Differing Site Conditions (Type I)",
            "field_condition_description": "Geotechnical boring log B-14 indicated stiff clay at El. -18.0 FT, but sheet-pile driving encountered uncharted submerged timber wharf pilings and granite riprap from El. -11.5 FT to -19.0 FT.",
            "direct_cost_impact_usd": 184500,
            "critical_path_delay_days": 14,
        },
        "request_properties": {
            "project_name": {"type": "string", "description": "Active project contract name.", "default": "USACE Floodwall Monolith"},
            "contract_clause_reference": {"type": "string", "description": "Applicable notice/change clause (e.g., FAR 52.236-2, AIA A201 4.3.4).", "default": "FAR 52.236-2 Differing Site Conditions"},
            "field_condition_description": {"type": "string", "description": "Detailed narrative of plan discrepancy or subsurface condition.", "minLength": 20},
            "direct_cost_impact_usd": {"type": "number", "description": "Estimated direct labor, equipment, and material cost impact in USD.", "default": 184500},
            "critical_path_delay_days": {"type": "integer", "description": "Estimated CPM schedule delay in calendar days.", "default": 14},
        },
        "required_fields": ["project_name", "field_condition_description"],
    },
    {
        "num": "10",
        "slug": "osha-emr-site-safety-auditor",
        "title": "OSHA 29 CFR 1926 USACE EM 385-1-1 AHA & Insurance EMR Auditor API",
        "short_description": "Generate trade-specific Activity Hazard Analyses (AHA), Site-Specific Safety Plans, Trenching/Fall-Protection checklists, and Experience Modification Rate (EMR) audits.",
        "category": "Business",
        "method": "POST",
        "route": "/v1/audit/osha-emr-site-safety",
        "operation_name": "Generate OSHA 1926 & USACE EM 385-1-1 Safety AHA",
        "operation_id": "auditOshaEmrSiteSafety",
        "accent_rgb": (4, 120, 87),
        "sample_request": {
            "project_name": "Caltrans District 7 Deep Storm Drain Box Culvert Excavation",
            "contractor_emr": 0.84,
            "max_allowed_emr": 1.00,
            "high_hazard_activities": [
                "Trenching & Shoring below 18 FT in Type C Soil (29 CFR 1926 Subpart P)",
                "Crawler Crane 110-Ton Precast Box Culvert Picks near energized 34.5kV overhead lines",
            ],
        },
        "request_properties": {
            "project_name": {"type": "string", "description": "Project title.", "default": "Caltrans Deep Box Culvert Excavation"},
            "contractor_emr": {"type": "number", "description": "Contractor NCCI Experience Modification Rate (EMR).", "default": 0.84},
            "max_allowed_emr": {"type": "number", "description": "Owner/Specification maximum allowed EMR threshold.", "default": 1.00},
            "high_hazard_activities": {"type": "array", "description": "List of high-hazard construction scopes requiring AHA generation.", "items": {"type": "string"}},
        },
        "required_fields": ["project_name", "high_hazard_activities"],
    },
    {
        "num": "11",
        "slug": "dot-planholder-competitor-mlot-analyzer",
        "title": "DOT Planholder List Competitor Bid Behavior & MLOT Analyzer API",
        "short_description": "Analyze official DOT planholder lists against historical head-to-head letting results to predict aggressive bidders, Margin Left on Table (MLOT), and optimal markup.",
        "category": "Data",
        "method": "POST",
        "route": "/v1/analyze/planholder-competitor-spread",
        "operation_name": "Analyze DOT Planholder List & Competitor Bid Spread",
        "operation_id": "analyzePlanholderCompetitorSpread",
        "accent_rgb": (30, 58, 138),
        "sample_request": {
            "letting_id": "GDOT-PI-0017482",
            "engineers_estimate_usd": 9400000,
            "our_direct_cost_usd": 8150000,
            "planholders": [
                {"contractor_name": "C.W. Matthews Contracting Co.", "historical_avg_vs_engineer_pct": -4.2, "recent_win_rate_pct": 34.0},
                {"contractor_name": "E.R. Snell Contractor Inc.", "historical_avg_vs_engineer_pct": -2.8, "recent_win_rate_pct": 28.5},
            ],
        },
        "request_properties": {
            "letting_id": {"type": "string", "description": "Official DOT letting or contract ID.", "default": "GDOT-PI-0017482"},
            "engineers_estimate_usd": {"type": "number", "description": "Published DOT Engineer's Estimate in USD.", "default": 9400000},
            "our_direct_cost_usd": {"type": "number", "description": "Estimator's unburdened direct cost in USD.", "default": 8150000},
            "planholders": {"type": "array", "description": "Confirmed planholders and their historical bid behavior.", "items": {"type": "object"}},
        },
        "required_fields": ["letting_id", "engineers_estimate_usd", "our_direct_cost_usd", "planholders"],
    },
    {
        "num": "12",
        "slug": "subcontractor-scope-itb-aia-a401-generator",
        "title": "Trade Subcontractor Invitation to Bid ITB Scope Gap & AIA A401 API",
        "short_description": "Generate CSI-aligned Subcontractor Scope Sheets, Scope-Gap Inclusions/Exclusions Checklists, and AIA A401 Subcontract flow-down clauses.",
        "category": "Business",
        "method": "POST",
        "route": "/v1/generate/subcontractor-scope-itb",
        "operation_name": "Generate Subcontractor ITB Scope Sheet & AIA A401 Flow-Downs",
        "operation_id": "generateSubcontractorScopeItb",
        "accent_rgb": (4, 120, 87),
        "sample_request": {
            "project_name": "VA Medical Center Seismic Structural & MEP Modernization",
            "trade_division": "Division 26 - Electrical & Medium-Voltage Switchgear",
            "prime_contract_liquidated_damages_per_day_usd": 3500,
            "scope_highlights": [
                "Furnish and install two 2,500 kVA 15kV pad-mounted transformers and emergency generator paralleling switchgear",
                "Include all trenching, concrete duct banks, arc-flash study, and NETA acceptance testing",
            ],
        },
        "request_properties": {
            "project_name": {"type": "string", "description": "Project title.", "default": "VAMC Seismic & MEP Modernization"},
            "trade_division": {"type": "string", "description": "Target CSI MasterFormat division and trade.", "default": "Division 26 - Electrical"},
            "prime_contract_liquidated_damages_per_day_usd": {"type": "number", "description": "Prime contract daily liquidated damages flow-down in USD.", "default": 3500},
            "scope_highlights": {"type": "array", "description": "Key scope inclusions to verify in subcontractor buyout.", "items": {"type": "string"}},
        },
        "required_fields": ["project_name", "trade_division", "scope_highlights"],
    },
]


def _render_symbol07_png(path: Path, accent_rgb: Tuple[int, int, int], badge_num: str) -> None:
    """
    Renders a crisp 500x500 RGB PNG featuring Symbol #07 (Compass Quadrant Lock)
    on Warm Vellum (#FAF8F5) with Deep Obsidian Ink (#0A0D14) and the API's editorial accent.
    Zero external image library required.
    """
    width, height = 500, 500
    vellum = (250, 248, 245)      # #FAF8F5
    obsidian = (10, 13, 20)       # #0A0D14
    border_col = (214, 211, 205)  # #D6D3CD

    rows: List[bytes] = []
    cx, cy = 235.0, 265.0
    radius = 152.0

    # Top-right floating square quadrant bounds (scaled from 64x64 viewBox to 500x500)
    sq_x1, sq_y1 = 266, 98
    sq_x2, sq_y2 = 392, 224
    sq_r = 14

    for y in range(height):
        row = bytearray(1 + width * 3)
        row[0] = 0  # PNG filter type 0 (None)
        for x in range(width):
            # Outer card border (12px inset frame)
            if (x in (24, 25, 474, 475) and 24 <= y <= 475) or (y in (24, 25, 474, 475) and 24 <= x <= 475):
                r, g, b = border_col
            # Top architectural header rule bar (y: 26..36)
            elif 26 <= x <= 473 and 26 <= y <= 36:
                r, g, b = accent_rgb
            else:
                r, g, b = vellum

                # Check floating top-right square quadrant (x in [sq_x1..sq_x2], y in [sq_y1..sq_y2])
                in_sq = False
                if sq_x1 <= x <= sq_x2 and sq_y1 <= y <= sq_y2:
                    in_sq = True
                    # Rounded corners check
                    for corner_x, corner_y in [
                        (sq_x1 + sq_r, sq_y1 + sq_r),
                        (sq_x2 - sq_r, sq_y1 + sq_r),
                        (sq_x1 + sq_r, sq_y2 - sq_r),
                        (sq_x2 - sq_r, sq_y2 - sq_r),
                    ]:
                        if (x < sq_x1 + sq_r or x > sq_x2 - sq_r) and (y < sq_y1 + sq_r or y > sq_y2 - sq_r):
                            if (x - corner_x) ** 2 + (y - corner_y) ** 2 > sq_r ** 2:
                                in_sq = False

                if in_sq:
                    r, g, b = accent_rgb
                else:
                    # Check 270-degree Compass Sector (circle centered at cx, cy, minus top-right quadrant x > cx and y < cy)
                    dx = x - cx
                    dy = y - cy
                    dist = math.hypot(dx, dy)
                    if 94 <= x <= 250 and 78 <= y <= 422 and (y <= 172 or x >= 94.0 + 156.0 * (((y - 172.0) / 250.0) ** 1.85)):
                        r, g, b = obsidian

            idx = 1 + x * 3
            row[idx] = r
            row[idx + 1] = g
            row[idx + 2] = b
        rows.append(bytes(row))

    raw_data = b"".join(rows)

    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(raw_data, level=9)
    png_bytes = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")
    path.write_bytes(png_bytes)


def build_openapi_spec(api: Dict[str, Any], base_url: str = "https://rubricward.com") -> Dict[str, Any]:
    """Builds a RapidAPI-compliant OpenAPI 3.0.3 JSON specification for a RubricWard microservice."""
    route = api["route"]
    method = api["method"].lower()

    if method == "get":
        parameters = []
        for prop_name, prop_meta in api["request_properties"].items():
            parameters.append({
                "name": prop_name,
                "in": "query",
                "required": prop_name in api["required_fields"],
                "description": prop_meta["description"],
                "schema": {
                    "type": prop_meta["type"],
                    "default": prop_meta.get("default"),
                },
            })
        operation_obj = {
            "summary": api["operation_name"],
            "description": api["short_description"],
            "operationId": api["operation_id"],
            "parameters": parameters,
            "responses": {
                "200": {
                    "description": "Successful structured preconstruction JSON response",
                    "content": {"application/json": {"schema": {"type": "object"}}},
                }
            },
        }
    else:
        operation_obj = {
            "summary": api["operation_name"],
            "description": api["short_description"],
            "operationId": api["operation_id"],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": api["required_fields"],
                            "properties": api["request_properties"],
                        },
                        "example": api["sample_request"],
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Successful structured preconstruction JSON response",
                    "content": {"application/json": {"schema": {"type": "object"}}},
                }
            },
        }

    return {
        "openapi": "3.0.3",
        "info": {
            "title": api["title"],
            "version": "1.0.0",
            "description": api["short_description"],
        },
        "servers": [{"url": base_url}],
        "paths": {
            route: {method: operation_obj},
            "/v1/health": {
                "get": {
                    "summary": "Verify API Gateway Health Status",
                    "description": "Unprotected SLA and health-check endpoint returning HTTP 200 OK.",
                    "operationId": "getHealthCheckStatus",
                    "responses": {
                        "200": {
                            "description": "Service healthy",
                            "content": {"application/json": {"schema": {"type": "object"}}},
                        }
                    },
                }
            },
        },
    }


def build_readme(api: Dict[str, Any]) -> str:
    """Generates a comprehensive RapidAPI Studio Long Description / README in Markdown."""
    sample_json = json.dumps(api["sample_request"], indent=2)
    return f"""# {api['title']}

**By RubricWard Preconstruction & DOT Systems** (`https://rubricward.com`)

{api['short_description']}

---

## Key Capabilities & Construction Preconstruction Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes project manuals, DOT pay items, Davis-Bacon wage classifications, and AIA billing schedules in memory.
- **Built for ConTech ERPs, Heavy-Civil Estimators & Surety Underwriters:** Ready to plug directly into Procore, Autodesk Construction Cloud, HeavyBid workflows, or AI estimating agents via `@rubricward/mcp-server`.
- **Route:** `{api['method']} {api['route']}`

---

## Example Request Payload

```json
{sample_json}
```

---

## Pricing Tiers
- **BASIC (`$0 / mo`):** `10 requests / month` hard limit (`10 requests / hour` rate limit) for testing and evaluation.
- **PRO (`$49 / mo`):** `200 requests / month` for active estimating teams and specialty subcontractors.
- **ULTRA (`$149 / mo` — Recommended):** `1,000 requests / month` for regional general contractors and heavy-civil primes.
- **MEGA (`$399 / mo`):** `4,000 requests / month` for ConTech SaaS platforms, surety brokerages, and multi-office builders.
"""


def generate_all_kits(base_url: str = "https://rubricward.com") -> int:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for api in RUBRICWARD_RAPIDAPI_CATALOG:
        num = api["num"]
        openapi_path = ASSETS_DIR / f"rapidapi_api{num}_openapi.json"
        logo_path = ASSETS_DIR / f"api{num}_{api['slug'].replace('-', '_')}_logo.png"
        readme_path = ASSETS_DIR / f"rapidapi_api{num}_readme.md"

        openapi_spec = build_openapi_spec(api, base_url=base_url)
        openapi_path.write_text(json.dumps(openapi_spec, indent=2), encoding="utf-8")
        _render_symbol07_png(logo_path, api["accent_rgb"], num)
        readme_path.write_text(build_readme(api), encoding="utf-8")

    print(f"[RUBRICWARD RAPIDAPI KIT] Generated 12 OpenAPI 3.0.3 specs, 12 500x500 PNG logos, and 12 Markdown READMEs -> {ASSETS_DIR}")
    return len(RUBRICWARD_RAPIDAPI_CATALOG)


if __name__ == "__main__":
    generate_all_kits()

