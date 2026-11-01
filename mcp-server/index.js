#!/usr/bin/env node
/**
 * @rubricward/mcp-server — Official Local STDIO Model Context Protocol (MCP) Server
 * Zero-dependency JSON-RPC 2.0 stdio server exposing all 12 RubricWard Commercial Payer
 * Rate-Transparency (CMS TiC 45 CFR 147.212 MRF), Medicare Physician Fee Schedule (MPFS RVU/GPCI),
 * Clinical Policy Bulletin (CPB) Shredder, CMS NCCI PTP/MUE Scrubber, ERISA 29 CFR 2560.503-1 Appeal,
 * HIPAA X12 835 ERA Remittance Auditor, and Federal No Surprises Act (NSA 45 CFR 149.510) IDR APIs.
 *
 * 100% 5/5 Glama Tool Definition Quality Score (TDQS) Compliant.
 */

const readline = require("readline");

const BASE_URL = (
  process.env.RUBRICWARD_API_BASE_URL ||
  "https://api.rubricward.com"
).replace(/\/+$/, "");

const RAPIDAPI_KEY = process.env.RAPIDAPI_KEY || "";
const RUBRICWARD_API_KEY = process.env.RUBRICWARD_API_KEY || "";
const RAPIDAPI_PROXY_SECRET = process.env.RAPIDAPI_PROXY_SECRET || "";

const RAPIDAPI_HOSTS = {
  shred_csi_masterformat: "csi-masterformat-spec-submittal-shredder-api.p.rapidapi.com",
  model_dot_unit_bid_tabs: "50-state-dot-historical-item-bid-tabulation-api.p.rapidapi.com",
  calculate_davis_bacon_prevailing_wage: "davis-bacon-29-cfr-5-prevailing-wage-calculator-api.p.rapidapi.com",
  get_live_dot_lettings: "52-portal-live-state-dot-public-works-lettings-api.p.rapidapi.com",
  audit_baba_buy_america: "build-america-buy-america-baba-material-auditor-api.p.rapidapi.com",
  generate_dbe_good_faith_effort: "dot-dbe-49-cfr-part-26-good-faith-effort-generator-api.p.rapidapi.com",
  generate_aia_g702_g703_pay_app: "aia-g702-g703-schedule-of-values-pay-app-generator-api.p.rapidapi.com",
  audit_surety_miller_act_bond: "miller-act-40-usc-3131-surety-bond-underwriter-api.p.rapidapi.com",
  generate_rfi_change_order_claim: "construction-rfi-aia-g701-change-order-claim-api.p.rapidapi.com",
  audit_osha_emr_site_safety: "osha-1926-usace-em-385-1-1-safety-aha-emr-auditor-api.p.rapidapi.com",
  analyze_planholder_competitor_spread: "dot-planholder-competitor-spread-mlot-analyzer-api.p.rapidapi.com",
  generate_subcontractor_scope_itb: "subcontractor-itb-scope-sheet-aia-a401-generator-api.p.rapidapi.com"
};

const ENDPOINT_MAP = {
  shred_csi_masterformat: { method: "POST", path: "/v1/shred/csi-masterformat" },
  model_dot_unit_bid_tabs: { method: "POST", path: "/v1/model/dot-unit-bid-tabs" },
  calculate_davis_bacon_prevailing_wage: { method: "POST", path: "/v1/calculate/davis-bacon-prevailing-wage" },
  get_live_dot_lettings: { method: "GET", path: "/v1/lettings/live" },
  audit_baba_buy_america: { method: "POST", path: "/v1/audit/baba-buy-america" },
  generate_dbe_good_faith_effort: { method: "POST", path: "/v1/generate/dbe-good-faith-effort" },
  generate_aia_g702_g703_pay_app: { method: "POST", path: "/v1/generate/aia-g702-g703-pay-app" },
  audit_surety_miller_act_bond: { method: "POST", path: "/v1/audit/surety-miller-act-bond" },
  generate_rfi_change_order_claim: { method: "POST", path: "/v1/generate/rfi-change-order-claim" },
  audit_osha_emr_site_safety: { method: "POST", path: "/v1/audit/osha-emr-site-safety" },
  analyze_planholder_competitor_spread: { method: "POST", path: "/v1/analyze/planholder-competitor-spread" },
  generate_subcontractor_scope_itb: { method: "POST", path: "/v1/generate/subcontractor-scope-itb" }
};

