# Trade Subcontractor Invitation to Bid ITB Scope Gap & AIA A401 API

**By RubricWard Preconstruction & DOT Systems** (`https://rubricward.com`)

Generate CSI-aligned Subcontractor Scope Sheets, Scope-Gap Inclusions/Exclusions Checklists, and AIA A401 Subcontract flow-down clauses.

---

## Key Capabilities & Construction Preconstruction Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes project manuals, DOT pay items, Davis-Bacon wage classifications, and AIA billing schedules in memory.
- **Built for ConTech ERPs, Heavy-Civil Estimators & Surety Underwriters:** Ready to plug directly into Procore, Autodesk Construction Cloud, HeavyBid workflows, or AI estimating agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/generate/subcontractor-scope-itb`

---

## Example Request Payload

```json
{
  "project_name": "VA Medical Center Seismic Structural & MEP Modernization",
  "trade_division": "Division 26 - Electrical & Medium-Voltage Switchgear",
  "prime_contract_liquidated_damages_per_day_usd": 3500,
  "scope_highlights": [
    "Furnish and install two 2,500 kVA 15kV pad-mounted transformers and emergency generator paralleling switchgear",
    "Include all trenching, concrete duct banks, arc-flash study, and NETA acceptance testing"
  ]
}
```

---

## Pricing Tiers
- **BASIC (`$0 / mo`):** `10 requests / month` hard limit (`10 requests / hour` rate limit) for testing and evaluation.
- **PRO (`$49 / mo`):** `200 requests / month` for active estimating teams and specialty subcontractors.
- **ULTRA (`$149 / mo` — Recommended):** `1,000 requests / month` for regional general contractors and heavy-civil primes.
- **MEGA (`$399 / mo`):** `4,000 requests / month` for ConTech SaaS platforms, surety brokerages, and multi-office builders.
