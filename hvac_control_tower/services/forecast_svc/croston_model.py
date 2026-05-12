"""
forecast_svc/croston_model.py
L3: Croston's method baseline for intermittent spare-parts demand (spec §4.3).
Used as the baseline that the primary model must beat by ≥15% WAPE.
Also implements SBA (Syntetos-Boylan Approximation) as improved variant.
"""

import numpy as np
import pandas as pd


class CrostonForecaster:
    """Classic Croston's method for intermittent demand."""

    def __init__(self, alpha: float = 0.1):
        self.alpha = alpha
        self.is_fitted = False
        self._z_hat = 0.0  # smoothed demand size
        self._p_hat = 1.0  # smoothed inter-demand interval

    def fit(self, y: np.ndarray) -> None:
        y = np.asarray(y, dtype=float)
        # Initialize with first non-zero demand
        non_zero = y[y > 0]
        if len(non_zero) == 0:
            self._z_hat = 0.0
            self._p_hat = len(y)
            self.is_fitted = True
            return

        self._z_hat = non_zero[0]
        self._p_hat = 1.0

        q = 0  # periods since last demand
        for val in y:
            q += 1
            if val > 0:
                self._z_hat = self.alpha * val + (1 - self.alpha) * self._z_hat
                self._p_hat = self.alpha * q + (1 - self.alpha) * self._p_hat
                q = 0

        self.is_fitted = True

    def predict(self, h: int = 1) -> np.ndarray:
        """Forecast next h periods."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted.")
        if self._p_hat == 0:
            forecast = 0.0
        else:
            forecast = self._z_hat / self._p_hat
        return np.full(h, forecast)


class SBAForecaster:
    """Syntetos-Boylan Approximation — bias-corrected Croston."""

    def __init__(self, alpha: float = 0.1):
        self.alpha = alpha
        self.croston = CrostonForecaster(alpha=alpha)

    def fit(self, y: np.ndarray) -> None:
        self.croston.fit(y)

    def predict(self, h: int = 1) -> np.ndarray:
        raw = self.croston.predict(h)
        # SBA correction factor
        correction = 1 - self.alpha / 2
        return raw * correction

    @property
    def is_fitted(self):
        return self.croston.is_fitted


def compute_wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Weighted Absolute Percentage Error."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    total = np.sum(np.abs(y_true))
    if total == 0:
        return 0.0
    return float(np.sum(np.abs(y_true - y_pred)) / total)


def evaluate_intermittent(y_series: np.ndarray, train_pct: float = 0.8) -> dict:
    """
    Compare Croston vs SBA on a single intermittent series.
    Returns WAPE for both methods.
    """
    n = len(y_series)
    split = int(n * train_pct)
    train, test = y_series[:split], y_series[split:]
    h = len(test)

    croston = CrostonForecaster()
    croston.fit(train)
    croston_pred = croston.predict(h)

    sba = SBAForecaster()
    sba.fit(train)
    sba_pred = sba.predict(h)

    return {
        "croston_wape": round(compute_wape(test, croston_pred), 4),
        "sba_wape": round(compute_wape(test, sba_pred), 4),
        "improvement_pct": round(
            (compute_wape(test, croston_pred) - compute_wape(test, sba_pred))
            / max(compute_wape(test, croston_pred), 1e-9) * 100, 2
        ),
    }
