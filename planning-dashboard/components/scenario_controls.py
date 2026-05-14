"""components/scenario_controls.py — Blueprint §15.2 Scenario Control Component Library.

Thin wrappers over Dash/DBC primitives. All controls write to a shared
`scenario-params-store` (dcc.Store) via callback-ready IDs.
"""
import dash_bootstrap_components as dbc
from dash import dcc, html
from config import COLORS


def _label_row(label: str, unit: str = "") -> html.Div:
    """Small label row above a control."""
    text = f"{label}  ({unit})" if unit else label
    return html.Div(text, style={
        "fontSize": "0.72rem", "fontWeight": "600", "letterSpacing": "0.06em",
        "color": COLORS["text_secondary"], "marginBottom": "4px", "textTransform": "uppercase",
    })


def ScenarioSlider(slider_id: str, label: str, min_val: float, max_val: float,
                   step: float = 1.0, default: float = None,
                   unit: str = "", marks: dict = None) -> html.Div:
    """§15.2 <ScenarioSlider> — continuous numeric input (surge %, price ±%, capacity %)."""
    val = default if default is not None else min_val
    return html.Div([
        _label_row(label, unit),
        dcc.Slider(
            id=slider_id,
            min=min_val, max=max_val, step=step, value=val,
            marks=marks or {min_val: str(min_val), max_val: str(max_val)},
            tooltip={"placement": "bottom", "always_visible": True},
            className="scenario-slider",
        ),
    ], style={"marginBottom": "18px"})


def ScenarioToggle(toggle_id: str, label: str, value: bool = False) -> html.Div:
    """§15.2 <ScenarioToggle> — binary on/off (supplier disruption, mode constraint)."""
    return html.Div([
        dbc.Switch(
            id=toggle_id,
            label=html.Span(label, style={
                "fontSize": "0.8rem", "color": COLORS["text_primary"],
            }),
            value=value,
            style={"marginBottom": "10px"},
        ),
    ])


def ScenarioMultiSelect(select_id: str, label: str, options: list,
                       value: list = None) -> html.Div:
    """§15.2 <ScenarioMultiSelect> — region/category/supplier multi-select."""
    return html.Div([
        _label_row(label),
        dcc.Dropdown(
            id=select_id,
            options=[{"label": o, "value": o} for o in options],
            value=value or [],
            multi=True,
            style={
                "backgroundColor": COLORS["surface"],
                "color": COLORS["text_primary"],
                "border": f"1px solid {COLORS['border']}",
                "fontSize": "0.82rem",
            },
            className="scenario-dropdown",
        ),
    ], style={"marginBottom": "18px"})


def scenario_panel(title: str, children: list) -> dbc.Card:
    """Container card for a group of scenario controls."""
    return dbc.Card([
        dbc.CardHeader(
            html.Span([
                html.Span("🎛️ ", style={"marginRight": "4px"}),
                title,
            ], style={
                "fontSize": "0.8rem", "fontWeight": "700",
                "color": COLORS["text_primary"], "letterSpacing": "0.04em",
            }),
            style={
                "backgroundColor": COLORS["card"],
                "borderBottom": f"1px solid {COLORS['border']}",
                "padding": "10px 14px",
            },
        ),
        dbc.CardBody(children, style={"padding": "14px"}),
    ], style={
        "backgroundColor": COLORS["card"],
        "border": f"1px solid {COLORS['border']}",
        "borderRadius": "10px",
        "marginBottom": "16px",
    })
