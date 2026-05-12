# HVAC Cognitive Control Tower — AI Agent Build Instructions
**Document Type:** System Design & Build Methodology for AI Coding Agent
**Target Reader:** Claude (or equivalent AI engineering agent) operating under CLAUDE.md
**Mission:** Implement the five-layer HVAC Demand-Supply Cognitive Control Tower end-to-end, with verifiable testing at every layer.

---

## 0. How to Read This Document (Agent Protocol)
Before writing any code, the agent **MUST** follow the CLAUDE.md discipline:

1. **Think before coding.** State assumptions, surface ambiguity, propose the simplest viable path.
2. **Simplicity first.** Build the minimum that satisfies the success criteria in §10. No speculative abstractions.
3. **Surgical changes.** Each commit traces to one numbered task below.
4. **Goal-driven execution.** Every task in §9 has a `verify:` clause. Do not mark a task done until its verification passes.

If any requirement below conflicts with CLAUDE.md, stop and ask — do not silently reconcile.

---

## 1. System Intent (One Paragraph)
Build a closed-loop "Sensing-to-Steering" platform that ingests IoT telemetry, weather, ERP, and regulatory signals; forecasts HVAC equipment and spare-parts demand at ≥80% accuracy (1 − WAPE); simulates supply scenarios on a digital twin; optimizes multi-echelon inventory with RL agents; and autonomously executes re-routing, reorder, and dispatch actions. Anything outside this scope is out of scope.

---

## 2. Architectural Ground Rules
The agent will implement five layers as independently deployable services communicating over a typed event bus. This is non-negotiable because it is the only way each layer can be tested in isolation.

| Layer | Service Name | Primary Tech | Owns |
|---|---|---|---|
| L1 Ingestion | sensing-svc | Kafka + NiFi connectors | Raw signal normalization |
| L2 Digital Twin | twin-svc | Python + BIM/thermo models | Scenario simulation |
| L3 Intelligence | forecast-svc | LightGBM, LSTM, Temporal CNN | Predictions |
| L4 Optimization | policy-svc | Ray RLlib, MEIO solver | Reorder & allocation decisions |
| L5 Orchestration | tower-svc | FastAPI + React dashboard | Execution & UI |

**Inter-service contract:** Protobuf schemas in `/contracts`. No service may read another's database.

---

## 3. Pre-Build Clarifications the Agent Must Resolve
Per CLAUDE.md §1, before writing code the agent asks the user (or records explicit assumptions) for:

1. **Deployment target:** cloud (AWS/Azure/GCP) or on-prem? Affects Kafka vs. managed equivalents.
2. **SKU cardinality:** confirm 2,000–5,000 SKU range and which qualify as "Hero SKUs."
3. **Historical data availability:** minimum 24 months of sales required for LightGBM training — is this available?
4. **Real IoT hardware vs. simulated telemetry** for the first milestone?
5. **Service-level target:** design doc cites both 95% and 98% — which is the contractual target for policy-svc?

If unanswered, the agent records assumptions at the top of `/docs/ASSUMPTIONS.md` and proceeds with the most conservative interpretation.

---

## 4. Layer-by-Layer Build Methodology

### 4.1 Layer 1 — Data Perception & Ingestion
**Build order:**
1. Define Protobuf schemas: `TelemetryEvent`, `WeatherEvent`, `ERPEvent`, `RegulatoryEvent`.
2. Implement Kafka topics: one per event type, partitioned by `site_id`.
3. Write connectors: NOAA API poller (15-min cadence), ERP CDC reader, IoT MQTT bridge.
4. Add a dead-letter queue for malformed events. Nothing else fancy.

**Constraints:**
- Latency budget: edge-to-broker ≤ 10 ms for telemetry.
- Sensor node cost assumption: < $50/node (informs sampling rate, not code).
- Sampling interval: 1–5 min for vibration/pressure/refrigerant.

**Do NOT:** Add feature flags, multi-tenant routing, or schema-evolution tooling until L1 tests pass.

### 4.2 Layer 2 — Digital Twin & Simulation
**Build order:**
1. Ingest BIM geometry into a graph store (Neo4j or in-memory NetworkX for v1).
2. Implement thermodynamic performance curves per equipment class (chiller, AHU, RTU).
3. Build a `Scenario` object: inputs (copper price Δ, weather shock, lead-time shock), outputs (inventory trajectory, fill-rate trajectory).
4. Implement BOM Health monitor: poll component lifecycle feed, flag EOL ≤ 12 months → emit `LastTimeBuy` event.

**Verification:** A copper +10% scenario must complete in < 30 s and produce a monotonically reasonable cost delta.

