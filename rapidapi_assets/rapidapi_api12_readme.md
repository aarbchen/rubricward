# Managed Care Payer Contract Redline & Rate-Escalator Term Sheet API

**By RubricWard Commercial Payer MRF, ERISA Appeal & NSA IDR Systems** (`https://rubricward.com`)

Generate managed care payer contract redlines, anti-downcoding covenants, ASC implant pass-through carve-outs, and CPI-U annual rate-escalator term sheets.

---

## Key Capabilities & Healthcare Revenue Cycle Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes commercial payer Clinical Policy Bulletins, CMS TiC MRF CPT/DRG rate cohorts, Medicare MPFS RVU/GPCI baselines, and X12 835 remittances in memory.
- **Built for Healthcare RCM Platforms, Specialty Physician Groups, ASCs & ERISA Appeal Attorneys:** Ready to plug into Epic, Athenahealth, Waystar, or AI revenue cycle agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/generate/subcontractor-scope-itb`

---

## Example Request Payload

```json
{
  "project_id": "TXDOI-MRF-CPT-29881-DFW",
  "trade_package": "Commercial PPO / HMO & Self-Funded ASO Fee Schedule Addendum (Orthopedic & ASC Carve-Out)"
}
```

---

## Pricing Tiers
- **BASIC (`$0 / mo`):** `10 requests / month` hard limit (`10 requests / hour` rate limit) for testing and evaluation.
- **PRO (`$49 / mo`):** `200 requests / month` for specialty physician groups and ASC billing teams.
- **ULTRA (`$149 / mo` — Recommended):** `1,000 requests / month` for multi-specialty groups, RCM billing companies, and NSA IDR arbitration desks.
- **MEGA (`$399 / mo`):** `4,000 requests / month` for hospital health systems, healthcare fintech platforms, and ERISA litigation firms.
