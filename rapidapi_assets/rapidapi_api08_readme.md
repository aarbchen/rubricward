# 50-State Prompt-Pay Statute Interest Penalty & Clean-Claim Calculator API

**By RubricWard Commercial Payer MRF, ERISA Appeal & NSA IDR Systems** (`https://rubricward.com`)

Calculate 50-state statutory prompt-pay interest penalties (TX Ins. Code Ch. 1301 18% APR, CA H&S 1371 15% APR, FL 627.6131 12% APR) on overdue commercial payer claims.

---

## Key Capabilities & Healthcare Revenue Cycle Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes commercial payer Clinical Policy Bulletins, CMS TiC MRF CPT/DRG rate cohorts, Medicare MPFS RVU/GPCI baselines, and X12 835 remittances in memory.
- **Built for Healthcare RCM Platforms, Specialty Physician Groups, ASCs & ERISA Appeal Attorneys:** Ready to plug into Epic, Athenahealth, Waystar, or AI revenue cycle agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/audit/surety-miller-act-bond`

---

## Example Request Payload

```json
{
  "contractor_name": "Texas Orthopedic & Spine Surgical Associates PLLC",
  "target_project_bid_usd": 1830000
}
```

---

## Pricing Tiers
- **BASIC (`$0 / mo`):** `10 requests / month` hard limit (`10 requests / hour` rate limit) for testing and evaluation.
- **PRO (`$49 / mo`):** `200 requests / month` for specialty physician groups and ASC billing teams.
- **ULTRA (`$149 / mo` — Recommended):** `1,000 requests / month` for multi-specialty groups, RCM billing companies, and NSA IDR arbitration desks.
- **MEGA (`$399 / mo`):** `4,000 requests / month` for hospital health systems, healthcare fintech platforms, and ERISA litigation firms.
