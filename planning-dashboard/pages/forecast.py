"""pages/forecast.py — Dashboard 3: Forecast Analytics"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page, callback, Input, Output
import pandas as pd
import numpy as np

from components.kpi_card import kpi_row
from components.charts import fan_chart, quantile_dot_plot
from components.explainability import shap_waterfall_chart
from components.copilot import narrative_card
from config import COLORS, LEGEND_STYLE, apply_dark_layout, hex_to_rgba, ALERT_THRESHOLDS
from data.data_loader import (
    get_forecast_accuracy_kpis, get_forecast_fan_chart, get_fva_waterfall,
    get_forecast_quantiles,
)

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
    quantiles = get_forecast_quantiles(region=region, category=category)

    thr = ALERT_THRESHOLDS["forecast"]

    # Coverage % KPI (placeholder: P90-P10 coverage using ratio of range vs median)
    p50_mean = sum(quantiles["p50"]) / len(quantiles["p50"])
    p90_mean = sum(quantiles["p90"]) / len(quantiles["p90"])
    coverage_pct = round((p90_mean - p50_mean) / max(p50_mean, 1) * 100 + 78, 1)
    kpis["coverage"] = {
        "value": coverage_pct, "target": 80.0, "delta": round(coverage_pct - 80.0, 1),
        "unit": "%", "status": "warning" if not (thr["coverage_low"] <= coverage_pct <= thr["coverage_high"]) else "success",
        "ai_generated": True,
    }
    calibration_warn = not (thr["coverage_low"] <= coverage_pct <= thr["coverage_high"])

    # Format KPIs for kpi_row
    kpi_labels = {
        "mape": "MAPE", "wape": "WAPE", "r2": "Model R²", "bias": "Bias",
        "mae": "MAE", "coverage": "Coverage %",
    }
    formatted_kpis = {kpi_labels.get(k, k): v for k, v in kpis.items()}

    # §16.3 New fan chart from quantiles
    new_fan_fig = fan_chart(
        dates=quantiles["dates"], p10=quantiles["p10"], p25=quantiles["p25"],
        p50=quantiles["p50"], p75=quantiles["p75"], p90=quantiles["p90"],
        actuals=quantiles["actuals"],
        title="Forecast Uncertainty Fan Chart (P10/P25/P50/P75/P90)",
    )

    # FVA waterfall
    fva_colors = [COLORS["danger"], COLORS["success"], COLORS["success"], COLORS["warning"], COLORS["primary"]]
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

    # §16.4 Calibration warning banner
    calib_banner = html.Div(
        [f"⚠ Coverage {coverage_pct:.1f}% is outside [{thr['coverage_low']:.0f}%–{thr['coverage_high']:.0f}%] target — conformal recalibration recommended."],
        style={
            "backgroundColor": f"{COLORS['warning']}18",
            "border": f"1px solid {COLORS['warning']}66",
            "borderLeft": f"3px solid {COLORS['warning']}",
            "borderRadius": "6px", "padding": "8px 14px",
            "color": COLORS["warning"], "fontSize": "0.82rem",
            "marginBottom": "12px",
        }
    ) if calibration_warn else html.Div()

    # §14.1 Narrative
    wape_val = kpis.get("wape", {}).get("value", 0)
    narrative = (
        f"Portfolio **WAPE {wape_val:.1f}%** (target 12%). "
        f"FVA positive for 82% of SKUs this month. "
        f"Coverage at **{coverage_pct:.1f}%** "
        f"({'⚠ recalibrate' if calibration_warn else '✓ within target range'})."
    )

    # Generate SHAP Explanation for Forecast Error (Mock Data)
    shap_features = [
        {"name": "Weather (Cold Snap)", "impact": 1.2},
        {"name": "Promo (Black Friday)", "impact": 2.5},
        {"name": "Lead Time Variablity", "impact": 0.8},
        {"name": "Base Noise", "impact": -0.5}
    ]
    base_wape = 8.0
    final_wape = base_wape + sum(f["impact"] for f in shap_features)
    explain_fig = shap_waterfall_chart(base_value=base_wape, features=shap_features, final_value=final_wape, title="Explainable AI (SHAP): WAPE Drivers")

    return html.Div([
        html.H5("Forecast Analytics", style={"color": COLORS["text_primary"], "fontWeight": "700", "marginBottom": "4px"}),
        html.Div(f"Accuracy KPIs • Fan chart • FVA waterfall • Bias gauge — {horizon} Horizon",
                 style={"color": COLORS["text_secondary"], "fontSize": "0.83rem", "marginBottom": "16px"}),
        narrative_card(narrative, dashboard_id="forecast"),
        calib_banner,
        kpi_row(formatted_kpis, cols=6),
        # §16.3 Fan chart
        dbc.Row([
            dbc.Col(dcc.Graph(figure=new_fan_fig, config={"displayModeBar": False}), md=8, className="mb-3"),
            dbc.Col(dcc.Graph(figure=bias_fig,    config={"displayModeBar": False}), md=4, className="mb-3"),
        ]),
        dbc.Row([dbc.Col(dcc.Graph(figure=fva_fig, config={"displayModeBar": False}), className="mb-3")]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=quantile_dot_plot(outcomes=np.random.normal(loc=quantiles["p50"][-1] if len(quantiles["p50"]) > 0 else 100, scale=(quantiles["p90"][-1] - quantiles["p10"][-1]) / 3.29 if len(quantiles["p90"]) > 0 else 15, size=100).tolist(), title="Next Period Quantile Dot Plot"), config={"displayModeBar": False}), md=6, className="mb-3"),
            dbc.Col(explain_fig, md=6, className="mb-3")
        ]),
    ])

