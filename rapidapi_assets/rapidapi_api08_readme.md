# Miller Act 40 USC 3131 & Surety Bond Capacity Underwriter API

**By RubricWard Preconstruction & DOT Systems** (`https://rubricward.com`)

Underwrite contractor working capital, net worth, and WIP backlog to calculate Single/Aggregate Surety Bond limits and sliding-scale bond premiums.

---

## Key Capabilities & Construction Preconstruction Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes project manuals, DOT pay items, Davis-Bacon wage classifications, and AIA billing schedules in memory.
- **Built for ConTech ERPs, Heavy-Civil Estimators & Surety Underwriters:** Ready to plug directly into Procore, Autodesk Construction Cloud, HeavyBid workflows, or AI estimating agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/audit/surety-miller-act-bond`

---

## Example Request Payload

```json
{
  "contractor_name": "Lone Star Heavy Civil Constructors Inc.",
  "current_assets_usd": 6400000,
  "current_liabilities_usd": 2950000,
  "tangible_net_worth_usd": 5100000,
  "uncompleted_wip_backlog_usd": 19500000,
  "target_project_bid_usd": 11200000
}
```

---

## Pricing Tiers
- **BASIC (`$0 / mo`):** `10 requests / month` hard limit (`10 requests / hour` rate limit) for testing and evaluation.
- **PRO (`$49 / mo`):** `200 requests / month` for active estimating teams and specialty subcontractors.
- **ULTRA (`$149 / mo` — Recommended):** `1,000 requests / month` for regional general contractors and heavy-civil primes.
- **MEGA (`$399 / mo`):** `4,000 requests / month` for ConTech SaaS platforms, surety brokerages, and multi-office builders.
