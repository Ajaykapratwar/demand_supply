# Assumptions (per HVAC Cognitive Control Tower §3)

## Resolved Assumptions

1. **Deployment target:** Local development. Services communicate via in-memory event bus (no Kafka/cloud in v1).
2. **SKU cardinality:** ~10 SKUs detected in dataset (SKU001–SKU010). Hero SKUs defined as top-20% by volume.
3. **Historical data:** 2018–2024+ available (~6 years, exceeds 24-month minimum for LightGBM training).
4. **IoT hardware:** Simulated telemetry for v1. Synthetic sensor data generated from equipment performance curves.
5. **Service-level target:** Using 96% for critical parts, 98% for mission-critical equipment per §4.4 spec. The 95% value in other sections is treated as a minimum floor.

## Conservative Interpretations

- Lead-time distribution assumed normal with σ_L = 1.2 days (within ≤1.5 day constraint).
- Default Z = 1.65 (95th percentile) for safety stock, overridable per SKU class.
- Carrying cost rate: 20% annually (midpoint of 18–25% range), = ~1.67%/month.
- Regions: North, South, East, West (4 regions from dataset).
- Warehouses: WH001–WH050 (from logistics dataset).