### 4.3 Layer 3 — Intelligence & Inference
**Build order:**
1. Feature store: derive features from L1 topics; persist in Parquet partitioned by date.
2. LightGBM + LASSO pipeline for equipment demand. Target: R² ≥ 0.91 on holdout.
3. LSTM / Temporal CNN for intermittent parts. Target: outperform Croston baseline on WAPE.
4. Pattern decomposition module: STL or Prophet-style organic vs. promo split.
5. Model registry: MLflow. One model per SKU class, versioned.
6. Bias guardrail: Each model emits a 30-day rolling bias metric; CI fails if |bias| > 5%.

### 4.4 Layer 4 — Policy & Decision Optimization
**Build order:**
1. Implement the safety-stock formula exactly as specified:

$$SS = Z \times \sqrt{(L_{avg} \cdot \sigma_D^2) + (D_{avg}^2 \cdot \sigma_L^2)}$$

with Z = 1.65 default, overridable per SKU class.

2. MEIO solver: linear program coordinating factory → DC → branch. Use OR-Tools first; only swap to Gurobi if LP exceeds 5-minute solve time.
3. Ray RLlib agent: observation = (inventory, demand forecast, lead-time distribution); action = (reorder qty, safety-stock multiplier); reward = −(holding cost + stockout penalty).
4. Train RL in the Digital Twin (L2). Do not let it touch production until shadow-mode KPIs match MEIO baseline ± 2%.

**Inventory targets enforced in optimizer constraints:**
- Turnover 4.0–6.0×/yr
- Carrying cost 18–25%
- Fill rate ≥ 96% (critical), ≥ 98% (mission-critical)
- σ_L ≤ 1.5 days (input constraint; if violated, raise alert, do not silently absorb)

### 4.5 Layer 5 — Orchestration & Execution
**Build order:**
1. FastAPI gateway exposing: `/forecast`, `/scenario`, `/reorder`, `/alerts`.
2. React dashboard with exactly the five widgets specified (Demand Heatmap, ABC-XYZ Matrix, Lead-Time Gauge, Stockout Alerts, Service-Level Toggle). No additional widgets in v1.
3. Autonomous response rules engine: triggers within 30 s for logistics events, 5–20 min for mission-critical equipment failures.
4. Closed-loop writer: persists actual outcomes back to the Digital Twin for model retraining.

**Surgical-change rule:** When adding a widget, the agent does not restyle existing widgets. Match existing CSS even if suboptimal.

---

## 5. Data & Event Contracts (Authoritative)
All contracts live in `/contracts/*.proto`. Breaking changes require a version bump and a migration note in `/docs/CHANGELOG.md`. No service mutates another service's schema.

**Minimum required messages:** `TelemetryEvent`, `ForecastResult`, `ReorderDecision`, `ScenarioRequest`, `ScenarioResult`, `AnomalyAlert`.

---

## 6. Testing Framework (End-to-End)
Testing is layered to match the architecture. Each layer has unit, integration, and contract tests; the full system has scenario, chaos, and acceptance tests.

### 6.1 Unit Tests (per service)
- Tooling: pytest + hypothesis for property tests.
- Coverage gate: ≥ 85% lines on forecast-svc and policy-svc; ≥ 70% elsewhere.
- Property tests for the safety-stock formula: monotonicity in σ_D, σ_L; Z=0 ⇒ SS=0.

### 6.2 Contract Tests
- Tooling: Pact or protobuf-compat-check.
- Rule: CI fails if any consumer's expected schema diverges from producer's published schema.

### 6.3 Integration Tests (per layer pair)
- Spin up L1+L3 with docker-compose; inject 10k synthetic events; assert forecast service consumes without lag > 5 s.
- Spin up L3+L4; feed canned forecasts; assert reorder decisions respect turnover and fill-rate bounds.

### 6.4 Model Validation Tests
- Backtest harness: rolling-origin evaluation, 12 folds.
- Pass criteria:
  - Equipment demand: R² ≥ 0.91 mean, ≥ 0.85 worst fold.
  - 1 − WAPE ≥ 80% for Hero SKUs.
  - Bias within ±5%.
  - Intermittent parts: WAPE beats Croston by ≥ 15%.
- Drift monitor: Population Stability Index > 0.2 → auto-retrain trigger.

### 6.5 Simulation / Scenario Tests
Run these canonical scenarios against L2+L3+L4 weekly in CI:

1. Early September freeze (temp drop to <20°F two weeks early).
2. Copper +10% spot-price shock.
3. SEER2 transition cliff: 30% of catalog obsoletes in 60 days.
4. Tier-1 supplier outage: σ_L doubles for 30 days.

Each scenario asserts a documented expected response (e.g., scenario 1 must trigger pre-position of furnaces to northern DCs within the simulated 48 hours).

### 6.6 Chaos & Resilience Tests
- Tooling: Chaos Mesh or LitmusChaos.
- Drills: kill Kafka broker, drop 20% of IoT events, inject 2-second NOAA API latency. System must degrade gracefully — no silent data loss, alerts emitted within 60 s.

