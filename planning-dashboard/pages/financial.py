"""pages/financial.py — Dashboard 6: Financial Impact"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page

from components.kpi_card import kpi_row
from config import COLORS, LEGEND_STYLE, apply_dark_layout
from data.mock_data import financial_kpis, scenario_pl_bridge, budget_vs_forecast

register_page(__name__, path="/financial", name="Financial Impact")

_kpis   = financial_kpis()
_bridge = scenario_pl_bridge()
_bvf    = budget_vs_forecast()

_bridge_fig = go.Figure(go.Waterfall(
    x=_bridge["component"], y=_bridge["value"],
    measure=["absolute"] + ["relative"]*(len(_bridge)-2) + ["total"],
    text=[f"${v:+.1f}M" for v in _bridge["value"]], textposition="outside",
    textfont=dict(color=COLORS["text_primary"]),
    connector=dict(line=dict(color=COLORS["border"], width=1)),
    increasing=dict(marker=dict(color=COLORS["success"])),
    decreasing=dict(marker=dict(color=COLORS["danger"])),
    totals=dict(marker=dict(color=COLORS["accent"])),
))
apply_dark_layout(_bridge_fig, title="Scenario P&L Bridge — Demand Surge Impact ($M)",
                  height=290, showlegend=False,
                  yaxis=dict(title="$M", gridcolor=COLORS["border"]))

_bvf_fig = go.Figure()
_bvf_fig.add_trace(go.Bar(x=_bvf["month"], y=_bvf["budget"], name="Budget",
                           marker_color=COLORS["chart_3"], opacity=0.7))
_bvf_fig.add_trace(go.Scatter(x=_bvf["month"], y=_bvf["forecast"], name="Forecast",
                               line=dict(color=COLORS["primary"], width=2, dash="dash")))
_act = _bvf.dropna(subset=["actual"])
_bvf_fig.add_trace(go.Scatter(x=_act["month"], y=_act["actual"], name="Actual",
                               mode="lines+markers", line=dict(color=COLORS["success"], width=2),
                               marker=dict(size=5)))
apply_dark_layout(_bvf_fig, title="Budget vs Forecast vs Actual ($M)", height=280,
                  yaxis=dict(title="Revenue $M", gridcolor=COLORS["border"]),
                  legend=dict(**LEGEND_STYLE, orientation="h", y=1.08), barmode="group")

layout = html.Div([
    html.H5("Financial Impact", style={"color": COLORS["text_primary"], "fontWeight": "700", "marginBottom": "4px"}),
    html.Div("Revenue/margin KPIs • Scenario P&L bridge • Budget vs forecast",
             style={"color": COLORS["text_secondary"], "fontSize": "0.83rem", "marginBottom": "20px"}),
    kpi_row(_kpis, cols=3),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=_bridge_fig, config={"displayModeBar": False}), md=6, className="mb-3"),
        dbc.Col(dcc.Graph(figure=_bvf_fig,    config={"displayModeBar": False}), md=6, className="mb-3"),
    ]),
])
