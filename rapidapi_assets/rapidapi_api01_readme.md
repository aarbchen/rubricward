# CSI MasterFormat Divisions 00-48 Spec & Submittal Shredder API

**By RubricWard Preconstruction & DOT Systems** (`https://rubricward.com`)

Shred raw Construction Project Manuals into CSI MasterFormat Divisions 00-48 tables, submittal logs, liquidated damages, and retainage rules.

---

## Key Capabilities & Construction Preconstruction Use Cases
- **Stateless & Deterministic:** Zero database side effects; processes project manuals, DOT pay items, Davis-Bacon wage classifications, and AIA billing schedules in memory.
- **Built for ConTech ERPs, Heavy-Civil Estimators & Surety Underwriters:** Ready to plug directly into Procore, Autodesk Construction Cloud, HeavyBid workflows, or AI estimating agents via `@rubricward/mcp-server`.
- **Route:** `POST /v1/shred/csi-masterformat`

---

## Example Request Payload

```json
{
  "project_name": "TxDOT IH-45 Corridor Mill & Superpave Overlay",
  "solicitation_number": "CSJ-0912-72-614",
  "state_code": "TX",
  "specification_text": "SECTION 01 11 00 SUMMARY OF WORK: Liquidated damages of $2,500/calendar day apply beyond 240 calendar days. Retainage 5%. SECTION 03 30 00 CAST-IN-PLACE CONCRETE: Submit mix design and mill certs. SECTION 32 12 16 ASPHALT PAVING: TxDOT Item 3076 Superpave D-GR-B 18,500 Tons."
}
```

---

## Pricing Tiers
- **BASIC (`$0 / mo`):** `10 requests / month` hard limit (`10 requests / hour` rate limit) for testing and evaluation.
- **PRO (`$49 / mo`):** `200 requests / month` for active estimating teams and specialty subcontractors.
- **ULTRA (`$149 / mo` — Recommended):** `1,000 requests / month` for regional general contractors and heavy-civil primes.
- **MEGA (`$399 / mo`):** `4,000 requests / month` for ConTech SaaS platforms, surety brokerages, and multi-office builders.
