# 50-State Commercial Payer TiC MRF Allowed-Amount & QPA Rate Modeler API

**By RubricWard Commercial Payer MRF, ERISA Appeal & NSA IDR Systems** (`https://rubricward.com`)

Model 50-State CMS Transparency in Coverage (TiC 45 CFR 147.212) machine-readable file 25th, 50th (Median QPA), and 75th-percentile commercial allowed amounts by CPT/DRG.

---

## Key Capabilities & Healthcare Revenue Cycle Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes commercial payer Clinical Policy Bulletins, CMS TiC MRF CPT/DRG rate cohorts, Medicare MPFS RVU/GPCI baselines, and X12 835 remittances in memory.
- **Built for Healthcare RCM Platforms, Specialty Physician Groups, ASCs & ERISA Appeal Attorneys:** Ready to plug into Epic, Athenahealth, Waystar, or AI revenue cycle agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/model/dot-unit-bid-tabs`

---

## Example Request Payload

```json
{
  "state_code": "TX",
  "pay_item_description": "CPT 29881 \u2014 Arthroscopy, Knee, Surgical; with Meniscectomy (Medial OR Lateral)",
  "unit": "CLAIM",
  "quantity": 420
}
```

---

## Pricing Tiers
- **BASIC (`$0 / mo`):** `10 requests / month` hard limit (`10 requests / hour` rate limit) for testing and evaluation.
- **PRO (`$49 / mo`):** `200 requests / month` for specialty physician groups and ASC billing teams.
- **ULTRA (`$149 / mo` — Recommended):** `1,000 requests / month` for multi-specialty groups, RCM billing companies, and NSA IDR arbitration desks.
- **MEGA (`$399 / mo`):** `4,000 requests / month` for hospital health systems, healthcare fintech platforms, and ERISA litigation firms.
