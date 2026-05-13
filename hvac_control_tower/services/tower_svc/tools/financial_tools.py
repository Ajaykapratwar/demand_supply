from typing import List, Dict, Any
from datetime import datetime

# Dummy representations of database execution

def get_financial_kpis(kpi_names: List[str] = None, period: str = "current") -> List[Dict[str, Any]]:
    """Retrieves current or historical financial KPIs."""
    # MVP dummy implementation
    return [
        {
            "kpi": "EVA",
            "value": 15.2,
            "unit": "USD_M",
            "data_freshness": datetime.now().isoformat(),
            "citations": ["fact_financial.eva"]
        },
        {
            "kpi": "carrying_cost",
            "value": 2.1,
            "unit": "USD_M",
            "data_freshness": datetime.now().isoformat(),
            "citations": ["fact_inventory.carrying_cost"]
        }
    ]

def get_cost_breakdown(dimension: str = "category") -> List[Dict[str, Any]]:
    """Breaks down costs by category, region, or plant."""
    return [
        {"dimension": "logistics", "cost": 4.5, "unit": "USD_M"},
        {"dimension": "materials", "cost": 12.0, "unit": "USD_M"},
    ]

def get_budget_variance(period: str = "current") -> Dict[str, Any]:
    """Retrieves budget vs actual variance."""
    return {"budget": 100.0, "actual": 95.0, "variance": -5.0, "unit": "USD_M"}

def get_cash_flow_forecast(horizon_days: int = 90) -> List[Dict[str, Any]]:
    """Retrieves cash flow forecast over the specified horizon."""
    return [{"period": "next_quarter", "projected_inflow": 50, "projected_outflow": 40}]

def run_what_if_scenario(scenario_name: str, parameters: dict, target_kpis: List[str]) -> Dict[str, Any]:
    """Executes a financial what-if scenario."""
    from services.tower_svc.api import get_state
    
    # In a real implementation this would call the twin_svc ScenarioEngine
    return {
        "scenario_name": scenario_name,
        "impacts": {kpi: -0.05 for kpi in target_kpis},
        "citations": ["scenario_engine.simulation"]
    }

def get_kpi_tradeoffs(source_kpi: str, target_kpis: List[str], direction: str) -> List[Dict[str, Any]]:
    """Retrieves KPI interdependency tradeoff data."""
    return [
        {
            "source_kpi": source_kpi,
            "target_kpi": tk,
            "direction": "negative" if direction == "increase" else "positive",
            "magnitude": 0.85,
            "citations": ["dim_kpi_interdependency"]
        }
        for tk in target_kpis
    ]
