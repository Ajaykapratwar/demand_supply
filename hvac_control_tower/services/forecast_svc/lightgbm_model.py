"""
forecast_svc/lightgbm_model.py
L3: Primary demand forecaster using LightGBM (spec §4.3).
Targets: R² ≥ 0.91 on holdout, 1-WAPE ≥ 80% on Hero SKUs.
Supports quantile regression for P50/P75/P90 outputs.
"""

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from services.forecast_svc.feature_store import LIGHTGBM_FEATURES, TARGET_COL, get_available_features


LIGHTGBM_PARAMS = {
    "n_estimators": 1000,
    "max_depth": 7,
    "learning_rate": 0.03,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "min_child_samples": 10,
    "reg_alpha": 0.05,
    "reg_lambda": 0.5,
    "random_state": 42,
    "n_jobs": -1,
    "verbose": -1,
}


class LightGBMForecaster:
    """LightGBM demand forecaster with quantile support."""

    def __init__(self, quantile: float = 0.5):
        self.quantile = quantile
        params = LIGHTGBM_PARAMS.copy()
        if quantile == 0.5:
            params["objective"] = "regression"
            params["metric"] = "rmse"
        else:
            params["objective"] = "quantile"
            params["alpha"] = quantile
            params["metric"] = "quantile"
        self.model = lgb.LGBMRegressor(**params)
        self.feature_names = None
        self.is_fitted = False

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series,
            X_val: pd.DataFrame = None, y_val: pd.Series = None) -> None:
        self.feature_names = get_available_features(X_train)
        fit_params = {}
        if X_val is not None and y_val is not None:
            fit_params["eval_set"] = [(X_val[self.feature_names], y_val)]
            fit_params["callbacks"] = [lgb.early_stopping(50, verbose=False)]
        self.model.fit(X_train[self.feature_names], y_train, **fit_params)
        self.is_fitted = True

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model not fitted.")
        return self.model.predict(X[self.feature_names])

    def cross_validate(self, X: pd.DataFrame, y: pd.Series,
                       n_splits: int = 5) -> dict:
        """Rolling-origin TimeSeriesSplit CV (spec §6.4: 12 folds for backtest)."""
        features = get_available_features(X)
        tscv = TimeSeriesSplit(n_splits=n_splits)
        r2_scores, mae_scores, wape_scores = [], [], []

        for train_idx, val_idx in tscv.split(X):
            X_tr, X_vl = X.iloc[train_idx], X.iloc[val_idx]
            y_tr, y_vl = y.iloc[train_idx], y.iloc[val_idx]

            model = lgb.LGBMRegressor(**{**LIGHTGBM_PARAMS, "objective": "regression"})
            model.fit(X_tr[features], y_tr,
                      eval_set=[(X_vl[features], y_vl)],
                      callbacks=[lgb.early_stopping(30, verbose=False)])
            preds = model.predict(X_vl[features])

            r2_scores.append(r2_score(y_vl, preds))
            mae_scores.append(mean_absolute_error(y_vl, preds))
            total_actual = np.sum(np.abs(y_vl))
            wape = np.sum(np.abs(y_vl - preds)) / total_actual if total_actual > 0 else 1.0
            wape_scores.append(wape)

        return {
            "cv_r2_mean": round(np.mean(r2_scores), 4),
            "cv_r2_min": round(np.min(r2_scores), 4),
            "cv_mae_mean": round(np.mean(mae_scores), 2),
            "cv_wape_mean": round(np.mean(wape_scores), 4),
            "cv_accuracy": round(1 - np.mean(wape_scores), 4),
        }


def build_quantile_forecasters(X_train, y_train, X_val, y_val) -> dict:
    """Train P50, P75, P90 LightGBM forecasters."""
    forecasters = {}
    for q, label in [(0.50, "p50"), (0.75, "p75"), (0.90, "p90")]:
        f = LightGBMForecaster(quantile=q)
        f.fit(X_train, y_train, X_val, y_val)
        forecasters[label] = f
    return forecasters


def generate_quantile_forecasts(forecasters: dict, X_test: pd.DataFrame) -> pd.DataFrame:
    """Generate P50/P75/P90 forecasts with safety stock and risk flags."""
    results = pd.DataFrame(index=X_test.index)
    results["P50"] = forecasters["p50"].predict(X_test)
    results["P75"] = forecasters["p75"].predict(X_test)
    results["P90"] = forecasters["p90"].predict(X_test)

    # Enforce monotonicity
    results["P75"] = results[["P50", "P75"]].max(axis=1)
    results["P90"] = results[["P75", "P90"]].max(axis=1)

    results["safety_stock"] = results["P90"] - results["P50"]
    results["risk_flag"] = (results["safety_stock"] / results["P50"].clip(lower=1)) > 0.30

    return results
