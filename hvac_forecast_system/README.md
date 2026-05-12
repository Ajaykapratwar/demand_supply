# HVAC Inventory Forecasting & Allocation System

A two-stage ML system for HVAC supply chain optimization in the India market.

## Overview

**Stage 1 — Demand Forecasting:** Predict AC unit demand per Region × Month using weather signals, macro indicators, and historical sales (XGBoost + Prophet).

**Stage 2 — Inventory Allocation:** Given probabilistic demand forecasts (P50/P90), allocate optimal inventory across warehouses using Linear Programming (PuLP) to minimise cost subject to capacity, safety stock, and SLA constraints.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run full pipeline
python -m src.feature_store.merge_pipeline       # Step 1: Build feature store
python run_pipeline.py                            # Steps 2-9: Full pipeline

# Run tests
pytest tests/ -m unit -v                          # Unit tests only
pytest tests/ -v --cov=src --cov-report=html      # Full suite with coverage
```

## Project Structure

```
hvac_forecast_system/
├── data/raw/                  # 5 source CSVs (DS1-DS5)
├── data/processed/            # Parquet feature tables
├── data/outputs/              # Forecasts & allocation plans
├── src/
│   ├── feature_store/         # Merge, feature eng, imputation
│   ├── forecasting/           # XGBoost, Prophet, quantile forecaster
│   ├── allocation/            # LP optimizer, safety stock
│   ├── cost_estimator/        # Lasso cost model
│   └── evaluation/            # Metrics, reports
├── tests/
│   ├── unit/                  # Fast unit tests
│   ├── integration/           # Pipeline-level tests
│   └── regression/            # Accuracy gate tests (>80%)
├── configs/                   # YAML configs
└── requirements.txt
```

## Key Metrics & Targets

| Metric | Target | Description |
|--------|--------|-------------|
| R² | ≥ 0.80 | Variance explained by model |
| MAPE | ≤ 20% | Mean Absolute Percentage Error |
| RMSE % | ≤ 20% | RMSE normalised by mean demand |
| Allocation SLA | ≥ 95% | Fulfillment rate across regions |

## Datasets

| Dataset | Rows | Key Signal |
|---------|------|------------|
| DS1 Order History | 14,400 | Fulfillment Rate, Backordered Units |
| DS2 Sales Revenue | 14,400 | Net Units Sold (target), Revenue |
| DS3 Demand Signals | 14,400 | Weather (r=0.59), Google Trends |
| DS4 Warehouse Capacity | 10,800 | Utilization%, Days of Supply |
| DS5 Logistics Cost | 14,400 | Cost/Unit, CO2 Emissions |

## Architecture

```
Raw CSVs → Feature Store → XGBoost P50/P75/P90 → Allocation LP → Evaluation
                         → Lasso Cost Estimator ↗
```
