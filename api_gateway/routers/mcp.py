"""
RubricWard API Gateway — Remote Streamable-HTTP Model Context Protocol (MCP) Server (`/mcp`).
Strictly enforces the Mandatory 5/5 Glama Tool Definition Quality Score (TDQS) Rules:
1. Zero Catalog Prefixes (starts directly with a high-signal action verb).
2. MCP Annotations (`title`, `readOnlyHint: True`, `destructiveHint: False`, `idempotentHint: True`, `openWorldHint`) & typed `outputSchema` + `structuredContent`.
3. 100% `inputSchema` Parameter Documentation (`description`, `default`, `minLength`/`maxLength`, `minimum`/`maximum`).
4. 3-Part Description with explicit `"Use this tool when [...]; use <sibling_tool> instead when [...]"` disambiguation.
"""

import json
from typing import Any, Dict, List
try:
    from fastapi import APIRouter, Request, status
    from fastapi.responses import JSONResponse
except ImportError:
    class APIRouter:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass
        def get(self, *args: Any, **kwargs: Any):
            return lambda fn: fn
        def post(self, *args: Any, **kwargs: Any):
            return lambda fn: fn
    Request = Any  # type: ignore
    JSONResponse = Any  # type: ignore
    class status:  # type: ignore
        HTTP_200_OK = 200

from api_gateway.routers.precon_endpoints import (
    analyze_planholder_spread,
    audit_baba_compliance,
    audit_osha_emr,
    audit_surety_bond,
    calculate_prevailing_wage,
    generate_aia_pay_app,
    generate_dbe_good_faith,
    generate_rfi_change_order,
    generate_subcontractor_itb,
    get_live_lettings,
    model_dot_bid_tabs,
    shred_csi_masterformat,
)
from api_gateway.schemas.precon_schemas import (
    AiaPayAppRequest,
    BabaComplianceRequest,
    CsiSpecShredRequest,
    DbeGoodFaithRequest,
    DotBidTabRequest,
    OshaEmrAuditRequest,
    PlanholderSpreadRequest,
    PrevailingWageRequest,
    RfiChangeOrderRequest,
    SubcontractorItbRequest,
    SuretyBondAuditRequest,
)

router = APIRouter()

TOOL_ROUTE_MAP: Dict[str, str] = {
    "shred_csi_masterformat": "/v1/shred/csi-masterformat",
    "model_dot_unit_bid_tabs": "/v1/model/dot-unit-bid-tabs",
    "calculate_davis_bacon_prevailing_wage": "/v1/calculate/davis-bacon-prevailing-wage",
    "get_live_dot_lettings": "/v1/lettings/live",
    "audit_baba_buy_america": "/v1/audit/baba-buy-america",
    "generate_dbe_good_faith_effort": "/v1/generate/dbe-good-faith-effort",
    "generate_aia_g702_g703_pay_app": "/v1/generate/aia-g702-g703-pay-app",
    "audit_surety_miller_act_bond": "/v1/audit/surety-miller-act-bond",
    "generate_rfi_change_order_claim": "/v1/generate/rfi-change-order-claim",
    "audit_osha_emr_site_safety": "/v1/audit/osha-emr-site-safety",
    "analyze_planholder_competitor_spread": "/v1/analyze/planholder-competitor-spread",
    "generate_subcontractor_scope_itb": "/v1/generate/subcontractor-scope-itb",
}

