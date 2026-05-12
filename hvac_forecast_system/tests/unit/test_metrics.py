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
    metrics = {"R2": 0.55, "MAPE_%": 15.0, "RMSE_%": 18.0, "MAE_%": 12.0}
    result = check_acceptance(metrics)
    assert result["r2_pass"] is False
    assert result["all_pass"] is False


@pytest.mark.unit
def test_check_acceptance_passes_good_metrics():
    metrics = {"R2": 0.85, "MAPE_%": 12.0, "RMSE_%": 14.0, "MAE_%": 10.0}
    result = check_acceptance(metrics)
    assert result["all_pass"] is True
