# Construction RFI Differing Site Conditions & AIA G701 Change Order API

**By RubricWard Preconstruction & DOT Systems** (`https://rubricward.com`)

Analyze plan discrepancies or Differing Site Conditions (FAR 52.236-2), calculate Critical Path Time-Impact float consumption, and draft AIA G701 Change Orders.

---

## Key Capabilities & Construction Preconstruction Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes project manuals, DOT pay items, Davis-Bacon wage classifications, and AIA billing schedules in memory.
- **Built for ConTech ERPs, Heavy-Civil Estimators & Surety Underwriters:** Ready to plug directly into Procore, Autodesk Construction Cloud, HeavyBid workflows, or AI estimating agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/generate/rfi-change-order-claim`

---

## Example Request Payload

```json
{
  "project_name": "USACE Norfolk District Floodwall Sector Gate Monolith",
  "contract_clause_reference": "FAR 52.236-2 Differing Site Conditions (Type I)",
  "field_condition_description": "Geotechnical boring log B-14 indicated stiff clay at El. -18.0 FT, but sheet-pile driving encountered uncharted submerged timber wharf pilings and granite riprap from El. -11.5 FT to -19.0 FT.",
  "direct_cost_impact_usd": 184500,
  "critical_path_delay_days": 14
}
```

---

## Pricing Tiers
- **BASIC (`$0 / mo`):** `10 requests / month` hard limit (`10 requests / hour` rate limit) for testing and evaluation.
- **PRO (`$49 / mo`):** `200 requests / month` for active estimating teams and specialty subcontractors.
- **ULTRA (`$149 / mo` — Recommended):** `1,000 requests / month` for regional general contractors and heavy-civil primes.
- **MEGA (`$399 / mo`):** `4,000 requests / month` for ConTech SaaS platforms, surety brokerages, and multi-office builders.
