# Changelog

## v1.0.0 — Initial Build (2026-05-13)

### Added
- Five-layer architecture: sensing → twin → forecast → policy → tower
- Contract definitions (TelemetryEvent, ForecastResult, ReorderDecision, etc.)
- In-memory event bus for inter-service communication
- L1: Data ingestion with normalization and dead-letter queue
- L2: Digital twin with scenario simulation (copper shock, weather, supplier outage)
- L3: LightGBM demand forecaster + Croston baseline for intermittent parts
- L3: Feature store with lag, rolling, cyclic, and supply-side features
- L3: Bias guardrail (30-day rolling, ±5% threshold)
- L4: Safety stock formula per spec §4.4
- L4: MEIO solver (factory → DC → branch) using PuLP
- L5: FastAPI gateway with /forecast, /scenario, /reorder, /alerts
- L5: Autonomous response rules engine
- L5: Closed-loop feedback writer
- Comprehensive tests: unit, integration, contract, scenario
