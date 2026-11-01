# DOT DBE 49 CFR Part 26 Subcontractor & Good Faith Effort Generator API

**By RubricWard Preconstruction & DOT Systems** (`https://rubricward.com`)

Calculate certified DBE/MBE/WBE participation credit (100% subcontractor vs. 60% regular dealer) and generate audit-proof 49 CFR Part 26 Good Faith Effort logs.

---

## Key Capabilities & Construction Preconstruction Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes project manuals, DOT pay items, Davis-Bacon wage classifications, and AIA billing schedules in memory.
- **Built for ConTech ERPs, Heavy-Civil Estimators & Surety Underwriters:** Ready to plug directly into Procore, Autodesk Construction Cloud, HeavyBid workflows, or AI estimating agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/generate/dbe-good-faith-effort`

---

## Example Request Payload

```json
{
  "project_name": "FDOT SR-826 Palmetto Expressway Interchange Reconstruction",
  "total_base_bid_usd": 14850000,
  "dbe_goal_percent": 11.5,
  "proposed_dbe_commitments": [
    {
      "firm_name": "Sunshine Barricade & MOT LLC",
      "certification": "FDOT DBE",
      "role": "Subcontractor",
      "work_scope": "Maintenance of Traffic & Pavement Markings",
      "quote_amount_usd": 1180000
    },
    {
      "firm_name": "Gulfstream Aggregate Supply Inc.",
      "certification": "FDOT DBE",
      "role": "Regular Dealer",
      "work_scope": "Limestone Base & Pipe Bedding",
      "quote_amount_usd": 920000
    }
  ]
}
```

---

## Pricing Tiers
- **BASIC (`$0 / mo`):** `10 requests / month` hard limit (`10 requests / hour` rate limit) for testing and evaluation.
- **PRO (`$49 / mo`):** `200 requests / month` for active estimating teams and specialty subcontractors.
- **ULTRA (`$149 / mo` — Recommended):** `1,000 requests / month` for regional general contractors and heavy-civil primes.
- **MEGA (`$399 / mo`):** `4,000 requests / month` for ConTech SaaS platforms, surety brokerages, and multi-office builders.
