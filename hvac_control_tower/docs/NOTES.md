# Notes

## Pre-existing code observations
- `hvac_forecast_system/` contains the original flat pipeline (retained, not deleted per CLAUDE.md §3).
- Original system uses XGBoost quantile regression; new system adds LightGBM as primary per spec §4.3.
- Original safety stock uses simple P90-P50 gap; new system uses spec formula with σ_D, σ_L, lead-time.
- Original LP optimizer is single-echelon; new system implements multi-echelon (factory → DC → branch).
