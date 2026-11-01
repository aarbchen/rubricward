# Specialty Group EIN NPI Payer Leverage & Revenue Left on Table RLOT API

**By RubricWard Commercial Payer MRF, ERISA Appeal & NSA IDR Systems** (`https://rubricward.com`)

Compare a medical group or ASC's contracted CPT/APC fee schedule against regional peer EIN/NPI groups in the same MSA using CMS TiC MRF files to quantify annual RLOT.

---

## Key Capabilities & Healthcare Revenue Cycle Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes commercial payer Clinical Policy Bulletins, CMS TiC MRF CPT/DRG rate cohorts, Medicare MPFS RVU/GPCI baselines, and X12 835 remittances in memory.
- **Built for Healthcare RCM Platforms, Specialty Physician Groups, ASCs & ERISA Appeal Attorneys:** Ready to plug into Epic, Athenahealth, Waystar, or AI revenue cycle agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/analyze/planholder-competitor-spread`

---

## Example Request Payload

```json
{
  "project_id": "TXDOI-MRF-CPT-29881-DFW",
  "engineers_estimate_usd": 2450000
}
```

---

## Pricing Tiers
- **BASIC (`$0 / mo`):** `10 requests / month` hard limit (`10 requests / hour` rate limit) for testing and evaluation.
- **PRO (`$49 / mo`):** `200 requests / month` for specialty physician groups and ASC billing teams.
- **ULTRA (`$149 / mo` — Recommended):** `1,000 requests / month` for multi-specialty groups, RCM billing companies, and NSA IDR arbitration desks.
- **MEGA (`$399 / mo`):** `4,000 requests / month` for hospital health systems, healthcare fintech platforms, and ERISA litigation firms.
