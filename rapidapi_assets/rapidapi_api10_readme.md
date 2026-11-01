# OSHA 29 CFR 1926 USACE EM 385-1-1 AHA & Insurance EMR Auditor API

**By RubricWard Preconstruction & DOT Systems** (`https://rubricward.com`)

Generate trade-specific Activity Hazard Analyses (AHA), Site-Specific Safety Plans, Trenching/Fall-Protection checklists, and Experience Modification Rate (EMR) audits.

---

## Key Capabilities & Construction Preconstruction Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes project manuals, DOT pay items, Davis-Bacon wage classifications, and AIA billing schedules in memory.
- **Built for ConTech ERPs, Heavy-Civil Estimators & Surety Underwriters:** Ready to plug directly into Procore, Autodesk Construction Cloud, HeavyBid workflows, or AI estimating agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/audit/osha-emr-site-safety`

---

## Example Request Payload

```json
{
  "project_name": "Caltrans District 7 Deep Storm Drain Box Culvert Excavation",
  "contractor_emr": 0.84,
  "max_allowed_emr": 1.0,
  "high_hazard_activities": [
    "Trenching & Shoring below 18 FT in Type C Soil (29 CFR 1926 Subpart P)",
    "Crawler Crane 110-Ton Precast Box Culvert Picks near energized 34.5kV overhead lines"
  ]
}
```

---

## Pricing Tiers
- **BASIC (`$0 / mo`):** `10 requests / month` hard limit (`10 requests / hour` rate limit) for testing and evaluation.
- **PRO (`$49 / mo`):** `200 requests / month` for active estimating teams and specialty subcontractors.
- **ULTRA (`$149 / mo` — Recommended):** `1,000 requests / month` for regional general contractors and heavy-civil primes.
- **MEGA (`$399 / mo`):** `4,000 requests / month` for ConTech SaaS platforms, surety brokerages, and multi-office builders.
