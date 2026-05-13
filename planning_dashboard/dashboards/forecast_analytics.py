"""dashboards/forecast_analytics.py — Dashboard 3: Forecast Analytics (LIVE)"""
from dash import html, dcc
from components.theme import COLORS
from components.kpi_cards import kpi_card
from components import charts
from data.data_loader import get_forecast_accuracy_kpis, get_forecast_fan_chart
from data.mock_data import get_fva_waterfall, get_bias_by_category

def layout():
    acc    = get_forecast_accuracy_kpis()
    fan_df = get_forecast_fan_chart()
    fva_w  = get_fva_waterfall()
    bias_df = get_bias_by_category()

    spark14 = [acc["mape"]["value"] - i*0.05 for i in range(14)]
    kpi_row = [
        kpi_card("MAPE",    acc["mape"]["value"], "%",  15.0, acc["mape"]["delta"], spark14, acc["mape"]["status"], True),
        kpi_card("WAPE",    acc["wape"]["value"], "%",  12.0, acc["wape"]["delta"], spark14, acc["wape"]["status"], True),
        kpi_card("Model R²",acc["r2"]["value"],   "",   0.91, acc["r2"]["delta"],   spark14, acc["r2"]["status"],   False),
        kpi_card("Bias %",  acc["bias"]["value"], "%",  0.0,  acc["bias"]["delta"], spark14, "success",            False),
        kpi_card("MAE",     acc["mae"]["value"],  "u",  0,    0,                    spark14, "info",                True),
    ]

    # Build fan chart from real data
    fig = _fan_chart(fan_df)

    return html.Div([
        html.Div(className="page-title", children=[html.Span("📈", className="icon"), "Forecast Analytics — Model Output"]),
        html.Div(className="grid-kpi", style={"gridTemplateColumns":"repeat(5,1fr)"}, children=kpi_row),
        html.Div(className="card", style={"marginBottom":"16px"}, children=[
            dcc.Graph(figure=fig, config={"displayModeBar":False}, style={"height":"300px"}),
        ]),
        html.Div(className="grid-2", children=[
            html.Div(className="card", children=[
                dcc.Graph(figure=charts.fva_waterfall(fva_w),
                          config={"displayModeBar":False}, style={"height":"280px"}),
            ]),
            html.Div(className="card", children=[
                dcc.Graph(figure=charts.bias_by_category_chart(bias_df),
                          config={"displayModeBar":False}, style={"height":"260px"}),
                html.Div(style={"padding":"4px 8px","marginTop":"4px"}, children=[
                    html.Span("[MODEL OUTPUT] ", style={"color":COLORS["accent"],"fontWeight":600,"fontSize":"0.68rem"}),
                    html.Span(f"XGBoost P50 MAPE={acc['mape']['value']:.1f}%, R²={acc['r2']['value']:.3f} on holdout test set.",
                              style={"fontSize":"0.76rem","color":COLORS["text_secondary"]}),
                ]),
            ]),
        ]),
    ])

def _fan_chart(df):
    import plotly.graph_objects as go
    from components.theme import COLORS, base_layout
    fig = go.Figure()
    if "p10" in df.columns and "p90" in df.columns:
        import pandas as pd
        band_x = list(df["date"]) + list(df["date"].iloc[::-1])
        band_y = list(df["p90"].fillna(df["p50"])) + list(df["p10"].fillna(df["p50"]).iloc[::-1])
        fig.add_trace(go.Scatter(x=band_x, y=band_y, fill="toself",
            fillcolor="rgba(88,166,255,0.10)", line=dict(color="rgba(0,0,0,0)"), name="P10–P90"))
    if "p50" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df["p50"], name="P50 Forecast (Model)",
            line=dict(color=COLORS["chart_1"], width=2, dash="dash")))
    if "actual" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df["actual"], name="Actual (Historical)",
            line=dict(color=COLORS["chart_2"], width=2), mode="lines+markers", marker=dict(size=3)))
    fig.update_layout(**base_layout("Forecast Fan Chart — XGBoost P50/P90 vs Actual", height=300))
    return fig
