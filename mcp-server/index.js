#!/usr/bin/env node
/**
 * @rubricward/mcp-server — Official STDIO Model Context Protocol (MCP) Server
 * 12 Commercial Payer TiC MRF, Medicare MPFS RVU/GPCI, ERISA Appeal & Federal NSA IDR Tools (5/5 Glama TDQS Compliant)
 */

const BASE_URL = process.env.RUBRICWARD_API_URL || "https://rubricward.com";
const API_KEY = process.env.RUBRICWARD_API_KEY || process.env.RAPIDAPI_KEY || "";

const ENDPOINT_MAP = {
  shred_payer_cpb_lcd_medical_policy: "/v1/shred/cpb-lcd-medical-policy",
  model_tic_payer_mrf_negotiated_rates: "/v1/model/tic-payer-mrf-rates",
  calculate_medicare_mpfs_rvu_gpci: "/v1/calculate/medicare-mpfs-rvu-gpci",
  get_live_payer_mrf_rate_disparities: "/v1/mrf-disparities/live",
  scrub_ncci_ptp_mue_modifier_25_59: "/v1/scrub/ncci-ptp-mue-modifiers",
  generate_nsa_idr_erisa_appeal_brief: "/v1/synthesize/nsa-idr-erisa-appeal",
  reconcile_hipaa_835_era_remittance: "/v1/reconcile/hipaa-835-era-remittance",
  audit_caqh_pecos_nppes_credentialing: "/v1/audit/caqh-pecos-credentialing",
  generate_nsa_good_faith_estimate_gfe: "/v1/estimate/gfe-advanced-eob",
  screen_oig_leie_stark_aks_compliance: "/v1/screen/oig-leie-stark-aks",
  analyze_ein_npi_payer_rate_spread: "/v1/benchmark/ein-npi-payer-spread",
  generate_payer_contract_redline_demand: "/v1/generate/payer-contract-redline",
};

const TOOLS = [
  {
    "name": "shred_payer_cpb_lcd_medical_policy",
    "title": "Payer CPB & CMS LCD Medical Policy Shredder",
    "description": "Shred commercial payer Clinical Policy Bulletins (CPBs), CMS Local Coverage Determinations (LCDs/NCDs), and prior-authorization denial notices into structured ICD-10/CPT medical necessity criteria, conservative therapy duration thresholds, and ERISA 29 CFR 2560.503-1 clinical appeal checklists. Stateless, read-only, non-destructive execution with a 100 KB payload cap. Use this tool when parsing unstructured clinical coverage policies or prior-auth denials; use generate_nsa_idr_erisa_appeal_brief instead when synthesizing a formal ERISA or Federal NSA IDR legal brief.",
    "annotations": {
      "title": "Payer CPB & CMS LCD Medical Policy Shredder",
      "readOnlyHint": true,
      "destructiveHint": false,
      "idempotentHint": true,
      "openWorldHint": false
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
      "readOnlyHint": true,
      "destructiveHint": false,
      "idempotentHint": true,
      "openWorldHint": false
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
      "readOnlyHint": true,
      "destructiveHint": false,
      "idempotentHint": true,
      "openWorldHint": false
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
      "readOnlyHint": true,
      "destructiveHint": false,
      "idempotentHint": true,
      "openWorldHint": true
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
      "readOnlyHint": true,
      "destructiveHint": false,
      "idempotentHint": true,
      "openWorldHint": false
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
      "readOnlyHint": true,
      "destructiveHint": false,
      "idempotentHint": true,
      "openWorldHint": false
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
      "readOnlyHint": true,
      "destructiveHint": false,
      "idempotentHint": true,
      "openWorldHint": false
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
      "readOnlyHint": true,
      "destructiveHint": false,
      "idempotentHint": true,
      "openWorldHint": false
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
      "readOnlyHint": true,
      "destructiveHint": false,
      "idempotentHint": true,
      "openWorldHint": false
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
      "readOnlyHint": true,
      "destructiveHint": false,
      "idempotentHint": true,
      "openWorldHint": false
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
      "readOnlyHint": true,
      "destructiveHint": false,
      "idempotentHint": true,
      "openWorldHint": false
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
      "readOnlyHint": true,
      "destructiveHint": false,
      "idempotentHint": true,
      "openWorldHint": false
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
];

async function executeTool(name, args) {
  const route = ENDPOINT_MAP[name];
  if (!route) {
    throw new Error(`Unknown RubricWard MCP tool: ${name}`);
  }
  const isGet = route === "/v1/mrf-disparities/live" || route === "/v1/lettings/live";
  const url = new URL(route, BASE_URL);
  if (isGet && args) {
    if (args.state) url.searchParams.set("state", String(args.state));
    if (args.limit) url.searchParams.set("limit", String(args.limit));
  }
  const headers = { "Content-Type": "application/json" };
  if (API_KEY) {
    headers["X-RubricWard-Key"] = API_KEY;
    headers["X-RapidAPI-Key"] = API_KEY;
  }
  const resp = await fetch(url.toString(), {
    method: isGet ? "GET" : "POST",
    headers,
    body: isGet ? undefined : JSON.stringify(args || {}),
  });
  const data = await resp.json();
  return {
    content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    structuredContent: data,
    isError: !resp.ok,
  };
}

process.stdin.setEncoding("utf8");
let buffer = "";
process.stdin.on("data", async (chunk) => {
  buffer += chunk;
  const lines = buffer.split("\n");
  buffer = lines.pop() || "";
  for (const line of lines) {
    if (!line.trim()) continue;
    try {
      const req = JSON.parse(line);
      const id = req.id !== undefined ? req.id : null;
      if (req.method === "initialize") {
        process.stdout.write(JSON.stringify({
          jsonrpc: "2.0",
          id,
          result: {
            protocolVersion: "2025-06-18",
            capabilities: { tools: { listChanged: false } },
            serverInfo: { name: "@rubricward/mcp-server", version: "1.0.0" },
          },
        }) + "\n");
      } else if (req.method === "tools/list") {
        process.stdout.write(JSON.stringify({
          jsonrpc: "2.0",
          id,
          result: { tools: TOOLS },
        }) + "\n");
      } else if (req.method === "tools/call") {
        const res = await executeTool(req.params?.name, req.params?.arguments || {});
        process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id, result: res }) + "\n");
      }
    } catch (err) {
      process.stdout.write(JSON.stringify({
        jsonrpc: "2.0",
        id: null,
        error: { code: -32603, message: String(err.message || err) },
      }) + "\n");
    }
  }
});
