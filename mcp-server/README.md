# `@rubricward/mcp-server` — Construction Preconstruction, 50-State DOT Bid-Tab & Prevailing-Wage MCP Server

Connect Claude Desktop, Cursor, Windsurf, or any Model Context Protocol (MCP) agent directly to RubricWard's preconstruction, DOT unit-bid tabulation, Davis-Bacon `WH-347`, and AIA `G702/G703` microservices.

| Tool Name | Endpoint Route | Core Preconstruction Capability |
| :--- | :--- | :--- |
| `shred_csi_masterformat` | `POST /v1/shred/csi-masterformat` | Shreds CSI MasterFormat Divisions `00–48` into submittal logs & liquidated damages. |
| `model_dot_unit_bid_tabs` | `POST /v1/model/dot-unit-bid-tabs` | Models 36-month State DOT historical unit bid prices (`$/Ton`, `$/LF`, `$/CY`). |
| `calculate_davis_bacon_prevailing_wage` | `POST /v1/calculate/davis-bacon-prevailing-wage` | Computes `29 CFR Part 5` Davis-Bacon base + fringe rates & `WH-347` certified payroll. |
| `get_live_dot_lettings` | `GET /v1/lettings/live` | Queries 52 active State DOT, USACE Civil & Municipal public works lettings. |
| `audit_baba_buy_america` | `POST /v1/audit/baba-buy-america` | Audits BOMs for `BABA` (`23 CFR 635.410`) domestic iron/steel & De Minimis waivers. |
| `generate_dbe_good_faith_effort` | `POST /v1/generate/dbe-good-faith-effort` | Calculates `49 CFR Part 26` DBE subcontractor credit (100% vs. 60%) & `GFE` logs. |
| `generate_aia_g702_g703_pay_app` | `POST /v1/generate/aia-g702-g703-pay-app` | Builds balanced AIA `G702/G703` Schedules of Values (`SOV`) & retainage math. |
| `audit_surety_miller_act_bond` | `POST /v1/audit/surety-miller-act-bond` | Underwrites Miller Act (`40 U.S.C. 3131`) single/aggregate bond limits & premiums. |
| `generate_rfi_change_order_claim` | `POST /v1/generate/rfi-change-order-claim` | Drafts RFIs, Differing Site Condition (`FAR 52.236-2`) claims & AIA `G701` pricing. |
| `audit_osha_emr_site_safety` | `POST /v1/audit/osha-emr-site-safety` | Generates `OSHA 1926` / `USACE EM 385-1-1` Activity Hazard Analyses (`AHA`) & EMR audits. |
| `analyze_planholder_competitor_spread` | `POST /v1/analyze/planholder-competitor-spread` | Predicts low-bid spread & Margin Left on Table (`MLOT`) from DOT planholder lists. |
| `generate_subcontractor_scope_itb` | `POST /v1/generate/subcontractor-scope-itb` | Generates trade Subcontractor `ITB` scope checklists & AIA `A401` flow-downs. |