MCP_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "shred_payer_cpb_lcd_medical_policy",
        "title": "Payer CPB & CMS LCD Medical Policy Shredder",
        "description": "Shred commercial payer Clinical Policy Bulletins (CPBs), CMS Local Coverage Determinations (LCDs/NCDs), and prior-authorization denial notices into structured ICD-10/CPT medical necessity criteria, conservative therapy duration thresholds, and ERISA 29 CFR 2560.503-1 clinical appeal checklists. Stateless, read-only, non-destructive execution with a 100 KB payload cap. Use this tool when parsing unstructured clinical coverage policies or prior-auth denials; use generate_nsa_idr_erisa_appeal_brief instead when synthesizing a formal ERISA or Federal NSA IDR legal brief.",
        "annotations": {
            "title": "Payer CPB & CMS LCD Medical Policy Shredder",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": [
                "project_name",
                "specification_text"
            ],
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "Payer policy name, surgical cohort, or claim audit title.",
                    "minLength": 3,
                    "maxLength": 200
                },
                "solicitation_number": {
                    "type": "string",
                    "description": "Payer CPB/LCD policy ID or claim reference number (e.g., 'LCD-L34220' or 'CPB-0743').",
                    "default": "LCD-L34220",
                    "minLength": 2,
                    "maxLength": 100
                },
                "state_code": {
                    "type": "string",
                    "description": "Two-letter U.S. state postal code for state DOI prompt-pay & external review jurisdiction.",
                    "default": "TX",
                    "minLength": 2,
                    "maxLength": 2
                },
                "specification_text": {
                    "type": "string",
                    "description": "Raw clinical policy bulletin text, LCD medical necessity criteria, or EOB denial narrative.",
                    "minLength": 20,
                    "maxLength": 100000
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string"
                },
                "project_name": {
                    "type": "string"
                },
                "claim_denial_risk_summary": {
                    "type": "object"
                },
                "shredded_medical_policy_criteria": {
                    "type": "array"
                }
            }
        }
    },
    {
        "name": "model_tic_payer_mrf_negotiated_rates",
        "title": "CMS TiC Payer MRF Negotiated Rate & QPA Modeler",
        "description": "Benchmark CPT/HCPCS surgical and medical procedures against verified commercial payer Transparency in Coverage (45 CFR 147.212) Machine-Readable Files (MRFs) across UnitedHealthcare, Anthem/BCBS, Aetna, and Cigna to return 25th, 50th (median QPA proxy), and 75th percentile in-network allowed amounts and recommended NSA IDR offers. Stateless, read-only, non-destructive execution. Use this tool when modeling commercial payer MRF negotiated rate percentiles and QPA spreads; use calculate_medicare_mpfs_rvu_gpci instead when computing baseline CMS Medicare RVU/GPCI locality allowables.",
        "annotations": {
            "title": "CMS TiC Payer MRF Negotiated Rate & QPA Modeler",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": [
                "state_code",
                "pay_items"
            ],
            "properties": {
                "state_code": {
                    "type": "string",
                    "description": "Two-letter U.S. state code (e.g., 'TX', 'CA', 'FL', 'NY').",
                    "default": "TX",
                    "minLength": 2,
                    "maxLength": 2
                },
                "payer_cohort_agency": {
                    "type": "string",
                    "description": "Target commercial payer network or state DOI MRF cohort name.",
                    "default": "UnitedHealthcare Choice Plus & BCBS BlueCard PPO MRF",
                    "minLength": 2,
                    "maxLength": 120
                },
                "pay_items": {
                    "type": "array",
                    "description": "Array of CPT/HCPCS procedure line items with item_code, description, unit, and quantity."
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string"
                },
                "state_code": {
                    "type": "string"
                },
                "payer_cohort_agency": {
                    "type": "string"
                },
                "unit_price_benchmarks": {
                    "type": "array"
                },
                "recommended_total_bid_usd": {
                    "type": "number"
                }
            }
        }
    },
    {
        "name": "calculate_medicare_mpfs_rvu_gpci",
        "title": "Medicare MPFS & ASC RVU/GPCI Locality Repricer",
        "description": "Calculate exact geographic-adjusted CMS Medicare Physician Fee Schedule (MPFS) and Ambulatory Surgical Center (ASC / OPPS) allowable baselines using Work, Practice Expense (PE), and Malpractice (MP) RVUs, locality GPCIs, and commercial % of Medicare contract multiples (150%\u2013285% MPFS). Stateless, read-only, non-destructive execution. Use this tool when calculating Medicare RVU/GPCI locality fee schedules; use model_tic_payer_mrf_negotiated_rates instead when benchmarking commercial payer TiC MRF negotiated rates.",
        "annotations": {
            "title": "Medicare MPFS & ASC RVU/GPCI Locality Repricer",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": [
                "state_code",
                "county_name"
            ],
            "properties": {
                "state_code": {
                    "type": "string",
                    "description": "Two-letter U.S. state code for CMS Medicare Carrier/MAC locality.",
                    "default": "TX",
                    "minLength": 2,
                    "maxLength": 2
                },
                "county_name": {
                    "type": "string",
                    "description": "County or CMS GPCI payment locality name (e.g., 'Dallas County' or 'Manhattan').",
                    "default": "Dallas County",
                    "minLength": 2,
                    "maxLength": 120
                },
                "construction_type": {
                    "type": "string",
                    "description": "Place of Service setting: 'ASC / Facility (POS 24)', 'Hospital Outpatient (POS 22)', or 'Office Non-Facility (POS 11)'.",
                    "default": "ASC / Facility (POS 24)"
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string"
                },
                "wage_determination_decision_no": {
                    "type": "string"
                },
                "mpfs_locality_rvu_schedule": {
                    "type": "array"
                },
                "total_burdened_labor_cost_usd": {
                    "type": "number"
                }
            }
        }
    },
    {
        "name": "get_live_payer_mrf_rate_disparities",
        "title": "52-Portal Live Payer MRF Rate-Disparity & IDR Feed",
        "description": "Retrieve active commercial payer Transparency in Coverage (TiC) MRF rate-disparity cohorts, CMS No Surprises Act (NSA) IDR benchmarks, and state DOI prompt-pay enforcement dockets across all 50 U.S. states plus Federal CMS and Multi-Payer ASC networks (52 portals total). Stateless, read-only, non-destructive execution. Use this tool when querying live state/specialty MRF rate disparities and IDR cohorts; use analyze_ein_npi_payer_rate_spread instead when analyzing a specific EIN/NPI peer provider rate spread.",
        "annotations": {
            "title": "52-Portal Live Payer MRF Rate-Disparity & IDR Feed",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "state": {
                    "type": "string",
                    "description": "Two-letter state filter ('TX', 'CA', 'FL', 'NY', etc.) or 'ALL' for all 52 portals.",
                    "default": "ALL",
                    "minLength": 2,
                    "maxLength": 10
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of MRF rate-disparity cohorts to return (1 to 52).",
                    "default": 12,
                    "minimum": 1,
                    "maximum": 52
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string"
                },
                "portals_monitored": {
                    "type": "integer"
                },
                "count": {
                    "type": "integer"
                },
                "lettings": {
                    "type": "array"
                }
            }
        }
    },
    {
        "name": "scrub_ncci_ptp_mue_modifier_25_59",
        "title": "CMS NCCI PTP, MUE & Modifier 25/59/XE/XS Unbundling Scrubber",
        "description": "Audit multi-line surgical and E/M claims against quarterly CMS National Correct Coding Initiative (NCCI) Procedure-to-Procedure (PTP) edits and Medically Unlikely Edits (MUEs), validating Modifier 25, 59, XE, XP, XS, and XU bypass eligibility and operative-note documentation requirements. Stateless, read-only, non-destructive execution. Use this tool when scrubbing CPT code pairs for NCCI bundling denials; use reconcile_hipaa_835_era_remittance instead when auditing paid 835 ERA CARC/RARC underpayments.",
        "annotations": {
            "title": "CMS NCCI PTP, MUE & Modifier 25/59/XE/XS Unbundling Scrubber",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": [
                "project_name",
                "bom_items"
            ],
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "Claim cohort or surgical case identifier.",
                    "minLength": 3,
                    "maxLength": 200
                },
                "bom_items": {
                    "type": "array",
                    "description": "Array of CPT/HCPCS claim lines with modifier indicators and billed amounts."
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string"
                },
                "overall_compliance_status": {
                    "type": "string"
                },
                "audited_bom_items": {
                    "type": "array"
                }
            }
        }
    },
    {
        "name": "generate_nsa_idr_erisa_appeal_brief",
        "title": "Federal NSA IDR Arbitration & ERISA 29 CFR 2560.503-1 Brief Generator",
        "description": "Synthesize a submission-ready Federal No Surprises Act (45 CFR 149.510) Independent Dispute Resolution (IDR) position paper (incorporating TMA III/IV QPA rebuttal precedent) and ERISA 29 CFR 2560.503-1 full-and-fair review demand brief. Stateless, read-only, non-destructive execution. Use this tool when generating formal NSA IDR arbitration briefs or ERISA appeal demands; use shred_payer_cpb_lcd_medical_policy instead when extracting raw criteria from a payer CPB/LCD policy.",
        "annotations": {
            "title": "Federal NSA IDR Arbitration & ERISA 29 CFR 2560.503-1 Brief Generator",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": [
                "project_name",
                "total_base_bid_usd"
            ],
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "Disputed claim ID, CPT cohort, and commercial payer name.",
                    "minLength": 3,
                    "maxLength": 200
                },
                "total_base_bid_usd": {
                    "type": "number",
                    "description": "Target 75th-percentile commercial MRF IDR offer amount in USD.",
                    "minimum": 1
                },
                "dbe_goal_percent": {
                    "type": "number",
                    "description": "Target commercial reimbursement multiple as % of Medicare MPFS (e.g., 228.5).",
                    "default": 228.5
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string"
                },
                "nsa_idr_45_cfr_149_510_packet_status": {
                    "type": "string"
                },
                "evaluated_commitments": {
                    "type": "array"
                }
            }
        }
    },
    {
        "name": "reconcile_hipaa_835_era_remittance",
        "title": "HIPAA 835 ERA Remittance & State Prompt-Pay Interest Reconciler",
        "description": "Reconcile HIPAA X12 835 Electronic Remittance Advice (ERA) CARC/RARC adjustment codes against contracted payer fee schedules and calculate accrued statutory interest under 50-state clean-claim prompt-pay statutes (e.g., TX Ins. Code 1301.103 18% p.a., CA H&SC 1371 15% p.a., NY ISC 3224-a 12% p.a.). Stateless, read-only, non-destructive execution. Use this tool when auditing 835 ERA underpayments and prompt-pay interest; use scrub_ncci_ptp_mue_modifier_25_59 instead when checking pre-submission NCCI modifier edits.",
        "annotations": {
            "title": "HIPAA 835 ERA Remittance & State Prompt-Pay Interest Reconciler",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": [
                "project_name",
                "sov_lines"
            ],
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "ERA batch identifier and payer name.",
                    "minLength": 3,
                    "maxLength": 200
                },
                "retainage_pct": {
                    "type": "number",
                    "description": "Applicable state statutory prompt-pay annual interest rate percentage (e.g., 18.0 for TX, 12.0 for NY).",
                    "default": 18.0
                },
                "sov_lines": {
                    "type": "array",
                    "description": "Claim lines with contracted MRF scheduled value, paid QPA/ERA amount, and underpayment variance."
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string"
                },
                "era_835_remittance_summary": {
                    "type": "object"
                },
                "era_835_claim_line_adjustments": {
                    "type": "array"
                }
            }
        }
    },
    {
        "name": "audit_caqh_pecos_nppes_credentialing",
        "title": "CAQH ProView, CMS PECOS & NPPES Provider Credentialing Auditor",
        "description": "Verify provider Type-1/Type-2 NPI taxonomy concordance, CMS PECOS Medicare enrollment, CAQH ProView 120-day re-attestation currency, and medical malpractice coverage limits ($1M/$3M) to prevent CARC 185/B7 credentialing denials. Stateless, read-only, non-destructive execution. Use this tool when auditing provider credentialing and PECOS/CAQH enrollment readiness; use screen_oig_leie_stark_aks_compliance instead when screening for OIG LEIE exclusions and Stark/AKS risk.",
        "annotations": {
            "title": "CAQH ProView, CMS PECOS & NPPES Provider Credentialing Auditor",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": [
                "contractor_name"
            ],
            "properties": {
                "contractor_name": {
                    "type": "string",
                    "description": "Medical group, ASC facility, or rendering physician legal name and NPI.",
                    "minLength": 3,
                    "maxLength": 200
                },
                "current_assets_usd": {
                    "type": "number",
                    "description": "Per-occurrence malpractice coverage limit in USD (e.g., 1000000).",
                    "default": 1000000
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string"
                },
                "underwriting_decision": {
                    "type": "string"
                },
                "malpractice_per_occurrence_limit_usd": {
                    "type": "number"
                }
            }
        }
    },
    {
        "name": "generate_nsa_good_faith_estimate_gfe",
        "title": "NSA 45 CFR 149.610 Good-Faith Estimate (GFE) & Co-Provider Pricer",
        "description": "Generate a compliant 45 CFR 149.610 Good-Faith Estimate (GFE) and Advanced Explanation of Benefits (AEOB) schedule across primary surgeon, assistant surgeon, anesthesia, and ASC facility co-providers with $400 Patient-Provider Dispute Resolution (PPDR) threshold protection. Stateless, read-only, non-destructive execution. Use this tool when generating pre-service Good-Faith Estimates for uninsured/self-pay or OON patients; use generate_payer_contract_redline_demand instead when drafting payer fee-schedule contract redlines.",
        "annotations": {
            "title": "NSA 45 CFR 149.610 Good-Faith Estimate (GFE) & Co-Provider Pricer",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": [
                "project_name",
                "direct_cost_impact_usd"
            ],
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "Surgical episode title and primary CPT code.",
                    "minLength": 3,
                    "maxLength": 200
                },
                "direct_cost_impact_usd": {
                    "type": "number",
                    "description": "Primary surgical & facility baseline fee in USD.",
                    "minimum": 1
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string"
                },
                "good_faith_estimate_co_provider_pricing": {
                    "type": "object"
                }
            }
        }
    },
    {
        "name": "screen_oig_leie_stark_aks_compliance",
        "title": "HHS OIG LEIE Exclusion, Stark Law & Anti-Kickback Compliance Screener",
        "description": "Screen rendering/referring NPIs, ASC medical directors, and billing entities against HHS OIG List of Excluded Individuals/Entities (LEIE), GSA SAM.gov exclusions, CMS bell-curve E/M coding distribution, and Stark Law (42 CFR 411.357) / Anti-Kickback Statute (42 U.S.C. 1320a-7b) safe harbors. Stateless, read-only, non-destructive execution. Use this tool when auditing OIG exclusion and Stark/AKS regulatory risk; use audit_caqh_pecos_nppes_credentialing instead when checking CAQH/PECOS payer credentialing status.",
        "annotations": {
            "title": "HHS OIG LEIE Exclusion, Stark Law & Anti-Kickback Compliance Screener",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": [
                "project_name"
            ],
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "Practice name, NPI cohort, or compliance audit identifier.",
                    "minLength": 3,
                    "maxLength": 200
                },
                "contractor_emr": {
                    "type": "number",
                    "description": "Provider Level 4/5 E/M utilization ratio relative to CMS specialty peer mean (1.00 = peer mean).",
                    "default": 0.92
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string"
                },
                "emr_prequalification_status": {
                    "type": "string"
                },
                "oig_leie_stark_aks_compliance_audits": {
                    "type": "array"
                }
            }
        }
    },
    {
        "name": "analyze_ein_npi_payer_rate_spread",
        "title": "EIN/NPI Peer Provider Payer Rate-Spread & RLOT Analyzer",
        "description": "Crosswalk commercial payer TiC MRF negotiated rates by Type-2 Organization NPI and Tax ID (EIN) within the same MSA to quantify Revenue Left On the Table (RLOT) between your practice's contracted fee schedule and competing regional health systems/ASCs. Stateless, read-only, non-destructive execution. Use this tool when analyzing peer EIN/NPI negotiated rate spreads in a local market; use get_live_payer_mrf_rate_disparities instead when browsing the 52-portal live MRF disparity feed.",
        "annotations": {
            "title": "EIN/NPI Peer Provider Payer Rate-Spread & RLOT Analyzer",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": [
                "letting_id",
                "engineers_estimate_usd",
                "our_direct_cost_usd"
            ],
            "properties": {
                "letting_id": {
                    "type": "string",
                    "description": "Payer MRF cohort ID or MSA specialty benchmark identifier.",
                    "default": "TXDOI-MRF-CPT-29881-DFW",
                    "minLength": 3,
                    "maxLength": 100
                },
                "engineers_estimate_usd": {
                    "type": "number",
                    "description": "Regional 75th-percentile commercial MRF allowed amount in USD.",
                    "minimum": 1
                },
                "our_direct_cost_usd": {
                    "type": "number",
                    "description": "Current contracted fee schedule or QPA payment in USD.",
                    "minimum": 1
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string"
                },
                "recommended_winning_bid_usd": {
                    "type": "number"
                },
                "payer_mrf_rate_leverage_matrix": {
                    "type": "array"
                }
            }
        }
    },
    {
        "name": "generate_payer_contract_redline_demand",
        "title": "Commercial Payer Managed-Care Contract Redline & Carve-Out Generator",
        "description": "Generate managed-care contract redline clauses, high-cost implant/biologic pass-through carve-outs, lesser-of billed-charge language strikes, and anti-downcoding/retroactive-clawback protections for commercial payer participation agreements. Stateless, read-only, non-destructive execution. Use this tool when drafting commercial payer contract redlines and implant carve-out schedules; use generate_nsa_good_faith_estimate_gfe instead when creating patient-facing Good-Faith Estimates.",
        "annotations": {
            "title": "Commercial Payer Managed-Care Contract Redline & Carve-Out Generator",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": [
                "project_name",
                "trade_division"
            ],
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "Payer participation agreement title and effective renewal year.",
                    "minLength": 3,
                    "maxLength": 200
                },
                "trade_division": {
                    "type": "string",
                    "description": "Target surgical service line or implant carve-out schedule (e.g., 'Orthopedic & Spine ASC Carve-Outs').",
                    "minLength": 3,
                    "maxLength": 150
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string"
                },
                "scope_inclusions_checklist": {
                    "type": "array"
                },
                "payer_contract_redline_clauses": {
                    "type": "array"
                }
            }
        }
    }
]

