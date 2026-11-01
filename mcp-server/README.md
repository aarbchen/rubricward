# `@rubricward/mcp-server` — Commercial Payer TiC MRF, Medicare RVU/GPCI, ERISA Appeal & NSA IDR MCP Server

Connect Claude Desktop, Cursor, Windsurf, or any Model Context Protocol (MCP) agent directly to RubricWard's commercial payer Transparency in Coverage (`TiC 45 CFR 147.212`) machine-readable file (`MRF`), Medicare Physician Fee Schedule (`MPFS RVU/GPCI`), ERISA `29 CFR 2560.503-1` medical necessity appeal, and Federal No Surprises Act (`NSA 45 CFR 149.510`) IDR arbitration microservices.

| Tool Name | Endpoint Route | Core Healthcare Revenue Cycle & Payer Intelligence Capability |
| :--- | :--- | :--- |
| `shred_csi_masterformat` | `POST /v1/shred/csi-masterformat` | Shreds commercial payer Clinical Policy Bulletins (`CPB`) & Medicare `LCD/NCD` rules into prior-auth criteria & ERISA appeal triggers. |
| `model_dot_unit_bid_tabs` | `POST /v1/model/dot-unit-bid-tabs` | Models 50-State Commercial Payer TiC MRF allowed amounts (`25th / 50th QPA / 75th`) & `% of Medicare` multiples by CPT/DRG. |
| `calculate_davis_bacon_prevailing_wage` | `POST /v1/calculate/davis-bacon-prevailing-wage` | Computes locality-adjusted CMS Medicare `MPFS RVU` (`Work + PE + MP`), `GPCI`, and ASC payment rates. |
| `get_live_dot_lettings` | `GET /v1/lettings/live` | Queries 52 active State DOI/APCD MRF, CMS Federal IDR & Commercial Payer rate-disparity cohorts. |
| `audit_baba_buy_america` | `POST /v1/audit/baba-buy-america` | Scrubs multi-line claims against CMS `NCCI PTP` unbundling edits, `MUE` caps & Modifier `25/59/XS` rules. |
| `generate_dbe_good_faith_effort` | `POST /v1/generate/dbe-good-faith-effort` | Generates Federal No Surprises Act (`NSA 45 CFR 149.510`) 30-day Open Negotiation & IDR arbitration briefs. |
| `generate_aia_g702_g703_pay_app` | `POST /v1/generate/aia-g702-g703-pay-app` | Audits HIPAA `X12 835` Electronic Remittance Advice (`ERA`) `CARC/RARC` adjustments & contractual underpayments. |
| `audit_surety_miller_act_bond` | `POST /v1/audit/surety-miller-act-bond` | Calculates 50-State Statutory Prompt-Pay interest penalties (`12%–18% APR`) & clean-claim timely-filing deadlines. |
| `generate_rfi_change_order_claim` | `POST /v1/generate/rfi-change-order-claim` | Drafts citation-backed `ERISA 29 CFR 2560.503-1` Level-1/Level-2 medical necessity & experimental/investigational appeals. |
| `audit_osha_emr_site_safety` | `POST /v1/audit/osha-emr-site-safety` | Defends inpatient `MS-DRG / APR-DRG` claims against payer clinical validation & `CC/MCC` downcoding denials. |
| `analyze_planholder_competitor_spread` | `POST /v1/analyze/planholder-competitor-spread` | Analyzes regional specialty group `EIN/NPI` MRF rate spreads to quantify Revenue Left on Table (`RLOT`). |
| `generate_subcontractor_scope_itb` | `POST /v1/generate/subcontractor-scope-itb` | Generates managed care payer contract redlines, anti-recoupment clauses & CPI-U rate-escalator term sheets. |
