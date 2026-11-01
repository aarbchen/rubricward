r"""
RubricWard RapidAPI Studio Listing Kit Generator (D:\RubricWard\generate_rapidapi_kit.py)
Generates all 3 RapidAPI Studio Listing Assets for each of the 12 RubricWard Healthcare Payer MRF, ERISA Appeal & NSA IDR APIs:
1. OpenAPI 3.0.3 JSON specification (`rapidapi_assets/rapidapi_apiXX_openapi.json`)
2. 500x500 PNG API Logo (`rapidapi_assets/apiXX_logo.png`) featuring the Split Shield & Ledger M7 mark on Warm Vellum (#FAF8F5)
3. Full Markdown Long Description / README (`rapidapi_assets/rapidapi_apiXX_readme.md`)
"""

import json
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
        "title": "Commercial Payer Clinical Policy Bulletin CPB & LCD Prior-Auth Shredder API",
        "short_description": "Shred commercial payer Clinical Policy Bulletins (UHC, Anthem, Aetna, Cigna) and Medicare LCD/NCD guidelines into CPT medical necessity rules and ERISA appeal triggers.",
        "category": "Medical",
        "method": "POST",
        "route": "/v1/shred/csi-masterformat",
        "operation_name": "Shred Commercial Payer Clinical Policy Bulletin",
        "operation_id": "shredCommercialPayerCpb",
        "accent_rgb": (5, 150, 105),
        "sample_request": {
            "project_id": "TXDOI-MRF-CPT-29881-DFW",
            "target_trade": "Orthopedic Surgery & Ambulatory Surgery Center (ASC)",
            "spec_text": "COMMERCIAL PAYER CLINICAL POLICY BULLETIN (CPB-0742): Lumbar Laminotomy (CPT 63030) and Arthroscopic Meniscectomy (CPT 29881) require 6 weeks of documented supervised physical therapy, NSAID trial, and MRI confirming nerve root compression. ERISA appeal deadline is 180 calendar days under 29 CFR 2560.503-1.",
        },
        "request_properties": {
            "project_id": {"type": "string", "description": "Claim Cohort ID, Payer Policy ID, or NSA IDR Case Reference.", "default": "TXDOI-MRF-CPT-29881-DFW"},
            "target_trade": {"type": "string", "description": "Clinical specialty focus (e.g., Orthopedic Surgery & ASC, Neurosurgery / Spine).", "default": "Orthopedic Surgery & ASC"},
            "spec_text": {"type": "string", "description": "Unstructured Commercial Payer Clinical Policy Bulletin (CPB) or Medicare LCD/NCD text to shred.", "minLength": 10},
        },
        "required_fields": ["spec_text"],
    },
    {
        "num": "02",
        "slug": "dot-unit-bid-tab-modeler",
        "title": "50-State Commercial Payer TiC MRF Allowed-Amount & QPA Rate Modeler API",
        "short_description": "Model 50-State CMS Transparency in Coverage (TiC 45 CFR 147.212) machine-readable file 25th, 50th (Median QPA), and 75th-percentile commercial allowed amounts by CPT/DRG.",
        "category": "Data",
        "method": "POST",
        "route": "/v1/model/dot-unit-bid-tabs",
        "operation_name": "Model 50-State Commercial Payer TiC MRF Allowed Amounts",
        "operation_id": "modelCommercialPayerTicMrf",
        "accent_rgb": (4, 120, 87),
        "sample_request": {
            "state_code": "TX",
            "pay_item_description": "CPT 29881 — Arthroscopy, Knee, Surgical; with Meniscectomy (Medial OR Lateral)",
            "unit": "CLAIM",
            "quantity": 420,
        },
        "request_properties": {
            "state_code": {"type": "string", "description": "Two-letter U.S. state postal code (e.g., TX, CA, FL, PA, NY).", "default": "TX"},
            "pay_item_description": {"type": "string", "description": "CPT, HCPCS, APC, or MS-DRG procedure code and clinical description.", "default": "CPT 29881 — Knee Arthroscopy & Meniscectomy"},
            "unit": {"type": "string", "description": "Billing unit of measure (CLAIM, CASE, UNIT, RVU, DRG).", "default": "CLAIM"},
            "quantity": {"type": "number", "description": "Annual or disputed cohort claim volume for the procedure.", "default": 420},
        },
        "required_fields": ["state_code", "pay_item_description", "unit", "quantity"],
    },
    {
        "num": "03",
        "slug": "davis-bacon-prevailing-wage-calculator",
        "title": "CMS Medicare Physician Fee Schedule MPFS RVU GPCI & ASC Calculator API",
        "short_description": "Calculate locality-adjusted CMS Medicare Physician Fee Schedule (MPFS) Work/PE/MP RVU rates, GPCI locality multipliers, and commercial percent-of-Medicare schedules.",
        "category": "Finance",
        "method": "POST",
        "route": "/v1/calculate/davis-bacon-prevailing-wage",
        "operation_name": "Calculate CMS Medicare MPFS RVU & GPCI Locality Schedule",
        "operation_id": "calculateMedicareMpfsRvuGpci",
        "accent_rgb": (5, 150, 105),
        "sample_request": {
            "state_code": "TX",
            "county": "Dallas / Tarrant County (DFW Locality)",
            "construction_type": "ASC / Outpatient Facility",
            "estimated_crew_hours": 1250,
        },
        "request_properties": {
            "state_code": {"type": "string", "description": "Two-letter U.S. state code.", "default": "TX"},
            "county": {"type": "string", "description": "CMS Medicare GPCI locality or county name.", "default": "Dallas / Tarrant County (DFW Locality)"},
            "construction_type": {"type": "string", "description": "Place of Service setting (ASC / Outpatient Facility, HOPD, Inpatient, Office).", "default": "ASC / Outpatient Facility"},
            "estimated_crew_hours": {"type": "integer", "description": "Total annual claim encounters across the specialty cohort.", "default": 1250},
        },
        "required_fields": ["state_code", "county"],
    },
    {
        "num": "04",
        "slug": "live-dot-construction-lettings-feed",
        "title": "52-Portal Live Commercial Payer MRF Rate Disparities & NSA IDR Feed API",
        "short_description": "Stream pre-vetted commercial payer TiC MRF rate-disparity cohorts, ERISA claim underpayments, and Federal No Surprises Act (NSA) IDR arbitration cases across 52 portals.",
        "category": "Data",
        "method": "GET",
        "route": "/v1/lettings/live",
        "operation_name": "Get Live 52-Portal Commercial Payer MRF & NSA IDR Cohorts",
        "operation_id": "getLiveCommercialPayerMrfCohorts",
        "accent_rgb": (4, 120, 87),
        "sample_request": {"state": "ALL", "limit": 10},
        "request_properties": {
            "state": {"type": "string", "description": "Filter by two-letter state postal code (e.g., TX, CA, FL) or ALL.", "default": "ALL"},
            "limit": {"type": "integer", "description": "Maximum number of payer MRF & IDR cohorts to return (1-50).", "default": 10},
        },
        "required_fields": [],
    },
    {
        "num": "05",
        "slug": "baba-buy-america-material-auditor",
        "title": "CMS NCCI Procedure-to-Procedure PTP Unbundling MUE & Modifier Scrubber API",
        "short_description": "Scrub surgical and outpatient claim lines against CMS National Correct Coding Initiative (NCCI) PTP column-1/column-2 edits, MUE caps, and Modifier -25/-59/-XS rules.",
        "category": "Medical",
        "method": "POST",
        "route": "/v1/audit/baba-buy-america",
        "operation_name": "Audit Claim Lines Against CMS NCCI PTP & MUE Edits",
        "operation_id": "auditCmsNcciPtpMue",
        "accent_rgb": (5, 150, 105),
        "sample_request": {
            "project_id": "TXDOI-MRF-CPT-29881-DFW",
            "funding_agency": "CMS NCCI / Commercial Payer Claims Editing Engine",
        },
        "request_properties": {
            "project_id": {"type": "string", "description": "Claim Cohort or Encounter ID.", "default": "TXDOI-MRF-CPT-29881-DFW"},
            "funding_agency": {"type": "string", "description": "Governing coding edit standard or commercial payer.", "default": "CMS NCCI / Commercial Payer Claims Editing Engine"},
        },
        "required_fields": ["project_id"],
    },
    {
        "num": "06",
        "slug": "dot-dbe-good-faith-effort-generator",
        "title": "Federal No Surprises Act NSA 45 CFR 149.510 Open Negotiation & IDR API",
        "short_description": "Generate statutory 30-business-day Open Negotiation Notices, verify QPA deflation anomalies, and compile Federal No Surprises Act (45 CFR 149.510) IDR arbitration briefs.",
        "category": "Medical",
        "method": "POST",
        "route": "/v1/generate/dbe-good-faith-effort",
        "operation_name": "Generate Federal NSA 45 CFR 149.510 IDR Arbitration Brief",
        "operation_id": "generateNsaIdrArbitrationBrief",
        "accent_rgb": (4, 120, 87),
        "sample_request": {
            "project_id": "CMS-NSA-IDR-CPT-63047-NAT",
            "total_bid_amount_usd": 1420000,
            "dbe_goal_pct": 215.0,
        },
        "request_properties": {
            "project_id": {"type": "string", "description": "NSA IDR Dispute Case ID.", "default": "CMS-NSA-IDR-CPT-63047-NAT"},
            "total_bid_amount_usd": {"type": "number", "description": "Total target 75th-percentile commercial MRF arbitration offer across disputed claim cohort (USD).", "default": 1420000},
            "dbe_goal_pct": {"type": "number", "description": "Target commercial reimbursement as a percentage of CMS Medicare fee schedule (e.g., 215.0).", "default": 215.0},
        },
        "required_fields": ["project_id", "total_bid_amount_usd", "dbe_goal_pct"],
    },
    {
        "num": "07",
        "slug": "aia-g702-g703-pay-app-generator",
        "title": "HIPAA X12 835 Electronic Remittance Advice ERA CARC Underpayment Auditor API",
        "short_description": "Audit HIPAA X12 835 Electronic Remittance Advice (ERA) payment lines and CARC/RARC adjustments (CARC 45, 50, 96, 97, 197) against contracted fee schedules and TiC MRF benchmarks.",
        "category": "Finance",
        "method": "POST",
        "route": "/v1/generate/aia-g702-g703-pay-app",
        "operation_name": "Audit HIPAA X12 835 ERA Remittance & CARC Underpayments",
        "operation_id": "auditHipaa835EraRemittance",
        "accent_rgb": (5, 150, 105),
        "sample_request": {
            "project_id": "TXDOI-MRF-CPT-29881-DFW",
            "contractor_name": "Texas Orthopedic & Spine Surgical Associates PLLC",
            "contract_sum_usd": 1840000,
        },
        "request_properties": {
            "project_id": {"type": "string", "description": "Remittance Audit Batch ID.", "default": "TXDOI-MRF-CPT-29881-DFW"},
            "contractor_name": {"type": "string", "description": "Billing Provider Group or ASC legal name.", "default": "Texas Orthopedic & Spine Surgical Associates PLLC"},
            "contract_sum_usd": {"type": "number", "description": "Total contracted expected allowed amount across the remittance batch in USD.", "default": 1840000},
        },
        "required_fields": ["project_id", "contract_sum_usd"],
    },
    {
        "num": "08",
        "slug": "surety-miller-act-bond-underwriter",
        "title": "50-State Prompt-Pay Statute Interest Penalty & Clean-Claim Calculator API",
        "short_description": "Calculate 50-state statutory prompt-pay interest penalties (TX Ins. Code Ch. 1301 18% APR, CA H&S 1371 15% APR, FL 627.6131 12% APR) on overdue commercial payer claims.",
        "category": "Finance",
        "method": "POST",
        "route": "/v1/audit/surety-miller-act-bond",
        "operation_name": "Calculate 50-State Prompt-Pay Statutory Interest Penalty",
        "operation_id": "calculatePromptPayInterestPenalty",
        "accent_rgb": (4, 120, 87),
        "sample_request": {
            "contractor_name": "Texas Orthopedic & Spine Surgical Associates PLLC",
            "target_project_bid_usd": 1830000,
        },
        "request_properties": {
            "contractor_name": {"type": "string", "description": "Provider Group or Hospital legal name.", "default": "Texas Orthopedic & Spine Surgical Associates PLLC"},
            "target_project_bid_usd": {"type": "number", "description": "Net overdue clean-claim principal balance subject to statutory prompt-pay interest (USD).", "default": 1830000},
        },
        "required_fields": ["contractor_name", "target_project_bid_usd"],
    },
    {
        "num": "09",
        "slug": "construction-rfi-change-order-generator",
        "title": "ERISA 29 CFR 2560.503-1 Medical Necessity & IRO Appeal Drafter API",
        "short_description": "Draft citation-backed ERISA 29 CFR 2560.503-1 Level-1/Level-2 medical necessity appeals demanding same-specialty peer review and complete administrative claim files.",
        "category": "Medical",
        "method": "POST",
        "route": "/v1/generate/rfi-change-order-claim",
        "operation_name": "Generate ERISA 29 CFR 2560.503-1 Medical Necessity Appeal",
        "operation_id": "generateErisaMedicalNecessityAppeal",
        "accent_rgb": (5, 150, 105),
        "sample_request": {
            "project_id": "CADMHC-MRF-CPT-63030-SFO",
            "issue_summary": "Payer issued CARC 50 (Not Medically Necessary) denial on CPT 63030 Lumbar Microdiscectomy despite MRI confirming L4-L5 extruded disc herniation and 8 weeks failed PT.",
            "direct_cost_impact_usd": 68500,
        },
        "request_properties": {
            "project_id": {"type": "string", "description": "Denied Claim or Cohort ID.", "default": "CADMHC-MRF-CPT-63030-SFO"},
            "issue_summary": {"type": "string", "description": "Clinical summary of the CARC/RARC denial and documented objective medical necessity evidence.", "minLength": 10},
            "direct_cost_impact_usd": {"type": "number", "description": "Disputed principal claim allowed amount under commercial MRF 75th percentile in USD.", "default": 68500},
        },
        "required_fields": ["project_id", "issue_summary"],
    },
    {
        "num": "10",
        "slug": "osha-emr-site-safety-auditor",
        "title": "MS-DRG APR-DRG Inpatient Clinical Validation & DRG Downcode Defense API",
        "short_description": "Defend hospital inpatient claims against commercial payer MS-DRG / APR-DRG clinical validation denials and CC/MCC downcoding (Sepsis-3, AKI, Severe Malnutrition).",
        "category": "Medical",
        "method": "POST",
        "route": "/v1/audit/osha-emr-site-safety",
        "operation_name": "Audit Inpatient MS-DRG Clinical Validation & CC/MCC Capture",
        "operation_id": "auditInpatientMsDrgClinicalValidation",
        "accent_rgb": (4, 120, 87),
        "sample_request": {
            "project_id": "NYDFS-MRF-CPT-27447-NYC",
            "contractor_emr_current": 0.94,
        },
        "request_properties": {
            "project_id": {"type": "string", "description": "Inpatient DRG Audit Batch ID.", "default": "NYDFS-MRF-CPT-27447-NYC"},
            "contractor_emr_current": {"type": "number", "description": "Hospital Case Mix Index (CMI) or clean-claim clinical validation pass ratio.", "default": 0.94},
        },
        "required_fields": ["project_id"],
    },
    {
        "num": "11",
        "slug": "dot-planholder-competitor-mlot-analyzer",
        "title": "Specialty Group EIN NPI Payer Leverage & Revenue Left on Table RLOT API",
        "short_description": "Compare a medical group or ASC's contracted CPT/APC fee schedule against regional peer EIN/NPI groups in the same MSA using CMS TiC MRF files to quantify annual RLOT.",
        "category": "Data",
        "method": "POST",
        "route": "/v1/analyze/planholder-competitor-spread",
        "operation_name": "Analyze Specialty Group EIN/NPI Payer Leverage & RLOT",
        "operation_id": "analyzeSpecialtyGroupPayerRlot",
        "accent_rgb": (5, 150, 105),
        "sample_request": {
            "project_id": "TXDOI-MRF-CPT-29881-DFW",
            "engineers_estimate_usd": 2450000,
        },
        "request_properties": {
            "project_id": {"type": "string", "description": "Regional Market MRF Cohort ID.", "default": "TXDOI-MRF-CPT-29881-DFW"},
            "engineers_estimate_usd": {"type": "number", "description": "Annual cohort commercial revenue at 75th-percentile regional MRF benchmark in USD.", "default": 2450000},
        },
        "required_fields": ["project_id", "engineers_estimate_usd"],
    },
    {
        "num": "12",
        "slug": "subcontractor-scope-itb-aia-a401-generator",
        "title": "Managed Care Payer Contract Redline & Rate-Escalator Term Sheet API",
        "short_description": "Generate managed care payer contract redlines, anti-downcoding covenants, ASC implant pass-through carve-outs, and CPI-U annual rate-escalator term sheets.",
        "category": "Business",
        "method": "POST",
        "route": "/v1/generate/subcontractor-scope-itb",
        "operation_name": "Generate Managed Care Payer Contract Redline & Term Sheet",
        "operation_id": "generateManagedCareContractRedline",
        "accent_rgb": (4, 120, 87),
        "sample_request": {
            "project_id": "TXDOI-MRF-CPT-29881-DFW",
            "trade_package": "Commercial PPO / HMO & Self-Funded ASO Fee Schedule Addendum (Orthopedic & ASC Carve-Out)",
        },
        "request_properties": {
            "project_id": {"type": "string", "description": "Managed Care Contract Negotiation ID.", "default": "TXDOI-MRF-CPT-29881-DFW"},
            "trade_package": {"type": "string", "description": "Target payer contract line of business and specialty schedule.", "default": "Commercial PPO / HMO & Self-Funded ASO Fee Schedule Addendum"},
        },
        "required_fields": ["project_id", "trade_package"],
    },
]