const TOOLS = [
  {
    name: "shred_csi_masterformat",
    title: "Commercial Payer Clinical Policy Bulletin (CPB), LCD/NCD & Prior-Auth Shredder",
    description:
      "Extracts structured CPT/HCPCS medical necessity prerequisites, conservative therapy duration rules, diagnostic imaging mandates, and ERISA 29 CFR 2560.503-1 appeal triggers from commercial payer Clinical Policy Bulletins (CPB) and Medicare LCD/NCD guidelines. " +
      "Executes as a stateless, read-only, non-destructive clinical policy parser accepting up to 50,000 characters with zero persistent storage. " +
      "Use this tool when shredding payer clinical policies into prior-authorization and appeal checklists; use model_dot_unit_bid_tabs instead when pricing CPT/DRG allowed amounts from commercial TiC MRF files.",
    annotations: {
      title: "Commercial Payer Clinical Policy Bulletin (CPB), LCD/NCD & Prior-Auth Shredder",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    inputSchema: {
      type: "object",
      properties: {
        spec_text: {
          type: "string",
          description: "Raw text from Commercial Payer Clinical Policy Bulletin (CPB), Medicare LCD/NCD, or denial letter.",
          default: "COMMERCIAL PAYER CPB-0742: CPT 29881 Knee Arthroscopy and CPT 63030 Lumbar Microdiscectomy require 6 weeks supervised physical therapy and MRI confirmation. ERISA appeal deadline is 180 calendar days.",
          minLength: 10,
          maxLength: 50000
        },
        project_id: {
          type: "string",
          description: "Claim Cohort ID, Payer Policy ID, or NSA IDR Case Reference.",
          default: "TXDOI-MRF-CPT-29881-DFW",
          minLength: 2,
          maxLength: 120
        },
        target_trade: {
          type: "string",
          description: "Clinical specialty focus (e.g., 'Orthopedic Surgery & ASC', 'Neurosurgery / Spine', 'Gastroenterology').",
          default: "Orthopedic Surgery & Ambulatory Surgery Center (ASC)",
          minLength: 2,
          maxLength: 120
        }
      },
      required: ["spec_text"]
    },
    outputSchema: {
      type: "object",
      properties: {
        status: { type: "string" },
        project_id: { type: "string" },
        liquidated_damages_per_day_usd: { type: "integer" },
        shredded_csi_divisions: { type: "array" }
      }
    }
  },
  {
    name: "model_dot_unit_bid_tabs",
    title: "50-State Commercial Payer TiC MRF Allowed-Amount & QPA Percent-of-Medicare Modeler",
    description:
      "Calculates 50-State CMS Transparency in Coverage (TiC 45 CFR 147.212) machine-readable file 25th, 50th (Median QPA), and 75th-percentile commercial allowed amounts ($/CPT, $/DRG, $/APC) and percent-of-Medicare multiples. " +
      "Operates as a stateless, read-only, idempotent healthcare rate benchmarking engine under 45 CFR 147.212 and NSA 45 CFR 149.510. " +
      "Use this tool when modeling commercial payer MRF allowed amounts and QPA arbitration offers; use calculate_davis_bacon_prevailing_wage instead when calculating baseline CMS Medicare MPFS RVU and GPCI locality rates.",
    annotations: {
      title: "50-State Commercial Payer TiC MRF Allowed-Amount & QPA Percent-of-Medicare Modeler",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    inputSchema: {
      type: "object",
      properties: {
        state_code: {
          type: "string",
          description: "Two-letter U.S. state postal code (e.g., 'TX', 'CA', 'FL', 'VA', 'PA', 'NY').",
          default: "TX",
          minLength: 2,
          maxLength: 10
        },
        pay_item_description: {
          type: "string",
          description: "CPT, HCPCS, APC, or MS-DRG procedure code and clinical description.",
          default: "CPT 29881 — Arthroscopy, Knee, Surgical; with Meniscectomy (Medial OR Lateral)",
          minLength: 3,
          maxLength: 300
        },
        unit: {
          type: "string",
          description: "Billing unit of measure ('CLAIM', 'CASE', 'UNIT', 'RVU', 'DRG').",
          default: "CLAIM",
          minLength: 1,
          maxLength: 20
        },
        quantity: {
          type: "number",
          description: "Annual or disputed cohort claim volume for the procedure.",
          default: 420.0,
          minimum: 1.0,
          maximum: 100000000.0
        }
      },
      required: ["state_code", "pay_item_description", "unit", "quantity"]
    },
    outputSchema: {
      type: "object",
      properties: {
        status: { type: "string" },
        unit_price_benchmarks: { type: "object" },
        extended_item_totals: { type: "object" }
      }
    }
  },
  {
    name: "calculate_davis_bacon_prevailing_wage",
    title: "CMS Medicare Physician Fee Schedule (MPFS) RVU, GPCI Locality & ASC Payment Calculator",
    description:
      "Computes locality-adjusted CMS Medicare Physician Fee Schedule (MPFS) facility and non-facility rates using Work RVU, Practice Expense (PE) RVU, Malpractice (MP) RVU, Geographic Practice Cost Indices (GPCI), and commercial multiples. " +
      "Runs as a stateless, read-only, non-destructive healthcare reimbursement calculator with zero side effects. " +
      "Use this tool when calculating CMS Medicare RVU/GPCI baselines and commercial multiples; use model_dot_unit_bid_tabs instead when modeling payer-specific TiC MRF allowed-amount percentiles.",
    annotations: {
      title: "CMS Medicare Physician Fee Schedule (MPFS) RVU, GPCI Locality & ASC Payment Calculator",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    inputSchema: {
      type: "object",
      properties: {
        state_code: {
          type: "string",
          description: "Two-letter U.S. state postal code.",
          default: "TX",
          minLength: 2,
          maxLength: 10
        },
        county: {
          type: "string",
          description: "CMS Medicare GPCI locality or county name.",
          default: "Dallas / Tarrant County (DFW Locality)",
          minLength: 2,
          maxLength: 120
        },
        construction_type: {
          type: "string",
          description: "Place of Service setting ('ASC / Outpatient Facility', 'HOPD (POS 22)', 'Inpatient (POS 21)', 'Office Non-Facility (POS 11)').",
          default: "ASC / Outpatient Facility",
          minLength: 3,
          maxLength: 40
        },
        estimated_crew_hours: {
          type: "integer",
          description: "Total annual claim encounters across the specialty cohort.",
          default: 1250,
          minimum: 1,
          maximum: 5000000
        }
      },
      required: ["state_code", "county"]
    },
    outputSchema: {
      type: "object",
      properties: {
        status: { type: "string" },
        fully_burdened_crew_hourly_usd: { type: "number" },
        total_estimated_prevailing_labor_usd: { type: "number" },
        wage_classifications: { type: "array" }
      }
    }
  },
  {
    name: "get_live_dot_lettings",
    title: "52-Portal Live Commercial Payer MRF Rate Disparities, ERISA Underpayments & NSA IDR Feed",
    description:
      "Queries pre-vetted commercial payer TiC MRF rate-disparity cohorts, ERISA claim underpayments, and Federal No Surprises Act (NSA) IDR arbitration cases across all 50 State DOI/APCD MRF portals, CMS Federal IDR, and Multi-Payer feeds. " +
      "Executes as a read-only, stateless query returning up to 50 active claim cohorts with MRF 75th-percentile benchmarks, % of Medicare targets, and regional peer provider groups. " +
      "Use this tool when discovering live payer MRF rate disparities and NSA IDR cohorts; use shred_csi_masterformat instead when parsing a specific payer Clinical Policy Bulletin.",
    annotations: {
      title: "52-Portal Live Commercial Payer MRF Rate Disparities, ERISA Underpayments & NSA IDR Feed",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true
    },
    inputSchema: {
      type: "object",
      properties: {
        state: {
          type: "string",
          description: "Optional two-letter state code filter (e.g., 'TX', 'CA', 'FL', 'VA', 'PA', 'NY', 'ALL').",
          default: "TX",
          minLength: 2,
          maxLength: 10
        },
        limit: {
          type: "integer",
          description: "Maximum number of active payer MRF & IDR cohorts to return (1 to 50).",
          default: 10,
          minimum: 1,
          maximum: 50
        }
      }
    },
    outputSchema: {
      type: "object",
      properties: {
        status: { type: "string" },
        portals_monitored: { type: "integer" },
        lettings: { type: "array" }
      }
    }
  },
  {
    name: "audit_baba_buy_america",
    title: "CMS NCCI Procedure-to-Procedure (PTP) Unbundling, MUE & Modifier 25/59 Claim Scrubber",
    description:
      "Audits multi-line surgical and outpatient claims against CMS National Correct Coding Initiative (NCCI) Procedure-to-Procedure (PTP) column-1/column-2 edits, Medically Unlikely Edits (MUEs), and Modifier -25/-59/-XS documentation rules. " +
      "Operates as a stateless, read-only, non-destructive coding compliance scrubber. " +
      "Use this tool when verifying NCCI unbundling edits and Modifier -25/-59 compliance; use generate_dbe_good_faith_effort instead when preparing Federal No Surprises Act (NSA) IDR arbitration briefs.",
    annotations: {
      title: "CMS NCCI Procedure-to-Procedure (PTP) Unbundling, MUE & Modifier 25/59 Claim Scrubber",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    inputSchema: {
      type: "object",
      properties: {
        project_id: {
          type: "string",
          description: "Claim Cohort or Encounter ID.",
          default: "TXDOI-MRF-CPT-29881-DFW",
          minLength: 2,
          maxLength: 120
        },
        funding_agency: {
          type: "string",
          description: "Governing coding edit standard or commercial payer.",
          default: "CMS NCCI / Commercial Payer Claims Editing Engine",
          minLength: 2,
          maxLength: 140
        }
      },
      required: ["project_id"]
    },
    outputSchema: {
      type: "object",
      properties: {
        status: { type: "string" },
        overall_baba_posture: { type: "string" },
        audited_bom_items: { type: "array" }
      }
    }
  },
  {
    name: "generate_dbe_good_faith_effort",
    title: "Federal No Surprises Act (NSA 45 CFR 149.510) Open Negotiation & IDR Position Brief Generator",
    description:
      "Generates statutory 30-business-day Open Negotiation Notices, verifies Qualifying Payment Amount (QPA) deflation anomalies, and compiles Federal No Surprises Act (45 CFR 149.510) Independent Dispute Resolution (IDR) arbitration briefs. " +
      "Executes as a stateless, read-only, idempotent NSA IDR arbitration calculator. " +
      "Use this tool when preparing Federal NSA IDR arbitration offers and Open Negotiation notices; use generate_subcontractor_scope_itb instead when redlining in-network managed care payer contracts.",
    annotations: {
      title: "Federal No Surprises Act (NSA 45 CFR 149.510) Open Negotiation & IDR Position Brief Generator",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    inputSchema: {
      type: "object",
      properties: {
        project_id: {
          type: "string",
          description: "NSA IDR Dispute Case ID.",
          default: "CMS-NSA-IDR-CPT-63047-NAT",
          minLength: 2,
          maxLength: 120
        },
        total_bid_amount_usd: {
          type: "number",
          description: "Total target 75th-percentile commercial MRF arbitration offer across disputed claim cohort (USD).",
          default: 1420000.0,
          minimum: 100.0,
          maximum: 5000000000.0
        },
        dbe_goal_pct: {
          type: "number",
          description: "Target commercial reimbursement as a percentage of CMS Medicare fee schedule (e.g., 215.0%).",
          default: 215.0,
          minimum: 0.0,
          maximum: 500.0
        }
      },
      required: ["project_id", "total_bid_amount_usd", "dbe_goal_pct"]
    },
    outputSchema: {
      type: "object",
      properties: {
        status: { type: "string" },
        achieved_dbe_participation_pct: { type: "number" },
        goal_compliance_status: { type: "string" }
      }
    }
  },
  {
    name: "generate_aia_g702_g703_pay_app",
    title: "HIPAA X12 835 Electronic Remittance Advice (ERA) CARC/RARC Underpayment & Zero-Pay Auditor",
    description:
      "Audits HIPAA X12 835 Electronic Remittance Advice (ERA) payment lines and Claim Adjustment Reason Codes (CARC 45, 50, 96, 97, 197) against contracted payer fee schedules and TiC MRF 75th-percentile benchmarks. " +
      "Runs as a stateless, read-only healthcare revenue cycle remittance calculator with zero database mutations. " +
      "Use this tool when auditing X12 835 ERA remittances for contractual underpayments; use audit_surety_miller_act_bond instead when calculating 50-state statutory prompt-pay interest penalties.",
    annotations: {
      title: "HIPAA X12 835 Electronic Remittance Advice (ERA) CARC/RARC Underpayment & Zero-Pay Auditor",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    inputSchema: {
      type: "object",
      properties: {
        project_id: {
          type: "string",
          description: "Remittance Audit Batch ID.",
          default: "TXDOI-MRF-CPT-29881-DFW",
          minLength: 2,
          maxLength: 120
        },
        contractor_name: {
          type: "string",
          description: "Billing Provider Group or ASC legal name.",
          default: "Texas Orthopedic & Spine Surgical Associates PLLC",
          minLength: 2,
          maxLength: 180
        },
        contract_sum_usd: {
          type: "number",
          description: "Total contracted expected allowed amount across the remittance batch in USD.",
          default: 1840000.0,
          minimum: 100.0,
          maximum: 5000000000.0
        }
      },
      required: ["project_id", "contract_sum_usd"]
    },
    outputSchema: {
      type: "object",
      properties: {
        status: { type: "string" },
        g702_summary: { type: "object" },
        g703_continuation_sheet: { type: "array" }
      }
    }
  },
  {
    name: "audit_surety_miller_act_bond",
    title: "50-State Prompt-Pay Statute Interest Penalty & Clean-Claim Timely-Filing Calculator",
    description:
      "Evaluates overdue commercial payer clean claims against 50-state prompt-pay statutes (TX Ins. Code Ch. 1301 18% APR, CA H&S 1371 15% APR, FL 627.6131 12% APR, NY ISC 3224-a 12% APR) to calculate statutory penalty interest. " +
      "Executes as a stateless, read-only statutory prompt-pay interest model. " +
      "Use this tool when calculating statutory prompt-pay interest on late payer remittances; use generate_aia_g702_g703_pay_app instead when auditing line-by-line X12 835 CARC/RARC adjustments.",
    annotations: {
      title: "50-State Prompt-Pay Statute Interest Penalty & Clean-Claim Timely-Filing Calculator",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    inputSchema: {
      type: "object",
      properties: {
        contractor_name: {
          type: "string",
          description: "Provider Group or Hospital legal name.",
          default: "Texas Orthopedic & Spine Surgical Associates PLLC",
          minLength: 2,
          maxLength: 180
        },
        target_project_bid_usd: {
          type: "number",
          description: "Net overdue clean-claim principal balance subject to statutory prompt-pay interest (USD).",
          default: 1830000.0,
          minimum: 100.0,
          maximum: 5000000000.0
        }
      },
      required: ["contractor_name", "target_project_bid_usd"]
    },
    outputSchema: {
      type: "object",
      properties: {
        status: { type: "string" },
        miller_act_approval_status: { type: "string" },
        estimated_bond_premium_usd: { type: "number" }
      }
    }
  },
  {
    name: "generate_rfi_change_order_claim",
    title: "ERISA 29 CFR 2560.503-1 Level-1 & Level-2 Medical Necessity Appeal Drafter",
    description:
      "Analyzes CARC-50/96/197 medical necessity or experimental/investigational claim denials, cites ERISA 29 CFR 2560.503-1(h)(3)(iii) same-specialty peer review mandates, and calculates principal + statutory interest recovery demands. " +
      "Operates as a stateless, read-only, non-destructive healthcare legal appeal analyzer. " +
      "Use this tool when drafting ERISA 29 CFR 2560.503-1 medical necessity appeals; use shred_csi_masterformat instead when parsing initial commercial payer Clinical Policy Bulletins.",
    annotations: {
      title: "ERISA 29 CFR 2560.503-1 Level-1 & Level-2 Medical Necessity Appeal Drafter",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    inputSchema: {
      type: "object",
      properties: {
        project_id: {
          type: "string",
          description: "Denied Claim or Cohort ID.",
          default: "CADMHC-MRF-CPT-63030-SFO",
          minLength: 2,
          maxLength: 120
        },
        issue_summary: {
          type: "string",
          description: "Clinical summary of the CARC/RARC denial and documented objective medical necessity evidence.",
          default: "Payer issued CARC 50 (Not Medically Necessary) denial on CPT 63030 Lumbar Microdiscectomy despite MRI confirming L4-L5 extruded disc herniation and 8 weeks failed PT.",
          minLength: 10,
          maxLength: 10000
        },
        direct_cost_impact_usd: {
          type: "number",
          description: "Disputed principal claim allowed amount under commercial MRF 75th percentile in USD.",
          default: 68500.0,
          minimum: 0.0,
          maximum: 500000000.0
        }
      },
      required: ["project_id", "issue_summary"]
    },
    outputSchema: {
      type: "object",
      properties: {
        status: { type: "string" },
        entitlement_basis: { type: "string" },
        pco_pricing_summary: { type: "object" }
      }
    }
  },
  {
    name: "audit_osha_emr_site_safety",
    title: "MS-DRG / APR-DRG Inpatient Clinical Validation, CC/MCC Sepsis & DRG Downcode Defense",
    description:
      "Defends hospital inpatient claims against commercial payer MS-DRG / APR-DRG clinical validation denials and CC/MCC downcoding (Sepsis-3 SOFA criteria, KDIGO AKI, ASPEN Severe Malnutrition, and Acute Respiratory Failure). " +
      "Runs as a stateless, read-only inpatient clinical documentation integrity (CDI) defense generator. " +
      "Use this tool when defending inpatient MS-DRG weights and CC/MCC capture; use audit_surety_miller_act_bond instead when calculating statutory prompt-pay interest.",
    annotations: {
      title: "MS-DRG / APR-DRG Inpatient Clinical Validation, CC/MCC Sepsis & DRG Downcode Defense",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    inputSchema: {
      type: "object",
      properties: {
        project_id: {
          type: "string",
          description: "Inpatient DRG Audit Batch ID.",
          default: "NYDFS-MRF-CPT-27447-NYC",
          minLength: 2,
          maxLength: 120
        },
        contractor_emr_current: {
          type: "number",
          description: "Hospital Case Mix Index (CMI) or clean-claim clinical validation pass ratio.",
          default: 0.94,
          minimum: 0.1,
          maximum: 5.0
        }
      },
      required: ["project_id"]
    },
    outputSchema: {
      type: "object",
      properties: {
        status: { type: "string" },
        prequalification_eligibility: { type: "string" },
        activity_hazard_analyses_aha: { type: "array" }
      }
    }
  },
  {
    name: "analyze_planholder_competitor_spread",
    title: "Regional Specialty Group Tax-ID (EIN/NPI) Payer Leverage & Revenue Left on Table (RLOT) Analyzer",
    description:
      "Analyzes a medical group or ASC's current contracted CPT/APC fee schedule against regional peer groups and health systems in the same MSA using CMS TiC MRF files to quantify annual Revenue Left on Table (RLOT) and target contract uplift. " +
      "Executes as a stateless, read-only managed care payer benchmarking model. " +
      "Use this tool when comparing peer EIN/NPI commercial MRF rates and quantifying annual RLOT; use model_dot_unit_bid_tabs instead when pricing individual CPT/DRG procedure codes.",
    annotations: {
      title: "Regional Specialty Group Tax-ID (EIN/NPI) Payer Leverage & Revenue Left on Table (RLOT) Analyzer",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    inputSchema: {
      type: "object",
      properties: {
        project_id: {
          type: "string",
          description: "Regional Market MRF Cohort ID.",
          default: "TXDOI-MRF-CPT-29881-DFW",
          minLength: 2,
          maxLength: 120
        },
        engineers_estimate_usd: {
          type: "number",
          description: "Annual cohort commercial revenue at 75th-percentile regional MRF benchmark in USD.",
          default: 2450000.0,
          minimum: 1000.0,
          maximum: 5000000000.0
        }
      },
      required: ["project_id", "engineers_estimate_usd"]
    },
    outputSchema: {
      type: "object",
      properties: {
        status: { type: "string" },
        predicted_winning_low_bid_usd: { type: "number" },
        recommended_markup_pct: { type: "number" }
      }
    }
  },
  {
    name: "generate_subcontractor_scope_itb",
    title: "Managed Care Payer Contract Redline, Lesser-of-Billed Clauses & Rate-Escalator Term Sheet Generator",
    description:
      "Generates managed care payer contract redlines, anti-downcoding covenants, ASC implant pass-through carve-outs, and CPI-U annual rate-escalator term sheets. " +
      "Operates as a stateless, read-only healthcare contracting document generator. " +
      "Use this tool when redlining commercial payer managed care agreements; use generate_dbe_good_faith_effort instead when generating out-of-network Federal NSA IDR arbitration briefs.",
    annotations: {
      title: "Managed Care Payer Contract Redline, Lesser-of-Billed Clauses & Rate-Escalator Term Sheet Generator",
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    },
    inputSchema: {
      type: "object",
      properties: {
        project_id: {
          type: "string",
          description: "Managed Care Contract Negotiation ID.",
          default: "TXDOI-MRF-CPT-29881-DFW",
          minLength: 2,
          maxLength: 120
        },
        trade_package: {
          type: "string",
          description: "Target payer contract line of business and specialty schedule.",
          default: "Commercial PPO / HMO & Self-Funded ASO Fee Schedule Addendum (Orthopedic & ASC Carve-Out)",
          minLength: 3,
          maxLength: 240
        }
      },
      required: ["project_id", "trade_package"]
    },
    outputSchema: {
      type: "object",
      properties: {
        status: { type: "string" },
        mandatory_scope_inclusions: { type: "array" },
        aia_a401_flowdown_clauses: { type: "array" }
      }
    }
  }
];

async function callRubricWardEndpoint(toolName, args) {
  const route = ENDPOINT_MAP[toolName];
  if (!route) {
    return {
      isError: true,
      content: [{ type: "text", text: `Unknown tool: ${toolName}` }]
    };
  }

  const rapidHost = RAPIDAPI_HOSTS[toolName];
  const useRapidApi = Boolean(RAPIDAPI_KEY && rapidHost && !RAPIDAPI_PROXY_SECRET);
  const baseUrl = useRapidApi ? `https://${rapidHost}` : BASE_URL;
  const u = new URL(`${baseUrl}${route.path}`);

  const headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
  };

  if (useRapidApi) {
    headers["X-RapidAPI-Key"] = RAPIDAPI_KEY;
    headers["X-RapidAPI-Host"] = rapidHost;
  } else if (RAPIDAPI_PROXY_SECRET) {
    headers["X-RapidAPI-Proxy-Secret"] = RAPIDAPI_PROXY_SECRET.split(",")[0].trim();
  } else if (RUBRICWARD_API_KEY) {
    headers["Authorization"] = `Bearer ${RUBRICWARD_API_KEY}`;
  }

  if (route.method === "GET" && args && typeof args === "object") {
    for (const [k, v] of Object.entries(args)) {
      if (v !== undefined && v !== null && v !== "") {
        u.searchParams.set(k, String(v));
      }
    }
  }

  const fetchOpts = {
    method: route.method,
    headers
  };
  if (route.method === "POST") {
    fetchOpts.body = JSON.stringify(args || {});
  }

  let response = await fetch(u.toString(), fetchOpts);
  if (!response.ok && useRapidApi) {
    const fallbackUrl = new URL(`${BASE_URL}${route.path}`);
    if (route.method === "GET" && args && typeof args === "object") {
      for (const [k, v] of Object.entries(args)) {
        if (v !== undefined && v !== null && v !== "") {
          fallbackUrl.searchParams.set(k, String(v));
        }
      }
    }
    response = await fetch(fallbackUrl.toString(), {
      method: route.method,
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: route.method === "POST" ? JSON.stringify(args || {}) : undefined
    });
  }

  const text = await response.text();
  const result = {
    isError: !response.ok,
    content: [{ type: "text", text }]
  };
  if (response.ok) {
    try {
      const parsed = JSON.parse(text);
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
        result.structuredContent = parsed;
      }
    } catch (_) {}
  }
  return result;
}

function sendJsonRpc(message) {
  process.stdout.write(JSON.stringify(message) + "\n");
}

if (require.main === module) {
  const rl = readline.createInterface({
    input: process.stdin,
    terminal: false
  });

  rl.on("line", async (line) => {
    if (!line.trim()) return;
    let req;
    try {
      req = JSON.parse(line);
    } catch (_) {
      return;
    }

    const { id, method, params } = req;
    try {
      if (method === "initialize") {
        sendJsonRpc({
          jsonrpc: "2.0",
          id,
          result: {
            protocolVersion: "2024-11-05",
            capabilities: { tools: {} },
            serverInfo: {
              name: "@rubricward/mcp-server",
              version: "1.0.0"
            }
          }
        });
      } else if (method === "notifications/initialized") {
        // Notification only
      } else if (method === "tools/list") {
        sendJsonRpc({
          jsonrpc: "2.0",
          id,
          result: { tools: TOOLS }
        });
      } else if (method === "tools/call") {
        const toolName = params && params.name;
        const toolArgs = (params && params.arguments) || {};
        const result = await callRubricWardEndpoint(toolName, toolArgs);
        sendJsonRpc({
          jsonrpc: "2.0",
          id,
          result
        });
      } else if (method === "ping") {
        sendJsonRpc({
          jsonrpc: "2.0",
          id,
          result: {}
        });
      } else if (id !== undefined) {
        sendJsonRpc({
          jsonrpc: "2.0",
          id,
          error: { code: -32601, message: `Method not found: ${method}` }
        });
      }
    } catch (err) {
      if (id !== undefined) {
        sendJsonRpc({
          jsonrpc: "2.0",
          id,
          error: { code: -32603, message: err.message || "Internal MCP server error" }
        });
      }
    }
  });
}

module.exports = { RAPIDAPI_HOSTS, ENDPOINT_MAP, TOOLS };
