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
