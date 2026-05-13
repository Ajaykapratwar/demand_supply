"""pages/forecast.py — Dashboard 3: Forecast Analytics"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page

from components.kpi_card import kpi_row
from config import COLORS, LEGEND_STYLE, apply_dark_layout, hex_to_rgba
from data.mock_data import forecast_accuracy_kpis, forecast_fan_chart, fva_waterfall

register_page(__name__, path="/forecast", name="Forecast Analytics")

_kpis = forecast_accuracy_kpis()
_fan  = forecast_fan_chart()
_fva  = fva_waterfall()

# Fan chart
_fan_fig = go.Figure()
_fan_fig.add_trace(go.Scatter(
    x=list(_fan["week"]) + list(_fan["week"])[::-1],
    y=list(_fan["p90"]) + list(_fan["p10"])[::-1],
    fill="toself", fillcolor=hex_to_rgba(COLORS["primary"], 0.13),
    line=dict(color="rgba(0,0,0,0)"), name="P10–P90 band", hoverinfo="skip"))
_fan_fig.add_trace(go.Scatter(x=_fan["week"], y=_fan["p50"], name="P50 Forecast",
    line=dict(color=COLORS["primary"], width=2)))
actuals = _fan.dropna(subset=["actual"])
_fan_fig.add_trace(go.Scatter(x=actuals["week"], y=actuals["actual"], name="Actual",
    mode="lines+markers", line=dict(color=COLORS["success"], width=2), marker=dict(size=5)))
apply_dark_layout(_fan_fig, title="Forecast Fan Chart (P10/P50/P90 vs Actual)", height=280,
                  legend=dict(**LEGEND_STYLE, orientation="h", y=1.1))

# FVA waterfall
_fva_colors = [COLORS["danger"], COLORS["success"], COLORS["success"], COLORS["warning"], COLORS["primary"]]
_fva_fig = go.Figure(go.Bar(
    x=_fva["stage"], y=_fva["wape"], marker_color=_fva_colors,
    text=[f"{v:.1f}%" for v in _fva["wape"]], textposition="outside",
    textfont=dict(color=COLORS["text_primary"])))
apply_dark_layout(_fva_fig, title="Forecast Value Added (FVA) Waterfall — WAPE %",
                  height=260, showlegend=False,
                  yaxis=dict(title="WAPE %", gridcolor=COLORS["border"]))

# Bias gauge
_bias_fig = go.Figure(go.Indicator(
    mode="gauge+number+delta", value=2.3,
    title={"text": "Forecast Bias (%)", "font": {"color": COLORS["text_secondary"], "size": 12}},
    number={"suffix": "%", "font": {"color": COLORS["success"], "size": 28}},
    delta={"reference": 2.7, "suffix": "pp", "font": {"size": 13}},
    gauge={"axis": {"range": [-10, 10], "tickcolor": COLORS["text_secondary"],
                    "tickfont": {"color": COLORS["text_secondary"]}},
           "bar": {"color": COLORS["success"]},
           "steps": [{"range": [-10, -5], "color": "rgba(218,54,51,0.33)"},
                     {"range": [-5, 5],   "color": "rgba(63,185,80,0.2)"},
                     {"range": [5, 10],   "color": "rgba(218,54,51,0.33)"}],
           "threshold": {"line": {"color": COLORS["warning"], "width": 2}, "value": 5},
           "bgcolor": COLORS["surface"], "bordercolor": COLORS["border"]},
))
apply_dark_layout(_bias_fig, height=220, margin=dict(l=10, r=10, t=50, b=10))

layout = html.Div([
    html.H5("Forecast Analytics", style={"color": COLORS["text_primary"], "fontWeight": "700", "marginBottom": "4px"}),
    html.Div("Accuracy KPIs • Forecast fan chart • FVA waterfall • Bias gauge",
             style={"color": COLORS["text_secondary"], "fontSize": "0.83rem", "marginBottom": "20px"}),
    kpi_row(_kpis, cols=3),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=_fan_fig,  config={"displayModeBar": False}), md=8, className="mb-3"),
        dbc.Col(dcc.Graph(figure=_bias_fig, config={"displayModeBar": False}), md=4, className="mb-3"),
    ]),
    dbc.Row([dbc.Col(dcc.Graph(figure=_fva_fig, config={"displayModeBar": False}), className="mb-3")]),
])
