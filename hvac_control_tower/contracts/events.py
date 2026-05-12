"""
contracts/events.py
Typed event schemas for inter-service communication.
Replaces Protobuf for local deployment (per ASSUMPTIONS.md §1).
All services produce/consume these dataclasses exclusively.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional
import json


class EventType(Enum):
    TELEMETRY = "telemetry"
    WEATHER = "weather"
    ERP = "erp"
    REGULATORY = "regulatory"
    FORECAST_RESULT = "forecast_result"
    REORDER_DECISION = "reorder_decision"
    SCENARIO_REQUEST = "scenario_request"
    SCENARIO_RESULT = "scenario_result"
    ANOMALY_ALERT = "anomaly_alert"
    LAST_TIME_BUY = "last_time_buy"
    FEEDBACK = "feedback"


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class EquipmentType(Enum):
    CHILLER = "chiller"
    AHU = "ahu"
    RTU = "rtu"
    SPLIT_AC = "split_ac"
    WINDOW_AC = "window_ac"
    PORTABLE = "portable"
    TOWER = "tower"


@dataclass
class BaseEvent:
    event_id: str
    timestamp: str  # ISO 8601
    event_type: str
    site_id: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)


@dataclass
class TelemetryEvent(BaseEvent):
    """L1 → L2: IoT sensor readings."""
    equipment_id: str = ""
    equipment_type: str = ""
    temperature_c: float = 0.0
    pressure_kpa: float = 0.0
    vibration_mm_s: float = 0.0
    refrigerant_level_pct: float = 0.0
    power_kw: float = 0.0
    runtime_hours: float = 0.0
    region: str = ""


@dataclass
class WeatherEvent(BaseEvent):
    """L1 → L3: Weather signal."""
    region: str = ""
    max_temp_c: float = 0.0
    min_temp_c: float = 0.0
    cooling_degree_days: float = 0.0
    heatwave_severity: float = 0.0


@dataclass
class ERPEvent(BaseEvent):
    """L1 → L3/L4: ERP order/inventory signal."""
    region: str = ""
    sku: str = ""
    units_ordered: int = 0
    units_fulfilled: int = 0
    units_backordered: int = 0
    lead_time_days: float = 7.0
    current_inventory: int = 0


@dataclass
class RegulatoryEvent(BaseEvent):
    """L1 → L2: Regulatory changes (e.g., SEER2 transition)."""
    regulation_id: str = ""
    description: str = ""
    effective_date: str = ""
    affected_skus: list = field(default_factory=list)
    obsolescence_pct: float = 0.0


@dataclass
class ForecastResult(BaseEvent):
    """L3 → L4/L5: Demand forecast output."""
    region: str = ""
    sku_class: str = ""
    period: str = ""  # YYYY-MM
    p50: float = 0.0
    p75: float = 0.0
    p90: float = 0.0
    model_version: str = ""
    r2: float = 0.0
    wape: float = 0.0
    bias_pct: float = 0.0


@dataclass
class ReorderDecision(BaseEvent):
    """L4 → L5: Inventory reorder action."""
    sku: str = ""
    warehouse_id: str = ""
    region: str = ""
    reorder_qty: int = 0
    safety_stock: float = 0.0
    reorder_point: float = 0.0
    echelon: str = ""  # factory, dc, branch
    priority: str = "normal"


@dataclass
class ScenarioRequest(BaseEvent):
    """L5 → L2: Scenario simulation request."""
    scenario_name: str = ""
    parameters: dict = field(default_factory=dict)
    horizon_days: int = 90


@dataclass
class ScenarioResult(BaseEvent):
    """L2 → L5: Scenario simulation output."""
    scenario_name: str = ""
    cost_delta_pct: float = 0.0
    fill_rate_trajectory: list = field(default_factory=list)
    inventory_trajectory: list = field(default_factory=list)
    recommended_actions: list = field(default_factory=list)
    simulation_time_s: float = 0.0


@dataclass
class AnomalyAlert(BaseEvent):
    """Any layer → L5: Alert for anomalous conditions."""
    source_service: str = ""
    severity: str = "warning"
    metric_name: str = ""
    metric_value: float = 0.0
    threshold: float = 0.0
    description: str = ""
    recommended_action: str = ""


def validate_event(event: BaseEvent) -> bool:
    """Validate event has required fields. Returns True or raises ValueError."""
    if not event.event_id:
        raise ValueError("event_id is required")
    if not event.timestamp:
        raise ValueError("timestamp is required")
    if not event.event_type:
        raise ValueError("event_type is required")
    return True
