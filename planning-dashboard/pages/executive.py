"""pages/executive.py — Dashboard 1: Executive Summary"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page

from components.kpi_card import kpi_row
from components import charts
from config import COLORS, LEGEND_STYLE, apply_dark_layout, hex_to_rgba
from data.mock_data import executive_kpis, plan_vs_actual, scenario_comparison, risk_strip

register_page(__name__, path="/", name="Executive Summary")

_kpis      = executive_kpis()
_pva       = plan_vs_actual()
_scenarios = scenario_comparison()
_risks     = risk_strip()

# Plan vs Actual
_pva_fig = charts.plan_vs_actual_chart(_pva)

# Scenario table
_scenario_radar_fig = charts.scenario_radar(_scenarios)

_scenario_fig = go.Figure(go.Table(
    header=dict(values=list(_scenarios.columns), fill_color=COLORS["surface"],
                font=dict(color=COLORS["primary"], size=11, family="Inter"),
                align="left", line_color=COLORS["border"], height=32),
    cells=dict(values=[_scenarios[c].tolist() for c in _scenarios.columns],
               fill_color=[[COLORS["card"], COLORS["surface"]] * 10],
               font=dict(color=COLORS["text_primary"], size=11),
               align="left", line_color=COLORS["border"], height=28),
))
apply_dark_layout(_scenario_fig, title="Scenario Table", height=180,
                  margin=dict(l=0, r=0, t=40, b=0))

# Risk strip
_RISK_COLOR = {"HIGH": COLORS["danger"], "MEDIUM": COLORS["warning"], "LOW": COLORS["success"]}

def _risk_badge(r):
    color = _RISK_COLOR[r["risk"]]
    return dbc.Card(dbc.CardBody([
        html.Div([
            html.Span("●", style={"color": color, "marginRight": "6px"}),
            html.Span(r["supplier"], style={"fontWeight": "600", "fontSize": "0.82rem", "color": COLORS["text_primary"]}),
            html.Span(r["risk"], style={"color": color, "fontSize": "0.7rem", "fontWeight": "700",
                                        "border": f"1px solid {color}", "borderRadius": "4px",
                                        "padding": "1px 6px", "marginLeft": "8px"}),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "4px"}),
        html.Div(r["issue"], style={"fontSize": "0.76rem", "color": COLORS["text_secondary"]}),
        dbc.Progress(value=r["score"]*100,
                     color="danger" if r["risk"]=="HIGH" else "warning" if r["risk"]=="MEDIUM" else "success",
                     style={"height": "4px", "marginTop": "6px", "backgroundColor": COLORS["border"]}),
    ], style={"padding": "10px 14px"}),
    style={"backgroundColor": COLORS["surface"], "border": f"1px solid {color}44", "borderRadius": "8px"})

layout = html.Div([
    html.H5("Executive Summary", style={"color": COLORS["text_primary"], "fontWeight": "700", "marginBottom": "4px"}),
    html.Div("Real-time cross-functional KPI overview — Tactical Horizon",
             style={"color": COLORS["text_secondary"], "fontSize": "0.83rem", "marginBottom": "20px"}),
    
    # AI Brief
    html.Div(style={"marginBottom": "16px", "backgroundColor": COLORS["card"], "padding": "15px", "borderRadius": "8px", "border": f"1px solid {COLORS['border']}"}, children=[
        html.Div("[AI GENERATED]", style={"fontSize": "0.7rem", "color": COLORS["primary"], "fontWeight": "700", "marginBottom": "6px", "letterSpacing": "0.05em"}),
        html.P(
            "OTIF at 94.1% (−0.9pp vs target): driven by APAC stockout risk on SKU-0003 "
            "(7-day horizon) and EMEA supply delay. "
            "Top opportunity: redistribute 12K units from overstock EMEA DCs "
            "to LATAM before Q3 peak, yielding est. +$180K margin recovery. ",
            style={"fontSize": "0.85rem", "color": COLORS["text_primary"], "margin": "0", "lineHeight": "1.5"}
        ),
    ]),

    kpi_row(_kpis, cols=4),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=_pva_fig, config={"displayModeBar": False}), md=7, className="mb-3"),
        dbc.Col(dcc.Graph(figure=_scenario_radar_fig, config={"displayModeBar": False}), md=5, className="mb-3"),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=_scenario_fig, config={"displayModeBar": False}), md=12, className="mb-3"),
    ]),
    html.Div("SUPPLIER RISK STRIP", style={"fontSize": "0.72rem", "fontWeight": "700",
             "letterSpacing": "0.08em", "color": COLORS["text_secondary"], "marginBottom": "10px"}),
    dbc.Row([dbc.Col(_risk_badge(r), md=4, className="mb-2") for r in _risks]),
])
