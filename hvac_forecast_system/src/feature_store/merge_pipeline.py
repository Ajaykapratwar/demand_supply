"""
merge_pipeline.py
Merges all 5 datasets into master_feature_table.parquet
Join key: Region × Month (+ SKU where available)
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_raw_datasets(data_dir: str) -> dict:
    """Load all 5 raw CSVs. Returns dict of DataFrames."""
    base = Path(data_dir)
    return {
        "orders":    pd.read_csv(base / "dataset1_order_history.csv",    parse_dates=["Date"]),
        "sales":     pd.read_csv(base / "dataset2_sales_revenue.csv",    parse_dates=["Date"]),
        "signals":   pd.read_csv(base / "dataset3_demand_signals.csv",   parse_dates=["Date"]),
        "warehouse": pd.read_csv(base / "dataset4_warehouse_capacity.csv", parse_dates=["Date"]),
        "logistics": pd.read_csv(base / "dataset5_logistics_cost.csv",   parse_dates=["Date"]),
    }


def extract_year_month(df: pd.DataFrame, date_col: str = "Date") -> pd.DataFrame:
    df = df.copy()
    df["YearMonth"] = df[date_col].dt.to_period("M")
    return df


def aggregate_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate DS1 to Region × Month level."""
    df = extract_year_month(df)
    return df.groupby(["Region", "YearMonth"]).agg(
        Avg_Fulfillment_Rate=("Fulfillment_Rate_%", "mean"),
        Total_Units_Backordered=("Units_Backordered", "sum"),
        Total_Units_Ordered=("Units_Ordered", "sum"),
        Total_Units_Fulfilled=("Units_Fulfilled", "sum"),
    ).reset_index()


def aggregate_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate DS2 to Region × Month. Net_Units_Sold_TARGET is the demand label."""
    df = extract_year_month(df)
    return df.groupby(["Region", "YearMonth"]).agg(
        Net_Units_Sold=("Net_Units_Sold_TARGET", "sum"),
        Avg_Selling_Price=("Avg_Selling_Price_INR", "mean"),
        Avg_Discount=("Discount_%", "mean"),
        Total_Revenue=("Net_Revenue_INR", "sum"),
    ).reset_index()


def aggregate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate DS3 weather/macro signals to Region × Month."""
    df = extract_year_month(df)
    # Drop near-zero-variance features
    drop_cols = ["COVID_Impact_Score", "Semiconductor_Shortage_Score",
                 "Consumer_Confidence_Index"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])
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
    """Aggregate DS4 to Region × Month supply-side features."""
    df = extract_year_month(df)
    return df.groupby(["Region", "YearMonth"]).agg(
        Avg_Utilization=("Utilization_%", "mean"),
        Avg_Days_Of_Supply=("Days_Of_Supply_Remaining", "mean"),
        Total_Aged_Stock_90d=("Stock_Aging_90d_Plus", "sum"),
        Avg_SLA_Compliance=("SLA_Compliance_%", "mean"),
    ).reset_index()


def aggregate_logistics(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate DS5 to Region × Month cost features."""
    df = extract_year_month(df)
    return df.groupby(["Region", "YearMonth"]).agg(
        Total_Units_Shipped=("Units_Shipped", "sum"),
        Avg_Distance_KM=("Distance_KM", "mean"),
        Avg_Cost_Per_Unit=("Cost_Per_Unit_INR", "mean"),
        Total_CO2_Kg=("CO2_Emissions_Kg", "sum"),
    ).reset_index()


def build_master_table(data_dir: str, output_path: str) -> pd.DataFrame:
    """
    Full merge pipeline. Returns master feature table.
    Join key: Region × YearMonth
    """
    dfs = load_raw_datasets(data_dir)

    orders_agg    = aggregate_orders(dfs["orders"])
    sales_agg     = aggregate_sales(dfs["sales"])
    signals_agg   = aggregate_signals(dfs["signals"])
    warehouse_agg = aggregate_warehouse(dfs["warehouse"])
    logistics_agg = aggregate_logistics(dfs["logistics"])

    # Sequential left joins on Region × YearMonth
    master = (
        sales_agg
        .merge(orders_agg,    on=["Region", "YearMonth"], how="left")
        .merge(signals_agg,   on=["Region", "YearMonth"], how="left")
        .merge(warehouse_agg, on=["Region", "YearMonth"], how="left")
        .merge(logistics_agg, on=["Region", "YearMonth"], how="left")
    )

    # Sort chronologically
    master = master.sort_values(["Region", "YearMonth"]).reset_index(drop=True)

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    master.to_parquet(output_path, index=False)
    return master


if __name__ == "__main__":
    import sys
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data/raw"
    output_path = "data/processed/master_feature_table.parquet"
    master = build_master_table(data_dir, output_path)
    print(f"Master table built: {master.shape[0]} rows × {master.shape[1]} cols")
    print(f"Saved to {output_path}")
