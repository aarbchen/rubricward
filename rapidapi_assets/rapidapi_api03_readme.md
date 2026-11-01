# Davis-Bacon 29 CFR 5 & State Prevailing Wage Fringe Calculator API

**By RubricWard Preconstruction & DOT Systems** (`https://rubricward.com`)

Calculate federal Davis-Bacon (29 CFR Part 5) and State Little Davis-Bacon prevailing wage base rates, fringe burdens, and WH-347 payroll costs.

---

## Key Capabilities & Construction Preconstruction Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes project manuals, DOT pay items, Davis-Bacon wage classifications, and AIA billing schedules in memory.
- **Built for ConTech ERPs, Heavy-Civil Estimators & Surety Underwriters:** Ready to plug directly into Procore, Autodesk Construction Cloud, HeavyBid workflows, or AI estimating agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/calculate/davis-bacon-prevailing-wage`

---

## Example Request Payload

```json
{
  "state_code": "TX",
  "county_name": "Harris County",
  "construction_type": "Highway",
  "crew_classifications": [
    {
      "trade": "Power Equipment Operator (Asphalt Paver / Roller)",
      "estimated_hours": 1450
    },
    {
      "trade": "Cement Mason / Concrete Finisher",
      "estimated_hours": 980
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
