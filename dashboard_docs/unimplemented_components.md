# Blueprint v2.0 — Unimplemented Components & Architectural Gaps

This document tracks all components, modules, and features specified in the **AI-Powered Demand-Supply Blueprint v2.0** that are not yet implemented in the current `planning-dashboard` architecture.

## 1. Advanced AI & Simulation Modules
*Reference: §16.2 AI Technique Coverage Map*

- [x] **Fuzzy Logic Engine (`risk/fuzzy/`)**: Implementation of linguistic variables (e.g., "High Risk", "Moderate Stability") for supplier risk classification.
- [x] **Expert Rules Engine (`workflow-engine/rules/`)**: A logic-based system for routine decision automation, such as auto-approvals for low-value replenishment.
- [x] **Agent-Based Simulation (`simulation/agents/`)**: Multi-echelon simulation of distributor and retailer behavior for "Digital Twin" functionality.
- [x] **Native Explainable AI (SHAP/LIME)**: Direct integration of feature importance waterfalls into the UI for all AI-badged (✨) KPIs.

## 2. Specialized Visualization Components
*Reference: §16.3 Uncertainty Library & §17.8 Visualization Tactics*

- [x] **Supplier Network Graph**: A force-directed visualization (Nodes = Suppliers, Edges = Dependencies) for multi-tier risk visibility.
- [x] **Quantile Dot Plot (`<QuantileDotPlot>`)**: Discrete probabilistic outcome visualization using dot-density patterns.
- [x] **Density / Violin Plot (`<DensityPlot>`)**: Visualization of full outcome distributions for scenario comparisons.
- [x] **Pareto Frontier Interaction**: Interactive scatter plot for multi-objective optimization (Cost vs. Service vs. Carbon).
- [x] **Tornado Chart**: Sensitivity analysis visualization for identifying top drivers of forecast error or risk.

## 3. Workflow & Collaboration System
*Reference: §17.7 Planning Workflow & Collaboration*

- [x] **Guided S&OP Wizard**: A step-by-step UI flow for the monthly S&OP cycle (Demand Review → Supply Review → Pre-S&OP → Exec S&OP).
- [x] **Approval Drawer (`<ApprovalDrawer>`)**: A slide-out component for submitting, reviewing, and approving planning decisions without leaving the dashboard.
- [x] **Annotation System**: A collaborative layer allowing users to pin comments and @mentions to specific KPI tiles or chart data points.
- [x] **Co-editing & Presence**: Real-time collaborative scenario planning with user presence indicators (avatars) and conflict resolution.

## 4. Intelligence & Decision Support
*Reference: §14.1 Storytelling Taxonomy & §16.4 Calibration*

- [x] **Automated Insight Feed**: A proactive stream of "Rule + LLM" generated insights surfaced as an alerts feed.
- [x] **Executive Briefing Generator**: One-click or scheduled generation of PDF/Email briefing documents summarizing the consensus plan.
- [x] **Calibration Monitoring**: Real-time tracking of forecast quantile coverage with automatic triggers for conformal recalibration.
- [x] **Human-AI Collaboration Modes**: UI toggle to switch the system between "Analyst" (Push), "Decision Maker" (Pull), and "Coach" (Behavioral Feedback) modes.

## 5. Data Architecture (Missing Schema/Integration)
*Reference: §10.6, §11, §12.3, §14.3*

- [x] **Workforce Snapshot (`fact_workforce`)**: Integration of shift patterns, absenteeism, and skill-mix data into the Capacity dashboard.
- [x] **External Event Log (`fact_external_event`)**: Integration of weather, geopolitical, and strike events into the Risk dashboard.
- [x] **Pricing Change Fact (`fact_pricing_change`)**: Tracking of price elasticity and historical promo impacts.
- [x] **KPI Interdependency Storage**: Moving the PCTM model from hardcoded logic to a permanent database table.
- [x] **Industry Benchmark Integration**: Dynamic comparison against industry percentiles stored in `dim_industry_benchmark`.

---
*Last Updated: 2026-05-14*
*Status: Phase 4 & 5 Complete*
