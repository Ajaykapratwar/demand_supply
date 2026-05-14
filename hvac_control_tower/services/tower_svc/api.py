"""
tower_svc/api.py
L5: FastAPI gateway (spec §4.5).
Endpoints: /forecast, /scenario, /reorder, /alerts
No additional endpoints in v1.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import numpy as np

from routers import financial_copilot

app = FastAPI(
    title="HVAC Cognitive Control Tower",
    description="Five-layer demand-supply orchestration platform",
    version="1.0.0",
)

app.include_router(financial_copilot.router, prefix="/api/v1/copilot/financial")


# === Request/Response Models ===

class ForecastRequest(BaseModel):
    region: str
    horizon_months: int = Field(default=3, ge=1, le=12)


class ForecastResponse(BaseModel):
    region: str
    period: str
    p50: float
    p75: float
    p90: float
    safety_stock: float
    model_version: str = "lightgbm-v1"


class ScenarioRequest(BaseModel):
    scenario_name: str
    horizon_days: int = Field(default=90, ge=1, le=365)
    parameters: dict = Field(default_factory=dict)


class ScenarioResponse(BaseModel):
    scenario_name: str
    cost_delta_pct: float
    recommended_actions: list
    simulation_time_s: float


class ReorderRequest(BaseModel):
    region: str
    sku: Optional[str] = None


class ReorderResponse(BaseModel):
    region: str
    reorder_qty: int
    safety_stock: float
    reorder_point: float
    priority: str = "normal"


class AlertResponse(BaseModel):
    alert_id: str
    severity: str
    source: str
    description: str
    metric_value: float
    threshold: float


# === In-memory state (populated by pipeline) ===
_state = {
    "forecasts": {},
    "alerts": [],
    "reorder_decisions": [],
    "last_scenario": None,
}


def set_state(key: str, value):
    _state[key] = value


def get_state(key: str):
    return _state.get(key)


# === Endpoints (spec §4.5: exactly /forecast, /scenario, /reorder, /alerts) ===

@app.get("/")
def root():
    return {"service": "HVAC Cognitive Control Tower", "version": "1.0.0", "status": "healthy"}


@app.post("/forecast", response_model=list[ForecastResponse])
def get_forecast(request: ForecastRequest):
    """Return demand forecast for a region."""
    forecasts = _state.get("forecasts", {})
    region_data = forecasts.get(request.region)
    if not region_data:
        raise HTTPException(404, f"No forecast available for region: {request.region}")

    results = []
    for entry in region_data[:request.horizon_months]:
        results.append(ForecastResponse(
            region=request.region,
            period=entry.get("period", "unknown"),
            p50=round(entry.get("p50", 0), 1),
            p75=round(entry.get("p75", 0), 1),
            p90=round(entry.get("p90", 0), 1),
            safety_stock=round(entry.get("safety_stock", 0), 1),
        ))
    return results


@app.post("/scenario", response_model=ScenarioResponse)
def run_scenario(request: ScenarioRequest):
    """Run a what-if scenario simulation."""
    from services.twin_svc.scenario import ScenarioEngine, ScenarioInput

    engine = ScenarioEngine()
    try:
        result = engine.run_scenario(ScenarioInput(
            name=request.scenario_name,
            horizon_days=request.horizon_days,
            parameters=request.parameters,
        ))
    except ValueError as e:
        raise HTTPException(400, str(e))

    _state["last_scenario"] = result
    return ScenarioResponse(
        scenario_name=result.name,
        cost_delta_pct=result.cost_delta_pct,
        recommended_actions=result.recommended_actions,
        simulation_time_s=result.simulation_time_s,
    )


@app.post("/reorder", response_model=list[ReorderResponse])
def get_reorder(request: ReorderRequest):
    """Return reorder recommendations for a region."""
    decisions = _state.get("reorder_decisions", [])
    region_decisions = [d for d in decisions if d.get("region") == request.region]
    if not region_decisions:
        raise HTTPException(404, f"No reorder decisions for region: {request.region}")

    return [
        ReorderResponse(
            region=d["region"],
            reorder_qty=d.get("reorder_qty", 0),
            safety_stock=d.get("safety_stock", 0),
            reorder_point=d.get("reorder_point", 0),
            priority=d.get("priority", "normal"),
        )
        for d in region_decisions
    ]


@app.get("/alerts", response_model=list[AlertResponse])
def get_alerts(severity: Optional[str] = None):
    """Return active alerts, optionally filtered by severity."""
    alerts = _state.get("alerts", [])
    if severity:
        alerts = [a for a in alerts if a.get("severity") == severity]

    return [
        AlertResponse(
            alert_id=a.get("alert_id", ""),
            severity=a.get("severity", "info"),
            source=a.get("source", ""),
            description=a.get("description", ""),
            metric_value=a.get("metric_value", 0),
            threshold=a.get("threshold", 0),
        )
        for a in alerts
    ]
