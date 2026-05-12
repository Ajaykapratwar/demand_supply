"""
tests/test_metrics.py
Evaluation metric tests.
"""

import pytest
import numpy as np
from evaluation.metrics import (
    compute_regression_metrics, compute_bias, pinball_loss, check_acceptance,
)


@pytest.mark.unit
class TestRegressionMetrics:
    def test_perfect_predictions(self):
        y = np.array([100, 200, 300, 400, 500])
        metrics = compute_regression_metrics(y, y, "perfect")
        assert metrics["R2"] == 1.0
        assert metrics["MAE"] == 0.0
        assert metrics["WAPE"] == 0.0

    def test_imperfect_predictions(self):
        y_true = np.array([100, 200, 300])
        y_pred = np.array([110, 190, 310])
        metrics = compute_regression_metrics(y_true, y_pred, "imperfect")
        assert 0 < metrics["MAE"] < 20
        assert 0 < metrics["R2"] < 1.0

    def test_bias_positive(self):
        y_true = np.array([100, 200, 300])
        y_pred = np.array([120, 220, 320])
        bias = compute_bias(y_true, y_pred)
        assert bias > 0  # over-forecast

    def test_bias_negative(self):
        y_true = np.array([100, 200, 300])
        y_pred = np.array([80, 180, 280])
        bias = compute_bias(y_true, y_pred)
        assert bias < 0  # under-forecast

    def test_pinball_loss_median(self):
        y_true = np.array([10, 20, 30])
        y_pred = np.array([12, 18, 32])
        loss = pinball_loss(y_true, y_pred, 0.5)
        assert loss >= 0


@pytest.mark.unit
class TestAcceptanceCriteria:
    def test_all_pass(self):
        metrics = {
            "R2": 0.95,
            "accuracy_1_minus_WAPE": 0.85,
            "MAPE_%": 15,
            "bias_pct": 3.0,
        }
        result = check_acceptance(metrics)
        assert result["all_pass"] is True

    def test_r2_fail(self):
        metrics = {
            "R2": 0.80,
            "accuracy_1_minus_WAPE": 0.85,
            "MAPE_%": 15,
            "bias_pct": 3.0,
        }
        result = check_acceptance(metrics)
        assert result["r2_pass"] is False
        assert result["all_pass"] is False
