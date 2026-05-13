"""pages/forecast.py — Dashboard 3: Forecast Analytics"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page, callback, Input, Output
import pandas as pd

from components.kpi_card import kpi_row
from config import COLORS, LEGEND_STYLE, apply_dark_layout, hex_to_rgba
from data.data_loader import get_forecast_accuracy_kpis, get_forecast_fan_chart, get_fva_waterfall

register_page(__name__, path="/forecast", name="Forecast Analytics")

def layout(**kwargs):
    return html.Div(id="forecast-page-content")

@callback(
    Output("forecast-page-content", "children"),
    Input("global-filter-store", "data"),
)
def update_forecast_page(filter_data):
    filter_data = filter_data or {}
    region = filter_data.get("region", "Global")
    category = filter_data.get("category", "All")
    horizon = filter_data.get("horizon", "Tactical")
    
    kpis = get_forecast_accuracy_kpis(region=region, category=category)
    fan_df = get_forecast_fan_chart(region=region, category=category)
    fva_df = get_fva_waterfall(region=region, category=category)
    
    # Format KPIs for kpi_row
    kpi_labels = {
        "mape": "MAPE", "wape": "WAPE", "r2": "Model R²", "bias": "Bias", "mae": "MAE"
    }
    formatted_kpis = {kpi_labels.get(k, k): v for k, v in kpis.items()}
    
    # Fan chart
    fan_fig = go.Figure()
    
    # Use "date" column if present, else fallback to "week"
    x_col = "date" if "date" in fan_df.columns else "week"
    
    fan_fig.add_trace(go.Scatter(
        x=list(fan_df[x_col]) + list(fan_df[x_col])[::-1],
        y=list(fan_df["p90"]) + list(fan_df["p10"])[::-1],
        fill="toself", fillcolor=hex_to_rgba(COLORS["primary"], 0.13),
        line=dict(color="rgba(0,0,0,0)"), name="P10–P90 band", hoverinfo="skip"))
    
    fan_fig.add_trace(go.Scatter(x=fan_df[x_col], y=fan_df["p50"], name="P50 Forecast",
        line=dict(color=COLORS["primary"], width=2)))
        
    actuals = fan_df.dropna(subset=["actual"])
    if not actuals.empty:
        fan_fig.add_trace(go.Scatter(x=actuals[x_col], y=actuals["actual"], name="Actual",
            mode="lines+markers", line=dict(color=COLORS["success"], width=2), marker=dict(size=5)))
            
    apply_dark_layout(fan_fig, title="Forecast Fan Chart (P10/P50/P90 vs Actual)", height=280,
                      legend=dict(**LEGEND_STYLE, orientation="h", y=1.1))

    # FVA waterfall
    fva_colors = [COLORS["danger"], COLORS["success"], COLORS["success"], COLORS["warning"], COLORS["primary"]]
    # data_loader returns columns "step" and "value"
    x_col = "stage" if "stage" in fva_df.columns else "step"
    y_col = "wape"  if "wape"  in fva_df.columns else "value"
    fva_fig = go.Figure(go.Bar(
        x=fva_df[x_col], y=fva_df[y_col], marker_color=fva_colors,
        text=[f"{v:.1f}" for v in fva_df[y_col]], textposition="outside",
        textfont=dict(color=COLORS["text_primary"])))
    apply_dark_layout(fva_fig, title="Forecast Value Added (FVA) Waterfall — WAPE %",
                      height=260, showlegend=False,
                      yaxis=dict(title="WAPE %", gridcolor=COLORS["border"]))

    # Bias gauge
    bias_val = kpis.get("bias", {}).get("value", 2.3)
    bias_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=bias_val,
        title={"text": "Forecast Bias (%)", "font": {"color": COLORS["text_secondary"], "size": 12}},
        number={"suffix": "%", "font": {"color": COLORS["success"] if abs(bias_val) < 5 else COLORS["warning"], "size": 28}},
        delta={"reference": 0, "suffix": "pp", "font": {"size": 13}},
        gauge={"axis": {"range": [-10, 10], "tickcolor": COLORS["text_secondary"],
                        "tickfont": {"color": COLORS["text_secondary"]}},
               "bar": {"color": COLORS["success"] if abs(bias_val) < 5 else COLORS["warning"]},
               "steps": [{"range": [-10, -5], "color": "rgba(218,54,51,0.33)"},
                         {"range": [-5, 5],   "color": "rgba(63,185,80,0.2)"},
                         {"range": [5, 10],   "color": "rgba(218,54,51,0.33)"}],
               "threshold": {"line": {"color": COLORS["warning"], "width": 2}, "value": 5},
               "bgcolor": COLORS["surface"], "bordercolor": COLORS["border"]},
    ))
    apply_dark_layout(bias_fig, height=220, margin=dict(l=10, r=10, t=50, b=10))

    return html.Div([
        html.H5("Forecast Analytics", style={"color": COLORS["text_primary"], "fontWeight": "700", "marginBottom": "4px"}),
        html.Div(f"Accuracy KPIs • Forecast fan chart • FVA waterfall • Bias gauge — {horizon} Horizon",
                 style={"color": COLORS["text_secondary"], "fontSize": "0.83rem", "marginBottom": "20px"}),
        kpi_row(formatted_kpis, cols=5),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fan_fig,  config={"displayModeBar": False}), md=8, className="mb-3"),
            dbc.Col(dcc.Graph(figure=bias_fig, config={"displayModeBar": False}), md=4, className="mb-3"),
        ]),
        dbc.Row([dbc.Col(dcc.Graph(figure=fva_fig, config={"displayModeBar": False}), className="mb-3")]),
    ])
