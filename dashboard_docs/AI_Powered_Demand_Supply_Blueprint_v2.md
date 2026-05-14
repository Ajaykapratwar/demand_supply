I'll analyze the gaps and produce an updated blueprint that integrates all the missing sections from Doc 1 and Doc 2 while preserving the original blueprint's style. Given the substantial volume of content to add, I'll structure this as a comprehensive addendum/extension document that fits seamlessly into the existing blueprint.

Let me produce the updated blueprint now.

---

# AI-Powered Demand-Supply & Matching Planning Dashboard
## System Engineering Blueprint — Implementation-Ready Reference

**Document Version:** 2.0 (Expanded)
**Classification:** Principal Architecture Handoff
**Audience:** Autonomous AI Engineering Agent / Senior Engineering Team
**Changelog v2.0:** Integrated missing sections from research Doc 1 (UX/UI principles, storytelling layer, per-dashboard detailed specs, scenario visual interactions, human-AI collaboration models) and Doc 2 (production/operational KPIs, extended financial KPIs, resource & service KPIs, KPI interdependency analysis, hybrid ML risk taxonomy, uncertainty visualization techniques).

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
10. [**NEW** — Forecasting Engine Input Catalog (Full)](#10-forecasting-engine-input-catalog-full)
11. [**NEW** — Extended KPI Dictionary](#11-extended-kpi-dictionary)
12. [**NEW** — KPI Interdependency Analysis (PCTM)](#12-kpi-interdependency-analysis-pctm)
13. [**NEW** — Per-Dashboard Detailed Specifications](#13-per-dashboard-detailed-specifications)
14. [**NEW** — Storytelling & Decision Intelligence Layer](#14-storytelling--decision-intelligence-layer)
15. [**NEW** — Scenario Engine: Visual Interaction & Decision Mapping](#15-scenario-engine-visual-interaction--decision-mapping)
16. [**NEW** — Hybrid AI Risk Architecture & Uncertainty Visualization](#16-hybrid-ai-risk-architecture--uncertainty-visualization)
17. [**NEW** — UX/UI Design System & Principles](#17-uxui-design-system--principles)
18. [**NEW** — Platform Benchmarks & Industry KPI Targets](#18-platform-benchmarks--industry-kpi-targets)
19. [**NEW** — Deliverables Traceability Matrix](#19-deliverables-traceability-matrix)

---

## 1–9. (Sections 1 through 9 from v1.0 retained verbatim — see prior version)

> *Sections 1–9 remain as published in Blueprint v1.0. The expansions below add the missing depth identified in the gap analysis without altering existing content.*

---

## 10. Forecasting Engine Input Catalog (Full)

### 10.1 Purpose

This section restores the full 18-input forecasting catalog with business relevance, source, refresh frequency, visualization, and planning impact — the canonical reference for what feeds the Forecasting Engine (Module 3) and Feature Store (Module 2).

### 10.2 Demand-Side Inputs

| Input | Business Relevance | Data Source(s) | Refresh | Visualization | Planning Impact |
|---|---|---|---|---|---|
| Historical demand data | Base pattern; trend/seasonality | ERP, POS, orders | Daily / batch | Line charts, SKU×time heatmaps | Safety stock, base forecast |
| Sales trends | Growth/decline detection | CRM, ERP | Weekly / monthly | YoY trend lines, region bars | Strategic direction, budgets |
| Seasonal patterns | Periodic fluctuations | Decomposition outputs, calendars | Monthly | Seasonal decomposition charts, seasonal index heatmap | Seasonal builds, workforce scheduling |
| Promotions & campaigns | Uplift/cannibalization | TPM, marketing systems | Event-driven | Promo calendar, uplift bars, pre/post analysis | Demand shaping, pre-build, margin impact |
| Pricing changes | Elasticity & margin impact | Pricing systems, ERP | As changes occur | Price-vs-volume scatter, margin waterfall | Revenue mgmt, promo effectiveness, demand shaping |
| Market demand signals | POS, web traffic, social, search | POS, e-com, digital analytics, 3rd-party | Daily / real-time | Signal-vs-actual lines, correlation scatter | Demand sensing, short-term refinements |
| Regional variations | Geographic demand differences | Country/region systems | Daily / batch | Geo choropleth, region bar comparisons | Localized planning, network design |
| New-product life-cycle stage | Intro/growth/mature/decline | PLM, ERP | Weekly | Lifecycle ribbon, cohort curves | Phase-in/phase-out, range planning |

### 10.3 Supply-Side Inputs

| Input | Business Relevance | Data Source | Refresh | Visualization | Planning Impact |
|---|---|---|---|---|---|
| Inventory levels | Fulfillment constraint | WMS, ERP | Real-time / near-RT | DOS gauges, stock heatmaps | Replenishment, deployment, allocation |
| Supplier constraints | Capacity caps, allocation, reliability | SRM | Weekly / event-driven | Supplier scorecards, constraint flag tiles | Sourcing allocation, dual sourcing |
| Lead times | Replenishment / production horizon | Master data, procurement | Daily / batch | Lead-time histograms, variability box plots | Safety stock, reorder points, promise dates |
| Production capacity | Machine, labor, tooling | MES, production planning | Weekly / daily | Utilization gauges, load profiles | Production scheduling, overtime decisions |
| Workforce availability | Shift patterns, absenteeism, skill mix | HR, WFM | Daily / weekly | Availability heatmaps, utilization-vs-overtime | Scheduling, labor allocation |

### 10.4 External / Environmental Inputs

| Input | Business Relevance | Data Source | Refresh | Visualization | Planning Impact |
|---|---|---|---|---|---|
| Weather signals | Demand driver, logistics risk | Weather APIs (NOAA, OpenWeather) | Hourly / Daily | Weather-overlay maps, correlation charts | Short-term adjustments, logistics risk |
| Economic indicators | Macro demand environment | FRED, Eurostat, central banks | Monthly / quarterly | Macro-vs-demand trend, scenario sliders | Strategic scenarios, long-term plans |
| External event impacts | Strikes, geopolitics, pandemics, regulation | News APIs, risk providers, internal registers | Event-driven | Event timeline, impact tags, scenario overlays | Contingency, mitigation, buffers |

### 10.5 AI-Generated Inputs

| Input | Business Relevance | Source Model | Refresh | Visualization | Planning Impact |
|---|---|---|---|---|---|
| Anomaly detection outputs | Outliers, data issues, spikes/dips | Isolation Forest, LSTM-AE | Daily / RT | Anomaly flags, sparkline highlights | Forecast robustness, exception handling |
| Confidence intervals | Probabilistic forecast ranges | Quantile / ensemble models | Per run | Fan charts, density plots | Risk-aware safety stock, scenario bounds |
| Model performance metrics | Accuracy, bias, stability | Monitoring pipelines | Daily / weekly | Accuracy KPI cards, bias gauges | Model selection, retraining triggers |
| AI risk indicators | Composite risk scores | XGBoost + graph analytics | Daily / event-driven | Risk heatmaps, contribution trees | Proactive mitigation, planner prioritization |

### 10.6 Schema Additions to Support Full Catalog

```sql
-- Promotion dimension
CREATE TABLE dim_promotion (
  promo_id          VARCHAR(50) PRIMARY KEY,
  promo_name        VARCHAR(200),
  promo_type        VARCHAR(50),       -- TPR, BOGO, bundle, display
  start_date        DATE,
  end_date          DATE,
  uplift_pct_est    DECIMAL(6,2),
  channel_ids       VARCHAR(500),      -- comma-delimited
  status            VARCHAR(20)
);

-- Workforce snapshot fact
CREATE TABLE fact_workforce (
  workforce_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  date_key          DATE NOT NULL,
  location_id       VARCHAR(50) NOT NULL,
  shift_id          VARCHAR(20),
  planned_headcount INT,
  actual_headcount  INT,
  absenteeism_rate  DECIMAL(5,4),
  skill_mix_score   DECIMAL(5,4)
);

-- External event log
CREATE TABLE fact_external_event (
  event_id          VARCHAR(50) PRIMARY KEY,
  event_type        VARCHAR(50),       -- strike, weather, geopolitical, pandemic, regulation
  severity          VARCHAR(20),
  region            VARCHAR(50),
  start_ts          TIMESTAMP,
  end_ts            TIMESTAMP,
  impact_estimate   JSONB,
  source            VARCHAR(100)
);

-- Pricing change log
CREATE TABLE fact_pricing_change (
  pricing_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  effective_date    DATE,
  sku_id            VARCHAR(50),
  channel_id        VARCHAR(50),
  old_price_usd     DECIMAL(12,4),
  new_price_usd     DECIMAL(12,4),
  elasticity_est    DECIMAL(6,3)
);
```

---

## 11. Extended KPI Dictionary

### 11.1 Production & Operational KPIs (Dashboard 5 — Capacity Planning)

| KPI | Formula | Target | Schema Field |
|---|---|---|---|
| Capacity Utilization | Actual Output / Maximum Capacity | 80–90% | `fact_capacity.utilization_pct` |
| Schedule Adherence | Orders completed on planned date / Total planned orders | > 95% | `fact_production.schedule_adherence_pct` |
| First-Pass Yield (FPY) | Units passing QC without rework / Total units produced | > 98% | `fact_production.first_pass_yield_pct` |
| Throughput | Units produced / unit time | Line-specific | `fact_production.throughput_units_per_hr` |
| Changeover Time | Mean time to switch SKU/line | Industry-specific | `fact_production.changeover_minutes` |
| OEE (Overall Equipment Effectiveness) | Availability × Performance × Quality | > 85% world-class | `fact_capacity.oee_pct` |

### 11.2 Schema — Production Fact Table

```sql
CREATE TABLE fact_production (
  production_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  date_key               DATE NOT NULL,
  plant_id               VARCHAR(50) NOT NULL,
  line_id                VARCHAR(50) NOT NULL,
  sku_id                 VARCHAR(50) NOT NULL,
  planned_units          DECIMAL(18,4),
  actual_units           DECIMAL(18,4),
  good_units             DECIMAL(18,4),
  scrap_units            DECIMAL(18,4),
  schedule_adherence_pct DECIMAL(5,2),
  first_pass_yield_pct   DECIMAL(5,2),
  throughput_units_per_hr DECIMAL(10,2),
  changeover_minutes     DECIMAL(8,2),
  downtime_minutes       DECIMAL(8,2),
  INDEX idx_prod_plant_date (plant_id, date_key)
);

CREATE TABLE fact_capacity (
  capacity_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  date_key         DATE NOT NULL,
  resource_id      VARCHAR(50) NOT NULL,
  resource_type    VARCHAR(30) CHECK (resource_type IN ('machine','line','plant','warehouse','fleet')),
  available_hours  DECIMAL(8,2),
  planned_hours    DECIMAL(8,2),
  actual_hours     DECIMAL(8,2),
  utilization_pct  DECIMAL(5,2),
  availability_pct DECIMAL(5,2),
  performance_pct  DECIMAL(5,2),
  quality_pct      DECIMAL(5,2),
  oee_pct          DECIMAL(5,2) GENERATED ALWAYS AS (availability_pct * performance_pct * quality_pct / 10000.0)
);
```

### 11.3 Extended Financial KPIs (Dashboard 6 — Financial Impact)

| KPI | Formula | Target Direction | Schema Field |
|---|---|---|---|
| EVA (Economic Value Added) | NOPAT − (Invested Capital × WACC) | Maximize | `fact_financial.eva_usd` |
| ROIC | NOPAT / Invested Capital | Maximize | `fact_financial.roic_pct` |
| NOPAT | Operating Profit × (1 − Tax Rate) | Maximize | `fact_financial.nopat_usd` |
| Logistics Cost % of Sales | Total Logistics Cost / Net Sales | Minimize | `fact_financial.logistics_pct_sales` |
| Cost per Order | Total Fulfillment Cost / Total Orders | Minimize | `fact_financial.cost_per_order_usd` |
| Inventory Carrying Cost | Carrying Rate × Avg Inventory Value | Minimize | `fact_financial.carrying_cost_usd` |
| Cash-to-Cash Cycle | DIO + DSO − DPO (days) | Minimize | `fact_financial.cash_to_cash_days` |

```sql
CREATE TABLE fact_financial (
  financial_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  period_key            DATE NOT NULL,
  business_unit         VARCHAR(50),
  region                VARCHAR(50),
  revenue_usd           DECIMAL(18,2),
  cogs_usd              DECIMAL(18,2),
  operating_profit_usd  DECIMAL(18,2),
  nopat_usd             DECIMAL(18,2),
  invested_capital_usd  DECIMAL(18,2),
  wacc_pct              DECIMAL(5,4),
  eva_usd               DECIMAL(18,2),
  roic_pct              DECIMAL(7,4),
  logistics_cost_usd    DECIMAL(18,2),
  logistics_pct_sales   DECIMAL(7,4),
  total_orders          BIGINT,
  cost_per_order_usd    DECIMAL(10,2),
  carrying_cost_usd     DECIMAL(18,2),
  cash_to_cash_days     DECIMAL(6,2)
);
```

### 11.4 Resource Utilization KPIs

| KPI | Formula | Target | Schema Field |
|---|---|---|---|
| Machine OEE | Availability × Performance × Quality | > 85% | `fact_capacity.oee_pct` |
| Labor Productivity | Output Units / Labor Hours | Industry-specific | `fact_workforce.productivity_units_per_hr` |
| Warehouse Space Utilization | Occupied Pallet Positions / Total | 80–90% | `fact_warehouse.space_utilization_pct` |
| Fleet Utilization | Active Vehicle Hours / Available Hours | > 75% | `fact_fleet.utilization_pct` |
| Cross-Dock Turn Time | Mean inbound-to-outbound dwell time | Minimize | `fact_warehouse.cross_dock_minutes` |

### 11.5 Service KPIs (Extended)

| KPI | Formula | Target |
|---|---|---|
| OTIF | Orders delivered on time & in full / Total orders | > 95% |
| Customer Fill Rate | Units shipped / Units ordered | > 98% |
| CSAT (Customer Satisfaction Score) | Survey-based 1–5 scale, % top-box | > 80% |
| Customer Query Resolution Time | Mean time to resolve service tickets | < 24h |
| Returns Rate | Returned units / Shipped units | < 2% |
| Perfect Order Rate | OTIF × Quality × Documentation × Damage-free | > 90% |

```sql
CREATE TABLE fact_service (
  service_id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  date_key                DATE NOT NULL,
  customer_id             VARCHAR(50),
  region                  VARCHAR(50),
  orders_total            BIGINT,
  orders_otif             BIGINT,
  units_ordered           DECIMAL(18,4),
  units_shipped           DECIMAL(18,4),
  csat_score              DECIMAL(4,2),
  query_resolution_hours  DECIMAL(8,2),
  returns_units           DECIMAL(18,4),
  perfect_order_rate_pct  DECIMAL(5,2)
);
```

### 11.6 Risk & Exception KPIs

| KPI | Formula | Target |
|---|---|---|
| SLA Compliance | Orders meeting SLA / Total orders | > 95% |
| Exception Rate | Planning exceptions / Total plan rows | Minimize |
| Risk Score (composite) | Weighted XGBoost output (0–1) | Track by category |
| Mean Time to Mitigate | Mean elapsed time from detection to mitigation | Minimize |

---

## 12. KPI Interdependency Analysis (PCTM)

### 12.1 Methodology

The **KPI Accomplishment Cost Transformation Matrix (PCTM)** models cause-effect relationships between KPIs so that the dashboard can (a) prioritize KPIs aligned to organizational strategy, and (b) warn planners when improving one KPI degrades another.

### 12.2 Two Canonical KPI Clusters

**Pattern 1 — Efficiency Focus**

Mutually reinforcing efficiency KPIs:
- Supply Chain Management Cost ↓
- Inventory Cost ↓
- Turnover Cost ↓
- ROI ↑
- Sales ↑
- Product Flexibility ↑

**Pattern 2 — Innovation Focus**

Reinforcing growth/innovation KPIs:
- Product Flexibility ↑
- New Product Sales Rate ↑
- Time-to-Market ↓
- Forecast Accuracy on NPI ↑

### 12.3 Interdependency Storage

```sql
CREATE TABLE kpi_interdependency (
  source_kpi_name       VARCHAR(100) NOT NULL,
  target_kpi_name       VARCHAR(100) NOT NULL,
  relationship_type     VARCHAR(20) CHECK (relationship_type IN ('reinforcing','trade_off','neutral')),
  strength              DECIMAL(4,3),   -- -1.0 to 1.0
  pattern_cluster       VARCHAR(50),    -- efficiency_focus, innovation_focus, ...
  evidence_note         TEXT,
  PRIMARY KEY (source_kpi_name, target_kpi_name)
);
```

### 12.4 Dashboard Surfacing

On the Executive Summary, when a user clicks a KPI tile, a **side panel** lists:
1. KPIs that reinforce the selected metric (green chevrons).
2. KPIs in trade-off with it (red chevrons).
3. Recommended priority cluster (Efficiency vs Innovation) based on organization strategy stored in `org_strategy_config`.

### 12.5 AI Copilot Integration

The Copilot can be prompted with: *"What happens if we push inventory turns higher?"* — it queries `kpi_interdependency` to return: *"Pushing inventory turns will trade off against fill rate (correlation −0.62 historically) and may increase expediting cost (+0.41). Recommended: target turns improvement only on A-Z (high-volatility) SKUs."*

---

## 13. Per-Dashboard Detailed Specifications

For each of the 9 dashboards, the following sub-sections specify: layout, widgets, filters, drill-down paths, alert thresholds, AI recommendation phrasing templates, and role-based personalization. These supplement Module 6 (Dashboard Rendering Engine).

### 13.1 Dashboard 1 — Executive Summary

**Layout**

```
Row 1 (KPI Strip):    [Service Level] [Inventory Turns] [Total Cost] [Carbon] [Risk Score]
Row 2 (Main):         [Plan vs Actual vs Forecast Line+Bar]  |  [Scenario Comparison Table]
Row 3 (Insights):     [Risk Heat Strip by Region/Category]   |  [AI Brief: Top 3 actions]
```

**Filters:** Horizon (operational/tactical/strategic), Region, Business Unit, Scenario overlay

**Drill-down paths:**
- KPI tile → Operational dashboard (filtered)
- Scenario row → Scenario detail page
- Risk cell → Risk Monitoring dashboard

**Alert thresholds (defaults; configurable in `fact_kpi_snapshot.threshold_*`):**
- Service Level < 92% → red
- Risk Score > 0.7 → red
- Total Cost Δ vs plan > +5% → yellow; > +10% → red

**AI recommendation phrasing templates:**
- *"Increase safety stock by {pct}% in {region} to reduce stockout risk from {p_old}% to {p_new}%."*
- *"Shift production from {plant_a} to {plant_b} to improve OTIF by {delta_pp} pp with {cost_delta}% cost increase."*
- *"Defer {sku_count} low-margin SKUs in {region} to free {capacity_hrs} capacity hours for high-margin lines."*

**Role-based personalization:**

| Role | KPI Emphasis | Default Filters |
|---|---|---|
| CEO | Margin, Growth, Service | All regions, tactical horizon |
| CFO | Cost, Cash-to-Cash, EVA, ROIC | Financial scenario overlay default-on |
| CSO (Supply Chain Officer) | Service, Risk, OTIF | Operational + tactical horizons |
| COO | Capacity, OEE, Schedule adherence | Plant-grouped view |

### 13.2 Dashboard 2 — Operational Planning

**Layout**

```
Row 1: [Status strip: orders late | stockouts | capacity overload | exceptions]
Row 2: [Supply-Demand Balance Heatmap (SKU × week)] | [Inventory DOS Gauges]
Row 3: [Action Queue: transfers, expedites, cancellations] (full width, sortable)
```

**Filters:** 0–4 week horizon, planner, plant, carrier, SKU class (ABC/XYZ)

**Drill-down:** Heatmap cell → SKU-location detail; Action row → order detail

**Alerts:**
- Days-of-supply < safety stock days → red row
- Stockout probability > 5% → flashing badge
- Capacity overload > 100% → red gauge

**AI recommendations (inline):**
- *"Transfer {qty} units of {sku} from {dc_a} to {dc_b}; lead time 2 days; reduces stockout risk at {dc_b} from {p_old}% to {p_new}%."*
- *"Expedite PO #{po_id} via air freight; cost +{usd}; avoids stockout on {date}."*

### 13.3 Dashboard 3 — Forecast Analytics

**Layout**

```
Row 1: [MAPE] [WAPE] [Bias] [FVA Score] [Coverage %]
Row 2: [Forecast vs Actual line chart]  |  [Model leaderboard bar chart]
Row 3: [FVA Waterfall by process step]  |  [Bias gauge by planner]
```

**Filters:** Horizon, model family, segment (ABC/XYZ), planner, category

**Drill-down:** Segment → SKU; Planner → override history

**Alerts:**
- WAPE > 25% on A-class → red KPI card
- Override FVA < 0 (override hurt accuracy) → planner-specific badge
- Coverage outside [75%, 85%] → calibration warning

**AI recommendations:**
- *"Overrides by {planner} on {category} degraded WAPE by {pp} points over the last {weeks} weeks. Recommend coaching or process redesign."*
- *"Model {challenger} outperformed champion on {segment} by {pp} pp WAPE; promote challenger."*

### 13.4 Dashboard 4 — Inventory Optimization

**Layout**

```
Row 1: [Inventory Turns] [DOS] [Fill Rate] [Stockout Risk] [Working Capital]
Row 2: [Geo heatmap of inventory]  |  [Service-Level vs Inventory Investment Scatter]
Row 3: [Safety Stock Simulator: sliders for target service level → SS units, $ impact]
```

**Filters:** Category, region, ABC/XYZ class, policy type

**Drill-down:** Map region → DC → SKU; Scatter point → SKU detail

**Alerts:**
- DOS > 2× target → overstock flag
- DOS < 0.5× target → stockout risk flag

**AI recommendations:**
- *"Rebalance {qty} units from {dc_a} (overstock) to {dc_b} (understock); saves {usd} carrying cost; raises {dc_b} fill rate by {pp} pp."*
- *"Lower target service for C-class SKUs from 95% to 90%; releases {usd} working capital with negligible revenue impact (modeled −{usd_revenue})."*

### 13.5 Dashboard 5 — Capacity Planning

**Layout**

```
Row 1: [Utilization %] [OEE] [Schedule Adherence] [FPY] [Throughput]
Row 2: [Capacity Load Profile (Gantt-style by line × week)]
Row 3: [Bottleneck Drill: top 5 constrained resources] | [Scenario: overtime vs outsource vs demand shaping]
```

**Filters:** Plant, line, shift, time bucket (week/month)

**Drill-down:** Line → work center → operation

**Alerts:**
- Utilization > 95% sustained > 2 weeks → burnout/disruption risk
- OEE < 65% → maintenance + training review
- FPY < 95% → quality investigation

**AI recommendations:**
- *"Shift {qty} units of {sku} from {line_a} (101% loaded) to {line_b} (62% loaded); avoids {hrs} overtime hours; cost neutral."*
- *"Schedule planned maintenance on {line} during {window}; lowest forecast demand period; minimizes service impact."*

### 13.6 Dashboard 6 — Financial Impact

**Layout**

```
Row 1: [Revenue] [Gross Margin] [EVA] [ROIC] [Logistics % of Sales] [Cash-to-Cash]
Row 2: [Scenario P&L Bridge Waterfall: Base → Scenario]
Row 3: [Budget vs Forecast vs Actual Line]  |  [Cost Breakdown Donut]
```

**Filters:** Scenario, region, business unit, fiscal period

**Drill-down:** Waterfall bar → cost driver detail; Cost donut slice → P&L line item

**Alerts:**
- Margin Δ vs plan > −2 pp → red
- Cash-to-Cash days > target +10 → working capital warning

**AI recommendations:**
- *"Switching {sku_count} SKUs from air to ocean freight saves {usd}/quarter; service impact +{days} lead time, modeled OTIF impact −{pp} pp."*
- *"Defer {capex} capacity investment by 1 quarter; supported by current demand trajectory at {p_conf}% confidence."*

### 13.7 Dashboard 7 — Risk Monitoring

**Layout**

```
Row 1: [Composite Risk Score Gauge] [# Critical Risks] [# Mitigation Actions Open]
Row 2: [Probability × Impact Heatmap]  |  [Top Risks Table with owner/status]
Row 3: [Risk Trend Line]  |  [Risk Contribution Tree (SHAP-based)]
```

**Filters:** Risk category (supply, demand, geopolitical, financial), region, horizon

**Drill-down:** Risk row → driver decomposition (SHAP waterfall); driver → underlying data

**Alerts:**
- Composite risk > 0.75 → P1 incident creation
- New event detected in news feed with severity=high → push notification

**AI recommendations:**
- *"Supplier {x} reliability dropped {pp} pp over last 30 days; recommend qualifying alternate supplier {y} (lead time +{days}, cost +{pct}%)."*
- *"Geopolitical risk for {region} elevated; recommend pre-building {weeks} weeks of safety stock on {sku_list}."*

### 13.8 Dashboard 8 — Sustainability

**Layout**

```
Row 1: [Scope 1 CO2e] [Scope 2 CO2e] [Scope 3 CO2e] [Energy Intensity] [vs SBTi Target]
Row 2: [Emissions Breakdown Donut by Source]  |  [Pareto: Carbon vs Cost frontier]
Row 3: [Scenario Levers: mode, route, supplier substitution]
```

**Filters:** Scope, region, category, mode, supplier tier

**Drill-down:** Donut slice → lane/SKU; Pareto point → scenario detail

**Alerts:**
- Trajectory vs SBTi target > 5% off → red gauge
- New high-carbon lane added → review flag

**AI recommendations:**
- *"Switch {lanes} from air to rail; reduces Scope 3 by {tco2}; service impact: {days} extra lead time on {pct}% of volume."*
- *"Qualify supplier {y} (lower-carbon manufacturing); reduces Scope 3 by {tco2}/year; cost premium {pct}%."*

### 13.9 Dashboard 9 — Regional Planning

**Layout**

```
Row 1: [Regional KPI cards: per-region service, inventory, cost, risk]
Row 2: [Choropleth Map of Demand vs Supply Balance]  |  [Region vs Plan Bar Chart]
Row 3: [Local Scenario Sliders: regional surge, local sourcing %, port lead-time shock]
```

**Filters:** Country, cluster, DC, region tier

**Drill-down:** Map region → DC → store/customer

**Alerts:**
- Regional fill rate < target → red region overlay
- Cross-region imbalance > threshold → rebalancing prompt

**AI recommendations:**
- *"Increase local sourcing in {region} from {pct_old}% to {pct_new}%; reduces lead time by {days}, lowers Scope 3 by {tco2}, cost +{pct}%."*

---

## 14. Storytelling & Decision Intelligence Layer

This section expands Module 7 (AI Copilot & NLP Interface) with the full storytelling component taxonomy and Human-AI collaboration models.

### 14.1 Ten Storytelling Component Types

| # | Component | Description | Where Surfaced | Generation Method |
|---|---|---|---|---|
| 1 | Narrative insight | 2–3 sentence summary of dashboard state | Top of each dashboard | LLM + KPI snapshot prompt |
| 2 | AI-generated summary | Plan-level briefing for executives | Executive Summary email digest | LLM with retrieval-augmented context |
| 3 | Root-cause explanation | Attribution of KPI deviations to drivers | KPI tile expansion | SHAP + LLM narrative wrapping |
| 4 | Trend interpretation | "Demand is trending X% above forecast in Y region due to Z" | Forecast Analytics, Regional | Trend detection + LLM phrasing |
| 5 | Opportunity identification | Quantified improvement actions | Inline action cards | Optimization engine + LLM |
| 6 | Risk explanation | Plain-language risk statements with drivers | Risk Monitoring tile | XGBoost + SHAP + LLM |
| 7 | Executive briefing (PDF/email) | Periodic summary of plan and KPI movements | Scheduled (daily/weekly) | LLM + template |
| 8 | Automated insight generation | Rule + LLM pattern detection over KPI snapshots | Alerts feed | Hybrid rules engine + LLM |
| 9 | Natural-language explanations | Explain any AI recommendation in plain English | Tooltips on AI badges | LLM with feature-importance context |
| 10 | Prescriptive recommendations | Ranked actions with expected impact | Action queue, dashboard right panel | Optimization + ranking + LLM |

### 14.2 API Contract

```
GET  /api/v1/storytelling/dashboard/{dashboard_id}/narrative
GET  /api/v1/storytelling/kpi/{kpi_id}/root-cause
GET  /api/v1/storytelling/recommendations?context={GlobalFilterState}
POST /api/v1/storytelling/briefing      // generate executive briefing
GET  /api/v1/storytelling/insight-feed  // automated insights stream
```

Response envelope:
```json
{
  "component_type": "root_cause_explanation",
  "kpi": "OTIF",
  "summary": "OTIF dropped 2.3 pp this week.",
  "drivers": [
    { "factor": "Port congestion at Shanghai", "contribution_pp": -1.4 },
    { "factor": "Supplier X late shipments", "contribution_pp": -0.6 },
    { "factor": "Demand surge in EMEA", "contribution_pp": -0.3 }
  ],
  "recommended_actions": [ { "action_id": "...", "label": "...", "expected_impact": "..." } ],
  "confidence": 0.82,
  "ai_generated": true
}
```

### 14.3 Human-AI Collaboration Models

The system supports three distinct interaction modes; the active mode is configurable per role and per decision class.

**Mode 1 — AI as Analyst**
- AI surfaces issues, computes options, proposes ranked actions.
- Human reviews, may accept, modify, or reject.
- Default mode for tactical planners.

**Mode 2 — Planner as Decision Maker**
- AI provides analysis only on request (pull, not push).
- Planner constructs the plan; AI validates and warns.
- Default mode for strategic decisions and senior planners.

**Mode 3 — AI as Coach**
- AI observes planner behavior over time (overrides, scenarios run, KPI outcomes).
- Provides feedback: FVA score, override accuracy, scenario coverage gaps.
- Surfaces process improvements: *"Your overrides on category X have positive FVA, but those on category Y are systematically biased."*

```sql
CREATE TABLE collab_mode_config (
  role_id            VARCHAR(50),
  decision_class     VARCHAR(50),    -- routine_replenishment, allocation, capacity_decision, strategic
  active_mode        VARCHAR(20) CHECK (active_mode IN ('analyst','decision_maker','coach')),
  human_in_loop_required BOOLEAN DEFAULT TRUE,
  approval_threshold_usd DECIMAL(18,2),  -- auto-execute below threshold; require approval above
  PRIMARY KEY (role_id, decision_class)
);
```

### 14.4 Explainable AI & Confidence Communication

- **Model cards** — every model in MLflow registry has a model card: training data window, features used, validation metrics, known limitations, retraining cadence. Exposed via `GET /api/v1/models/{model_id}/card`.
- **Plain-language risk statements** — risk numbers always accompanied by sentence-form interpretation: *"There is a 1-in-20 chance of a stockout on this SKU within the next 4 weeks."*
- **Scenario-range communication** — instead of single point forecasts, executives see ranges with worded confidence: *"Demand likely between 850k and 1.05M units (80% confidence)."*
- **Trust indicators** on every AI-generated element: data-freshness badge, model accuracy badge, last-retrained timestamp.

### 14.5 Cognitive Load & Stakeholder Alignment Rationale

Storytelling is not decoration. It exists to:
1. **Reduce cognitive load** — surface "so what" and "now what" before raw numbers, so planners triage faster.
2. **Align stakeholders** — a shared, AI-generated narrative gives demand, supply, finance, and ops teams the same starting interpretation, reducing meeting time.
3. **Build trust in AI** — explanations and confidence bands make AI outputs auditable.

---

## 15. Scenario Engine: Visual Interaction & Decision Mapping

This section expands Module 5 (Scenario & Simulation Engine) with frontend interaction specifications and per-scenario decision mappings.

### 15.1 Full Scenario Specification Table

| Scenario Type | Required Inputs | Simulation Logic | Outputs | Visual Interaction | Business Decisions Enabled |
|---|---|---|---|---|---|
| Best/Worst case | Base forecast, variability, risk distributions | Monte Carlo N=10,000 over forecast distribution | Outcome ranges (cost, service, carbon) | Fan chart + scenario comparison bars | Strategic targets, risk appetite, buffer sizing |
| Demand surge | Historical surges, promo plans, external signals | Scale demand by factor/region; re-run allocation | Capacity load, inventory needs, expediting cost | Sliders (surge magnitude 0–500%), region multi-select | Contingency, safety stock, capacity reservations |
| Supply disruption | Supplier reliability, lead-time variability, alternates | Remove/cap suppliers; re-optimize network | Service impact, alt sourcing cost, risk | Toggle suppliers on/off; disruption duration slider | Dual sourcing, inventory positioning, mitigation |
| Pricing strategy | Price elasticity, margin structure, competitive response | Demand response function; margin impact | Volume, margin, inventory implications | Price sliders (±%); demand curve overlay | Pricing optimization, promo planning |
| Weather impact | Weather forecasts, demand correlations | Regime-based demand adjustments | Regional demand, logistics delays | Weather scenario selector; overlay maps | Seasonal planning, logistics mitigation |
| Capacity constraint | Capacity limits, overtime costs, outsource options | Constrained optimization with overuse penalty | Utilization, cost, service | Capacity sliders (per resource); constraint toggles | Capex decisions, outsourcing, demand shaping |
| Inventory shortage | Current stock, pipeline, lead times, service targets | Simulate stockouts; allocate scarce inventory | Fill rate, allocation by customer/channel | Allocation rules editor; priority matrix | Customer prioritization, allocation policies |
| Workforce shortage | Absenteeism, shift patterns, skill mix | Reduce capacity; simulate overtime/contractors | Production output, cost | Absence-rate sliders; shift scenario selector | Temp labor, cross-training, demand leveling |
| Budget impact | Budget constraints, cost drivers | Capex/opex limits; optimize within envelope | Scenario P&L, feasibility | Budget slider; scenario table | Plan feasibility, budget reallocation |
| Sustainability trade-off | Carbon factors, mode choices, cost/service data | Multi-objective optimization (cost vs carbon vs service) | Pareto frontier | Multi-objective scatter; Pareto-point selector | Carbon-vs-cost-vs-service strategy |

### 15.2 Scenario Control Component Library (Frontend)

| Component | Use | Props |
|---|---|---|
| `<ScenarioSlider>` | Continuous numeric inputs (surge factor, price ±%, capacity %) | `min`, `max`, `step`, `value`, `unit`, `label`, `onChange` |
| `<ScenarioToggle>` | Binary on/off (supplier disruption, mode constraint) | `value`, `label`, `onChange` |
| `<ScenarioMultiSelect>` | Region/category/supplier selection | `options`, `selected`, `onChange` |
| `<ScenarioDateRange>` | Disruption window | `start`, `end`, `onChange` |
| `<ScenarioParetoSelector>` | Pick a point on the Pareto frontier | `frontierData`, `onSelect` |
| `<ScenarioAllocationMatrix>` | Editable priority matrix for inventory allocation | `customers`, `priorities`, `onChange` |

All controls write to a `<dcc.Store id="scenario-params">` (Dash) / Zustand store (React) and a debounced (500ms) call dispatches the simulation job.

### 15.3 Scenario Decision Mapping (UI → Decision)

Each scenario screen exposes a **"Decisions Enabled" rail** on the right side listing the concrete decisions the scenario supports. Clicking a decision navigates to the workflow (approval, PO, allocation policy update) prefilled with the scenario's recommended values — closing the loop from analysis to action.

### 15.4 AI-Assisted Scenario Generation

The Copilot can auto-propose plausible scenarios based on:
- Recent anomalies in `fact_demand` or `fact_supply`
- Event signals in `fact_external_event`
- Risk score elevations in `fact_kpi_snapshot`

Example: *"Port strike risk detected for Long Beach (probability 0.34, source: news feed). Run supply disruption scenario? [Yes, generate]"* → one click creates and runs the scenario.

---

## 16. Hybrid AI Risk Architecture & Uncertainty Visualization

This section expands Module 9 (Risk Scoring) and Section 5 (AI/ML Methodology) with the hybrid model taxonomy and the full uncertainty visualization library.

### 16.1 Hybrid Risk Model Architecture

The blueprint v1.0 used XGBoost only. v2.0 introduces a **layered hybrid system** for explainability and auditability of routine decisions:

```
                Risk Decision Request
                         │
                  ┌──────▼──────┐
                  │  Decision   │
                  │  Classifier │  (routine vs strategic)
                  └──────┬──────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼────────┐                ┌───────▼────────┐
│ Interpretable  │                │  Black-Box     │
│ Layer          │                │  Layer         │
│ Decision Tree  │                │  XGBoost +     │
│ (routine,      │                │  Graph features│
│  auditable)    │                │  (advanced)    │
└───────┬────────┘                └───────┬────────┘
        │                                 │
        └────────────┬────────────────────┘
                     │
              ┌──────▼──────┐
              │ SHAP / LIME │  (explanation layer)
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │ Plain-Lang  │
              │ Risk Stmt   │  (Copilot wrapper)
              └─────────────┘
```

**Routing rule:** Routine decisions (replenishment within authorized limits, standard supplier evaluations) → decision tree (auditable rules). Advanced/strategic decisions (multi-tier supplier risk, geopolitical event impact, capacity investment risk) → XGBoost ensemble with graph features.

### 16.2 AI Technique Coverage Map (Doc 2 §5.2)

| AI Technique | Cognitive Category | Best Applied To | Status in v2.0 |
|---|---|---|---|
| Fuzzy Logic Programming | Rational Thinking | Risk management (imprecise inputs) | New: `risk/fuzzy/` module for supplier risk classification with linguistic variables |
| Machine Learning & Big Data | Human Acting | Demand sensing | Existing (Module 3) |
| Agent-Based Systems | Rational Acting | Multi-echelon simulations | New: `simulation/agents/` for distributor/retailer agent simulation |
| Artificial Neural Networks | Human Thinking | Forecasting (LSTM, Transformer) | Existing (Module 3) |
| Expert Systems | Human Acting | Supplier selection, routine approvals | New: rules engine in `workflow-engine/rules/` |

**Implementation note:** Fuzzy logic and expert systems are added in Phase 3; agent-based simulation in Phase 4 for digital twin. They share the explanation API with the existing ML stack.

### 16.3 Uncertainty Visualization Library

| Technique | Use Case | Component | When |
|---|---|---|---|
| Fan chart | Forecast over time with quantile bands | `<FanChart>` | Dashboards 1, 3, 4, 9 |
| Quantile dot plot | Discrete probabilistic outcomes (20–50 dots) | `<QuantileDotPlot>` | Executive briefings, risk modal |
| Error bars with historical overlay | Compare current forecast uncertainty to historical | `<ErrorBarOverlay>` | Forecast Analytics drill-down |
| Traffic-light reliability indicator | Quick visual confidence per KPI tile | `<ReliabilityBadge>` (green/yellow/red) | All KPI cards |
| Density / violin plot | Full distribution of scenario outcomes | `<DensityPlot>` | Scenario detail page |
| Confidence interval bracket | Inline text with bracket | `<CIInline>` | Narrative text, executive briefings |

Each component renders from the same probabilistic payload:
```json
{ "p10": 850, "p25": 920, "p50": 1000, "p75": 1080, "p90": 1150, "n_samples": 10000 }
```

### 16.4 Calibration Monitoring

The system continuously monitors quantile calibration:
- P10 actual coverage should be ≈10%; P90 ≈ 90%.
- Deviation > 5pp → calibration warning on Forecast Analytics dashboard.
- Auto-trigger conformal prediction recalibration.

---

## 17. UX/UI Design System & Principles

This section establishes the design system the frontend must follow.

### 17.1 Core Design Principles

1. **Task-oriented design** — every dashboard maps to a planning workflow (demand review, supply review, consensus, exception handling). Navigation labels are verbs/tasks, not data domains.
2. **Information hierarchy** — top-left = most critical KPI; eye-flow Z-pattern across desktop, F-pattern on mobile. Primary action always above the fold.
3. **Minimal clutter** — **maximum 7 widgets per dashboard view**; use progressive disclosure (drill-down, expansion panels) instead of crowding.
4. **Responsive layouts** — desktop-first (1440px baseline), tablet (1024px) fully supported, mobile (375px) for executive KPIs and alerts only.
5. **Dark mode by default** — control-room ergonomics; light mode toggle available.
6. **Accessibility — WCAG 2.1 AA compliance** — minimum 4.5:1 contrast for text, 3:1 for UI components; full keyboard navigation; ARIA labels on all interactive elements; color-blind-safe palettes (Okabe-Ito as fallback).
7. **Mobile executive dashboard** — distilled view: top 5 KPIs, alerts feed, scenario comparison summary. No deep editing on mobile.

### 17.2 Color System & Semantics

**Status semantics (mandatory across all dashboards):**

| Color | Hex | Semantic |
|---|---|---|
| Red `#f85149` | Critical / breach / stockout | Severity 1 |
| Orange `#d29922` | Warning / approaching threshold | Severity 2 |
| Yellow `#e3b341` | Informational warning | Severity 3 |
| Green `#3fb950` | On-track / improvement | Healthy |
| Blue `#58a6ff` | Informational / neutral data | Default chart |
| Purple `#bc8cff` | AI-generated content | AI badge |
| Gray `#8b949e` | Inactive / muted / secondary | Secondary text |

**Saturation rules:** higher saturation = higher severity. Pastel variants used for backgrounds; full saturation for foreground indicators.

**Color-blind safety:** Never rely on color alone — always pair with icon (✕, ⚠, ✓) or shape.

### 17.3 Attention Guidance Rules

- **Size**: Primary KPIs use 2.5rem+ numerals; secondary 1.25rem; tertiary 0.875rem.
- **Position**: Most important info top-left; AI-generated narrative immediately below KPI strip.
- **Motion**: Reserve animation for state changes (KPI delta arrows, scenario sim progress). Never decorative.
- **Iconography**: Reserved for status (✓ ⚠ ✕), AI-generated badge (✨), and drill-down affordance (›).

### 17.4 Typography Stack

```css
--font-display: "Inter", system-ui, sans-serif;     /* headers */
--font-body: "Inter", system-ui, sans-serif;         /* body */
--font-mono: "JetBrains Mono", monospace;            /* KPI numerals, IDs */

--size-h1: 1.75rem;  --weight-h1: 700;
--size-h2: 1.375rem; --weight-h2: 600;
--size-kpi: 2.5rem;  --weight-kpi: 700;  --font-kpi: var(--font-mono);
--size-body: 0.875rem; --weight-body: 400;
--size-caption: 0.75rem; --weight-caption: 500;  /* uppercase + letter-spacing 0.05em */
```

### 17.5 Component Library (Atomic Design)

```
atoms/      Button, Input, Badge, Icon, StatusDot, Spinner, ReliabilityBadge
molecules/  KpiCard, FilterPill, AlertBanner, BreadcrumbNav, Sparkline
organisms/  KpiStrip, ScenarioComparisonTable, ActionQueue, RiskHeatmap, FanChart
templates/  DashboardShell, ModalShell, DrawerShell
pages/      9 dashboards
```

### 17.6 KPI Card Specification

Every KPI card must include:
1. Metric title (caption style, uppercase)
2. Current value (display style, monospaced)
3. Target value (caption, muted)
4. Delta vs previous period (colored arrow + percent)
5. Sparkline (7–14 period trend)
6. Status indicator dot (red/yellow/green)
7. AI badge (✨) if value is AI-derived
8. Reliability badge (data freshness + confidence)

### 17.7 Planning Workflow & Collaboration

- **Guided S&OP step-by-step flow** — wizard component for monthly cycle: Demand Review → Supply Review → Pre-S&OP → Executive S&OP. Each step has its own dashboard view, completion checklist, and handoff.
- **Approval workflows** embedded into dashboards via the `<ApprovalDrawer>` — submit/approve/reject without context switch.
- **Annotations** — every chart and KPI tile accepts pinned comments (`fact_annotation` table) with @mentions and resolution status.
- **Co-editing scenarios** — operational transformation via WebSocket; presence indicators (avatars) on active scenario; conflict resolution via optimistic locking with merge UI.
- **Comment threads on plan versions** — threaded discussion attached to each `plan_version_id`; survives version supersession.

```sql
CREATE TABLE fact_annotation (
  annotation_id   UUID PRIMARY KEY,
  target_type     VARCHAR(50),         -- 'kpi','chart','plan_version','scenario'
  target_id       VARCHAR(100),
  parent_id       UUID,                -- for threading
  author_id       VARCHAR(50),
  body            TEXT,
  mentions        JSONB,
  resolved        BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMP,
  resolved_at     TIMESTAMP
);
```

### 17.8 Visualization Tactics Mapping

| Analytical Goal | Tactic | Technique | Where Used |
|---|---|---|---|
| Trend identification | Temporal analysis | Time-series line charts | Dashboards 1, 3, 6 |
| Multi-dimensional analysis | Clustering | Heatmaps (SKU × time, region × category) | Dashboards 2, 4, 7 |
| Spatial analysis | Geospatial mapping | Choropleth, bubble maps | Dashboards 4, 9 |
| Network analysis | Force-directed layout | Supplier dependency graph | Dashboard 7 (new component) |
| Scenario comparison | Coordinated views | Multi-panel small-multiples | Dashboard 1, scenario detail |
| Risk identification | Sensitivity analysis | Tornado charts, P×I matrix | Dashboard 7 |
| Distribution analysis | Density visualization | Violin, density plots | Scenario detail, forecast drill |

### 17.9 Supplier Network Graph (New Component)

For Dashboard 7, add a `<SupplierNetworkGraph>` force-directed visualization:
- Nodes = suppliers (sized by spend, colored by tier 1/2/3)
- Edges = dependency (weighted by volume share)
- Node halo color = risk score
- Click node → SHAP-driven risk decomposition modal
- Hover edge → lead time and reliability stats

---

## 18. Platform Benchmarks & Industry KPI Targets

### 18.1 Platform Comparison

| Capability | SAP IBP | Blue Yonder | Kinaxis | o9 | Anaplan | This System (target) |
|---|---|---|---|---|---|---|
| Probabilistic forecasting | Limited | Strong | Moderate | Strong | Limited | Strong (quantile + conformal) |
| Scenario engine (concurrent scenarios) | Yes | Yes | Strongest (concurrent planning) | Yes | Yes | Yes (unlimited, async) |
| Real-time streaming | Limited | Moderate | Moderate | Strong | Limited | Strong (Kafka + Flink) |
| Native AI Copilot | Joule (emerging) | Cognitive | Maestro | DigitalBrain | CoPlanner | Yes (LLM + RAG) |
| Explainable AI | Partial | Partial | Partial | Yes | Limited | Yes (SHAP + LLM narrative) |
| Multi-objective optimization (cost/service/carbon) | Yes | Yes | Yes | Yes | Limited | Yes (Pareto + scenario) |
| Open data stack | Limited | Moderate | Moderate | Moderate | Limited | Yes (lakehouse, dbt, Parquet) |
| Customization velocity | Slow | Moderate | Fast | Fast | Fast | Fast (modular microservices) |

**Differentiation thesis for this system:** open data layer + first-class AI Copilot + per-scenario decision mapping + WCAG-grade UX, at lower TCO than incumbents.

### 18.2 Industry KPI Benchmarks (reference, planner-configurable)

| KPI | CPG/Retail | Industrial/B2B | Pharma/Med Device | Automotive | Hi-Tech |
|---|---|---|---|---|---|
| Forecast WAPE (portfolio) | 15–25% | 20–30% | 10–20% | 15–25% | 25–40% |
| OTIF | 95–98% | 92–96% | 98–99.5% | 96–99% | 90–95% |
| Inventory Turns | 8–12× | 4–8× | 3–6× | 8–14× | 6–10× |
| DOS (finished goods) | 30–45 d | 45–75 d | 60–120 d | 25–40 d | 45–90 d |
| Fill rate | 95–98% | 90–95% | 98–99.5% | 95–98% | 92–96% |
| Cash-to-cash | 30–60 d | 60–120 d | 90–180 d | 30–75 d | 60–120 d |
| Logistics % of sales | 4–9% | 6–12% | 3–7% | 5–10% | 3–6% |
| OEE | 60–75% | 65–80% | 70–85% | 75–90% | 70–85% |

Benchmarks stored in `dim_industry_benchmark` and used to color KPI tiles when an organization's industry is configured.

```sql
CREATE TABLE dim_industry_benchmark (
  industry          VARCHAR(50),
  kpi_name          VARCHAR(100),
  percentile_25     DECIMAL(18,4),
  percentile_50     DECIMAL(18,4),
  percentile_75     DECIMAL(18,4),
  source            VARCHAR(200),
  as_of_date        DATE,
  PRIMARY KEY (industry, kpi_name, as_of_date)
);
```

---

## 19. Deliverables Traceability Matrix

This matrix maps the 11 deliverables originally requested in Doc 1 §10.1 to sections in this blueprint, closing the audit gap.

| # | Required Deliverable | Section(s) | Status |
|---|---|---|---|
| 1 | Detailed dashboard architecture | §2, §13 | ✅ |
| 2 | Dashboard hierarchy | §3 Module 6, §13 | ✅ |
| 3 | KPI dictionary | §3 Module 2 + §11, §12 | ✅ |
| 4 | Scenario planning framework | §3 Module 5 + §15 | ✅ |
| 5 | UX wireframe descriptions | §13 (per-dashboard layouts), §17 | ✅ |
| 6 | Storytelling framework | §14 | ✅ |
| 7 | AI recommendation framework | §3 Module 7, §14, §16 | ✅ |
| 8 | Executive dashboard strategy | §13.1 (with role personalization) | ✅ |
| 9 | Best practices comparison across platforms | §18.1 | ✅ |
| 10 | Industry benchmark analysis | §18.2 | ✅ |
| 11 | Implementation roadmap | §6.1 | ✅ |

---

*End of Blueprint v2.0*
*Treat as a living specification. All v1.0 content remains authoritative; v2.0 sections (10–19) are additive expansions resolving the gap analysis. Update section headers with version notes as design decisions evolve.*

---

**OK — ans provided in full above.** The blueprint v2.0 integrates every High, Medium, and Low priority gap from your analysis: full forecasting input catalog (§10), extended KPI dictionary with production/financial/resource/service KPIs and schemas (§11), PCTM interdependency model (§12), per-dashboard detailed specs with layouts/filters/drill-downs/alerts/AI recommendation templates/role personalization (§13), 10-component storytelling layer and 3 Human-AI collaboration modes (§14), full scenario interaction specs with visual controls and decision mapping (§15), hybrid AI risk architecture (decision tree + XGBoost + fuzzy + expert systems + agents) with full uncertainty visualization library (§16), complete UX/UI design system with WCAG/color/typography/component library/supplier network graph (§17), platform benchmarks and industry KPI targets (§18), and a deliverables traceability matrix (§19). Sections 1–9 of v1.0 are preserved verbatim.