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
    # Impute BEFORE region encoding (which drops 'Region' column)
    numeric_cols = master.select_dtypes(include=[np.number]).columns.tolist()
    master = median_impute_by_group(master, group_col="Region", numeric_cols=numeric_cols)
    master = build_model_features(master)
    remaining_nulls = master[XGBOOST_FEATURES].isnull().sum().sum()
    assert remaining_nulls == 0


@pytest.mark.integration
@pytest.mark.skipif(not Path(DATA_DIR).exists(),
                    reason="Raw data not available")
def test_xgboost_trains_on_real_data():
    master = build_master_table(DATA_DIR, OUTPUT_PATH)
    # Impute BEFORE region encoding (which drops 'Region' column)
    numeric_cols = master.select_dtypes(include=[np.number]).columns.tolist()
    master = median_impute_by_group(master, group_col="Region", numeric_cols=numeric_cols)
    master = build_model_features(master)

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
