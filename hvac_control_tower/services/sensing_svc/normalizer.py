"""
sensing_svc/normalizer.py
L1: Raw signal normalization and master table construction.
Aggregates all 5 datasets to Region x YearMonth grain,
then merges into a single master feature table.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def aggregate_orders(df: pd.DataFrame) -> pd.DataFrame:
    """DS1 → Region x Month aggregation."""
    return df.groupby(["Region", "YearMonth"]).agg(
        Avg_Fulfillment_Rate=("Fulfillment_Rate_%", "mean"),
        Total_Units_Backordered=("Units_Backordered", "sum"),
        Total_Units_Ordered=("Units_Ordered", "sum"),
        Total_Units_Fulfilled=("Units_Fulfilled", "sum"),
    ).reset_index()


def aggregate_sales(df: pd.DataFrame) -> pd.DataFrame:
    """DS2 → Region x Month. Net_Units_Sold is demand label."""
    return df.groupby(["Region", "YearMonth"]).agg(
        Net_Units_Sold=("Net_Units_Sold_TARGET", "sum"),
        Avg_Selling_Price=("Avg_Selling_Price_INR", "mean"),
        Avg_Discount=("Discount_%", "mean"),
        Total_Revenue=("Net_Revenue_INR", "sum"),
    ).reset_index()


def aggregate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """DS3 → Region x Month weather/macro features."""
    return df.groupby(["Region", "YearMonth"]).agg(
        Max_Temp_C=("Max_Temp_C", "mean"),
        Min_Temp_C=("Min_Temp_C", "mean"),
        Cooling_Degree_Days=("Cooling_Degree_Days", "sum"),
        Google_Trends_AC_Index=("Google_Trends_AC_Index", "mean"),
        Heatwave_Severity_Score=("Heatwave_Severity_Score", "mean"),
        Festive_Multiplier=("Festive_Multiplier", "max"),
        Composite_Demand_Index=("Composite_Demand_Index", "mean"),
        Forecast_Demand_Target=("Forecast_AC_Units_Next_Month_TARGET", "mean"),
    ).reset_index()


def aggregate_warehouse(df: pd.DataFrame) -> pd.DataFrame:
    """DS4 → Region x Month supply-side features."""
    return df.groupby(["Region", "YearMonth"]).agg(
        Avg_Utilization=("Utilization_%", "mean"),
        Avg_Days_Of_Supply=("Days_Of_Supply_Remaining", "mean"),
        Total_Aged_Stock_90d=("Stock_Aging_90d_Plus", "sum"),
        Avg_SLA_Compliance=("SLA_Compliance_%", "mean"),
    ).reset_index()


def aggregate_logistics(df: pd.DataFrame) -> pd.DataFrame:
    """DS5 → Region x Month cost/shipping features."""
    return df.groupby(["Region", "YearMonth"]).agg(
        Total_Units_Shipped=("Units_Shipped", "sum"),
        Avg_Distance_KM=("Distance_KM", "mean"),
        Avg_Cost_Per_Unit=("Cost_Per_Unit_INR", "mean"),
        Total_CO2_Kg=("CO2_Emissions_Kg", "sum"),
    ).reset_index()


def build_master_table(datasets: dict, output_path: str = None) -> pd.DataFrame:
    """
    Merge all 5 aggregated datasets on Region x YearMonth.
    datasets: dict with keys {orders, sales, signals, warehouse, logistics}.
    """
    orders_agg = aggregate_orders(datasets["orders"])
    sales_agg = aggregate_sales(datasets["sales"])
    signals_agg = aggregate_signals(datasets["signals"])
    warehouse_agg = aggregate_warehouse(datasets["warehouse"])
    logistics_agg = aggregate_logistics(datasets["logistics"])

    master = (
        sales_agg
        .merge(orders_agg, on=["Region", "YearMonth"], how="left")
        .merge(signals_agg, on=["Region", "YearMonth"], how="left")
        .merge(warehouse_agg, on=["Region", "YearMonth"], how="left")
        .merge(logistics_agg, on=["Region", "YearMonth"], how="left")
    )

    master = master.sort_values(["Region", "YearMonth"]).reset_index(drop=True)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        master.to_parquet(output_path, index=False)

    return master


def impute_nulls(df: pd.DataFrame, group_col: str = "Region") -> pd.DataFrame:
    """Per-region median imputation. Fallback: global median."""
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        group_medians = df.groupby(group_col)[col].transform("median")
        global_median = df[col].median()
        df[col] = df[col].fillna(group_medians).fillna(global_median)
    return df

