#!/usr/bin/env node
/**
 * @rubricward/mcp-server — Official Local STDIO Model Context Protocol (MCP) Server
 * Zero-dependency JSON-RPC 2.0 stdio server exposing all 12 RubricWard Construction
 * Preconstruction, 50-State DOT Historical Item Bid Tabulation, Davis-Bacon Prevailing
 * Wage (29 CFR Part 5 / WH-347), CSI MasterFormat Divisions 00-48 Spec Shredder,
 * BABA, DOT DBE (49 CFR Part 26), AIA G702/G703, and Miller Act Surety APIs.
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
    title: "CSI MasterFormat Divisions 00-48 Spec & Submittal Shredder",
    description:
      "Extracts structured CSI MasterFormat Divisions 00-48 submittal registers, liquidated damages per day, retainage caps, and warranty terms from raw construction project manuals and special provisions. " +
      "Executes as a stateless, read-only, non-destructive parser accepting up to 50,000 characters of specification text with zero persistent payload storage. " +
      "Use this tool when shredding specifications into division submittal logs; use model_dot_unit_bid_tabs instead when pricing historical DOT unit pay items.",
    annotations: {
      title: "CSI MasterFormat Divisions 00-48 Spec & Submittal Shredder",
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
          description: "Raw text from Project Manual, Special Provisions, or CSI MasterFormat Divisions 00-48 specification.",
          default: "SECTION 01 10 00 SUMMARY: Replace 4 prestressed bridge spans and place 68,000 tons of Superpave HMA. Liquidated damages are $4,200 per calendar day.",
          minLength: 10,
          maxLength: 50000
        },
        project_id: {
          type: "string",
          description: "DOT CSJ, Contract ID, or Project Number.",
          default: "TXDOT-CSJ-0015-13-412",
          minLength: 2,
          maxLength: 120
        },
        target_trade: {
          type: "string",
          description: "Primary trade focus (e.g., 'Heavy Civil / Highway & Bridge', 'Div 26 Electrical').",
          default: "Heavy Civil / Highway & Bridge",
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
    title: "50-State DOT Historical Item Bid Tabulation & Spread Modeler",
    description:
      "Calculates historical 36-month State DOT low, median, and 75th-percentile unit bid prices ($/Ton, $/LF, $/CY, $/SY, $/LB) and recommended unit bids for heavy-civil pay items. " +
      "Operates as a stateless, read-only, idempotent pricing engine with unbalanced-bid guardrail verification under 23 CFR 635.102. " +
      "Use this tool when pricing DOT unit pay items and takeoff quantities; use calculate_davis_bacon_prevailing_wage instead when calculating craft labor base and fringe rates.",
    annotations: {
      title: "50-State DOT Historical Item Bid Tabulation & Spread Modeler",
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
          description: "DOT Pay Item code and description (e.g., '341-6008 Superpave HMA').",
          default: "Dense-Graded Hot-Mix Asphalt (Superpave SP-C PG 76-22)",
          minLength: 3,
          maxLength: 300
        },
        unit: {
          type: "string",
          description: "Pay item unit of measure ('TON', 'LF', 'CY', 'SY', 'LB', 'EA', 'LS').",
          default: "TON",
          minLength: 1,
          maxLength: 20
        },
        quantity: {
          type: "number",
          description: "Estimated takeoff quantity for the pay item.",
          default: 68000.0,
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
    title: "Davis-Bacon (29 CFR 5) & State Prevailing Wage Fringe Calculator",
    description:
      "Computes locality-adjusted Davis-Bacon and state prevailing wage base hourly rates, bona fide fringe benefits, overtime rates, and Form WH-347 certified payroll burdens across construction trades. " +
      "Runs as a stateless, read-only, non-destructive labor compliance calculator with zero side effects. " +
      "Use this tool when calculating prevailing craft wages and WH-347 fringes; use model_dot_unit_bid_tabs instead when modeling material/composite unit bid tabulations.",
    annotations: {
      title: "Davis-Bacon (29 CFR 5) & State Prevailing Wage Fringe Calculator",
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
          description: "Project county name.",
          default: "Travis County",
          minLength: 2,
          maxLength: 120
        },
        construction_type: {
          type: "string",
          description: "Davis-Bacon construction type ('Highway', 'Heavy', 'Building', 'Residential').",
          default: "Highway",
          minLength: 3,
          maxLength: 40
        },
        estimated_crew_hours: {
          type: "integer",
          description: "Total estimated project crew man-hours.",
          default: 14500,
          minimum: 40,
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
    title: "52-Portal Live State DOT Lettings, USACE & Public Works Feed",
    description:
      "Queries pre-vetted, high-value heavy-civil, highway, bridge, water/wastewater, and commercial construction lettings across all 50 State DOTs, USACE, and Municipal portals. " +
      "Executes as a read-only, stateless query returning up to 50 active lettings with Engineer's Estimates, DBE goals, and official planholders. " +
      "Use this tool when discovering open construction lettings and planholder lists; use shred_csi_masterformat instead when parsing a specific project specification.",
    annotations: {
      title: "52-Portal Live State DOT Lettings, USACE & Public Works Feed",
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
          description: "Maximum number of active lettings to return (1 to 50).",
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
    title: "Build America, Buy America (BABA / 23 CFR 635.410) Material Auditor",
    description:
      "Audits construction Bill of Materials (BOM) line items against federal FHWA/USACE Build America, Buy America (BABA) domestic iron, steel, and manufactured product thresholds (>55% domestic cost) and OMB M-24-02 De Minimis waivers. " +
      "Operates as a stateless, read-only, non-destructive compliance auditor. " +
      "Use this tool when verifying domestic steel/material certifications; use generate_dbe_good_faith_effort instead when auditing DBE subcontractor participation credits.",
    annotations: {
      title: "Build America, Buy America (BABA / 23 CFR 635.410) Material Auditor",
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
          description: "Project or Contract ID.",
          default: "USACE-W912EP-27-B-0004",
          minLength: 2,
          maxLength: 120
        },
        funding_agency: {
          type: "string",
          description: "Federal or state infrastructure funding agency.",
          default: "FHWA / USACE Infrastructure",
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
    title: "DOT DBE (49 CFR Part 26) Subcontractor & Good Faith Effort Generator",
    description:
      "Calculates Disadvantaged Business Enterprise (DBE) participation credits under 49 CFR 26.55 (100% subcontractor vs. 60% regular dealer), verifies Commercially Useful Function (CUF), and generates Good Faith Effort (GFE) logs. " +
      "Executes as a stateless, read-only, idempotent compliance calculator. " +
      "Use this tool when calculating DOT DBE participation goals; use generate_subcontractor_scope_itb instead when drafting trade-specific subcontractor invitations to bid.",
    annotations: {
      title: "DOT DBE (49 CFR Part 26) Subcontractor & Good Faith Effort Generator",
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
          description: "DOT Project ID.",
          default: "TXDOT-CSJ-0015-13-412",
          minLength: 2,
          maxLength: 120
        },
        total_bid_amount_usd: {
          type: "number",
          description: "Total prime contract bid amount in USD.",
          default: 17850000.0,
          minimum: 10000.0,
          maximum: 5000000000.0
        },
        dbe_goal_pct: {
          type: "number",
          description: "Contract DBE participation goal percentage.",
          default: 11.5,
          minimum: 0.0,
          maximum: 50.0
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
    title: "AIA G702 / G703 Schedule of Values (SOV) & Retainage Billing Generator",
    description:
      "Generates a balanced AIA Document G702 Application for Payment summary and G703 Continuation Sheet Schedule of Values with statutory retainage and net progress payment calculations. " +
      "Runs as a stateless, read-only financial calculator with zero database mutations. " +
      "Use this tool when structuring progress billings and Schedules of Values; use audit_surety_miller_act_bond instead when underwriting contractor bonding capacity.",
    annotations: {
      title: "AIA G702 / G703 Schedule of Values (SOV) & Retainage Billing Generator",
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
          description: "Project identifier.",
          default: "TXDOT-CSJ-0015-13-412",
          minLength: 2,
          maxLength: 120
        },
        contractor_name: {
          type: "string",
          description: "Prime or Subcontractor legal name.",
          default: "Webber Civil Constructors LLC",
          minLength: 2,
          maxLength: 180
        },
        contract_sum_usd: {
          type: "number",
          description: "Original Contract Sum in USD.",
          default: 17850000.0,
          minimum: 1000.0,
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
    title: "Miller Act (40 U.S.C. 3131) & Surety Bond Capacity Underwriter",
    description:
      "Evaluates contractor working capital, tangible net worth, and uncompleted WIP backlog to determine Single and Aggregate Surety Bond limits and sliding-scale SF-24/SF-25 bond premiums. " +
      "Executes as a stateless, read-only surety underwriting model. " +
      "Use this tool when verifying Miller Act bond capacity and premiums; use generate_aia_g702_g703_pay_app instead when generating monthly progress payment applications.",
    annotations: {
      title: "Miller Act (40 U.S.C. 3131) & Surety Bond Capacity Underwriter",
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
          description: "Contractor legal name.",
          default: "Apex Civil & Utility Constructors LLC",
          minLength: 2,
          maxLength: 180
        },
        target_project_bid_usd: {
          type: "number",
          description: "Target project bid amount requiring 100% Performance and Payment Bonds (USD).",
          default: 12400000.0,
          minimum: 10000.0,
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
    title: "Construction RFI, Differing Site Conditions & AIA G701 Change Order Drafter",
    description:
      "Analyzes subsurface differing site conditions (FAR 52.236-2) or drawing conflicts, models Critical Path Time-Impact Analysis (TIA) delay days, and prices AIA G701 Change Order requests. " +
      "Operates as a stateless, read-only, non-destructive construction claims analyzer. " +
      "Use this tool when drafting RFIs and differing site condition change orders; use shred_csi_masterformat instead when parsing initial pre-bid specifications.",
    annotations: {
      title: "Construction RFI, Differing Site Conditions & AIA G701 Change Order Drafter",
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
          description: "Project ID.",
          default: "CALTRANS-04-2Q7404",
          minLength: 2,
          maxLength: 120
        },
        issue_summary: {
          type: "string",
          description: "Description of the plan discrepancy or differing subsurface condition.",
          default: "Encountered uncharted 48-inch cast-iron main at Bent 4 micropile elevation -38.0 ft.",
          minLength: 10,
          maxLength: 10000
        },
        direct_cost_impact_usd: {
          type: "number",
          description: "Estimated direct cost impact in USD.",
          default: 184500.0,
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
    title: "OSHA 29 CFR 1926, USACE EM 385-1-1 AHA & Insurance EMR Auditor",
    description:
      "Generates trade-specific Activity Hazard Analyses (AHA) under USACE EM 385-1-1 and OSHA 29 CFR 1926 and evaluates contractor Experience Modification Rate (EMR) bid prequalification eligibility. " +
      "Runs as a stateless, read-only safety compliance generator. " +
      "Use this tool when preparing site-specific safety plans and AHA matrices; use audit_surety_miller_act_bond instead when evaluating financial bonding limits.",
    annotations: {
      title: "OSHA 29 CFR 1926, USACE EM 385-1-1 AHA & Insurance EMR Auditor",
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
          description: "Project ID.",
          default: "USACE-W912EP-27-B-0004",
          minLength: 2,
          maxLength: 120
        },
        contractor_emr_current: {
          type: "number",
          description: "Contractor current NCCI Experience Modification Rate (EMR).",
          default: 0.78,
          minimum: 0.3,
          maximum: 2.5
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
    title: "DOT Planholder List, Competitor Bid Behavior & MLOT Analyzer",
    description:
      "Analyzes official project planholder lists against historical DOT letting results to predict the winning low bid, Margin Left on Table (MLOT), and optimal markup percentage. " +
      "Executes as a stateless, read-only competitive bidding model. " +
      "Use this tool when analyzing competitor planholders and markup strategy; use model_dot_unit_bid_tabs instead when pricing individual line-item quantities.",
    annotations: {
      title: "DOT Planholder List, Competitor Bid Behavior & MLOT Analyzer",
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
          description: "DOT Project ID.",
          default: "TXDOT-CSJ-0015-13-412",
          minLength: 2,
          maxLength: 120
        },
        engineers_estimate_usd: {
          type: "number",
          description: "Official DOT Engineer's Estimate in USD.",
          default: 18450000.0,
          minimum: 10000.0,
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
    title: "Trade Subcontractor Invitation to Bid (ITB), Scope Gap & AIA A401 Generator",
    description:
      "Generates trade-specific Subcontractor Invitations to Bid (ITB), scope inclusion/exclusion checklists, and AIA A401 subcontract flow-down clauses. " +
      "Operates as a stateless, read-only document generator. " +
      "Use this tool when issuing trade subcontractor bid packages and scope checklists; use generate_dbe_good_faith_effort instead when calculating 49 CFR Part 26 DBE goal credit.",
    annotations: {
      title: "Trade Subcontractor Invitation to Bid (ITB), Scope Gap & AIA A401 Generator",
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
          description: "Project ID.",
          default: "TXDOT-CSJ-0015-13-412",
          minLength: 2,
          maxLength: 120
        },
        trade_package: {
          type: "string",
          description: "Target subcontractor trade package.",
          default: "Division 26 — Roadway ITS Fiber Duct Bank & High-Mast Illumination",
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