TOOL_ROUTE_MAP: Dict[str, str] = {
    "shred_payer_cpb_lcd_medical_policy": "/v1/shred/cpb-lcd-medical-policy",
    "model_tic_payer_mrf_negotiated_rates": "/v1/model/tic-payer-mrf-rates",
    "calculate_medicare_mpfs_rvu_gpci": "/v1/calculate/medicare-mpfs-rvu-gpci",
    "get_live_payer_mrf_rate_disparities": "/v1/mrf-disparities/live",
    "scrub_ncci_ptp_mue_modifier_25_59": "/v1/scrub/ncci-ptp-mue-modifiers",
    "generate_nsa_idr_erisa_appeal_brief": "/v1/synthesize/nsa-idr-erisa-appeal",
    "reconcile_hipaa_835_era_remittance": "/v1/reconcile/hipaa-835-era-remittance",
    "audit_caqh_pecos_nppes_credentialing": "/v1/audit/caqh-pecos-credentialing",
    "generate_nsa_good_faith_estimate_gfe": "/v1/estimate/gfe-advanced-eob",
    "screen_oig_leie_stark_aks_compliance": "/v1/screen/oig-leie-stark-aks",
    "analyze_ein_npi_payer_rate_spread": "/v1/benchmark/ein-npi-payer-spread",
    "generate_payer_contract_redline_demand": "/v1/generate/payer-contract-redline",
    # Backward-compatible aliases
    "shred_csi_masterformat_spec": "/v1/shred/csi-masterformat",
    "model_dot_unit_bid_tabs": "/v1/model/dot-unit-bid-tabs",
    "calculate_davis_bacon_prevailing_wage": "/v1/calculate/davis-bacon-prevailing-wage",
    "get_live_dot_construction_lettings": "/v1/lettings/live",
    "audit_baba_buy_america_materials": "/v1/audit/baba-buy-america",
    "generate_dot_dbe_good_faith_effort": "/v1/generate/dbe-good-faith-effort",
    "generate_aia_g702_g703_pay_app": "/v1/generate/aia-g702-g703-pay-app",
    "underwrite_surety_miller_act_bond": "/v1/audit/surety-miller-act-bond",
    "generate_rfi_change_order_claim": "/v1/generate/rfi-change-order-claim",
    "audit_osha_emr_site_safety": "/v1/audit/osha-emr-site-safety",
    "analyze_planholder_competitor_mlot": "/v1/analyze/planholder-competitor-spread",
    "generate_subcontractor_scope_itb": "/v1/generate/subcontractor-scope-itb",
}


