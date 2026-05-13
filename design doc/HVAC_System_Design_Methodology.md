# HVAC Inventory Forecasting & Allocation System
## System Design, Methodology & Engineering Specification

**Version:** 1.0  
**Domain:** HVAC Supply Chain — India Market  
**Datasets:** 5 structured CSVs (Jan 2018 – Dec 2023, 72 monthly snapshots)  
**Target Accuracy:** MSE/MAE/RMSE meeting >80% benchmark on held-out test set

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Dataset Summary & Key Findings](#2-dataset-summary--key-findings)
3. [System Architecture](#3-system-architecture)
4. [Project File Structure](#4-project-file-structure)
5. [Feature Store Design](#5-feature-store-design)
6. [Forecasting Layer](#6-forecasting-layer)
7. [Allocation Optimizer](#7-allocation-optimizer)
8. [Evaluation Metrics & Acceptance Criteria](#8-evaluation-metrics--acceptance-criteria)
9. [Testing Strategy (pytest)](#9-testing-strategy-pytest)
10. [File-by-File Specification](#10-file-by-file-specification)
11. [Pipeline Execution Order](#11-pipeline-execution-order)
12. [Risk Register](#12-risk-register)

---

## 1. Problem Statement

The objective is to build a two-stage ML system for an HVAC distributor operating across 5 Indian regions:

**Stage 1 — Demand Forecasting:** Predict AC unit demand per SKU × Region × Month using weather signals, macro indicators, and historical sales.

**Stage 2 — Inventory Allocation:** Given probabilistic demand forecasts (P50/P90), allocate optimal inventory across 50 warehouses minimising total cost subject to capacity, safety stock, and SLA constraints.

**Business KPIs to improve:**
- Reduce stockouts (current Fulfillment Rate mean: 88.3%; target: ≥95%)
- Reduce dead stock (100% of warehouses have avg Stock_Aging_90d > 50 units)
- Minimise logistics + carrying cost per unit

---

## 2. Dataset Summary & Key Findings

| Dataset | Rows | Key Signal | Forecasting Role |
|---------|------|-----------|-----------------|
| DS1 Order History | 14,400 | Fulfillment Rate, Backordered Units | Demand actuals, supply gaps |
| DS2 Sales Revenue | 14,400 | Net Units Sold, Revenue, Discount | Primary demand labels |
| DS3 Demand Signals | 14,400 | Max_Temp_C (r=0.594), CDD, Google Trends | Core feature inputs |
| DS4 Warehouse Capacity | 10,800 | Utilization%, DaysOfSupply, Aging | Allocation constraints |
| DS5 Logistics Cost | 14,400 | CO2 (r=0.677 with volume), Cost/Unit | Allocation objective |

**Critical findings driving model choices:**
- DS3 weather features have moderate-strong correlations (r=0.51–0.59) with demand → XGBoost viable
- DS4 warehouse variables are uncorrelated (synthetic uniform) → LP optimizer, not ML, for allocation
- DS5 Cost_Per_Unit is decorrelated from distance/volume → Lasso for cost estimation only
- 3% null rate across numeric columns → imputation required before modeling
- Semiconductor_Shortage_Score (skew 3.56) and COVID_Impact_Score (91.7% zero) → drop or binary encode

---

## 3. System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    RAW DATA LAYER                        │
│  DS1 Orders │ DS2 Sales │ DS3 Signals │ DS4 WH │ DS5 Cost│
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                 FEATURE STORE                            │
│  Join Key: SKU × Region × Month                         │
│  - Demand actuals (DS1+DS2)                             │
│  - Weather & macro features with lags (DS3)             │
│  - Supply-side features (DS4)                           │
│  - Cost lane features (DS5)                             │
│  Output: master_feature_table.parquet                   │
└──────────────────────┬───────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼           
┌──────────────────┐     ┌──────────────────────┐
│ FORECASTING      │     │ COST ESTIMATOR        │
│ XGBoost (demand) │     │ Lasso Regression      │
│ Prophet (trend)  │     │ (Cost_Per_Unit_INR)   │
│ Output: P50/P90  │     └──────────┬────────────┘
└────────┬─────────┘                │
         │                          │
         └──────────┬───────────────┘
                    ▼
┌──────────────────────────────────────────────────────────┐
│              ALLOCATION OPTIMIZER (PuLP LP)              │
│  Inputs: P50/P90 forecasts + DS4 capacity + cost lanes  │
│  Constraints: capacity, demand satisfaction, safety      │
│               stock, inventory availability, SLA         │
│  Objective: min(carrying + logistics + stockout penalty) │
│  Output: allocation_plan.csv                            │
└──────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│              EVALUATION & MONITORING                     │
│  Metrics: RMSE, MAE, MAPE, R², Pinball Loss (quantile)  │
│  Tests: pytest suite (unit + integration + regression)   │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Project File Structure

```
hvac_forecast_system/
│
├── data/
│   ├── raw/
│   │   ├── dataset1_order_history.csv
│   │   ├── dataset2_sales_revenue.csv
│   │   ├── dataset3_demand_signals.csv
│   │   ├── dataset4_warehouse_capacity.csv
│   │   └── dataset5_logistics_cost.csv
│   ├── processed/
│   │   ├── master_feature_table.parquet
│   │   ├── train_features.parquet
│   │   ├── val_features.parquet
│   │   └── test_features.parquet
│   └── outputs/
│       ├── demand_forecasts.csv
│       ├── quantile_forecasts.csv
│       └── allocation_plan.csv
│
├── src/
│   ├── __init__.py
│   ├── feature_store/
│   │   ├── __init__.py
│   │   ├── merge_pipeline.py          # DS1–DS5 join logic
│   │   ├── feature_engineering.py     # Lag features, rolling means
│   │   └── imputation.py              # Median/KNN imputation
│   │
│   ├── forecasting/
│   │   ├── __init__.py
│   │   ├── xgboost_model.py           # XGBoost demand forecaster
│   │   ├── prophet_model.py           # Prophet time-series layer
│   │   ├── quantile_forecaster.py     # P50/P75/P90 outputs
│   │   └── model_registry.py          # Save/load trained models
│   │
│   ├── allocation/
│   │   ├── __init__.py
│   │   ├── lp_optimizer.py            # PuLP linear program
│   │   ├── safety_stock.py            # P90 - P50 safety stock logic
│   │   └── constraints.py             # Constraint definitions
│   │
│   ├── cost_estimator/
│   │   ├── __init__.py
│   │   └── lasso_cost_model.py        # Lasso for Cost_Per_Unit
│   │
│   └── evaluation/
│       ├── __init__.py
│       ├── metrics.py                 # RMSE, MAE, MAPE, R², Pinball
│       └── reports.py                 # Metric summary generation
│
├── tests/
│   ├── conftest.py                    # Shared fixtures
│   ├── unit/
│   │   ├── test_imputation.py
│   │   ├── test_feature_engineering.py
│   │   ├── test_merge_pipeline.py
│   │   ├── test_xgboost_model.py
│   │   ├── test_quantile_forecaster.py
│   │   ├── test_safety_stock.py
│   │   ├── test_lp_optimizer.py
│   │   └── test_metrics.py
│   ├── integration/
│   │   ├── test_full_pipeline.py
│   │   └── test_allocation_end_to_end.py
│   └── regression/
│       └── test_model_accuracy.py     # Enforces >80% accuracy gates
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_feature_store_validation.ipynb
│   └── 03_model_evaluation.ipynb
│
├── configs/
│   ├── model_config.yaml              # Hyperparameters
│   ├── constraint_config.yaml         # LP constraints
│   └── pipeline_config.yaml           # Run settings
│
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## 5. Feature Store Design

### 5.1 Join Key

All datasets are joined on composite key: `(Region × Month)` for regional aggregates, extended to `(SKU × Region × Month)` where SKU-level data is available.

### 5.2 `src/feature_store/merge_pipeline.py`

```python
"""
merge_pipeline.py
Merges all 5 datasets into master_feature_table.parquet
Join key: Region × Month (+ SKU where available)
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_raw_datasets(data_dir: str) -> dict:
    """Load all 5 raw CSVs. Returns dict of DataFrames."""
    base = Path(data_dir)
    return {
        "orders":    pd.read_csv(base / "dataset1_order_history.csv",    parse_dates=["Date"]),
        "sales":     pd.read_csv(base / "dataset2_sales_revenue.csv",    parse_dates=["Date"]),
        "signals":   pd.read_csv(base / "dataset3_demand_signals.csv",   parse_dates=["Date"]),
        "warehouse": pd.read_csv(base / "dataset4_warehouse_capacity.csv", parse_dates=["Date"]),
        "logistics": pd.read_csv(base / "dataset5_logistics_cost.csv",   parse_dates=["Date"]),
    }


def extract_year_month(df: pd.DataFrame, date_col: str = "Date") -> pd.DataFrame:
    df = df.copy()
    df["YearMonth"] = df[date_col].dt.to_period("M")
    return df


def aggregate_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate DS1 to Region × Month level."""
    df = extract_year_month(df)
    return df.groupby(["Region", "YearMonth"]).agg(
        Avg_Fulfillment_Rate=("Fulfillment_Rate_%", "mean"),
        Total_Units_Backordered=("Units_Backordered", "sum"),
        Total_Units_Ordered=("Units_Ordered", "sum"),
        Total_Units_Fulfilled=("Units_Fulfilled", "sum"),
    ).reset_index()


def aggregate_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate DS2 to Region × Month. Net_Units_Sold_TARGET is the demand label."""
    df = extract_year_month(df)
    return df.groupby(["Region", "YearMonth"]).agg(
        Net_Units_Sold=("Net_Units_Sold_TARGET", "sum"),
        Avg_Selling_Price=("Avg_Selling_Price_INR", "mean"),
        Avg_Discount=("Discount_%", "mean"),
        Total_Revenue=("Net_Revenue_INR", "sum"),
    ).reset_index()


def aggregate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate DS3 weather/macro signals to Region × Month."""
    df = extract_year_month(df)
    # Drop near-zero-variance features
    drop_cols = ["COVID_Impact_Score", "Semiconductor_Shortage_Score",
                 "Consumer_Confidence_Index"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])
    return df.groupby(["Region", "YearMonth"]).agg(
        Max_Temp_C=("Max_Temp_C", "mean"),
        Min_Temp_C=("Min_Temp_C", "mean"),
        Cooling_Degree_Days=("Cooling_Degree_Days", "sum"),
        Google_Trends_AC_Index=("Google_Trends_AC_Index", "mean"),
        Heatwave_Severity_Score=("Heatwave_Severity_Score", "mean"),
        Festive_Multiplier=("Festive_Multiplier", "max"),
        Composite_Demand_Index=("Composite_Demand_Index", "mean"),
        Forecast_Demand_Target=("Forecast_AC_Units_Next_Month_TARGET", "mean"),
    ).reset_index()


def aggregate_warehouse(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate DS4 to Region × Month supply-side features."""
    df = extract_year_month(df)
    return df.groupby(["Region", "YearMonth"]).agg(
        Avg_Utilization=("Utilization_%", "mean"),
        Avg_Days_Of_Supply=("Days_Of_Supply_Remaining", "mean"),
        Total_Aged_Stock_90d=("Stock_Aging_90d_Plus", "sum"),
        Avg_SLA_Compliance=("SLA_Compliance_%", "mean"),
    ).reset_index()


def aggregate_logistics(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate DS5 to Region × Month cost features."""
    df = extract_year_month(df)
    return df.groupby(["Region", "YearMonth"]).agg(
        Total_Units_Shipped=("Units_Shipped", "sum"),
        Avg_Distance_KM=("Distance_KM", "mean"),
        Avg_Cost_Per_Unit=("Cost_Per_Unit_INR", "mean"),
        Total_CO2_Kg=("CO2_Emissions_Kg", "sum"),
    ).reset_index()


def build_master_table(data_dir: str, output_path: str) -> pd.DataFrame:
    """
    Full merge pipeline. Returns master feature table.
    Join key: Region × YearMonth
    """
    dfs = load_raw_datasets(data_dir)

    orders_agg    = aggregate_orders(dfs["orders"])
    sales_agg     = aggregate_sales(dfs["sales"])
    signals_agg   = aggregate_signals(dfs["signals"])
    warehouse_agg = aggregate_warehouse(dfs["warehouse"])
    logistics_agg = aggregate_logistics(dfs["logistics"])

    # Sequential left joins on Region × YearMonth
    master = (
        sales_agg
        .merge(orders_agg,    on=["Region", "YearMonth"], how="left")
        .merge(signals_agg,   on=["Region", "YearMonth"], how="left")
        .merge(warehouse_agg, on=["Region", "YearMonth"], how="left")
        .merge(logistics_agg, on=["Region", "YearMonth"], how="left")
    )

    # Sort chronologically
    master = master.sort_values(["Region", "YearMonth"]).reset_index(drop=True)
    master.to_parquet(output_path, index=False)
    return master
```

### 5.3 `src/feature_store/feature_engineering.py`

```python
"""
feature_engineering.py
Creates lag features, rolling statistics, and cyclic time encodings.
"""

import pandas as pd
import numpy as np


LAG_WINDOWS   = [1, 2, 3, 6]      # months lag for demand signal
ROLL_WINDOWS  = [3, 6]             # rolling mean windows


def add_lag_features(df: pd.DataFrame, target_col: str = "Net_Units_Sold",
                     group_col: str = "Region") -> pd.DataFrame:
    """Add lag_1 through lag_6 for target per region."""
    df = df.sort_values([group_col, "YearMonth"]).copy()
    for lag in LAG_WINDOWS:
        df[f"{target_col}_lag_{lag}"] = (
            df.groupby(group_col)[target_col].shift(lag)
        )
    return df


def add_rolling_features(df: pd.DataFrame, target_col: str = "Net_Units_Sold",
                          group_col: str = "Region") -> pd.DataFrame:
    """Add rolling mean and std over 3 and 6 month windows."""
    df = df.sort_values([group_col, "YearMonth"]).copy()
    for w in ROLL_WINDOWS:
        df[f"{target_col}_roll_mean_{w}"] = (
            df.groupby(group_col)[target_col]
            .transform(lambda x: x.shift(1).rolling(w, min_periods=1).mean())
        )
        df[f"{target_col}_roll_std_{w}"] = (
            df.groupby(group_col)[target_col]
            .transform(lambda x: x.shift(1).rolling(w, min_periods=1).std())
        )
    return df


def add_cyclic_time_features(df: pd.DataFrame,
                              period_col: str = "YearMonth") -> pd.DataFrame:
    """Encode month as sin/cos to capture seasonality."""
    df = df.copy()
    month_num = df[period_col].dt.month if hasattr(df[period_col], "dt") else \
                df[period_col].apply(lambda p: p.month)
    df["month_sin"] = np.sin(2 * np.pi * month_num / 12)
    df["month_cos"] = np.cos(2 * np.pi * month_num / 12)
    df["month_num"] = month_num
    return df


def add_region_encoding(df: pd.DataFrame, region_col: str = "Region") -> pd.DataFrame:
    """One-hot encode regions."""
    return pd.get_dummies(df, columns=[region_col], prefix="region", drop_first=False)


def build_model_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply full feature engineering pipeline. Call after merge."""
    df = add_lag_features(df)
    df = add_rolling_features(df)
    df = add_cyclic_time_features(df)
    df = add_region_encoding(df)
    return df


# Selected feature set for XGBoost (max 10 features, avoids overfitting)
XGBOOST_FEATURES = [
    "Max_Temp_C",
    "Cooling_Degree_Days",
    "Google_Trends_AC_Index",
    "Composite_Demand_Index",
    "Festive_Multiplier",
    "Net_Units_Sold_lag_1",
    "Net_Units_Sold_lag_3",
    "Net_Units_Sold_roll_mean_3",
    "month_sin",
    "month_cos",
]

TARGET_COL = "Net_Units_Sold"
```

### 5.4 `src/feature_store/imputation.py`

```python
"""
imputation.py
Handles ~3% null rate across all numeric columns.
Strategy: median imputation per Region group.
"""

import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer


def median_impute_by_group(df: pd.DataFrame, group_col: str = "Region",
                            numeric_cols: list = None) -> pd.DataFrame:
    """Fill nulls with per-group median. Fallback: global median."""
    df = df.copy()
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_cols:
        group_medians = df.groupby(group_col)[col].transform("median")
        global_median = df[col].median()
        df[col] = df[col].fillna(group_medians).fillna(global_median)

    return df


def validate_no_nulls(df: pd.DataFrame, cols: list) -> bool:
    """Assert no nulls remain in specified columns after imputation."""
    null_counts = df[cols].isnull().sum()
    if null_counts.any():
        raise ValueError(f"Nulls remain after imputation:\n{null_counts[null_counts > 0]}")
    return True
```

---

## 6. Forecasting Layer

### 6.1 `src/forecasting/xgboost_model.py`

```python
"""
xgboost_model.py
XGBoost demand forecaster with quantile outputs.
Targets: Net_Units_Sold (P50 point forecast)
Quantile targets: P75, P90 using objective='reg:quantileerror'
Regularization: max_depth=5, early_stopping, 5-fold TimeSeriesSplit CV
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.feature_store.feature_engineering import XGBOOST_FEATURES, TARGET_COL


XGBOOST_PARAMS = {
    "n_estimators":        500,
    "max_depth":           5,
    "learning_rate":       0.05,
    "subsample":           0.8,
    "colsample_bytree":    0.8,
    "min_child_weight":    5,
    "reg_alpha":           0.1,       # L1
    "reg_lambda":          1.0,       # L2
    "random_state":        42,
    "early_stopping_rounds": 30,
    "eval_metric":         "rmse",
}

QUANTILE_PARAMS = {
    **XGBOOST_PARAMS,
    "objective":           "reg:quantileerror",
    "eval_metric":         "quantile",
}


class XGBoostDemandForecaster:

    def __init__(self, quantile: float = 0.5):
        self.quantile = quantile
        params = QUANTILE_PARAMS.copy()
        params["quantile_alpha"] = quantile
        self.model = xgb.XGBRegressor(**params)
        self.feature_names = XGBOOST_FEATURES
        self.is_fitted = False

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series,
            X_val: pd.DataFrame, y_val: pd.Series) -> None:
        self.model.fit(
            X_train[self.feature_names], y_train,
            eval_set=[(X_val[self.feature_names], y_val)],
            verbose=False,
        )
        self.is_fitted = True

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        return self.model.predict(X[self.feature_names])

    def cross_validate(self, X: pd.DataFrame, y: pd.Series,
                        n_splits: int = 5) -> dict:
        """TimeSeriesSplit CV. Returns mean/std of MAE and RMSE."""
        tscv = TimeSeriesSplit(n_splits=n_splits)
        mae_scores, rmse_scores = [], []

        for train_idx, val_idx in tscv.split(X):
            X_tr, X_vl = X.iloc[train_idx], X.iloc[val_idx]
            y_tr, y_vl = y.iloc[train_idx], y.iloc[val_idx]

            model = xgb.XGBRegressor(**{**QUANTILE_PARAMS, "quantile_alpha": 0.5})
            model.fit(X_tr[self.feature_names], y_tr,
                      eval_set=[(X_vl[self.feature_names], y_vl)],
                      verbose=False)
            preds = model.predict(X_vl[self.feature_names])
            mae_scores.append(mean_absolute_error(y_vl, preds))
            rmse_scores.append(np.sqrt(mean_squared_error(y_vl, preds)))

        return {
            "cv_mae_mean":  np.mean(mae_scores),
            "cv_mae_std":   np.std(mae_scores),
            "cv_rmse_mean": np.mean(rmse_scores),
            "cv_rmse_std":  np.std(rmse_scores),
        }


def build_quantile_forecasters(X_train, y_train,
                                X_val, y_val) -> dict:
    """
    Train P50, P75, P90 forecasters.
    Returns dict: {"p50": model, "p75": model, "p90": model}
    """
    forecasters = {}
    for q, label in [(0.50, "p50"), (0.75, "p75"), (0.90, "p90")]:
        f = XGBoostDemandForecaster(quantile=q)
        f.fit(X_train, y_train, X_val, y_val)
        forecasters[label] = f
    return forecasters
```

### 6.2 `src/forecasting/prophet_model.py`

```python
"""
prophet_model.py
Facebook Prophet as time-series layer. Handles:
- Trend + yearly/monthly seasonality
- Indian festive season holidays (Diwali, Holi)
- External regressors: Max_Temp_C, Festive_Multiplier
Used as fallback / ensemble layer per region.
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error


INDIAN_HOLIDAYS = {
    "holiday": ["Diwali", "Holi", "Eid", "Christmas", "Summer Peak"],
    "ds": ["2018-11-07", "2018-03-02", "2018-06-15", "2018-12-25", "2018-05-15"],
    "lower_window": [0, 0, 0, 0, 0],
    "upper_window": [3, 1, 1, 1, 14],
}


def make_holiday_df() -> pd.DataFrame:
    """Generate holiday DataFrame for Prophet across 2018–2023."""
    rows = []
    base_holidays = [
        {"holiday": "Diwali",      "month": 10, "day": 20, "lower": 0,  "upper": 4},
        {"holiday": "Holi",        "month": 3,  "day": 10, "lower": 0,  "upper": 1},
        {"holiday": "Summer_Peak", "month": 5,  "day": 1,  "lower": 0,  "upper": 30},
    ]
    for year in range(2018, 2024):
        for h in base_holidays:
            rows.append({
                "holiday":       h["holiday"],
                "ds":            pd.Timestamp(year=year, month=h["month"], day=h["day"]),
                "lower_window":  h["lower"],
                "upper_window":  h["upper"],
            })
    return pd.DataFrame(rows)


class ProphetRegionalForecaster:

    def __init__(self, region: str):
        self.region = region
        self.model = Prophet(
            seasonality_mode="multiplicative",
            yearly_seasonality=True,
            weekly_seasonality=False,
            holidays=make_holiday_df(),
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0,
        )
        self.model.add_regressor("Max_Temp_C")
        self.model.add_regressor("Festive_Multiplier")

    def prepare_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prophet expects columns: ds, y, + regressors."""
        prophet_df = df.rename(columns={
            "YearMonth": "ds",
            "Net_Units_Sold": "y",
        })[["ds", "y", "Max_Temp_C", "Festive_Multiplier"]].copy()
        prophet_df["ds"] = prophet_df["ds"].dt.to_timestamp()
        return prophet_df

    def fit(self, df: pd.DataFrame) -> None:
        self.model.fit(self.prepare_df(df))

    def predict(self, future_df: pd.DataFrame) -> pd.DataFrame:
        forecast = self.model.predict(future_df)
        return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

    def evaluate(self, df: pd.DataFrame) -> dict:
        prep = self.prepare_df(df)
        forecast = self.model.predict(prep)
        y_true = prep["y"].values
        y_pred = forecast["yhat"].values
        return {
            "mae":  mean_absolute_error(y_true, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
            "mape": np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1))) * 100,
        }
```

### 6.3 `src/forecasting/quantile_forecaster.py`

```python
"""
quantile_forecaster.py
Orchestrates P50/P75/P90 outputs. Computes:
- Safety stock = P90 - P50
- Risk flag if gap > 30% of P50
"""

import pandas as pd
import numpy as np
from src.forecasting.xgboost_model import build_quantile_forecasters


def generate_quantile_forecasts(X_train, y_train, X_val, y_val,
                                  X_test) -> pd.DataFrame:
    """
    Returns DataFrame with columns:
    [index, P50, P75, P90, safety_stock, risk_flag]
    """
    forecasters = build_quantile_forecasters(X_train, y_train, X_val, y_val)

    results = pd.DataFrame(index=X_test.index)
    results["P50"] = forecasters["p50"].predict(X_test)
    results["P75"] = forecasters["p75"].predict(X_test)
    results["P90"] = forecasters["p90"].predict(X_test)

    # Ensure monotonicity: P50 <= P75 <= P90
    results["P75"] = results[["P50", "P75"]].max(axis=1)
    results["P90"] = results[["P75", "P90"]].max(axis=1)

    results["safety_stock"] = results["P90"] - results["P50"]
    results["risk_flag"]    = (results["safety_stock"] / results["P50"].clip(lower=1)) > 0.30

    return results
```

---

## 7. Allocation Optimizer

### 7.1 `src/allocation/safety_stock.py`

```python
"""
safety_stock.py
Safety stock calculation from quantile forecasts.
Safety Stock = P90 - P50 per warehouse-region pair.
"""

import pandas as pd
import numpy as np


def compute_safety_stock(forecast_df: pd.DataFrame) -> pd.DataFrame:
    """
    Input: DataFrame with P50, P90 per Region × YearMonth
    Output: same with safety_stock_units added
    """
    df = forecast_df.copy()
    df["safety_stock_units"] = (df["P90"] - df["P50"]).clip(lower=0)
    return df


def compute_reorder_point(df: pd.DataFrame,
                           lead_time_days: int = 7,
                           days_per_month: int = 30) -> pd.DataFrame:
    """
    Reorder point = daily_demand * lead_time + safety_stock
    daily_demand estimated from P50 / 30
    """
    df = df.copy()
    df["daily_demand_p50"] = df["P50"] / days_per_month
    df["reorder_point"] = (
        df["daily_demand_p50"] * lead_time_days + df["safety_stock_units"]
    ).round()
    return df
```

### 7.2 `src/allocation/lp_optimizer.py`

```python
"""
lp_optimizer.py
PuLP Linear Program for inventory allocation.

Decision variables: x[w, r] = units allocated from warehouse w to region r

Objective: minimize
  sum_{w,r} cost_per_unit[w,r] * x[w,r]            (logistics cost)
  + sum_w carrying_cost_rate * avg_inventory[w]     (carrying cost)
  + sum_r stockout_penalty * max(0, demand[r] - supplied[r])  (penalty)

Constraints:
  1. Warehouse capacity: sum_r x[w,r] <= capacity[w]
  2. Demand satisfaction: sum_w x[w,r] >= P50_demand[r]
  3. Safety stock: inventory[w] - sum_r x[w,r] >= safety_stock[w]
  4. Inventory availability: sum_r x[w,r] <= current_inventory[w]
  5. SLA compliance: sum_w x[w,r] / demand[r] >= sla_target (0.95)
  6. Non-negativity: x[w,r] >= 0
"""

import pandas as pd
import numpy as np
from pulp import (LpProblem, LpMinimize, LpVariable, lpSum,
                  LpStatus, value, PULP_CBC_CMD)


CARRYING_COST_RATE   = 0.02    # 2% of unit value per month
STOCKOUT_PENALTY     = 5000    # INR per unfulfilled unit
SLA_TARGET           = 0.95    # 95% fulfillment rate


def run_allocation_optimizer(
    warehouses: pd.DataFrame,    # cols: warehouse_id, capacity, current_inventory, safety_stock
    regions: pd.DataFrame,       # cols: region, p50_demand, p90_demand
    cost_matrix: pd.DataFrame,   # cols: warehouse_id, region, cost_per_unit
) -> pd.DataFrame:
    """
    Solve LP. Returns allocation_plan DataFrame.
    Columns: [warehouse_id, region, allocated_units, cost]
    """
    prob = LpProblem("HVAC_Inventory_Allocation", LpMinimize)

    W = warehouses["warehouse_id"].tolist()
    R = regions["region"].tolist()

    # Decision variables
    x = {
        (w, r): LpVariable(f"x_{w}_{r}", lowBound=0, cat="Continuous")
        for w in W for r in R
    }

    # Cost lookup helpers
    cost_lookup    = cost_matrix.set_index(["warehouse_id", "region"])["cost_per_unit"].to_dict()
    cap_lookup     = warehouses.set_index("warehouse_id")["capacity"].to_dict()
    inv_lookup     = warehouses.set_index("warehouse_id")["current_inventory"].to_dict()
    ss_lookup      = warehouses.set_index("warehouse_id")["safety_stock"].to_dict()
    demand_lookup  = regions.set_index("region")["p50_demand"].to_dict()

    # Objective
    logistics_cost = lpSum(
        cost_lookup.get((w, r), 999999) * x[(w, r)]
        for w in W for r in R
    )
    carrying_cost = lpSum(
        CARRYING_COST_RATE * (inv_lookup[w] - lpSum(x[(w, r)] for r in R))
        for w in W
    )
    prob += logistics_cost + carrying_cost

    # Constraint 1: Warehouse capacity
    for w in W:
        prob += lpSum(x[(w, r)] for r in R) <= cap_lookup[w], f"cap_{w}"

    # Constraint 2: Demand satisfaction
    for r in R:
        prob += lpSum(x[(w, r)] for w in W) >= demand_lookup[r], f"demand_{r}"

    # Constraint 3: Safety stock preserved
    for w in W:
        prob += (inv_lookup[w] - lpSum(x[(w, r)] for r in R)) >= ss_lookup[w], f"ss_{w}"

    # Constraint 4: Inventory availability
    for w in W:
        prob += lpSum(x[(w, r)] for r in R) <= inv_lookup[w], f"avail_{w}"

    # Constraint 5: SLA compliance per region
    for r in R:
        prob += (
            lpSum(x[(w, r)] for w in W) >= SLA_TARGET * demand_lookup[r]
        ), f"sla_{r}"

    # Solve
    prob.solve(PULP_CBC_CMD(msg=0))

    status = LpStatus[prob.status]
    if status != "Optimal":
        raise RuntimeError(f"LP did not reach optimal solution. Status: {status}")

    # Extract results
    rows = []
    for w in W:
        for r in R:
            units = value(x[(w, r)]) or 0.0
            if units > 0.01:
                rows.append({
                    "warehouse_id":    w,
                    "region":          r,
                    "allocated_units": round(units),
                    "cost_per_unit":   cost_lookup.get((w, r), 0),
                    "total_cost_INR":  round(units * cost_lookup.get((w, r), 0)),
                })

    return pd.DataFrame(rows)
```

---

## 8. Evaluation Metrics & Acceptance Criteria

### 8.1 `src/evaluation/metrics.py`

```python
"""
metrics.py
All evaluation metrics for forecasting and allocation layers.
Acceptance threshold: >80% accuracy equivalent per metric.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (mean_absolute_error, mean_squared_error,
                              r2_score, mean_absolute_percentage_error)


# ─── Acceptance Thresholds ─────────────────────────────────────────────
THRESHOLDS = {
    "r2_min":          0.80,     # R² ≥ 0.80
    "mape_max":        20.0,     # MAPE ≤ 20% (=80% accuracy)
    "rmse_pct_max":    20.0,     # RMSE as % of mean demand ≤ 20%
    "mae_pct_max":     15.0,     # MAE as % of mean demand ≤ 15%
    "pinball_max":     150.0,    # Pinball loss ≤ 150 units at P90
    "sla_min":         0.95,     # Allocation SLA ≥ 95%
}


def compute_regression_metrics(y_true: np.ndarray,
                                y_pred: np.ndarray,
                                label: str = "") -> dict:
    """Full regression metric suite."""
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    mean_demand = np.mean(y_true)

    mae   = mean_absolute_error(y_true, y_pred)
    mse   = mean_squared_error(y_true, y_pred)
    rmse  = np.sqrt(mse)
    mape  = mean_absolute_percentage_error(y_true, y_pred) * 100
    r2    = r2_score(y_true, y_pred)
    rmse_pct = (rmse / mean_demand) * 100 if mean_demand > 0 else np.inf
    mae_pct  = (mae  / mean_demand) * 100 if mean_demand > 0 else np.inf

    return {
        "label":    label,
        "MAE":      round(mae, 3),
        "MSE":      round(mse, 3),
        "RMSE":     round(rmse, 3),
        "MAPE_%":   round(mape, 3),
        "R2":       round(r2, 4),
        "RMSE_%":   round(rmse_pct, 3),
        "MAE_%":    round(mae_pct, 3),
    }


def pinball_loss(y_true: np.ndarray, y_pred: np.ndarray,
                  quantile: float) -> float:
    """
    Pinball (quantile) loss. Lower is better.
    Used to evaluate P75 and P90 quantile forecasts.
    """
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    err = y_true - y_pred
    loss = np.where(err >= 0, quantile * err, (quantile - 1) * err)
    return float(np.mean(loss))


def check_acceptance(metrics: dict) -> dict:
    """
    Returns pass/fail per metric against THRESHOLDS.
    Raises AssertionError if any metric fails (use in CI).
    """
    results = {}
    results["r2_pass"]       = metrics.get("R2", 0)       >= THRESHOLDS["r2_min"]
    results["mape_pass"]     = metrics.get("MAPE_%", 999) <= THRESHOLDS["mape_max"]
    results["rmse_pct_pass"] = metrics.get("RMSE_%", 999) <= THRESHOLDS["rmse_pct_max"]
    results["mae_pct_pass"]  = metrics.get("MAE_%", 999)  <= THRESHOLDS["mae_pct_max"]
    results["all_pass"]      = all(results.values())
    return results


def evaluate_allocation(allocation_df: pd.DataFrame,
                         demand_df: pd.DataFrame) -> dict:
    """
    Compute allocation-layer metrics.
    allocation_df: [region, allocated_units]
    demand_df: [region, p50_demand]
    """
    merged = demand_df.merge(
        allocation_df.groupby("region")["allocated_units"].sum().reset_index(),
        on="region", how="left"
    ).fillna(0)

    merged["fulfillment_rate"] = merged["allocated_units"] / merged["p50_demand"].clip(lower=1)
    overall_sla = merged["allocated_units"].sum() / merged["p50_demand"].sum()

    return {
        "overall_sla":        round(overall_sla, 4),
        "regions_below_sla":  (merged["fulfillment_rate"] < 0.95).sum(),
        "total_allocated":    int(merged["allocated_units"].sum()),
        "total_demand":       int(merged["p50_demand"].sum()),
    }
```

### 8.2 Metric Interpretation Guide

| Metric | Target | What it measures |
|--------|--------|-----------------|
| **R²** | ≥ 0.80 | Variance explained by the model; 0.80 = model explains 80% of demand variance |
| **MAPE** | ≤ 20% | Mean Absolute Percentage Error; ≤ 20% implies ≥ 80% forecast accuracy |
| **RMSE %** | ≤ 20% of mean | RMSE normalised by mean demand; scale-invariant |
| **MAE %** | ≤ 15% of mean | Same as RMSE % but less sensitive to outliers |
| **Pinball Loss (P90)** | ≤ 150 units | Quality of safety stock buffer; lower = P90 better calibrated |
| **Allocation SLA** | ≥ 95% | % of P50 demand satisfied by LP allocation |

---

## 9. Testing Strategy (pytest)

### 9.1 `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests (fast, no I/O)
    integration: Integration tests (pipeline-level)
    regression: Accuracy gate tests (must pass before merge)
    slow: Tests taking >10 seconds
```

### 9.2 `tests/conftest.py`

```python
"""
conftest.py — Shared fixtures for all test modules.
"""

import pytest
import pandas as pd
import numpy as np


@pytest.fixture(scope="session")
def sample_demand_df():
    """Minimal 60-row region×month demand DataFrame."""
    np.random.seed(42)
    regions = ["North", "South", "East", "West", "Central"]
    months = pd.period_range("2020-01", "2020-12", freq="M")
    rows = []
    for r in regions:
        for m in months:
            rows.append({
                "Region": r, "YearMonth": m,
                "Net_Units_Sold": int(np.random.normal(700, 150)),
                "Max_Temp_C": np.random.uniform(20, 45),
                "Cooling_Degree_Days": np.random.uniform(0, 500),
                "Google_Trends_AC_Index": np.random.uniform(5, 100),
                "Composite_Demand_Index": np.random.uniform(0.1, 1.0),
                "Festive_Multiplier": np.random.choice([1.0, 1.2, 1.5]),
            })
    return pd.DataFrame(rows)


@pytest.fixture(scope="session")
def sample_warehouse_df():
    """50 warehouses with capacity and inventory."""
    np.random.seed(0)
    return pd.DataFrame({
        "warehouse_id":     [f"WH{i:03d}" for i in range(1, 6)],
        "capacity":         [5000, 4000, 6000, 3500, 4500],
        "current_inventory":[3000, 2500, 4000, 2000, 3000],
        "safety_stock":     [300,  250,  400,  200,  300],
    })


@pytest.fixture(scope="session")
def sample_region_df():
    return pd.DataFrame({
        "region":     ["North", "South", "East", "West", "Central"],
        "p50_demand": [1200, 800, 600, 700, 500],
        "p90_demand": [1500, 1000, 750, 900, 650],
    })


@pytest.fixture(scope="session")
def sample_cost_matrix(sample_warehouse_df, sample_region_df):
    np.random.seed(1)
    rows = []
    for wh in sample_warehouse_df["warehouse_id"]:
        for r in sample_region_df["region"]:
            rows.append({
                "warehouse_id": wh,
                "region": r,
                "cost_per_unit": round(np.random.uniform(400, 800), 2),
            })
    return pd.DataFrame(rows)
```

### 9.3 `tests/unit/test_imputation.py`

```python
"""Unit tests for imputation module."""

import pytest
import pandas as pd
import numpy as np
from src.feature_store.imputation import median_impute_by_group, validate_no_nulls


@pytest.mark.unit
def test_median_impute_fills_all_nulls():
    df = pd.DataFrame({
        "Region": ["North", "North", "South", "South"],
        "Max_Temp_C": [35.0, np.nan, 28.0, np.nan],
        "Units": [500, np.nan, 400, 300],
    })
    result = median_impute_by_group(df, group_col="Region",
                                    numeric_cols=["Max_Temp_C", "Units"])
    assert result["Max_Temp_C"].isnull().sum() == 0
    assert result["Units"].isnull().sum() == 0


@pytest.mark.unit
def test_median_impute_uses_group_median():
    df = pd.DataFrame({
        "Region": ["North"] * 4,
        "Max_Temp_C": [30.0, 40.0, np.nan, 50.0],
    })
    result = median_impute_by_group(df, group_col="Region",
                                    numeric_cols=["Max_Temp_C"])
    expected = np.median([30.0, 40.0, 50.0])    # group median before fill
    assert abs(result["Max_Temp_C"].iloc[2] - expected) < 1.0


@pytest.mark.unit
def test_validate_no_nulls_raises_on_remaining_nulls():
    df = pd.DataFrame({"A": [1.0, np.nan]})
    with pytest.raises(ValueError, match="Nulls remain"):
        validate_no_nulls(df, cols=["A"])


@pytest.mark.unit
def test_validate_no_nulls_passes_clean_df():
    df = pd.DataFrame({"A": [1.0, 2.0]})
    assert validate_no_nulls(df, cols=["A"]) is True
```

### 9.4 `tests/unit/test_feature_engineering.py`

```python
"""Unit tests for feature engineering."""

import pytest
import pandas as pd
import numpy as np
from src.feature_store.feature_engineering import (
    add_lag_features, add_rolling_features, add_cyclic_time_features
)


@pytest.fixture
def simple_ts():
    months = pd.period_range("2020-01", "2020-12", freq="M")
    return pd.DataFrame({
        "Region": ["North"] * 12,
        "YearMonth": months,
        "Net_Units_Sold": list(range(100, 1300, 100)),
    })


@pytest.mark.unit
def test_lag_features_length_preserved(simple_ts):
    result = add_lag_features(simple_ts, "Net_Units_Sold", "Region")
    assert len(result) == len(simple_ts)


@pytest.mark.unit
def test_lag_1_is_previous_month(simple_ts):
    result = add_lag_features(simple_ts, "Net_Units_Sold", "Region")
    # Row index 1: lag_1 should equal row 0 value
    assert result["Net_Units_Sold_lag_1"].iloc[1] == simple_ts["Net_Units_Sold"].iloc[0]


@pytest.mark.unit
def test_lag_1_first_row_is_nan(simple_ts):
    result = add_lag_features(simple_ts, "Net_Units_Sold", "Region")
    assert pd.isna(result["Net_Units_Sold_lag_1"].iloc[0])


@pytest.mark.unit
def test_cyclic_features_range(simple_ts):
    result = add_cyclic_time_features(simple_ts, "YearMonth")
    assert result["month_sin"].between(-1, 1).all()
    assert result["month_cos"].between(-1, 1).all()


@pytest.mark.unit
def test_rolling_mean_3_correct_value(simple_ts):
    result = add_rolling_features(simple_ts, "Net_Units_Sold", "Region")
    # Row 3 rolling mean should be mean of rows 0,1,2 (shifted by 1)
    expected = np.mean([100, 200, 300])
    assert abs(result["Net_Units_Sold_roll_mean_3"].iloc[3] - expected) < 1e-5
```

### 9.5 `tests/unit/test_metrics.py`

```python
"""Unit tests for evaluation metrics."""

import pytest
import numpy as np
from src.evaluation.metrics import (
    compute_regression_metrics, pinball_loss, check_acceptance
)


@pytest.mark.unit
def test_perfect_forecast_r2_is_1():
    y = np.array([100, 200, 300, 400, 500], dtype=float)
    metrics = compute_regression_metrics(y, y)
    assert metrics["R2"] == pytest.approx(1.0, abs=1e-5)
    assert metrics["MAE"] == pytest.approx(0.0, abs=1e-5)


@pytest.mark.unit
def test_mape_correct():
    y_true = np.array([100.0, 200.0])
    y_pred = np.array([110.0, 180.0])
    metrics = compute_regression_metrics(y_true, y_pred)
    expected_mape = np.mean([10.0/100, 20.0/200]) * 100
    assert abs(metrics["MAPE_%"] - expected_mape) < 0.01


@pytest.mark.unit
def test_pinball_loss_at_median_is_mae_half():
    y_true = np.array([100.0, 200.0, 300.0])
    y_pred = np.array([120.0, 180.0, 310.0])
    pb = pinball_loss(y_true, y_pred, quantile=0.5)
    # At q=0.5, pinball = 0.5 * MAE
    from sklearn.metrics import mean_absolute_error
    expected = 0.5 * mean_absolute_error(y_true, y_pred)
    assert abs(pb - expected) < 1e-5


@pytest.mark.unit
def test_check_acceptance_fails_low_r2():
    metrics = {"R2": 0.65, "MAPE_%": 15.0, "RMSE_%": 18.0, "MAE_%": 12.0}
    result = check_acceptance(metrics)
    assert result["r2_pass"] is False
    assert result["all_pass"] is False


@pytest.mark.unit
def test_check_acceptance_passes_good_metrics():
    metrics = {"R2": 0.85, "MAPE_%": 12.0, "RMSE_%": 14.0, "MAE_%": 10.0}
    result = check_acceptance(metrics)
    assert result["all_pass"] is True
```

### 9.6 `tests/unit/test_lp_optimizer.py`

```python
"""Unit tests for PuLP allocation optimizer."""

import pytest
import pandas as pd
import numpy as np
from src.allocation.lp_optimizer import run_allocation_optimizer


@pytest.mark.unit
def test_optimizer_returns_dataframe(sample_warehouse_df, sample_region_df,
                                      sample_cost_matrix):
    result = run_allocation_optimizer(
        sample_warehouse_df, sample_region_df, sample_cost_matrix
    )
    assert isinstance(result, pd.DataFrame)
    assert "allocated_units" in result.columns
    assert "warehouse_id" in result.columns


@pytest.mark.unit
def test_allocation_satisfies_demand(sample_warehouse_df, sample_region_df,
                                      sample_cost_matrix):
    result = run_allocation_optimizer(
        sample_warehouse_df, sample_region_df, sample_cost_matrix
    )
    region_totals = result.groupby("region")["allocated_units"].sum()
    for _, row in sample_region_df.iterrows():
        r = row["region"]
        allocated = region_totals.get(r, 0)
        assert allocated >= row["p50_demand"] * 0.95, (
            f"Region {r}: allocated {allocated} < 95% of demand {row['p50_demand']}"
        )


@pytest.mark.unit
def test_allocation_respects_warehouse_capacity(sample_warehouse_df,
                                                  sample_region_df,
                                                  sample_cost_matrix):
    result = run_allocation_optimizer(
        sample_warehouse_df, sample_region_df, sample_cost_matrix
    )
    wh_totals = result.groupby("warehouse_id")["allocated_units"].sum()
    cap = sample_warehouse_df.set_index("warehouse_id")["capacity"].to_dict()
    for wh, total in wh_totals.items():
        assert total <= cap[wh] + 1, (
            f"Warehouse {wh}: allocated {total} > capacity {cap[wh]}"
        )


@pytest.mark.unit
def test_no_negative_allocations(sample_warehouse_df, sample_region_df,
                                   sample_cost_matrix):
    result = run_allocation_optimizer(
        sample_warehouse_df, sample_region_df, sample_cost_matrix
    )
    assert (result["allocated_units"] >= 0).all()
```

### 9.7 `tests/unit/test_safety_stock.py`

```python
"""Unit tests for safety stock calculations."""

import pytest
import pandas as pd
import numpy as np
from src.allocation.safety_stock import compute_safety_stock, compute_reorder_point


@pytest.fixture
def forecast_df():
    return pd.DataFrame({
        "Region": ["North", "South"],
        "P50": [1000.0, 600.0],
        "P75": [1150.0, 720.0],
        "P90": [1300.0, 800.0],
    })


@pytest.mark.unit
def test_safety_stock_equals_p90_minus_p50(forecast_df):
    result = compute_safety_stock(forecast_df)
    assert result["safety_stock_units"].iloc[0] == pytest.approx(300.0)
    assert result["safety_stock_units"].iloc[1] == pytest.approx(200.0)


@pytest.mark.unit
def test_safety_stock_non_negative(forecast_df):
    df = forecast_df.copy()
    df["P90"] = df["P50"] - 10   # P90 < P50 (edge case)
    result = compute_safety_stock(df)
    assert (result["safety_stock_units"] >= 0).all()


@pytest.mark.unit
def test_reorder_point_exceeds_safety_stock(forecast_df):
    ss_df = compute_safety_stock(forecast_df)
    rop_df = compute_reorder_point(ss_df, lead_time_days=7)
    assert (rop_df["reorder_point"] >= rop_df["safety_stock_units"]).all()
```

### 9.8 `tests/unit/test_xgboost_model.py`

```python
"""Unit tests for XGBoost forecaster."""

import pytest
import pandas as pd
import numpy as np
from src.forecasting.xgboost_model import XGBoostDemandForecaster
from src.feature_store.feature_engineering import XGBOOST_FEATURES


@pytest.fixture
def mock_training_data():
    np.random.seed(42)
    n = 200
    X = pd.DataFrame(np.random.randn(n, len(XGBOOST_FEATURES)),
                      columns=XGBOOST_FEATURES)
    y = pd.Series(np.random.randint(300, 1200, size=n), name="Net_Units_Sold")
    return X, y


@pytest.mark.unit
def test_forecaster_fits_without_error(mock_training_data):
    X, y = mock_training_data
    model = XGBoostDemandForecaster(quantile=0.5)
    model.fit(X[:150], y[:150], X[150:], y[150:])
    assert model.is_fitted is True


@pytest.mark.unit
def test_forecaster_predict_shape(mock_training_data):
    X, y = mock_training_data
    model = XGBoostDemandForecaster(quantile=0.5)
    model.fit(X[:150], y[:150], X[150:], y[150:])
    preds = model.predict(X[150:])
    assert len(preds) == 50


@pytest.mark.unit
def test_p90_exceeds_p50(mock_training_data):
    X, y = mock_training_data
    p50 = XGBoostDemandForecaster(quantile=0.50)
    p90 = XGBoostDemandForecaster(quantile=0.90)
    p50.fit(X[:150], y[:150], X[150:], y[150:])
    p90.fit(X[:150], y[:150], X[150:], y[150:])
    preds_50 = p50.predict(X[150:])
    preds_90 = p90.predict(X[150:])
    assert np.mean(preds_90) > np.mean(preds_50)
```

### 9.9 `tests/integration/test_full_pipeline.py`

```python
"""
Integration test: full pipeline from raw data to forecasts.
Requires actual dataset files in data/raw/.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from src.feature_store.merge_pipeline import build_master_table
from src.feature_store.feature_engineering import build_model_features, XGBOOST_FEATURES, TARGET_COL
from src.feature_store.imputation import median_impute_by_group
from src.forecasting.xgboost_model import XGBoostDemandForecaster
from src.evaluation.metrics import compute_regression_metrics, check_acceptance


DATA_DIR    = "data/raw"
OUTPUT_PATH = "data/processed/master_feature_table.parquet"


@pytest.mark.integration
@pytest.mark.skipif(not Path(DATA_DIR).exists(),
                    reason="Raw data not available")
def test_feature_store_builds_without_error():
    master = build_master_table(DATA_DIR, OUTPUT_PATH)
    assert len(master) > 0
    assert "Net_Units_Sold" in master.columns
    assert "Max_Temp_C" in master.columns


@pytest.mark.integration
@pytest.mark.skipif(not Path(DATA_DIR).exists(),
                    reason="Raw data not available")
def test_pipeline_no_nulls_after_imputation():
    master = build_master_table(DATA_DIR, OUTPUT_PATH)
    master = build_model_features(master)
    numeric_cols = master.select_dtypes(include=[np.number]).columns.tolist()
    master = median_impute_by_group(master, numeric_cols=numeric_cols)
    remaining_nulls = master[XGBOOST_FEATURES].isnull().sum().sum()
    assert remaining_nulls == 0


@pytest.mark.integration
@pytest.mark.skipif(not Path(DATA_DIR).exists(),
                    reason="Raw data not available")
def test_xgboost_trains_on_real_data():
    master = build_master_table(DATA_DIR, OUTPUT_PATH)
    master = build_model_features(master)
    numeric_cols = master.select_dtypes(include=[np.number]).columns.tolist()
    master = median_impute_by_group(master, numeric_cols=numeric_cols)

    master = master.dropna(subset=XGBOOST_FEATURES + [TARGET_COL])
    split = int(0.8 * len(master))
    X_train = master.iloc[:split][XGBOOST_FEATURES]
    y_train = master.iloc[:split][TARGET_COL]
    X_val   = master.iloc[split:][XGBOOST_FEATURES]
    y_val   = master.iloc[split:][TARGET_COL]

    model = XGBoostDemandForecaster(quantile=0.5)
    model.fit(X_train, y_train, X_val, y_val)
    preds = model.predict(X_val)
    assert len(preds) == len(y_val)
```

### 9.10 `tests/regression/test_model_accuracy.py`

```python
"""
Regression accuracy gate tests.
These MUST pass before any model is promoted to production.
Thresholds: R² >= 0.80, MAPE <= 20%, RMSE% <= 20%
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from src.feature_store.merge_pipeline import build_master_table
from src.feature_store.feature_engineering import build_model_features, XGBOOST_FEATURES, TARGET_COL
from src.feature_store.imputation import median_impute_by_group
from src.forecasting.xgboost_model import XGBoostDemandForecaster
from src.evaluation.metrics import compute_regression_metrics, check_acceptance, pinball_loss


DATA_DIR    = "data/raw"
OUTPUT_PATH = "data/processed/master_feature_table.parquet"


def load_and_prepare():
    master = build_master_table(DATA_DIR, OUTPUT_PATH)
    master = build_model_features(master)
    numeric_cols = master.select_dtypes(include=[np.number]).columns.tolist()
    master = median_impute_by_group(master, numeric_cols=numeric_cols)
    master = master.dropna(subset=XGBOOST_FEATURES + [TARGET_COL])

    # Chronological split: 80% train, 10% val, 10% test
    n = len(master)
    train_end = int(0.8 * n)
    val_end   = int(0.9 * n)

    return (
        master.iloc[:train_end],
        master.iloc[train_end:val_end],
        master.iloc[val_end:],
    )


@pytest.mark.regression
@pytest.mark.skipif(not Path(DATA_DIR).exists(),
                    reason="Raw data not available")
class TestModelAccuracyGates:

    def test_r2_exceeds_80_percent(self):
        train, val, test = load_and_prepare()
        model = XGBoostDemandForecaster(quantile=0.5)
        model.fit(train[XGBOOST_FEATURES], train[TARGET_COL],
                  val[XGBOOST_FEATURES],   val[TARGET_COL])
        preds = model.predict(test[XGBOOST_FEATURES])
        metrics = compute_regression_metrics(test[TARGET_COL].values, preds,
                                              label="XGBoost P50")
        assert metrics["R2"] >= 0.80, (
            f"R² = {metrics['R2']} is below 0.80 threshold. "
            f"Full metrics: {metrics}"
        )

    def test_mape_below_20_percent(self):
        train, val, test = load_and_prepare()
        model = XGBoostDemandForecaster(quantile=0.5)
        model.fit(train[XGBOOST_FEATURES], train[TARGET_COL],
                  val[XGBOOST_FEATURES],   val[TARGET_COL])
        preds = model.predict(test[XGBOOST_FEATURES])
        metrics = compute_regression_metrics(test[TARGET_COL].values, preds)
        assert metrics["MAPE_%"] <= 20.0, (
            f"MAPE = {metrics['MAPE_%']}% exceeds 20% threshold"
        )

    def test_rmse_pct_below_20_percent(self):
        train, val, test = load_and_prepare()
        model = XGBoostDemandForecaster(quantile=0.5)
        model.fit(train[XGBOOST_FEATURES], train[TARGET_COL],
                  val[XGBOOST_FEATURES],   val[TARGET_COL])
        preds = model.predict(test[XGBOOST_FEATURES])
        metrics = compute_regression_metrics(test[TARGET_COL].values, preds)
        assert metrics["RMSE_%"] <= 20.0, (
            f"RMSE% = {metrics['RMSE_%']}% exceeds 20% threshold"
        )

    def test_p90_pinball_loss_acceptable(self):
        train, val, test = load_and_prepare()
        model_p90 = XGBoostDemandForecaster(quantile=0.90)
        model_p90.fit(train[XGBOOST_FEATURES], train[TARGET_COL],
                      val[XGBOOST_FEATURES],   val[TARGET_COL])
        preds_p90 = model_p90.predict(test[XGBOOST_FEATURES])
        pb = pinball_loss(test[TARGET_COL].values, preds_p90, quantile=0.90)
        assert pb <= 150.0, f"P90 Pinball loss = {pb:.2f} exceeds threshold of 150"

    def test_all_metrics_pass_acceptance(self):
        train, val, test = load_and_prepare()
        model = XGBoostDemandForecaster(quantile=0.5)
        model.fit(train[XGBOOST_FEATURES], train[TARGET_COL],
                  val[XGBOOST_FEATURES],   val[TARGET_COL])
        preds = model.predict(test[XGBOOST_FEATURES])
        metrics = compute_regression_metrics(test[TARGET_COL].values, preds)
        gates = check_acceptance(metrics)
        assert gates["all_pass"], (
            f"One or more accuracy gates failed: {gates}\n"
            f"Full metrics: {metrics}"
        )
```

---

## 10. File-by-File Specification

### `configs/model_config.yaml`

```yaml
xgboost:
  n_estimators: 500
  max_depth: 5
  learning_rate: 0.05
  subsample: 0.8
  colsample_bytree: 0.8
  min_child_weight: 5
  reg_alpha: 0.1
  reg_lambda: 1.0
  early_stopping_rounds: 30
  quantiles: [0.50, 0.75, 0.90]
  cv_folds: 5

prophet:
  seasonality_mode: multiplicative
  changepoint_prior_scale: 0.05
  seasonality_prior_scale: 10.0
  regressors: [Max_Temp_C, Festive_Multiplier]

lasso_cost:
  alpha: 0.1
  max_iter: 1000
  cv_folds: 5
  features: [Units_Shipped, Distance_KM]
```

### `configs/constraint_config.yaml`

```yaml
allocation:
  sla_target: 0.95
  carrying_cost_rate: 0.02
  stockout_penalty_inr: 5000
  lead_time_days: 7
  min_days_of_supply: 7
  max_aged_stock_ratio: 0.30

safety_stock:
  method: quantile_gap          # P90 - P50
  min_buffer_units: 50
```

### `requirements.txt`

```
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
prophet>=1.1.5
pulp>=2.7.0
pyarrow>=12.0.0
pytest>=7.4.0
pytest-cov>=4.1.0
scipy>=1.11.0
pyyaml>=6.0
```

---

## 11. Pipeline Execution Order

```
Step 1 — Data Ingestion
  python -m src.feature_store.merge_pipeline
  → Outputs: data/processed/master_feature_table.parquet

Step 2 — Feature Engineering
  python -m src.feature_store.feature_engineering
  → Outputs: lag, rolling, cyclic features added to master table

Step 3 — Train/Val/Test Split (80/10/10 chronological)
  python -m src.forecasting.model_registry split

Step 4 — Train XGBoost P50/P75/P90 Forecasters
  python -m src.forecasting.xgboost_model train
  → Outputs: models/xgb_p50.json, xgb_p75.json, xgb_p90.json

Step 5 — Train Prophet per Region (5 models)
  python -m src.forecasting.prophet_model train
  → Outputs: models/prophet_{region}.pkl

Step 6 — Generate Quantile Forecasts
  python -m src.forecasting.quantile_forecaster predict
  → Outputs: data/outputs/quantile_forecasts.csv

Step 7 — Compute Safety Stock
  python -m src.allocation.safety_stock compute
  → Outputs: data/outputs/safety_stock.csv

Step 8 — Run LP Allocation Optimizer
  python -m src.allocation.lp_optimizer optimize
  → Outputs: data/outputs/allocation_plan.csv

Step 9 — Evaluate All Models
  python -m src.evaluation.metrics evaluate
  → Outputs: data/outputs/evaluation_report.csv

Step 10 — Run Full Test Suite
  pytest tests/ -v --cov=src --cov-report=html
  → All regression tests must pass before deployment
```

---

## 12. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| DS4/DS5 are synthetically uniform — LP may produce degenerate solutions | High | High | Add real warehouse utilization constraints from DS4; validate allocation against actual DS1 fulfillment rates |
| XGBoost overfits on 72 monthly time points | Medium | High | Limit features to 10, apply TimeSeriesSplit CV, use early stopping, L1/L2 regularization |
| Prophet fails for regions with sparse history | Low | Medium | Fall back to ARIMA or Lasso regression for sparse SKU-region pairs |
| Quantile monotonicity violation (P90 < P50) | Medium | Medium | Enforce post-prediction clipping: P75 = max(P50,P75); P90 = max(P75,P90) |
| LP infeasibility if total inventory < total demand | Medium | High | Add slack variable per region with high penalty; alert before solving |
| Data leakage via future lag values in training | Medium | Critical | Strictly enforce chronological split; shift all lag features by 1 before training |
| Cost_Per_Unit decorrelated from distance (DS5) | High | Medium | Do not include Cost_Per_Unit as a predicted feature in demand model; use raw DS5 values directly in LP |

---

*Document generated for HVAC Inventory Forecasting & Allocation System — v1.0*
