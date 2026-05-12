"""
lasso_cost_model.py
Lasso regression for Cost_Per_Unit_INR estimation.
Features: Units_Shipped, Distance_KM
Used to feed cost estimates into LP optimizer when actuals are unavailable.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LassoCV
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


COST_FEATURES = ["Units_Shipped", "Distance_KM"]
COST_TARGET   = "Cost_Per_Unit_INR"


class LassoCostEstimator:

    def __init__(self, alphas: list = None, cv_folds: int = 5):
        self.alphas = alphas or [0.001, 0.01, 0.1, 1.0, 10.0]
        self.cv_folds = cv_folds
        self.model = None
        self.is_fitted = False

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        """Fit LassoCV with TimeSeriesSplit."""
        tscv = TimeSeriesSplit(n_splits=self.cv_folds)
        self.model = LassoCV(alphas=self.alphas, cv=tscv, max_iter=1000)
        self.model.fit(X[COST_FEATURES], y)
        self.is_fitted = True

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        return self.model.predict(X[COST_FEATURES])

    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> dict:
        preds = self.predict(X)
        return {
            "mae":       mean_absolute_error(y, preds),
            "rmse":      np.sqrt(mean_squared_error(y, preds)),
            "r2":        r2_score(y, preds),
            "best_alpha": self.model.alpha_,
        }
