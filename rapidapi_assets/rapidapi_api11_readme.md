# DOT Planholder List Competitor Bid Behavior & MLOT Analyzer API

**By RubricWard Preconstruction & DOT Systems** (`https://rubricward.com`)

Analyze official DOT planholder lists against historical head-to-head letting results to predict aggressive bidders, Margin Left on Table (MLOT), and optimal markup.

---

## Key Capabilities & Construction Preconstruction Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes project manuals, DOT pay items, Davis-Bacon wage classifications, and AIA billing schedules in memory.
- **Built for ConTech ERPs, Heavy-Civil Estimators & Surety Underwriters:** Ready to plug directly into Procore, Autodesk Construction Cloud, HeavyBid workflows, or AI estimating agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/analyze/planholder-competitor-spread`

---

## Example Request Payload

```json
{
  "letting_id": "GDOT-PI-0017482",
  "engineers_estimate_usd": 9400000,
  "our_direct_cost_usd": 8150000,
  "planholders": [
    {
      "contractor_name": "C.W. Matthews Contracting Co.",
      "historical_avg_vs_engineer_pct": -4.2,
      "recent_win_rate_pct": 34.0
    },
    {
      "contractor_name": "E.R. Snell Contractor Inc.",
      "historical_avg_vs_engineer_pct": -2.8,
      "recent_win_rate_pct": 28.5
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
