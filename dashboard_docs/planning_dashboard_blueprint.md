# AI-Powered Demand-Supply & Matching Planning Dashboard
## System Engineering Blueprint — Implementation-Ready Reference

**Document Version:** 1.0  
**Classification:** Principal Architecture Handoff  
**Audience:** Autonomous AI Engineering Agent / Senior Engineering Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Consolidated System Architecture](#2-consolidated-system-architecture)
3. [Functional Module Breakdown](#3-functional-module-breakdown)
4. [Data Architecture & Schema Design](#4-data-architecture--schema-design)
5. [AI/ML Methodology](#5-aiml-methodology)
6. [Development Methodology](#6-development-methodology)
7. [Testing & Validation Framework](#7-testing--validation-framework)
8. [Assumptions & Gap Resolution](#8-assumptions--gap-resolution)
9. [AI-Agent Execution Optimization](#9-ai-agent-execution-optimization)

---

## 1. Executive Summary

### 1.1 System Purpose

This system is an **enterprise-grade, AI-powered Planning Dashboard** for Demand-Supply & Matching use cases. It serves as the primary decision-intelligence interface, converting raw forecasting engine outputs and operational data into actionable plans, scenario comparisons, and prescriptive recommendations for multi-stakeholder supply chain organizations.

### 1.2 Core Objectives

- **Align demand and supply plans** across short (0–4 weeks), mid (1–12 months), and long (12–36+ months) planning horizons.
- **Minimize total cost to serve** — encompassing inventory, logistics, production, and expediting costs.
- **Maximize service level** (OTIF, fill rate) and revenue within risk, budget, and sustainability constraints.
- **Reduce planning cycle time** through AI copilots, scenario automation, and inline action queues.
- **Make trade-offs explicit and quantifiable** — cost vs. service vs. carbon vs. risk — via multi-objective scenario comparison.

### 1.3 Business/Operational Goals

| Goal | Metric | Target Direction |
|---|---|---|
| Demand-supply balance | Stockout Rate, Overstock Risk | Minimize |
| Inventory cost minimization | Inventory Carrying Cost, DOS | Minimize |
| Service excellence | OTIF, Fill Rate | Maximize |
| Forecast quality | MAPE, WAPE, Bias, FVA | Improve |
| Agility | Planning Cycle Time, Exception Rate | Reduce |
| Sustainability | Carbon Scope 1/2/3 | Meet SBTi targets |
| Financial performance | EVA, ROIC, Margin | Maximize |

### 1.4 Key Technical Capabilities

- Multi-horizon planning views (operational / tactical / strategic)
- Probabilistic demand forecasting with confidence intervals and fan charts
- What-if scenario engine with constraint-based optimization (Monte Carlo, sensitivity analysis)
- Role-based dashboards for 6+ distinct stakeholder types
- AI Copilot with natural language query interface
- Real-time and batch data ingestion from ERP, WMS, POS, MES, SRM, HR systems
- Anomaly detection, FVA analysis, and root-cause attribution
- Explainable AI (SHAP/LIME) integrated into recommendation surfaces
- Approval workflows, collaborative annotations, and plan versioning

---

## 2. Consolidated System Architecture

### 2.1 Architecture Overview

The system is organized into four major tiers: **Data Sources → Data & AI Platform → Planning Application → Users & Roles**. All tiers communicate via event-driven and API-based integration.

```
┌─────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                         │
│  ERP │ POS/Channels │ WMS/TMS │ MES │ SRM │ HR │ External  │
└──────────────────────────┬──────────────────────────────────┘
                           │ Batch + Streaming (Kafka/Kinesis)
┌──────────────────────────▼──────────────────────────────────┐
│                   DATA & AI PLATFORM                        │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │Data Lakehouse│  │Stream Process│  │  AI Services Layer │ │
│  │(Databricks / │  │(Flink/Spark  │  │  Forecast Engine   │ │
│  │ Snowflake /  │  │ Streaming)   │  │  Optimization Svc  │ │
│  │ Fabric)      │  │              │  │  Anomaly Detection │ │
│  └──────┬───────┘  └──────┬───────┘  │  NLP/Copilot       │ │
│         └─────────────────┴──────────┤  Risk Scoring      │ │
│                                      └────────┬───────────┘ │
│                               ┌───────────────▼──────────┐  │
│                               │  Scenario & Simulation    │  │
│                               │  Engine (Monte Carlo,     │  │
│                               │  Constraint Optimization) │  │
│                               └───────────────┬──────────┘  │
└───────────────────────────────────────────────┼─────────────┘
                                                │ REST/GraphQL
┌───────────────────────────────────────────────▼─────────────┐
│                    PLANNING APPLICATION                      │
│  ┌──────────────────┐   ┌──────────────────────────────────┐│
│  │ API & Microservs │   │   Planning Dashboards (React)    ││
│  │ (Node.js/Python) │   │   9 Dashboard Views              ││
│  │                  │   │   Role-Based Personalization      ││
│  └──────────────────┘   └──────────────────────────────────┘│
│  ┌──────────────────┐   ┌──────────────────────────────────┐│
│  │   AI Copilot &   │   │    Approval Workflow Engine       ││
│  │   NLP Interface  │   │    Annotations / Versioning       ││
│  └──────────────────┘   └──────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────┐
│                     USERS & ROLES                           │
│  CXO │ Demand Planners │ SC Managers │ Ops │ Finance │ Sales│
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Component Definitions

| Component | Technology | Responsibility |
|---|---|---|
| Data Lakehouse | Databricks / Snowflake / MS Fabric | Central governed repository; star schema; data products |
| Stream Processing | Apache Kafka + Apache Flink or Spark Streaming | Real-time order/shipment/IoT event ingestion |
| Forecast Engine | Python (scikit-learn, Prophet, PyTorch), MLflow | Multi-model demand forecasting, ensemble, quantile |
| Optimization Service | Python (OR-Tools / Gurobi / PuLP) | Constraint-based allocation, replenishment, scheduling |
| Anomaly Detection | Isolation Forest, LSTM Autoencoders | Data quality, demand spikes, supply disruptions |
| NLP / Copilot | LLM (OpenAI / Anthropic API) + LangChain | Natural language querying, narrative insight generation |
| Risk Scoring | Gradient Boosting (XGBoost/LightGBM) + SHAP | Composite risk score by SKU/lane/supplier |
| Scenario Engine | Monte Carlo (NumPy/SciPy), Sensitivity (SALib) | What-if simulation, scenario branching, Pareto frontiers |
| API Layer | Node.js (Express) or FastAPI (Python) | REST + GraphQL endpoints; auth; RBAC |
| Frontend | React 18 + TypeScript + ECharts/Recharts/Plotly | 9 dashboard views; role-based personalization |
| Approval Engine | Custom workflow (state machine) + BullMQ | Plan submission, approval, rejection, versioning |
| Auth | Auth0 / Keycloak (OIDC/SCIM) | SSO, RBAC, row-level security |
| Observability | OpenTelemetry + Grafana + Prometheus | Distributed tracing, metrics, alerting |

### 2.3 Communication Protocols

| Integration | Protocol | Notes |
|---|---|---|
| Frontend ↔ API | REST (JSON) + GraphQL subscriptions | GraphQL for real-time KPI feeds via WebSocket |
| AI Services ↔ API | gRPC (internal) | Low-latency inference calls |
| Lakehouse ↔ AI Services | Apache Arrow / Parquet over S3/ADLS | Feature store reads |
| Stream Processing ↔ Lakehouse | Kafka Connect / Delta Live Tables | CDC, micro-batch landing |
| External Systems (ERP/WMS) | REST APIs, SFTP, JDBC connectors | Batch ingestion via orchestration (Airflow/Prefect) |
| Notifications | WebSocket + Email (SendGrid) + Slack | Threshold alerts, plan approvals |

### 2.4 Scalability Architecture

- **Stateless API services** horizontally scaled via Kubernetes (HPA on CPU/request latency).
- **AI inference services** run as separate deployments; heavy scenario simulations dispatched as async jobs (BullMQ/Celery) to prevent API blocking.
- **Pre-aggregated materialized views** (dbt models) in the lakehouse for dashboard query performance.
- **Redis cache** for hot KPI tile data (TTL: 5 minutes for operational, 1 hour for tactical).
- **Tenant-aware data partitioning** (schema-per-tenant or row-level tenant_id) for multi-tenancy.
- **CDN (Cloudflare)** for static React assets.

### 2.5 Fault Tolerance

- AI services implement **circuit breakers** (Hystrix pattern); fallback returns last-known-good forecast.
- **Kafka consumer groups** with at-least-once delivery and idempotent write logic.
- **Database read replicas** for dashboard queries (no read load on write primary).
- **Plan versioning** stored immutably; rollback to any prior approved version.
- All scenario simulations are **idempotent and replayable** via job ID.

---

## 3. Functional Module Breakdown

### Module 1: Data Ingestion & Integration

**Responsibility:** Collect, normalize, and land all source data into the lakehouse.

**Inputs:**
- ERP (SAP/Oracle): sales orders, purchase orders, production orders, master data
- WMS: inventory levels, warehouse transactions
- POS/Channels: point-of-sale actuals, e-commerce transactions
- MES: capacity utilization, production actuals, OEE
- SRM: supplier scorecards, lead times, allocation limits
- HR: shift schedules, absenteeism
- External APIs: weather (NOAA/OpenWeather), macroeconomic (FRED/Eurostat), news/risk feeds

**Outputs:** Normalized Parquet/Delta tables in lakehouse bronze and silver layers.

**Internal Logic:**
```
for each source:
  1. Extract (REST API / SFTP / JDBC connector)
  2. Validate schema, null checks, range checks
  3. Apply transformation (unit normalization, timezone, currency)
  4. Write to bronze layer (raw, append-only)
  5. Run dbt silver transformation (dedup, SCD2 for dimensions)
  6. Trigger downstream feature engineering job
```

**Error Handling:**
- Schema drift → quarantine record in `_quarantine` table; alert data engineer.
- Source downtime → retry with exponential backoff (max 5 retries); use last-known snapshot.
- Data quality failure (>5% nulls on critical field) → halt silver transformation; raise P2 alert.

**Dependencies:** Airflow/Prefect orchestration, Kafka (streaming), dbt Core.

---

### Module 2: Feature Store & Data Products

**Responsibility:** Produce governed, versioned, reusable feature sets for ML models and dashboard KPIs.

**Key Feature Groups:**

| Feature Group | Features | Refresh |
|---|---|---|
| demand_features | demand_mean_4w, demand_std_4w, yoy_growth, promo_flag, promo_uplift_pct | Daily |
| supply_features | supplier_reliability_score, lead_time_mean, lead_time_cv, capacity_available_pct | Daily |
| inventory_features | dos_current, safety_stock_days, stockout_probability, overstock_flag | Real-time |
| external_features | weather_severity_score, gdp_growth_qoq, inflation_rate, event_flag | Daily/Monthly |
| model_features | forecast_mape_30d, forecast_bias_30d, fva_score, override_rate | Per forecast run |

**Outputs:** Feature tables in silver/gold layer; served via feature API (Feast or custom).

**State Management:** Point-in-time correct joins enforced; no future data leakage in training.

---

### Module 3: Forecasting Engine

**Responsibility:** Generate probabilistic, multi-horizon demand forecasts with accuracy tracking.

**Inputs:** Historical demand, seasonal calendars, promotion plans, external signals (weather, macro).

**Outputs per SKU-Location-Horizon:**
- `forecast_mean`: point forecast
- `forecast_p10`, `forecast_p50`, `forecast_p90`: quantile forecasts
- `confidence_band_width`: uncertainty measure
- `model_used`: champion model identifier
- `mape_30d`, `wape_30d`, `bias_30d`, `fva_score`: accuracy KPIs

**Model Pipeline:** Detailed in Section 5.

**API Interactions:**
- `POST /api/v1/forecast/run` → triggers forecast job, returns `job_id`
- `GET /api/v1/forecast/{sku_id}/{location_id}/{horizon}` → returns forecast record
- `GET /api/v1/forecast/accuracy` → returns aggregated accuracy KPIs

**Error Handling:** If champion model fails, challenger model is automatically promoted; fallback to naive seasonal model.

---

### Module 4: Inventory Optimization Service

**Responsibility:** Compute optimal safety stock targets, reorder points, and allocation rules.

**Inputs:** Forecasts (mean + quantiles), lead time distributions, service level targets, carrying cost rates.

**Outputs:**
- `safety_stock_units`: recommended safety stock
- `reorder_point`: trigger level for replenishment
- `target_dos`: days of supply target
- `recommended_allocation`: allocation split by customer/channel during constraint

**Calculation Logic:**
```
For each SKU-Location:
  sigma_demand = forecast_p90 - forecast_p50  // proxy for demand std
  sigma_lead_time = lead_time_std from supplier data
  z = norm.ppf(service_level_target)          // z-score for CSL
  safety_stock = z * sqrt(
    lead_time_mean * sigma_demand^2 +
    demand_mean^2 * sigma_lead_time^2
  )
  reorder_point = (demand_mean * lead_time_mean) + safety_stock
```

**What-If Simulation:**
- Slider input: `target_service_level` (85% → 99%)
- Output: Required safety stock units, working capital impact, stockout probability delta

---

### Module 5: Scenario & Simulation Engine

**Responsibility:** Generate, compare, and persist named scenarios with full KPI impact quantification.

**Supported Scenario Types** (see full table in Section 6 of research):

| Scenario | Core Simulation Logic |
|---|---|
| Best/Worst Case | Monte Carlo sampling over forecast distribution; N=10,000 runs |
| Demand Surge | Scale demand by region/category factor; re-run allocation optimization |
| Supply Disruption | Remove/cap supplier capacity; re-optimize network; compute service delta |
| Pricing Strategy | Apply price elasticity function; compute volume/margin/inventory impact |
| Capacity Constraint | Constrained optimization with penalty for overload |
| Sustainability Trade-off | Multi-objective Pareto optimization (cost vs carbon) |

**Scenario Schema:**
```json
{
  "scenario_id": "uuid",
  "name": "Demand Surge Q4 +30%",
  "type": "demand_surge",
  "base_plan_id": "uuid",
  "parameters": { "surge_factor": 1.30, "regions": ["APAC", "EMEA"] },
  "status": "completed",
  "outputs": {
    "total_cost_delta_usd": 450000,
    "service_level_delta_pct": -2.1,
    "carbon_delta_tco2": 120,
    "inventory_delta_units": 85000,
    "expediting_cost_usd": 75000
  },
  "created_at": "ISO8601",
  "created_by": "user_id"
}
```

**API:**
- `POST /api/v1/scenarios` → create & run scenario (async)
- `GET /api/v1/scenarios/{id}` → fetch results
- `GET /api/v1/scenarios/compare?ids=id1,id2,id3` → side-by-side KPI comparison

---

### Module 6: Dashboard Rendering Engine (Frontend)

**Responsibility:** Render 9 role-based dashboard views with real-time KPI tiles, charts, and interactive scenario controls.

**Technology:** | Framework | Plotly Dash (`dash`, `dash-core-components`, `dash-html-components`, `dash-bootstrap-components`) |
| Charting | `plotly.express`, `plotly.graph_objects` |
| Data | `pandas`, `numpy` (use realistic synthetic/mock data) |
| Styling | `dash-bootstrap-components` (theme: `dbc.themes.DARKLY` or `CYBORG`) |
| Layout | Multi-page via `dash.page_container` or tab-based navigation |
| State | Dash callbacks with `dcc.Store` for scenario state |

**9 Dashboard Views:**

| # | Dashboard | Primary Users | Key Widgets |
|---|---|---|---|
| 1 | Executive Summary | CXO, CEO, CFO | KPI cards, plan vs actual, scenario comparison, risk strip, AI brief |
| 2 | Operational Planning | Demand Planners, SC Managers | Supply-demand balance heatmap, inventory DOS gauges, action queue |
| 3 | Forecast Analytics | Demand Planners | Accuracy KPI cards, forecast vs actual, FVA waterfall, bias gauge |
| 4 | Inventory Optimization | SC Managers | Geo heatmap, service vs inventory scatter, safety stock simulator |
| 5 | Capacity Planning | Plant Managers, Ops | Utilization gauges, load profiles, Gantt-like capacity view |
| 6 | Financial Impact | Finance | Revenue/margin KPI cards, scenario P&L bridge waterfall, budget vs forecast |
| 7 | Risk Monitoring | SC Managers, Risk Teams | Risk score gauge, probability×impact heatmap, mitigation action table |
| 8 | Sustainability | ESG, Executives | Carbon KPI cards, emissions breakdown donut, Pareto scatter |
| 9 | Regional Planning | Regional Managers | Choropleth maps, region vs plan bars, local scenario sliders |

**Shared Layout Shell:**
```
[Top Nav: Logo | Horizon Selector | Global Filters | User | Notifications]
[Left Sidebar: Dashboard Nav Tree | Favorites]
[Main Content Area: Dashboard Widgets]
[Right Panel: AI Copilot / Alerts Feed (collapsible)]
```

**Global Filter State (Zustand store):**
```typescript
interface GlobalFilterState {
  horizon: 'operational' | 'tactical' | 'strategic';
  region: string[];
  businessUnit: string[];
  category: string[];
  dateRange: { start: Date; end: Date };
  scenario: string | null; // active scenario overlay
}
```

**Real-Time Updates:**
- WebSocket subscription for operational dashboard (orders, inventory levels).
- React Query polling (30s) for tactical dashboard KPIs.
- Manual refresh for strategic views.

---

### Module 7: AI Copilot & NLP Interface

**Responsibility:** Accept natural language queries from planners, return structured answers, charts, and recommendations; generate narrative summaries per dashboard.

**Architecture:**
```
User Query → Intent Classification (fine-tuned BERT or LLM prompt) →
  → Query Router:
      → "Data Query" → SQL generation → lakehouse → tabular response
      → "Scenario Request" → Scenario Engine API → result card
      → "Recommendation" → Recommendation Engine → ranked action list
      → "Explanation" → SHAP/feature importance retrieval → plain-language explanation
  → Response Formatter (text + optional chart spec)
  → Frontend Copilot Panel
```

**Narrative Insight Generation (per dashboard load):**
```
prompt = f"""
You are a supply chain planning analyst. Given these KPIs: {kpi_summary},
generate a 2-3 sentence executive brief identifying:
1. The most critical issue requiring action
2. The top opportunity
3. The primary risk
Be specific, quantitative, and direct.
"""
```

**API:**
- `POST /api/v1/copilot/query` → `{ query: string, context: GlobalFilterState }` → `{ response: string, chart_spec?: object, actions?: Action[] }`
- `GET /api/v1/copilot/narrative/{dashboard_id}` → `{ summary: string, insights: Insight[] }`

---

### Module 8: Approval Workflow & Versioning Engine

**Responsibility:** Route plan changes through configurable approval chains; maintain immutable version history.

**State Machine:**
```
DRAFT → SUBMITTED → [APPROVED | REJECTED | ESCALATED]
APPROVED → ACTIVE
ACTIVE → SUPERSEDED (when newer version approved)
```

**Plan Version Schema:**
```json
{
  "plan_version_id": "uuid",
  "plan_type": "demand | supply | consensus",
  "horizon": "tactical",
  "version_number": 3,
  "status": "APPROVED",
  "submitted_by": "user_id",
  "approved_by": "user_id",
  "scenario_id": "uuid | null",
  "kpi_snapshot": { "mape": 18.2, "otif": 94.1, "total_cost_usd": 4500000 },
  "diff_from_prior": { "cost_delta": -120000, "service_delta": 0.8 },
  "created_at": "ISO8601",
  "approved_at": "ISO8601"
}
```

**Notifications:** Email + in-app + Slack on state transitions.

---

### Module 9: RBAC & Security Layer

**Responsibility:** Enforce role-based access to dashboards, data, and actions.

**Roles:**

| Role | Dashboard Access | Data Scope | Action Permissions |
|---|---|---|---|
| EXECUTIVE | 1, 6, 7, 8 | All regions, aggregated | View only |
| DEMAND_PLANNER | 1, 2, 3 | Assigned categories | Submit forecasts, override |
| SC_MANAGER | 1, 2, 4, 7 | Assigned regions | Submit supply plans, approve transfers |
| PLANT_MANAGER | 5 | Assigned plants | View, update capacity |
| FINANCE | 6 | All, financial metrics | View, submit budget scenarios |
| ADMIN | All | All | Full |

**Row-Level Security:** Enforced at API layer (JWT claims → data filter injection into all queries).

**Column-Level Security:** Margin and cost data masked for PLANT_MANAGER role.

---

## 4. Data Architecture & Schema Design

### 4.1 Lakehouse Layer Model

```
Bronze (Raw):       Source-faithful, append-only, timestamped
Silver (Cleaned):   Deduplicated, type-cast, SCD2 dimensions, validated
Gold (Aggregated):  Business-level aggregations, KPI tables, feature tables
Serving (API):      Materialized views, Redis cache for dashboard queries
```

### 4.2 Core Fact Tables (Silver/Gold)

#### `fact_demand`
```sql
CREATE TABLE fact_demand (
  demand_id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  date_key          DATE NOT NULL,
  sku_id            VARCHAR(50) NOT NULL REFERENCES dim_product(sku_id),
  location_id       VARCHAR(50) NOT NULL REFERENCES dim_location(location_id),
  channel_id        VARCHAR(50) REFERENCES dim_channel(channel_id),
  customer_id       VARCHAR(50) REFERENCES dim_customer(customer_id),
  demand_units      DECIMAL(18,4) NOT NULL,
  demand_value_usd  DECIMAL(18,2),
  demand_type       VARCHAR(20) CHECK (demand_type IN ('actual','statistical','consensus')),
  promo_flag        BOOLEAN DEFAULT FALSE,
  promo_id          VARCHAR(50),
  source_system     VARCHAR(50),
  ingested_at       TIMESTAMP NOT NULL,
  INDEX idx_demand_sku_date (sku_id, date_key),
  INDEX idx_demand_location_date (location_id, date_key)
);
```

#### `fact_forecast`
```sql
CREATE TABLE fact_forecast (
  forecast_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  run_id            VARCHAR(50) NOT NULL,      -- forecast run identifier
  date_key          DATE NOT NULL,
  sku_id            VARCHAR(50) NOT NULL,
  location_id       VARCHAR(50) NOT NULL,
  horizon_type      VARCHAR(20) CHECK (horizon_type IN ('operational','tactical','strategic')),
  model_id          VARCHAR(50) NOT NULL,
  forecast_mean     DECIMAL(18,4),
  forecast_p10      DECIMAL(18,4),
  forecast_p50      DECIMAL(18,4),
  forecast_p90      DECIMAL(18,4),
  confidence_width  DECIMAL(18,4),
  mape_30d          DECIMAL(8,4),
  wape_30d          DECIMAL(8,4),
  bias_30d          DECIMAL(8,4),
  fva_score         DECIMAL(8,4),
  created_at        TIMESTAMP NOT NULL,
  INDEX idx_forecast_sku_date (sku_id, date_key),
  INDEX idx_forecast_run (run_id)
);
```

#### `fact_inventory`
```sql
CREATE TABLE fact_inventory (
  inventory_id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  snapshot_timestamp   TIMESTAMP NOT NULL,
  sku_id               VARCHAR(50) NOT NULL,
  location_id          VARCHAR(50) NOT NULL,
  on_hand_units        DECIMAL(18,4),
  in_transit_units     DECIMAL(18,4),
  allocated_units      DECIMAL(18,4),
  available_units      DECIMAL(18,4) GENERATED ALWAYS AS (on_hand_units - allocated_units),
  dos_current          DECIMAL(8,2),   -- days of supply
  safety_stock_target  DECIMAL(18,4),
  reorder_point        DECIMAL(18,4),
  stockout_probability DECIMAL(6,4),
  inventory_value_usd  DECIMAL(18,2),
  INDEX idx_inv_sku_ts (sku_id, snapshot_timestamp),
  INDEX idx_inv_stockout (stockout_probability)   -- for risk queries
);
```

#### `fact_supply`
```sql
CREATE TABLE fact_supply (
  supply_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  date_key            DATE NOT NULL,
  sku_id              VARCHAR(50) NOT NULL,
  supplier_id         VARCHAR(50) REFERENCES dim_supplier(supplier_id),
  location_id         VARCHAR(50) NOT NULL,
  planned_receipt_qty DECIMAL(18,4),
  confirmed_qty       DECIMAL(18,4),
  lead_time_days      DECIMAL(6,2),
  supply_type         VARCHAR(20) CHECK (supply_type IN ('purchase','transfer','production')),
  status              VARCHAR(20),
  INDEX idx_supply_sku_date (sku_id, date_key)
);
```

#### `fact_kpi_snapshot`
```sql
CREATE TABLE fact_kpi_snapshot (
  kpi_id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  snapshot_date       DATE NOT NULL,
  kpi_name            VARCHAR(100) NOT NULL,
  kpi_category        VARCHAR(50),         -- forecast, inventory, service, financial, etc.
  dimension_type      VARCHAR(50),         -- global, region, category, sku
  dimension_value     VARCHAR(200),
  kpi_value           DECIMAL(18,6),
  kpi_unit            VARCHAR(20),         -- pct, units, usd, days, score
  target_value        DECIMAL(18,6),
  threshold_warning   DECIMAL(18,6),
  threshold_critical  DECIMAL(18,6),
  INDEX idx_kpi_date_name (snapshot_date, kpi_name),
  INDEX idx_kpi_category (kpi_category)
);
```

### 4.3 Dimension Tables

#### `dim_product`
```sql
CREATE TABLE dim_product (
  sku_id          VARCHAR(50) PRIMARY KEY,
  sku_name        VARCHAR(200),
  category_l1     VARCHAR(100),
  category_l2     VARCHAR(100),
  brand           VARCHAR(100),
  lifecycle_stage VARCHAR(30) CHECK (lifecycle_stage IN ('intro','growth','mature','decline','eol')),
  abc_class       CHAR(1),     -- A/B/C demand classification
  xyz_class       CHAR(1),     -- X/Y/Z volatility classification
  unit_of_measure VARCHAR(20),
  unit_cost_usd   DECIMAL(12,4),
  lead_time_days  DECIMAL(6,2),
  is_active       BOOLEAN DEFAULT TRUE,
  valid_from      DATE,
  valid_to        DATE,        -- SCD2 handling
  is_current      BOOLEAN DEFAULT TRUE
);
```

#### `dim_location`
```sql
CREATE TABLE dim_location (
  location_id     VARCHAR(50) PRIMARY KEY,
  location_name   VARCHAR(200),
  location_type   VARCHAR(30) CHECK (location_type IN ('plant','dc','store','supplier','port')),
  country         VARCHAR(3),   -- ISO 3166-1 alpha-3
  region          VARCHAR(50),
  cluster         VARCHAR(50),
  latitude        DECIMAL(9,6),
  longitude       DECIMAL(9,6),
  capacity_units  DECIMAL(18,4),
  is_active       BOOLEAN DEFAULT TRUE
);
```

#### `dim_supplier`
```sql
CREATE TABLE dim_supplier (
  supplier_id         VARCHAR(50) PRIMARY KEY,
  supplier_name       VARCHAR(200),
  country             VARCHAR(3),
  tier                TINYINT,       -- 1 = direct, 2 = sub-supplier
  reliability_score   DECIMAL(5,4),  -- 0.0 to 1.0
  on_time_rate_90d    DECIMAL(5,4),
  quality_defect_rate DECIMAL(5,4),
  risk_category       VARCHAR(20) CHECK (risk_category IN ('low','medium','high','critical')),
  lead_time_days_mean DECIMAL(6,2),
  lead_time_days_std  DECIMAL(6,2),
  is_active           BOOLEAN DEFAULT TRUE
);
```

#### `dim_time`
```sql
CREATE TABLE dim_time (
  date_key          DATE PRIMARY KEY,
  year              SMALLINT,
  quarter           TINYINT,
  month             TINYINT,
  week_of_year      TINYINT,
  day_of_week       TINYINT,
  is_weekend        BOOLEAN,
  is_holiday        BOOLEAN,
  holiday_name      VARCHAR(100),
  fiscal_year       SMALLINT,
  fiscal_quarter    TINYINT,
  fiscal_period     TINYINT,
  season            VARCHAR(20)
);
```

### 4.4 Indexing & Performance

- Partition `fact_demand` and `fact_forecast` by `date_key` (monthly partitions).
- Partition `fact_inventory` by `snapshot_timestamp` (daily partitions, 90-day hot window).
- Cluster `fact_kpi_snapshot` by `(kpi_category, snapshot_date)` for dashboard tile queries.
- Materialized view `mv_executive_kpis`: pre-aggregated global KPIs refreshed every 15 minutes.
- Materialized view `mv_forecast_accuracy`: MAPE/WAPE/Bias per segment, refreshed daily post-forecast run.

### 4.5 Data Validation Rules

| Table | Field | Rule |
|---|---|---|
| fact_demand | demand_units | >= 0; reject if > 10x historical max (flag as anomaly candidate) |
| fact_forecast | forecast_p10 | <= forecast_p50 <= forecast_p90 (monotonicity) |
| fact_inventory | stockout_probability | 0.0 to 1.0 |
| dim_supplier | reliability_score | 0.0 to 1.0 |
| fact_supply | lead_time_days | > 0; < 365 |

---

## 5. AI/ML Methodology

### 5.1 Forecasting Model Pipeline

```
Raw Demand Data (fact_demand)
    ↓
[1. Preprocessing]
  - Outlier treatment: Winsorize at 99th percentile; flag for anomaly review
  - Intermittent demand: Classify using CV² > 0.49 and ADI > 1.32 (Syntetos-Boylan)
  - Calendar cleaning: Remove planned shutdowns from actuals
  - Aggregation: Ensure temporal consistency across granularities
    ↓
[2. Feature Engineering]
  - Lag features: demand_lag_1w, demand_lag_4w, demand_lag_52w
  - Rolling stats: demand_mean_4w, demand_std_4w, demand_trend_12w
  - Calendar: is_holiday, days_to_promo, quarter, month, week_of_year
  - External: promo_uplift_normalized, weather_severity_score, gdp_growth_qoq
  - Lifecycle: lifecycle_stage_encoded, abc_class_encoded
    ↓
[3. Model Selection (Champion/Challenger)]
  ┌──────────────────────────────────────────────┐
  │ Model Pool:                                  │
  │  - Prophet (trend + seasonality + holidays)  │
  │  - LightGBM with lag features (tabular ML)   │
  │  - LSTM (sequence deep learning)             │
  │  - Croston / SBA (intermittent demand)       │
  │  - Naive Seasonal (baseline/fallback)         │
  │  - Ensemble (weighted average of top 3)      │
  └──────────────────────────────────────────────┘
  Selection: Walk-forward cross-validation; champion = min WAPE on held-out window
    ↓
[4. Quantile Estimation]
  - Conformal prediction wrapper for P10/P50/P90
  - OR: LightGBM quantile regression (alpha = 0.1, 0.5, 0.9)
    ↓
[5. Forecast Output]
  → Write to fact_forecast
  → Compute accuracy KPIs (MAPE, WAPE, Bias, FVA)
  → Trigger inventory optimization service
```

### 5.2 Model Selection Logic (Decision Tree)

```
IF demand_adi > 1.32 AND demand_cv2 > 0.49:
    USE Croston/SBA (intermittent)
ELSE IF data_history_weeks < 26:
    USE Prophet with strong priors (limited history)
ELSE IF promo_flag_rate > 0.2 (promo-heavy SKU):
    USE LightGBM (captures promo features)
ELSE IF high_autocorrelation (ACF lag-52 > 0.5):
    USE Prophet + seasonal decomposition
ELSE:
    USE Ensemble (Prophet + LightGBM + LSTM)
Champion vs Challenger: retrain monthly; A/B test on 20% of SKUs
```

### 5.3 Anomaly Detection Pipeline

**Models:**
- Isolation Forest for point anomaly detection on demand time series.
- LSTM Autoencoder for sequence-level anomaly detection (unusual demand shape).
- Statistical: Grubbs test for extreme outlier flagging.

**Outputs:**
- `anomaly_score`: 0 to 1 (higher = more anomalous)
- `anomaly_type`: spike, dip, shift, missing
- `recommended_action`: exclude_from_training | investigate | accept

**Integration:** Anomaly flags displayed on Forecast Analytics dashboard; high-severity anomalies trigger Copilot narrative alert.

### 5.4 Risk Scoring Model

**Features:** supplier_reliability_score, lead_time_cv, on_time_rate_90d, geopolitical_risk_score (external), concentration_risk (single-source flag), weather_severity_score.

**Model:** XGBoost binary classifier (high_risk vs low_risk) → calibrated probability output.

**Explainability:** SHAP values for each risk score; top 3 contributing factors surfaced in Risk Monitoring dashboard tooltip.

**Retraining Trigger:** Monthly scheduled + event-driven (new disruption event detected in news feed).

### 5.5 Forecast Value Added (FVA) Calculation

```
FVA measures accuracy improvement at each planning process step vs naive baseline:

  baseline_wape = Naive Seasonal model WAPE
  statistical_wape = Statistical model WAPE
  after_override_wape = Final consensus WAPE (post planner override)

  FVA_statistical = baseline_wape - statistical_wape   (positive = improvement)
  FVA_override    = statistical_wape - after_override_wape

If FVA_override < 0 (planner overrides hurt accuracy):
  → Surface alert on Forecast Analytics dashboard
  → Copilot: "Overrides from [planner] degraded WAPE by X points on [category]"
```

### 5.6 Model Evaluation Metrics

| Metric | Formula | Target |
|---|---|---|
| MAPE | mean(|actual - forecast| / actual) × 100 | < 20% (stable SKUs), < 40% (intermittent) |
| WAPE | sum(|actual - forecast|) / sum(actual) × 100 | < 15% portfolio-level |
| Bias | mean(actual - forecast) / mean(actual) × 100 | ±5% |
| FVA (statistical) | baseline_wape - statistical_wape | > 0 |
| P10/P90 coverage | % actuals within [P10, P90] band | ~80% |

### 5.7 Retraining & Update Strategy

| Component | Trigger | Frequency |
|---|---|---|
| Forecast models | Scheduled + MAPE degradation (> 5pp in 2 weeks) | Weekly (full retrain monthly) |
| Anomaly detection | New data available | Daily |
| Risk scoring | Supplier event detected | Event-driven + Monthly |
| Copilot prompts | User feedback (thumbs down) | Continuous fine-tuning |

### 5.8 Fallback Logic

```
IF forecast_service unavailable:
  → Return last successful forecast from fact_forecast (max staleness: 24h)
  → Display staleness banner on dashboard
  → Alert on-call via PagerDuty

IF optimization_service timeout (> 30s):
  → Return prior approved plan
  → Queue optimization job for async completion
  → Notify planner when ready

IF LLM API (Copilot) unavailable:
  → Fall back to template-based narrative (rule engine)
  → Disable free-text query; show canned insight cards
```

---

## 6. Development Methodology

### 6.1 Implementation Roadmap

#### Phase 1 — Foundation (Weeks 1–12)

**Goals:** Data infrastructure, core APIs, Executive Summary + Operational dashboards.

**Week 1–3: Infrastructure Setup**
- Provision lakehouse (Databricks / Snowflake / Fabric)
- Deploy Kafka cluster + Kafka Connect for ERP/WMS connectors
- Set up Kubernetes cluster (EKS/AKS/GKE) with namespaces: `data`, `ai`, `api`, `frontend`
- Configure Auth0/Keycloak; define roles and scopes
- Set up CI/CD pipelines (GitHub Actions → ArgoCD)
- Deploy observability stack (Prometheus + Grafana + Jaeger)

**Week 4–6: Data Layer**
- Implement bronze ingestion connectors (ERP, WMS, POS)
- Build dbt silver/gold transformation models
- Implement `dim_product`, `dim_location`, `dim_supplier`, `dim_time`, `fact_demand`, `fact_inventory`
- Deploy data quality checks (Great Expectations)
- Build feature store (initial feature groups: demand, inventory)

**Week 7–9: Core AI Services**
- Implement Naive Seasonal + Prophet + LightGBM forecast models
- Build champion/challenger evaluation framework (MLflow)
- Implement Isolation Forest anomaly detection
- Build inventory optimization service (safety stock + reorder point)
- Deploy model serving API (FastAPI + MLflow serving)

**Week 10–12: Core Application**
- Build REST API layer (Node.js Express or FastAPI): auth, RBAC middleware, core endpoints
- Build React shell: layout, navigation, global filter store (Zustand), authentication flow
- Implement Dashboard 1 (Executive Summary): KPI tiles, plan vs actual chart, scenario comparison table
- Implement Dashboard 2 (Operational Planning): supply-demand balance heatmap, inventory DOS gauges, action queue
- Deploy to staging environment; UAT with 2–3 pilot users

**Phase 1 Exit Criteria:**
- Data freshness: operational data < 15 min lag
- Dashboard load time: < 3s for P95
- Forecast WAPE: < 25% on pilot SKUs
- Auth: RBAC enforced, all endpoints secured

---

#### Phase 2 — Intelligence (Weeks 13–36)

**Goals:** Full AI services, scenario engine, remaining domain dashboards, Copilot MVP.

**Week 13–18: Forecasting & Scenario Engine**
- Add LSTM and Croston models; implement ensemble
- Implement quantile forecasting (conformal prediction)
- Build Monte Carlo scenario simulation engine
- Implement sensitivity analysis (SALib)
- Build Scenario API + scenario persistence
- Dashboard 3 (Forecast Analytics): accuracy KPI cards, FVA waterfall, bias gauge
- Dashboard 4 (Inventory Optimization): geo heatmap, service vs inventory scatter, what-if sliders

**Week 19–24: Capacity, Risk, AI Copilot**
- Build XGBoost risk scoring model + SHAP explanation layer
- Implement Dashboard 5 (Capacity Planning): utilization gauges, load profiles
- Implement Dashboard 7 (Risk Monitoring): risk heatmap, probability×impact matrix
- Build AI Copilot MVP: intent classification, SQL generation, narrative API
- Integrate LLM (OpenAI/Anthropic) for narrative generation
- Add WebSocket real-time feed for operational dashboard

**Week 25–36: Remaining Dashboards + Workflow Engine**
- Dashboard 6 (Financial Impact): scenario P&L waterfall, budget vs forecast
- Dashboard 8 (Sustainability): carbon KPI cards, Pareto scatter
- Dashboard 9 (Regional Planning): choropleth maps, regional scenario sliders
- Build Approval Workflow Engine (state machine + BullMQ)
- Implement plan versioning and rollback
- Add collaborative annotations (comment threads on plan versions)
- Performance optimization: Redis caching, materialized views, query optimization

**Phase 2 Exit Criteria:**
- All 9 dashboards live in production
- Scenario engine: results in < 60s for standard scenarios
- Copilot: > 80% query resolution without human fallback
- Approval workflow: end-to-end plan approval in < 24h

---

#### Phase 3 — Optimization & Scale (Weeks 37–72)

**Goals:** Advanced AI, multi-tenancy, full S&OP integration, benchmarking.

- Demand sensing (real-time POS/web signal integration)
- Reinforcement learning for adaptive replenishment policies
- Full explainability layer (SHAP dashboard integration)
- Multi-tenant architecture hardening
- S&OP/IBP process workflow integration
- Network optimization (strategic capacity planning)
- Industry KPI benchmarking data integration
- Continuous model improvement pipeline (automated retraining + A/B)

#### Phase 4 — Maturity (Week 73+)

- Expand to procurement, network design use cases
- Advanced supply chain twin (digital twin simulation)
- Federated learning for privacy-preserving multi-entity forecasting

---

### 6.2 Project Folder Structure

```
planning-dashboard/
├── infra/                    # Terraform / Helm charts
│   ├── terraform/
│   └── helm/
├── data/
│   ├── dbt/                  # dbt models (bronze/silver/gold)
│   │   ├── models/
│   │   │   ├── bronze/
│   │   │   ├── silver/
│   │   │   └── gold/
│   │   └── tests/
│   ├── connectors/           # Kafka Connect configs, custom connectors
│   └── great_expectations/   # Data quality suites
├── ai-services/
│   ├── forecast/
│   │   ├── models/           # Prophet, LightGBM, LSTM, Croston, Ensemble
│   │   ├── pipelines/        # Feature engineering, training, evaluation
│   │   ├── serving/          # FastAPI model serving
│   │   └── tests/
│   ├── optimization/
│   │   ├── inventory/        # Safety stock, reorder point optimizer
│   │   ├── allocation/       # Constrained allocation solver
│   │   └── scenarios/        # Monte Carlo, sensitivity analysis
│   ├── anomaly/              # Isolation Forest, LSTM autoencoder
│   ├── risk/                 # XGBoost risk scorer, SHAP explainer
│   └── copilot/              # Intent classifier, SQL gen, LLM narrative
├── api/
│   ├── src/
│   │   ├── routes/           # Express/FastAPI route definitions
│   │   ├── middleware/       # Auth, RBAC, logging, rate limiting
│   │   ├── services/         # Business logic layer
│   │   ├── repositories/     # Data access layer (SQL queries)
│   │   └── schemas/          # Request/response validation (Zod/Pydantic)
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/       # Shared UI components
│   │   │   ├── charts/       # ECharts wrappers, Plotly wrappers
│   │   │   ├── kpi-cards/
│   │   │   ├── filters/
│   │   │   └── workflow/     # Approval UI components
│   │   ├── dashboards/       # 9 dashboard page components
│   │   │   ├── executive/
│   │   │   ├── operational/
│   │   │   ├── forecast-analytics/
│   │   │   ├── inventory/
│   │   │   ├── capacity/
│   │   │   ├── financial/
│   │   │   ├── risk/
│   │   │   ├── sustainability/
│   │   │   └── regional/
│   │   ├── store/            # Zustand global state
│   │   ├── hooks/            # React Query hooks per domain
│   │   ├── api/              # API client (axios instances)
│   │   └── types/            # TypeScript interfaces
│   └── tests/
├── workflow-engine/          # Approval state machine + BullMQ workers
├── .github/
│   └── workflows/            # CI/CD: lint, test, build, deploy
└── docs/
    ├── api/                  # OpenAPI specs
    └── architecture/         # ADRs, sequence diagrams
```

### 6.3 Environment Configuration

```env
# .env.example (never commit actual values)
# Database
DATABASE_URL=postgresql://user:pass@host:5432/planning_db
REDIS_URL=redis://host:6379

# Lakehouse
DATABRICKS_HOST=https://xxx.azuredatabricks.net
DATABRICKS_TOKEN=secret
SNOWFLAKE_ACCOUNT=xxx

# AI Services
OPENAI_API_KEY=secret           # or ANTHROPIC_API_KEY
MLFLOW_TRACKING_URI=http://mlflow:5000

# Auth
AUTH0_DOMAIN=xxx.auth0.com
AUTH0_CLIENT_ID=xxx
AUTH0_CLIENT_SECRET=secret
JWT_SECRET=secret

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_SCHEMA_REGISTRY_URL=http://schema-registry:8081

# Feature Flags
ENABLE_COPILOT=true
ENABLE_REALTIME_STREAMING=true
ENABLE_SCENARIO_ENGINE=true
```

### 6.4 CI/CD Pipeline

```yaml
# GitHub Actions (simplified)
on: [push, pull_request]
jobs:
  test:
    - run: pytest ai-services/ --cov
    - run: npm test --prefix frontend
    - run: npm test --prefix api
  lint:
    - run: ruff check ai-services/
    - run: eslint frontend/src
  build:
    - run: docker build -t planning-api:$SHA ./api
    - run: docker build -t planning-frontend:$SHA ./frontend
  deploy-staging:
    - run: argocd app sync planning-dashboard-staging
  deploy-prod:               # manual trigger only
    - run: argocd app sync planning-dashboard-prod
```

### 6.5 Technology Stack

| Layer | Technology |
|---|---|
| Framework | Plotly Dash (`dash`, `dash-core-components`, `dash-html-components`, `dash-bootstrap-components`) |
| Charting | `plotly.express`, `plotly.graph_objects` |
| Data | `pandas`, `numpy` (use realistic synthetic/mock data) |
| Styling | `dash-bootstrap-components` (theme: `dbc.themes.DARKLY` or `CYBORG`) |
| Layout | Multi-page via `dash.page_container` or tab-based navigation |
| State | Dash callbacks with `dcc.Store` for scenario state |

### 6.6 Color Palette (Dark Theme)
```python
COLORS = {
    "background":    "#0d1117",
    "surface":       "#161b22",
    "card":          "#1c2128",
    "border":        "#30363d",
    "primary":       "#58a6ff",
    "success":       "#3fb950",
    "warning":       "#d29922",
    "danger":        "#f85149",
    "info":          "#58a6ff",
    "text_primary":  "#e6edf3",
    "text_secondary":"#8b949e",
    "accent":        "#bc8cff",
    "chart_1":       "#58a6ff",
    "chart_2":       "#3fb950",
    "chart_3":       "#d29922",
    "chart_4":       "#f85149",
    "chart_5":       "#bc8cff",
}
```

### 6.7 Typography
- Headers: Bold, uppercase letter-spacing
- KPI values: Large (2.5rem+), monospaced where applicable
- Body: 0.875rem, secondary color

### 6.8 KPI Card Component Template
Each KPI card must include:
- Metric title (small, uppercase)
- Current value (large, bold)
- Target value (small, muted)
- Delta vs previous period (colored arrow + %)
- Mini sparkline (7–14 period trend)
- Status indicator dot (green/yellow/red)

---

## 7. Testing & Validation Framework

### 7.1 Unit Tests

**Forecast Models:**
```python
def test_prophet_forecast_produces_monotonic_quantiles():
    model = ProphetForecaster()
    result = model.predict(sku_id="SKU001", horizon=12)
    assert all(result.p10 <= result.p50)
    assert all(result.p50 <= result.p90)

def test_wape_calculation():
    actuals = [100, 120, 90, 110]
    forecasts = [105, 115, 95, 115]
    assert compute_wape(actuals, forecasts) == pytest.approx(4.44, abs=0.1)

def test_safety_stock_increases_with_higher_service_level():
    ss_95 = compute_safety_stock(service_level=0.95, demand_std=20, lt_mean=7, lt_std=2)
    ss_99 = compute_safety_stock(service_level=0.99, demand_std=20, lt_mean=7, lt_std=2)
    assert ss_99 > ss_95
```

**RBAC:**
```python
def test_plant_manager_cannot_access_financial_dashboard():
    token = generate_jwt(role="PLANT_MANAGER")
    response = client.get("/api/v1/dashboards/financial", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
```

**Scenario Engine:**
```python
def test_demand_surge_increases_inventory_requirement():
    base = ScenarioPlan(demand_factor=1.0)
    surge = ScenarioPlan(demand_factor=1.3, regions=["APAC"])
    assert surge.outputs.inventory_delta_units > 0
    assert surge.outputs.total_cost_delta_usd > 0
```

### 7.2 Integration Tests

- **Data pipeline end-to-end:** Ingest mock ERP CSV → validate bronze table → run dbt silver transform → assert silver row count, null rates.
- **Forecast API:** `POST /forecast/run` → poll `GET /forecast/{job_id}` until complete → assert `fact_forecast` populated with correct schema.
- **Scenario + Dashboard:** Create demand surge scenario → fetch Executive Summary dashboard → assert scenario overlay KPIs differ from base plan.

### 7.3 API Testing (Contract Tests)

All API endpoints tested with Pact (consumer-driven contract testing):
- Request schema validation (Zod/Pydantic).
- Response schema validation.
- Auth rejection (missing/invalid JWT → 401/403).
- Rate limiting (> 100 req/min → 429).

### 7.4 End-to-End Tests (Playwright)

```typescript
test('Demand Planner can submit forecast override', async ({ page }) => {
  await loginAs(page, 'demand_planner@test.com');
  await page.goto('/dashboards/forecast-analytics');
  await page.click('[data-testid="override-sku-SKU001"]');
  await page.fill('[data-testid="override-value"]', '1250');
  await page.click('[data-testid="submit-override"]');
  await expect(page.locator('[data-testid="success-toast"]')).toBeVisible();
});
```

### 7.5 Data Validation Tests (Great Expectations)

```python
# great_expectations suite: fact_demand
expect_column_values_to_not_be_null("sku_id")
expect_column_values_to_not_be_null("date_key")
expect_column_values_to_be_between("demand_units", min_value=0)
expect_column_values_to_be_of_type("demand_units", "float")
expect_column_pair_values_A_to_be_greater_than_B(
    column_A="demand_units", column_B=0, ignore_row_if="either_value_is_missing"
)
```

### 7.6 Performance / Load Tests (k6)

```javascript
// k6 load test: dashboard KPI endpoint
export default function () {
  const res = http.get('https://api.planning.internal/api/v1/kpis/executive',
    { headers: { Authorization: `Bearer ${TOKEN}` } });
  check(res, {
    'status 200': r => r.status === 200,
    'response < 500ms': r => r.timings.duration < 500,
  });
}
export const options = {
  vus: 200, duration: '5m',
  thresholds: { http_req_duration: ['p(95)<500'], http_req_failed: ['rate<0.01'] }
};
```

**Acceptance Thresholds:**
- P95 dashboard load: < 500ms (API response, cached data)
- P95 scenario simulation: < 60s (async job)
- P99 authentication: < 200ms
- Error rate: < 1% under 200 concurrent users

### 7.7 Security Tests

- **OWASP ZAP** automated scan on staging before each release.
- **JWT validation:** Test expired tokens, tampered signatures, wrong audience.
- **SQL injection:** Parameterized query audit; fuzz test all user-facing filter inputs.
- **Row-level security:** For each role, assert that queries return only authorized data (automated cross-role data leak test suite).
- **Secret scanning:** GitGuardian / truffleHog in CI.

### 7.8 AI/ML Validation Tests

| Test | Method | Acceptance |
|---|---|---|
| Forecast accuracy regression | Walk-forward backtest on 6-month holdout | WAPE < 25% (pilot SKUs) |
| Quantile calibration | P10 coverage ~10%, P90 coverage ~90% | Within ±5pp of nominal |
| Anomaly precision | Labeled anomaly dataset (synthetic + historical) | Precision > 0.80, Recall > 0.75 |
| Risk model AUC | Holdout evaluation on labeled disruption events | AUC > 0.80 |
| FVA positivity | Override FVA distribution | > 60% of overrides have positive FVA |
| Copilot accuracy | 50-query golden dataset (human-labeled) | > 80% correct intent classification |

### 7.9 Failure Recovery Tests

- **Kafka consumer restart:** Kill consumer mid-stream; assert no duplicate or lost messages after restart (idempotent consumer test).
- **AI service crash:** Bring down forecast service; assert dashboard shows staleness banner and last-good-forecast within 5s.
- **Database failover:** Simulate primary DB failure; assert read replica serves dashboard queries within 30s.
- **Scenario timeout:** Submit a scenario configured to exceed 60s; assert async fallback and notification delivered to user.

### 7.10 Edge Cases

| Scenario | Expected Behavior |
|---|---|
| SKU with zero historical demand | Croston model selected; P50 = 0; safety stock = minimum buffer |
| New SKU (< 4 weeks history) | Prophet with market-level priors; wide confidence band flagged |
| Supplier reliability = 0% | Critical risk flag; supply optimization excludes supplier |
| Demand surge > 500% | Scenario engine caps at 500%; alerts planner to validate input |
| Plan approval by unauthorized role | 403 returned; audit log entry created; email alert to admin |
| Concurrent scenario edits by 2 users | Optimistic locking; second user receives conflict error with merge option |

---

## 8. Assumptions & Gap Resolution

### 8.1 Architecture Assumptions

| Assumption | Rationale |
|---|---|
| Databricks/Snowflake as lakehouse | Industry standard; either works; interfaces abstracted via dbt |
| Kafka for streaming | Standard; can be replaced by Azure Event Hub or AWS Kinesis with same connector pattern |
| React 18 frontend | Modern standard; can be replaced by Angular/Vue with same component logic |
| LLM for Copilot via API (OpenAI/Anthropic) | Fastest path; can be swapped for on-prem open-source LLM (Llama, Mistral) if data sovereignty required |
| Single-region deployment initially | Multi-region added in Phase 3 |
| Currency = USD as base | Multi-currency conversion handled at ingestion layer via daily FX rates |

### 8.2 Data Schema Gaps Resolved

- **Promotion data structure:** Assumed standard trade promotion management (TPM) schema; `promo_id` FK in `fact_demand` with `dim_promotion` table (not detailed above; fields: promo_id, promo_type, uplift_pct, start_date, end_date, sku_ids, channel).
- **Carbon emission factors:** Assumed externally sourced (EPA/DEFRA/GHG Protocol emission factor databases); stored in `dim_emission_factor` table (mode, lane, activity → CO2e per unit).
- **Exact ERP field mapping:** Assumed SAP/Oracle standard fields; connector mapping config defined per deployment; abstracted behind bronze landing schema.

### 8.3 AI Dataset Assumptions

- Training data: minimum 2 years of weekly demand history per SKU-location for statistical models; 6 months for demand sensing.
- Labeled anomaly dataset: synthetically generated from historical data with injected spikes/dips for initial model training; replaced with real labeled data over time.
- Risk model labels: supplier disruptions labeled from historical procurement records and news event archive (prior 3 years).

### 8.4 Business Logic Assumptions

- **ABC classification:** A = top 80% revenue cumulative, B = 80–95%, C = 95–100%.
- **XYZ classification:** X = CV < 0.5 (stable), Y = 0.5–1.0 (variable), Z > 1.0 (highly variable).
- **Service level default targets:** A-X SKUs = 98%, A-Y = 95%, B = 90%, C = 85%.
- **Carrying cost rate:** 20% of unit cost per annum (configurable per deployment).
- **Planning horizon bucket granularity:** Operational = daily; Tactical = weekly/monthly; Strategic = quarterly.

---

## 9. AI-Agent Execution Optimization

### 9.1 Implementation Priority Order

Execute strictly in this sequence to avoid dependency blockers:

```
1. Infra provisioning (Terraform) → Kubernetes, DB, Kafka, Redis, Auth
2. dbt bronze/silver models → dimension tables, fact_demand, fact_inventory
3. Forecast Engine MVP → Prophet + Naive Seasonal + accuracy KPIs
4. Core API layer → auth middleware, RBAC, /forecast, /kpis/executive endpoints
5. React shell + Dashboard 1 (Executive) → unblocks UAT immediately
6. Dashboard 2 (Operational) → highest operational value
7. Inventory optimization service → feeds Dashboard 4
8. Scenario engine (Monte Carlo) → feeds scenario comparison in Dashboard 1
9. Remaining dashboards (3, 4, 5, 6, 7, 8, 9) → in parallel after step 8
10. AI Copilot + narrative generation → enhances all dashboards
11. Approval workflow engine → enables S&OP process digitization
12. Performance optimization → Redis, materialized views, load testing
```

### 9.2 Explicit Engineering Standards

- **All API responses paginated** with `{ data: [], total: int, page: int, page_size: int }`.
- **All timestamps stored in UTC**; converted to user timezone in frontend.
- **All monetary values stored in USD cents** (integer) to avoid floating-point errors; displayed with locale formatting.
- **All async jobs** must expose `/jobs/{job_id}/status` endpoint returning `{ status: 'pending'|'running'|'completed'|'failed', progress_pct: int, result_url?: string }`.
- **All chart components** must accept a `loading: boolean` prop and render skeleton states; never blank on data fetch.
- **All AI-generated text** must be clearly labeled with `[AI Generated]` badge in UI; editable by planner before approval.
- **All SHAP explanations** surface top 3 contributing features maximum in UI; full SHAP waterfall available on expand.
- **Plan version diffs** must highlight only changed cells (green = increase, red = decrease, gray = unchanged).

### 9.3 Coding Conventions

**Backend (Python AI services):**
- Type hints required on all functions.
- `pydantic` for all data models.
- `pytest` with `pytest-cov`; minimum 80% coverage.
- Logging: structured JSON via `structlog`.

**Backend (Node.js API):**
- TypeScript strict mode.
- `zod` for all input validation.
- `winston` for structured logging.
- `jest` + `supertest` for API tests.

**Frontend (React):**
- TypeScript strict mode.
- All chart configs in separate `*.config.ts` files (not inline in JSX).
- `React.memo` for all chart components (expensive renders).
- `data-testid` attributes required on all interactive elements.
- No `any` types in TypeScript.

### 9.4 Key Anti-Patterns to Avoid

| Anti-Pattern | Correct Approach |
|---|---|
| Blocking API on scenario simulation | Async job dispatch; polling via `/jobs/{id}/status` |
| Fetching full fact tables in dashboard query | Query materialized views / pre-aggregated gold tables |
| Hardcoded KPI thresholds in frontend | Thresholds stored in `fact_kpi_snapshot`; fetched at runtime |
| Single LLM call per dashboard load | Batch narrative generation; cache for 30 minutes |
| Role filtering in frontend only | Row-level security enforced at API AND database layers |
| Plan comparison by copying data | Immutable version IDs; diff computed server-side on demand |

### 9.5 Minimum Viable Deliverable Per Sprint (2-week sprints)

| Sprint | Deliverable | Done Criteria |
|---|---|---|
| 1 | Infra provisioned; CI/CD pipeline working | `kubectl get pods` shows all namespaces healthy; pipeline green |
| 2 | Bronze ingestion live; dbt silver models passing | Great Expectations suite passes; `fact_demand` populated |
| 3 | Forecast MVP; accuracy KPIs computed | WAPE < 30% on pilot SKUs in `fact_forecast` |
| 4 | API auth layer; Executive KPI endpoint | All endpoints return 401 without valid JWT; RBAC enforced |
| 5 | Dashboard 1 rendering real data | Executive Summary loads in < 3s; KPI tiles accurate |
| 6 | Dashboard 2 + real-time inventory feed | Operational dashboard updates within 15 min of WMS event |
| 7 | Scenario engine; demand surge simulation | Scenario result computed and stored within 60s |
| 8 | Dashboards 3 & 4 live | Forecast Analytics FVA waterfall accurate; Inventory scatter populates |
| 9 | Copilot MVP | 5 query types answered correctly (verified by product owner) |
| 10 | Approval workflow e2e | Plan submitted → approved → versioned → rollback tested |

---

*End of Blueprint — Version 1.0*  
*This document should be treated as a living specification; update section headers with version notes as design decisions evolve during implementation.*
