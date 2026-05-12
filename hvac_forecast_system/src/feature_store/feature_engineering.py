"""
feature_engineering.py
Creates lag features, rolling statistics, and cyclic time encodings.
"""

import pandas as pd
import numpy as np


LAG_WINDOWS   = [1, 2, 3, 6]      # months lag for demand signal
ROLL_WINDOWS  = [3, 6]             # rolling mean windows


def add_lag_features(df: pd.DataFrame, target_col: str = "Net_Units_Sold",
                     group_col: str = "Region") -> pd.DataFrame:
    """Add lag_1 through lag_6 for target per region."""
    df = df.sort_values([group_col, "YearMonth"]).copy()
    for lag in LAG_WINDOWS:
        df[f"{target_col}_lag_{lag}"] = (
            df.groupby(group_col)[target_col].shift(lag)
        )
    return df


def add_rolling_features(df: pd.DataFrame, target_col: str = "Net_Units_Sold",
                          group_col: str = "Region") -> pd.DataFrame:
    """Add rolling mean and std over 3 and 6 month windows."""
    df = df.sort_values([group_col, "YearMonth"]).copy()
    for w in ROLL_WINDOWS:
        df[f"{target_col}_roll_mean_{w}"] = (
            df.groupby(group_col)[target_col]
            .transform(lambda x: x.shift(1).rolling(w, min_periods=1).mean())
        )
        df[f"{target_col}_roll_std_{w}"] = (
            df.groupby(group_col)[target_col]
            .transform(lambda x: x.shift(1).rolling(w, min_periods=1).std())
        )
    return df


def add_cyclic_time_features(df: pd.DataFrame,
                              period_col: str = "YearMonth") -> pd.DataFrame:
    """Encode month as sin/cos to capture seasonality."""
    df = df.copy()
    month_num = df[period_col].dt.month if hasattr(df[period_col], "dt") else \
                df[period_col].apply(lambda p: p.month)
    df["month_sin"] = np.sin(2 * np.pi * month_num / 12)
    df["month_cos"] = np.cos(2 * np.pi * month_num / 12)
    df["month_num"] = month_num
    return df


def add_region_encoding(df: pd.DataFrame, region_col: str = "Region") -> pd.DataFrame:
    """One-hot encode regions."""
    return pd.get_dummies(df, columns=[region_col], prefix="region", drop_first=False)


def build_model_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply full feature engineering pipeline. Call after merge."""
    df = add_lag_features(df)
    df = add_rolling_features(df)
    df = add_cyclic_time_features(df)
    df = add_region_encoding(df)

    # Fill structural NaNs from lag/rolling (first rows of each group)
    lag_roll_cols = [c for c in df.columns if "_lag_" in c or "_roll_" in c]
    df[lag_roll_cols] = df[lag_roll_cols].fillna(0)
    return df


# Selected feature set for XGBoost (max 10 features, avoids overfitting)
XGBOOST_FEATURES = [
    # Demand signals
    "Max_Temp_C",
    "Cooling_Degree_Days",
    "Google_Trends_AC_Index",
    "Composite_Demand_Index",
    "Festive_Multiplier",
    # Lag features (strongest predictors)
    "Net_Units_Sold_lag_1",
    "Net_Units_Sold_lag_2",
    "Net_Units_Sold_lag_3",
    "Net_Units_Sold_lag_6",
    # Rolling statistics
    "Net_Units_Sold_roll_mean_3",
    "Net_Units_Sold_roll_mean_6",
    "Net_Units_Sold_roll_std_3",
    # Time encodings
    "month_sin",
    "month_cos",
    "month_num",
]

TARGET_COL = "Net_Units_Sold"
