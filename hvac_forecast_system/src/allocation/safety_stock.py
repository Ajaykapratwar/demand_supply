"""
safety_stock.py
Safety stock calculation from quantile forecasts.
Safety Stock = P90 - P50 per warehouse-region pair.
"""

import pandas as pd
import numpy as np


def compute_safety_stock(forecast_df: pd.DataFrame) -> pd.DataFrame:
    """
    Input: DataFrame with P50, P90 per Region × YearMonth
    Output: same with safety_stock_units added
    """
    df = forecast_df.copy()
    df["safety_stock_units"] = (df["P90"] - df["P50"]).clip(lower=0)
    return df


def compute_reorder_point(df: pd.DataFrame,
                           lead_time_days: int = 7,
                           days_per_month: int = 30) -> pd.DataFrame:
    """
    Reorder point = daily_demand * lead_time + safety_stock
    daily_demand estimated from P50 / 30
    """
    df = df.copy()
    df["daily_demand_p50"] = df["P50"] / days_per_month
    df["reorder_point"] = (
        df["daily_demand_p50"] * lead_time_days + df["safety_stock_units"]
    ).round()
    return df
