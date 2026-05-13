"""dashboards/executive.py — Dashboard 1: Executive Summary (LIVE DATA)"""
from dash import html, dcc
from components.theme import COLORS
from components.kpi_cards import kpi_card
from components import charts
from data.data_loader import (
    get_executive_kpis, get_plan_vs_actual, get_action_queue
)
from data.mock_data import get_scenarios

KPI_CONFIG = [
    ("otif",         "OTIF",           "%",    False),
    ("fill_rate",    "Fill Rate",      "%",    False),
    ("stockout_rate","Stockout Rate",  "%",    True),
    ("mape",         "Forecast MAPE",  "%",    True),
    ("dos",          "Days of Supply", "days", True),
    ("revenue",      "Revenue",        "Cr",   False),
    ("r2",           "Model R²",       "",     False),
    ("co2",          "Carbon (tCO2)",  "t",    True),
]

def layout():
    kpis      = get_executive_kpis()
    pva_df    = get_plan_vs_actual()
    scenarios = get_scenarios()
    queue     = get_action_queue()

    kpi_cards = []
    for key, label, unit, invert in KPI_CONFIG:
        k = kpis[key]
        kpi_cards.append(kpi_card(
            label=label, value=k["value"], unit=unit,
            target=k["target"], delta=k["delta"],
            sparkline_data=k["spark"],
            status=k["status"], delta_invert=invert,
        ))

    return html.Div([
        html.Div(className="page-title", children=[
            html.Span("📊", className="icon"), "Executive Summary — Live Data",
        ]),
        html.Div(className="ai-brief", style={"marginBottom":"16px"}, children=[
            html.Div("[AI GENERATED]", className="ai-badge"),
            html.P(
                f"Fill rate at {kpis['fill_rate']['value']:.1f}% vs 98% target. "
                f"Model R²={kpis['r2']['value']:.3f} on test set (target ≥0.91). "
                f"Stockout rate {kpis['stockout_rate']['value']:.2f}% — review action queue below."
            ),
        ]),
        html.Div(className="grid-kpi", children=kpi_cards),
        html.Div(className="grid-2", style={"marginBottom":"16px"}, children=[
            html.Div(className="card", children=[
                dcc.Graph(figure=charts.plan_vs_actual_chart(pva_df),
                          config={"displayModeBar": False}, style={"height":"280px"}),
            ]),
            html.Div(className="card", children=[
                dcc.Graph(figure=charts.scenario_radar(scenarios),
                          config={"displayModeBar": False}, style={"height":"300px"}),
            ]),
        ]),
        html.Div(className="card", children=[
            html.Div("ACTION QUEUE — LIVE ANOMALIES", className="section-header"),
            *[_action_row(item) for item in queue],
        ]),
    ])

def _action_row(item):
    color = {"CRITICAL": COLORS["danger"], "HIGH": COLORS["warning"],
             "MEDIUM": COLORS["primary"]}.get(item["priority"], COLORS["text_secondary"])
    return html.Div(style={"display":"flex","gap":"12px","padding":"8px 0",
                           "borderBottom":f"1px solid {COLORS['border']}","alignItems":"center"}, children=[
        html.Span(item["priority"], style={"background": color+"22","color":color,
                  "padding":"2px 8px","borderRadius":"4px","fontSize":"0.68rem",
                  "fontWeight":700,"minWidth":"70px","textAlign":"center"}),
        html.Span(f"{item['sku']} · {item['region']}", style={"fontSize":"0.78rem","color":COLORS["text_secondary"],"minWidth":"120px"}),
        html.Span(item["issue"], style={"fontSize":"0.82rem","color":COLORS["text_primary"],"flex":1}),
        html.Span(f"→ {item['action']}", style={"fontSize":"0.76rem","color":COLORS["text_secondary"]}),
    ])
