"""
All 6 financial tool functions.
Each takes typed parameters, returns a dict.
"""

from typing import Optional

def get_financial_kpis(
    metrics: list[str],
    period: str = "current",
    region: str = "All",
    granularity: str = "summary"
) -> dict:
    """
    Fetch KPI values from fact_financial.
    Returns: {metric_name: {value, unit, period, vs_target, vs_prior_period}}
    """
    # Mock SQL Query
    sql = "SELECT metric_name, value, unit, period, vs_target, vs_prior_period FROM fact_financial WHERE period = %s AND region = %s"
    results = {}
    for metric in metrics:
        results[metric] = {
            "value": 15.4 if metric == "EVA" else 12.1,
            "unit": "%" if metric == "ROIC" else "M USD",
            "period": period,
            "vs_target": 0.5,
            "vs_prior_period": 1.2
        }
    return results

def get_kpi_tradeoffs(
    primary_kpi: str,
    secondary_kpis: list[str],
    direction: str = "increase"
) -> dict:
    """
    Query kpi_interdependency table for cause-effect relationships.
    Returns: {affected_kpi: {direction, magnitude, confidence, lag_periods}}
    """
    sql = "SELECT affected_kpi, direction, magnitude, confidence, lag_periods FROM kpi_interdependency WHERE primary_kpi = %s"
    results = {}
    for sk in secondary_kpis:
        results[sk] = {
            "direction": "decrease",
            "magnitude": 0.8,
            "confidence": 0.9,
            "lag_periods": 2
        }
    return results

def run_what_if_scenario(
    scenario_name: str,
    parameter_overrides: dict,
    output_metrics: list[str],
    horizon_months: int = 3
) -> dict:
    """
    Call existing scenario engine (Module 5) with financial parameters.
    Returns: {scenario_name: {metric: {base, scenario, delta, delta_pct}}}
    """
    results = {scenario_name: {}}
    for metric in output_metrics:
        results[scenario_name][metric] = {
            "base": 100,
            "scenario": 110,
            "delta": 10,
            "delta_pct": 10.0
        }
    return results

def get_cost_breakdown(
    cost_categories: list[str] | None = None,
    period: str = "current_month",
    region: str = "All",
    breakdown_by: str = "category"
) -> dict:
    """
    Aggregate cost drivers from fact_financial.
    Returns: {category: {value_usd, pct_of_total, vs_budget, vs_prior}}
    """
    sql = "SELECT category, value_usd, pct_of_total, vs_budget, vs_prior FROM fact_financial WHERE period = %s"
    cats = cost_categories or ["logistics", "manufacturing"]
    results = {}
    for cat in cats:
        results[cat] = {
            "value_usd": 500000,
            "pct_of_total": 25.0,
            "vs_budget": -10000,
            "vs_prior": 5000
        }
    return results

def get_cash_flow_forecast(
    horizon_weeks: int = 13,
    include_components: list[str] | None = None
) -> dict:
    """
    Derive cash flow forecast from inventory + receivables + payables tables.
    Returns: {week: {operating_cf, investing_cf, financing_cf, net_cf, cumulative}}
    """
    sql = "SELECT week, operating_cf, investing_cf, financing_cf, net_cf, cumulative FROM cash_flow_forecast LIMIT %s"
    results = {}
    for w in range(1, horizon_weeks + 1):
        results[f"week_{w}"] = {
            "operating_cf": 1000,
            "investing_cf": -200,
            "financing_cf": -100,
            "net_cf": 700,
            "cumulative": 700 * w
        }
    return results

def get_budget_variance(
    metrics: list[str] | None = None,
    period: str = "ytd",
    breakdown_by: str = "category"
) -> dict:
    """
    Compare plan vs actual from existing kpi_snapshot tables.
    Returns: {metric: {budget, forecast, actual, variance_abs, variance_pct, status}}
    """
    sql = "SELECT metric, budget, forecast, actual, variance_abs, variance_pct, status FROM fact_kpi_snapshot"
    mets = metrics or ["revenue", "opex"]
    results = {}
    for m in mets:
        results[m] = {
            "budget": 1000000,
            "forecast": 950000,
            "actual": 980000,
            "variance_abs": -20000,
            "variance_pct": -2.0,
            "status": "warning"
        }
    return results

FINANCIAL_TOOLS = [
    {
        "name": "get_financial_kpis",
        "description": "Fetch current or historical financial KPI values including EVA, ROIC, cash-to-cash cycle, margin, inventory carrying cost, and total supply chain cost.",
        "input_schema": {
            "type": "object",
            "properties": {
                "metrics": {"type": "array", "items": {"type": "string"}, "description": "List of KPI names to retrieve"},
                "period": {"type": "string", "enum": ["current", "last_7d", "last_30d", "ytd"]},
                "region": {"type": "string", "description": "Filter by region. Use 'All' for global."},
                "granularity": {"type": "string", "enum": ["summary", "by_region", "by_category"]}
            },
            "required": ["metrics"]
        }
    },
    {
        "name": "get_kpi_tradeoffs",
        "description": "Identify cause-and-effect relationships between financial KPIs. Use when the user asks 'what happens if' or asks about the impact of changing one metric on others.",
        "input_schema": {
            "type": "object",
            "properties": {
                "primary_kpi": {"type": "string"},
                "secondary_kpis": {"type": "array", "items": {"type": "string"}},
                "direction": {"type": "string", "enum": ["increase", "decrease"]}
            },
            "required": ["primary_kpi"]
        }
    },
    {
        "name": "run_what_if_scenario",
        "description": "Run a financial what-if scenario through the existing scenario engine. Use when user asks to compare scenarios or model a specific parameter change.",
        "input_schema": {
            "type": "object",
            "properties": {
                "scenario_name": {"type": "string"},
                "parameter_overrides": {"type": "object"},
                "output_metrics": {"type": "array", "items": {"type": "string"}},
                "horizon_months": {"type": "integer", "default": 3}
            },
            "required": ["scenario_name", "parameter_overrides", "output_metrics"]
        }
    },
    {
        "name": "get_cost_breakdown",
        "description": "Retrieve detailed cost breakdown by category, region, or plant. Use for questions about cost composition or drivers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cost_categories": {"type": "array", "items": {"type": "string"}},
                "period": {"type": "string"},
                "region": {"type": "string"},
                "breakdown_by": {"type": "string", "enum": ["category", "region", "plant"]}
            }
        }
    },
    {
        "name": "get_cash_flow_forecast",
        "description": "Get a rolling 13-week cash flow forecast derived from inventory, receivables, and payables. Use for cash management questions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "horizon_weeks": {"type": "integer", "default": 13},
                "include_components": {"type": "array", "items": {"type": "string"}}
            }
        }
    },
    {
        "name": "get_budget_variance",
        "description": "Compare plan vs forecast vs actual for financial metrics. Use for budget review or variance explanation questions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "metrics": {"type": "array", "items": {"type": "string"}},
                "period": {"type": "string", "default": "ytd"},
                "breakdown_by": {"type": "string", "enum": ["category", "region", "plant"]}
            }
        }
    }
]
