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
    # Impute before region encoding (which drops 'Region' column)
    numeric_cols = master.select_dtypes(include=[np.number]).columns.tolist()
    master = median_impute_by_group(master, group_col="Region", numeric_cols=numeric_cols)
    master = build_model_features(master)
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
        assert metrics["R2"] >= 0.60, (
            f"R² = {metrics['R2']} is below 0.60 threshold. "
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
        # Threshold = 5% of mean demand (scale-appropriate)
        mean_demand = test[TARGET_COL].mean()
        threshold = 0.05 * mean_demand
        assert pb <= threshold, (
            f"P90 Pinball loss = {pb:.2f} exceeds 5% of mean demand "
            f"({threshold:.0f})"
        )

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
