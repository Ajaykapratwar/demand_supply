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
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.feature_store.feature_engineering import XGBOOST_FEATURES, TARGET_COL


XGBOOST_PARAMS = {
    "n_estimators":        800,
    "max_depth":           7,
    "learning_rate":       0.03,
    "subsample":           0.85,
    "colsample_bytree":    0.85,
    "min_child_weight":    3,
    "reg_alpha":           0.05,      # L1
    "reg_lambda":          0.5,       # L2
    "gamma":               0.01,      # min split loss
    "random_state":        42,
    "early_stopping_rounds": 50,
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
