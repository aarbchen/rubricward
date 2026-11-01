# Build America Buy America BABA & 23 CFR 635.410 Material Auditor API

**By RubricWard Preconstruction & DOT Systems** (`https://rubricward.com`)

Audit construction Bills of Materials against Build America, Buy America (BABA) and FHWA 23 CFR 635.410 domestic iron, steel, and manufactured product rules.

---

## Key Capabilities & Construction Preconstruction Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes project manuals, DOT pay items, Davis-Bacon wage classifications, and AIA billing schedules in memory.
- **Built for ConTech ERPs, Heavy-Civil Estimators & Surety Underwriters:** Ready to plug directly into Procore, Autodesk Construction Cloud, HeavyBid workflows, or AI estimating agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/audit/baba-buy-america`

---

## Example Request Payload

```json
{
  "project_name": "PennDOT I-81 Composite Bridge Deck Replacement",
  "funding_agency": "FHWA / DOT",
  "bom_items": [
    {
      "material_name": "ASTM A709 Grade 50W Structural Steel Plate Girders",
      "category": "Iron/Steel",
      "country_of_melt_and_pour": "US",
      "domestic_cost_pct": 100.0,
      "extended_cost_usd": 1420000
    },
    {
      "material_name": "Elastomeric Bridge Bearing Pads",
      "category": "Construction Material",
      "country_of_melt_and_pour": "US",
      "domestic_cost_pct": 92.0,
      "extended_cost_usd": 84000
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