def _render_symbol07_png(path: Path, accent_rgb: Tuple[int, int, int], badge_num: str) -> None:
    """
    Renders a crisp 500x500 RGB PNG featuring the Split Shield & Ledger M7 mark
    on Warm Vellum (#FAF8F5) with Deep Obsidian Ink (#0A0D14) and Surgical Emerald (#059669).
    Zero external image library required.
    """
    width, height = 500, 500
    vellum = (250, 248, 245)      # #FAF8F5
    obsidian = (10, 13, 20)       # #0A0D14
    border_col = (214, 211, 205)  # #D6D3CD

    rows: List[bytes] = []
    sq_x1, sq_y1 = 266, 98
    sq_x2, sq_y2 = 392, 296
    sq_r = 14

    for y in range(height):
        row = bytearray(1 + width * 3)
        row[0] = 0
        for x in range(width):
            if (x in (24, 25, 474, 475) and 24 <= y <= 475) or (y in (24, 25, 474, 475) and 24 <= x <= 475):
                r, g, b = border_col
            elif 26 <= x <= 473 and 26 <= y <= 36:
                r, g, b = accent_rgb
            else:
                r, g, b = vellum
                in_sq = False
                if sq_x1 <= x <= sq_x2 and sq_y1 <= y <= sq_y2:
                    in_sq = True
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
                elif 94 <= x <= 250 and 78 <= y <= 422 and (y <= 172 or x >= 94.0 + 156.0 * (((y - 172.0) / 250.0) ** 1.85)):
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
                    "description": "Successful structured healthcare payer MRF & IDR JSON response",
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
                    "description": "Successful structured healthcare payer MRF & IDR JSON response",
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
    sample_json = json.dumps(api["sample_request"], indent=2)
    return f"""# {api['title']}

**By RubricWard Commercial Payer MRF, ERISA Appeal & NSA IDR Systems** (`https://rubricward.com`)

{api['short_description']}

---

## Key Capabilities & Healthcare Revenue Cycle Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes commercial payer Clinical Policy Bulletins, CMS TiC MRF CPT/DRG rate cohorts, Medicare MPFS RVU/GPCI baselines, and X12 835 remittances in memory.
- **Built for Healthcare RCM Platforms, Specialty Physician Groups, ASCs & ERISA Appeal Attorneys:** Ready to plug into Epic, Athenahealth, Waystar, or AI revenue cycle agents via `@rubricward/mcp-server`.
- **Route:** `{api['method']} {api['route']}`

---

## Example Request Payload

```json
{sample_json}
```

---

## Pricing Tiers
- **BASIC (`$0 / mo`):** `10 requests / month` hard limit (`10 requests / hour` rate limit) for testing and evaluation.
- **PRO (`$49 / mo`):** `200 requests / month` for specialty physician groups and ASC billing teams.
- **ULTRA (`$149 / mo` — Recommended):** `1,000 requests / month` for multi-specialty groups, RCM billing companies, and NSA IDR arbitration desks.
- **MEGA (`$399 / mo`):** `4,000 requests / month` for hospital health systems, healthcare fintech platforms, and ERISA litigation firms.
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