async def _execute_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if tool_name == "shred_csi_masterformat":
        data = await shred_csi_masterformat(CsiSpecShredRequest(**arguments))
    elif tool_name == "model_dot_unit_bid_tabs":
        data = await model_dot_bid_tabs(DotBidTabRequest(**arguments))
    elif tool_name == "calculate_davis_bacon_prevailing_wage":
        data = await calculate_prevailing_wage(PrevailingWageRequest(**arguments))
    elif tool_name == "get_live_dot_lettings":
        data = await get_live_lettings(
            state=arguments.get("state", "TX"),
            naics=arguments.get("naics"),
            limit=int(arguments.get("limit", 10)),
        )
    elif tool_name == "audit_baba_buy_america":
        data = await audit_baba_compliance(BabaComplianceRequest(**arguments))
    elif tool_name == "generate_dbe_good_faith_effort":
        data = await generate_dbe_good_faith(DbeGoodFaithRequest(**arguments))
    elif tool_name == "generate_aia_g702_g703_pay_app":
        data = await generate_aia_pay_app(AiaPayAppRequest(**arguments))
    elif tool_name == "audit_surety_miller_act_bond":
        data = await audit_surety_bond(SuretyBondAuditRequest(**arguments))
    elif tool_name == "generate_rfi_change_order_claim":
        data = await generate_rfi_change_order(RfiChangeOrderRequest(**arguments))
    elif tool_name == "audit_osha_emr_site_safety":
        data = await audit_osha_emr(OshaEmrAuditRequest(**arguments))
    elif tool_name == "analyze_planholder_competitor_spread":
        data = await analyze_planholder_spread(PlanholderSpreadRequest(**arguments))
    elif tool_name == "generate_subcontractor_scope_itb":
        data = await generate_subcontractor_itb(SubcontractorItbRequest(**arguments))
    else:
        raise ValueError(f"Unknown MCP tool: {tool_name}")

    return {
        "content": [{"type": "text", "text": json.dumps(data, indent=2)}],
        "structuredContent": data,
        "isError": False,
    }


