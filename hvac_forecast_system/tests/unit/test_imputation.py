"""Unit tests for imputation module."""

import pytest
import pandas as pd
import numpy as np
from src.feature_store.imputation import median_impute_by_group, validate_no_nulls


@pytest.mark.unit
def test_median_impute_fills_all_nulls():
    df = pd.DataFrame({
        "Region": ["North", "North", "South", "South"],
        "Max_Temp_C": [35.0, np.nan, 28.0, np.nan],
        "Units": [500, np.nan, 400, 300],
    })
    result = median_impute_by_group(df, group_col="Region",
                                    numeric_cols=["Max_Temp_C", "Units"])
    assert result["Max_Temp_C"].isnull().sum() == 0
    assert result["Units"].isnull().sum() == 0


@pytest.mark.unit
def test_median_impute_uses_group_median():
    df = pd.DataFrame({
        "Region": ["North"] * 4,
        "Max_Temp_C": [30.0, 40.0, np.nan, 50.0],
    })
    result = median_impute_by_group(df, group_col="Region",
                                    numeric_cols=["Max_Temp_C"])
    expected = np.median([30.0, 40.0, 50.0])    # group median before fill
    assert abs(result["Max_Temp_C"].iloc[2] - expected) < 1.0


@pytest.mark.unit
def test_validate_no_nulls_raises_on_remaining_nulls():
    df = pd.DataFrame({"A": [1.0, np.nan]})
    with pytest.raises(ValueError, match="Nulls remain"):
        validate_no_nulls(df, cols=["A"])


@pytest.mark.unit
def test_validate_no_nulls_passes_clean_df():
    df = pd.DataFrame({"A": [1.0, 2.0]})
    assert validate_no_nulls(df, cols=["A"]) is True
