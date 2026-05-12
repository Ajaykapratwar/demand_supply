"""
forecast_svc/feature_store.py
L3: Feature engineering pipeline.
Derives lag, rolling, cyclic, and supply-side features from master table.
Persists features in Parquet partitioned by date.
"""

import pandas as pd
import numpy as np
from pathlib import Path

LAG_WINDOWS = [1, 2, 3, 6]
ROLL_WINDOWS = [3, 6]
TARGET_COL = "Net_Units_Sold"


# Feature list for LightGBM (spec §4.3)
LIGHTGBM_FEATURES = [
    # Demand signals
    "Max_Temp_C",
    "Cooling_Degree_Days",
    "Google_Trends_AC_Index",
    "Composite_Demand_Index",
    "Festive_Multiplier",
    "Heatwave_Severity_Score",
    # Supply-side signals
    "Avg_Utilization",
    "Avg_Days_Of_Supply",
    "Avg_SLA_Compliance",
    "Avg_Fulfillment_Rate",
    # Lag features
    "Net_Units_Sold_lag_1",
    "Net_Units_Sold_lag_2",
    "Net_Units_Sold_lag_3",
    "Net_Units_Sold_lag_6",
    # Rolling statistics
    "Net_Units_Sold_roll_mean_3",
    "Net_Units_Sold_roll_mean_6",
    "Net_Units_Sold_roll_std_3",
    # Cost signals
    "Avg_Cost_Per_Unit",
    # Time encodings
    "month_sin",
    "month_cos",
    "month_num",
]


def add_lag_features(df: pd.DataFrame, target: str = TARGET_COL,
                     group: str = "Region") -> pd.DataFrame:
    df = df.sort_values([group, "YearMonth"]).copy()
    for lag in LAG_WINDOWS:
        df[f"{target}_lag_{lag}"] = df.groupby(group)[target].shift(lag)
    return df


def add_rolling_features(df: pd.DataFrame, target: str = TARGET_COL,
                         group: str = "Region") -> pd.DataFrame:
    df = df.sort_values([group, "YearMonth"]).copy()
    for w in ROLL_WINDOWS:
        df[f"{target}_roll_mean_{w}"] = (
            df.groupby(group)[target]
            .transform(lambda x: x.shift(1).rolling(w, min_periods=1).mean())
        )
        df[f"{target}_roll_std_{w}"] = (
            df.groupby(group)[target]
            .transform(lambda x: x.shift(1).rolling(w, min_periods=1).std())
        )
    return df


def add_cyclic_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    month_num = df["YearMonth"].apply(lambda p: p.month)
    df["month_sin"] = np.sin(2 * np.pi * month_num / 12)
    df["month_cos"] = np.cos(2 * np.pi * month_num / 12)
    df["month_num"] = month_num
    return df


def add_region_encoding(df: pd.DataFrame) -> pd.DataFrame:
    return pd.get_dummies(df, columns=["Region"], prefix="region", drop_first=False)


def build_features(master: pd.DataFrame) -> pd.DataFrame:
    """Full feature engineering pipeline. Call after merge + imputation."""
    df = add_lag_features(master)
    df = add_rolling_features(df)
    df = add_cyclic_time_features(df)
    df = add_region_encoding(df)

    # Fill structural NaNs from lag/rolling
    lag_roll_cols = [c for c in df.columns if "_lag_" in c or "_roll_" in c]
    df[lag_roll_cols] = df[lag_roll_cols].fillna(0)

    return df


def get_available_features(df: pd.DataFrame) -> list:
    """Return only features that exist in the dataframe."""
    return [f for f in LIGHTGBM_FEATURES if f in df.columns]


def split_chronological(df: pd.DataFrame, train_ratio: float = 0.8,
                        val_ratio: float = 0.1) -> tuple:
    """80/10/10 chronological split. Returns (train, val, test)."""
    available = get_available_features(df)
    df = df.dropna(subset=available + [TARGET_COL])
    n = len(df)
    train_end = int(train_ratio * n)
    val_end = int((train_ratio + val_ratio) * n)
    return df.iloc[:train_end], df.iloc[train_end:val_end], df.iloc[val_end:]
