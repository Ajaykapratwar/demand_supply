"""
imputation.py
Handles ~3% null rate across all numeric columns.
Strategy: median imputation per Region group.
"""

import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer


def median_impute_by_group(df: pd.DataFrame, group_col: str = "Region",
                            numeric_cols: list = None) -> pd.DataFrame:
    """Fill nulls with per-group median. Fallback: global median."""
    df = df.copy()
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_cols:
        group_medians = df.groupby(group_col)[col].transform("median")
        global_median = df[col].median()
        df[col] = df[col].fillna(group_medians).fillna(global_median)

    return df


def validate_no_nulls(df: pd.DataFrame, cols: list) -> bool:
    """Assert no nulls remain in specified columns after imputation."""
    null_counts = df[cols].isnull().sum()
    if null_counts.any():
        raise ValueError(f"Nulls remain after imputation:\n{null_counts[null_counts > 0]}")
    return True
