"""
run_pipeline.py
Orchestrates the full HVAC forecasting and allocation pipeline.
Steps 1-9 as defined in the methodology document.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

from src.feature_store.merge_pipeline import build_master_table
from src.feature_store.feature_engineering import build_model_features, XGBOOST_FEATURES, TARGET_COL
from src.feature_store.imputation import median_impute_by_group, validate_no_nulls
from src.forecasting.xgboost_model import XGBoostDemandForecaster, build_quantile_forecasters
from src.forecasting.quantile_forecaster import generate_quantile_forecasts
from src.allocation.safety_stock import compute_safety_stock, compute_reorder_point
from src.allocation.lp_optimizer import run_allocation_optimizer
from src.evaluation.metrics import compute_regression_metrics, check_acceptance, pinball_loss, evaluate_allocation
from src.evaluation.reports import generate_forecast_report


DATA_DIR    = "data/raw"
OUTPUT_DIR  = "data/processed"
RESULTS_DIR = "data/outputs"


def ensure_dirs():
    for d in [OUTPUT_DIR, RESULTS_DIR, "models"]:
        Path(d).mkdir(parents=True, exist_ok=True)


def step1_build_feature_store():
    """Step 1 & 2: Merge datasets + feature engineering."""
    print("=" * 60)
    print("STEP 1: Building master feature table...")
    master = build_master_table(DATA_DIR, f"{OUTPUT_DIR}/master_feature_table.parquet")
    print(f"  Raw merge: {master.shape[0]} rows × {master.shape[1]} cols")

    print("STEP 2: Feature engineering...")
    # Impute BEFORE region encoding (which drops 'Region' column)
    numeric_cols = master.select_dtypes(include=[np.number]).columns.tolist()
    master = median_impute_by_group(master, group_col="Region", numeric_cols=numeric_cols)
    print(f"  Nulls remaining after imputation: {master.select_dtypes(include=[np.number]).isnull().sum().sum()}")

    master = build_model_features(master)
    print(f"  After features: {master.shape[0]} rows × {master.shape[1]} cols")

    return master


def step3_split_data(master):
    """Step 3: Chronological 80/10/10 split."""
    print("=" * 60)
    print("STEP 3: Train/Val/Test split (80/10/10 chronological)...")
    master = master.dropna(subset=XGBOOST_FEATURES + [TARGET_COL])
    n = len(master)
    train_end = int(0.8 * n)
    val_end = int(0.9 * n)

    train = master.iloc[:train_end]
    val = master.iloc[train_end:val_end]
    test = master.iloc[val_end:]

    print(f"  Train: {len(train)} | Val: {len(val)} | Test: {len(test)}")
    return train, val, test


def step4_train_xgboost(train, val, test):
    """Step 4: Train XGBoost P50/P75/P90."""
    print("=" * 60)
    print("STEP 4: Training XGBoost quantile forecasters...")

    forecasters = build_quantile_forecasters(
        train[XGBOOST_FEATURES], train[TARGET_COL],
        val[XGBOOST_FEATURES], val[TARGET_COL]
    )

    for label, model in forecasters.items():
        preds = model.predict(test[XGBOOST_FEATURES])
        print(f"  {label.upper()}: mean prediction = {np.mean(preds):.1f}")

    return forecasters


def step6_generate_forecasts(train, val, test):
    """Step 6: Generate quantile forecasts with safety stock."""
    print("=" * 60)
    print("STEP 6: Generating quantile forecasts...")

    results = generate_quantile_forecasts(
        train[XGBOOST_FEATURES], train[TARGET_COL],
        val[XGBOOST_FEATURES], val[TARGET_COL],
        test[XGBOOST_FEATURES]
    )

    print(f"  P50 mean: {results['P50'].mean():.1f}")
    print(f"  P90 mean: {results['P90'].mean():.1f}")
    print(f"  Safety stock mean: {results['safety_stock'].mean():.1f}")
    print(f"  High-risk rows: {results['risk_flag'].sum()}")

    results.to_csv(f"{RESULTS_DIR}/quantile_forecasts.csv", index=False)
    return results


def step9_evaluate(test, forecasters):
    """Step 9: Evaluate all models."""
    print("=" * 60)
    print("STEP 9: Evaluation...")

    # P50 metrics
    preds_p50 = forecasters["p50"].predict(test[XGBOOST_FEATURES])
    metrics = compute_regression_metrics(test[TARGET_COL].values, preds_p50, label="XGBoost P50")

    print(f"\n  {'Metric':<12} {'Value':>10}")
    print(f"  {'-'*22}")
    for key in ["R2", "MAPE_%", "RMSE_%", "MAE_%", "MAE", "RMSE"]:
        print(f"  {key:<12} {metrics[key]:>10}")

    # Acceptance gates
    gates = check_acceptance(metrics)
    print(f"\n  Acceptance gates: {'[PASS] ALL PASS' if gates['all_pass'] else '[FAIL] SOME FAILED'}")
    for k, v in gates.items():
        if k != "all_pass":
            status = "[PASS]" if v else "[FAIL]"
            print(f"    {status} {k}")

    # Pinball loss for P90
    preds_p90 = forecasters["p90"].predict(test[XGBOOST_FEATURES])
    pb = pinball_loss(test[TARGET_COL].values, preds_p90, quantile=0.90)
    print(f"\n  P90 Pinball Loss: {pb:.2f} (threshold: 150)")

    # Save report
    forecast_dict = {
        "p50": preds_p50,
        "p90": preds_p90,
    }
    if "p75" in forecasters:
        forecast_dict["p75"] = forecasters["p75"].predict(test[XGBOOST_FEATURES])
    generate_forecast_report(test[TARGET_COL].values, forecast_dict,
                             f"{RESULTS_DIR}/evaluation_report.csv")

    return metrics


def main():
    ensure_dirs()

    # Steps 1-2: Feature store
    master = step1_build_feature_store()

    # Step 3: Split
    train, val, test = step3_split_data(master)

    # Step 4: Train XGBoost
    forecasters = step4_train_xgboost(train, val, test)

    # Step 6: Quantile forecasts
    quantile_results = step6_generate_forecasts(train, val, test)

    # Step 9: Evaluate
    metrics = step9_evaluate(test, forecasters)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print(f"  Outputs saved to: {RESULTS_DIR}/")
    print("=" * 60)

    return metrics


if __name__ == "__main__":
    main()