### 6.7 Performance Tests
- Edge-to-broker latency: p99 ≤ 10 ms.
- Forecast inference: p95 ≤ 200 ms per SKU.
- Scenario simulation: ≤ 30 s for a 90-day horizon.
- Autonomous orchestration decision: ≤ 30 s end-to-end.

### 6.8 Security & Compliance Tests
- Static analysis: bandit, semgrep.
- Secrets scan in CI.
- PII/customer data classification check on every new topic.

### 6.9 Acceptance Tests (the gate to "done")
A single `make acceptance` target runs:
1. Full backtest on 24 months of historical data.
2. The four canonical scenarios.
3. A 72-hour soak test with synthetic live traffic.

Pass criteria are the §10 success metrics, no exceptions.

---

## 7. CI/CD Pipeline (Minimum Viable)
Stages, in order: `lint → unit → contract → integration → model-validation → security → build → deploy-staging → scenario-tests → acceptance-gate → deploy-prod`.

A failed stage halts the pipeline. No manual overrides without a recorded exception in `/docs/EXCEPTIONS.md`.

---

## 8. Observability (Built In, Not Bolted On)
- **Metrics:** Prometheus. Required SLIs: forecast accuracy (daily), fill rate (hourly), σ_L (daily), inventory turnover (weekly), orchestration latency (per event).
- **Tracing:** OpenTelemetry across all five services.
- **Logging:** Structured JSON, correlation ID = `event_id` from L1.
- **Dashboards:** One Grafana board per layer; one executive board mirroring §3 of the design doc.

---

## 9. Build Plan (Numbered, Verifiable)
The agent executes in this order. Each step has an explicit `verify:` clause per CLAUDE.md §4.

1. Repo scaffold + contracts → **verify:** `protoc` compiles all `.proto`; CI green on empty services.
2. L1 sensing-svc → **verify:** 10k synthetic events ingested, p99 latency ≤ 10 ms, DLQ catches malformed inputs.
3. L3 forecast-svc (LightGBM only) → **verify:** backtest R² ≥ 0.91 on Hero SKUs; bias within ±5%.
4. L3 intermittent models → **verify:** WAPE beats Croston by ≥ 15% on parts holdout.
5. L2 twin-svc → **verify:** copper +10% scenario completes < 30 s, output reviewed by user.
6. L4 MEIO solver → **verify:** inventory drops 15–30% vs. baseline in twin replay, fill rate ≥ 96%.
7. L4 RLlib agent (shadow mode) → **verify:** matches MEIO ± 2% over a 30-day twin replay.
8. L5 tower-svc API + dashboard (5 widgets) → **verify:** each widget renders against live staging data; orchestration latency ≤ 30 s.
9. Closed-loop feedback writer → **verify:** actuals appear in twin within 5 min; next training run consumes them.
10. Acceptance gate → **verify:** §10 metrics all green; produce signed acceptance report.

If any step fails, the agent stops, reports, and does not begin the next step.

---

## 10. Success Criteria (The Only Things That Define "Done")

| # | Metric | Target |
|---|---|---|
| 1 | Forecast accuracy (1 − WAPE) on Hero SKUs | ≥ 80% |
| 2 | Forecast bias | ±5% |
| 3 | Equipment-demand R² | ≥ 0.91 |
| 4 | Fill rate (critical parts) | ≥ 96% |
| 5 | Inventory reduction vs. baseline | 15–30% |
| 6 | Inventory turnover | 4.0–6.0× |
| 7 | Carrying cost rate | 18–25% |
| 8 | Lead-time variability σ_L | ≤ 1.5 days |
| 9 | IoT fault warning lead time | 4–8 weeks |
| 10 | Autonomous orchestration latency | ≤ 30 s |
| 11 | Edge processing latency p99 | ≤ 10 ms |
| 12 | Acceptance suite | All green |

Anything not on this table is out of scope for v1.

---

## 11. Anti-Goals (What the Agent Must NOT Do)
- Do not add a "user management" or "RBAC" subsystem unless asked — staging uses a static token.
- Do not introduce a second forecasting library "for flexibility."
- Do not refactor the safety-stock formula into a generic optimizer.
- Do not extend the dashboard beyond the five specified widgets.
- Do not delete pre-existing code the agent finds unfamiliar. Flag it in `/docs/NOTES.md` instead.
- Do not silently reconcile the 95% vs. 98% service-level discrepancy — escalate per §3.

---

## 12. Handover Artifacts
On completion, the agent delivers:

1. Running services with `docker-compose up` bringing the whole stack online.
2. `/docs/ASSUMPTIONS.md`, `/docs/CHANGELOG.md`, `/docs/EXCEPTIONS.md`, `/docs/ACCEPTANCE_REPORT.md`.
3. A 1-page diff summary showing every change traces to a numbered task in §9.
4. Grafana dashboards exported as JSON in `/observability`.
5. A short README explaining how to run the acceptance suite locally.

---

*End of instructions. The agent should now restate its understanding, list any ambiguities from §3, and propose a start date for Task 1 before writing code.*
