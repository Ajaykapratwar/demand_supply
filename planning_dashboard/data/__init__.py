"""
planning_dashboard/data/__init__.py
Exports both live data_loader functions and mock_data fallbacks.
Dashboard modules import from here.
"""
# Live data (real CSVs + model outputs)
from data.data_loader import (
    get_executive_kpis,
    get_plan_vs_actual,
    get_supply_demand_balance,
    get_inventory_dos_gauges,
    get_forecast_fan_chart,
    get_forecast_accuracy_kpis,
    get_capacity_utilization,
    get_capacity_load_profile,
    get_financial_summary,
    get_budget_vs_forecast_real,
    get_supplier_risk,
    get_sustainability_summary,
    get_co2_trend,
    get_regional_kpis,
    get_region_vs_plan,
    get_action_queue,
)

# Safety stock sim (scipy — in data_loader)
from data.mock_data import get_safety_stock_simulation

# Scenario/mock data for views not yet connected to a live model
from data.mock_data import (
    get_scenarios,
    get_pl_bridge_waterfall,
    get_fva_waterfall,
    get_bias_by_category,
    get_inventory_geo_data,
    get_service_vs_inventory_scatter,
    get_risk_matrix,
    get_mitigation_actions,
    get_pareto_scatter,
    get_sustainability_kpis,
    get_emissions_breakdown,
    get_kpi_sparklines,
)