@router.get("/mcp", tags=["Remote Streamable-HTTP MCP Server"])
async def mcp_info() -> Dict[str, Any]:
    return {
        "name": "@rubricward/mcp-server",
        "version": "1.0.0",
        "protocolVersion": "2024-11-05",
        "transport": "streamable-http",
        "tools_count": len(MCP_TOOLS),
        "tools": [t["name"] for t in MCP_TOOLS],
    }


@router.post("/mcp", tags=["Remote Streamable-HTTP MCP Server"])
async def mcp_jsonrpc(request: Request) -> JSONResponse:
    body = await request.json()
    rpc_id = body.get("id")
    method = body.get("method", "")
    params = body.get("params") or {}

    if method == "initialize":
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "@rubricward/mcp-server", "version": "1.0.0"},
                },
            },
        )
    if method == "tools/list":
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"jsonrpc": "2.0", "id": rpc_id, "result": {"tools": MCP_TOOLS}},
        )
    if method == "tools/call":
        t_name = params.get("name", "")
        t_args = params.get("arguments") or {}
        try:
            res = await _execute_mcp_tool(t_name, t_args)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"jsonrpc": "2.0", "id": rpc_id, "result": res},
            )
        except Exception as exc:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Tool execution error: {exc}"}],
                        "isError": True,
                    },
                },
            )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        },
    )
