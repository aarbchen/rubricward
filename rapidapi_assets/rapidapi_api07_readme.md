# AIA G702 G703 Schedule of Values SOV & Retainage Billing Generator API

**By RubricWard Preconstruction & DOT Systems** (`https://rubricward.com`)

Convert construction bid items into a balanced, front-load-compliant AIA G702 Application for Payment and G703 Continuation Sheet with retainage math.

---

## Key Capabilities & Construction Preconstruction Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes project manuals, DOT pay items, Davis-Bacon wage classifications, and AIA billing schedules in memory.
- **Built for ConTech ERPs, Heavy-Civil Estimators & Surety Underwriters:** Ready to plug directly into Procore, Autodesk Construction Cloud, HeavyBid workflows, or AI estimating agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/generate/aia-g702-g703-pay-app`

---

## Example Request Payload

```json
{
  "project_name": "City of Austin Walnut Creek WWTP Digester Rehab",
  "application_number": 4,
  "retainage_pct": 5.0,
  "sov_lines": [
    {
      "item_no": "01",
      "description": "Mobilization, Bonds & Submittals",
      "scheduled_value_usd": 380000,
      "prev_completed_usd": 380000,
      "this_period_usd": 0,
      "stored_materials_usd": 0
    },
    {
      "item_no": "02",
      "description": "Cast-in-Place Structural Digester Wall Rehab",
      "scheduled_value_usd": 1950000,
      "prev_completed_usd": 820000,
      "this_period_usd": 465000,
      "stored_materials_usd": 115000
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
