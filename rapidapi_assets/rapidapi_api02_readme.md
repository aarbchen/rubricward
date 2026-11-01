# 50-State DOT Historical Item Bid Tabulation & Spread Modeler API

**By RubricWard Preconstruction & DOT Systems** (`https://rubricward.com`)

Model 50-State DOT historical unit-price bid tabulations ($/Ton, $/LF, $/CY), low/median/high bidder spreads, and recommended unit bid prices.

---

## Key Capabilities & Construction Preconstruction Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes project manuals, DOT pay items, Davis-Bacon wage classifications, and AIA billing schedules in memory.
- **Built for ConTech ERPs, Heavy-Civil Estimators & Surety Underwriters:** Ready to plug directly into Procore, Autodesk Construction Cloud, HeavyBid workflows, or AI estimating agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/model/dot-unit-bid-tabs`

---

## Example Request Payload

```json
{
  "state_code": "TX",
  "dot_agency": "TxDOT",
  "letting_quarter": "2026-Q4",
  "pay_items": [
    {
      "item_code": "3076-6001",
      "description": "Dense-Graded Hot-Mix Asphalt (Superpave)",
      "unit": "TON",
      "quantity": 18500
    },
    {
      "item_code": "0464-6008",
      "description": "Reinforced Concrete Pipe (Class III 36-Inch)",
      "unit": "LF",
      "quantity": 2400
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
