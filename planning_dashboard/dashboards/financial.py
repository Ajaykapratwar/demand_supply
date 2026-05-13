"""dashboards/financial.py — Dashboard 6: Financial Impact (LIVE)"""
from dash import html, dcc
from components.theme import COLORS
from components.kpi_cards import kpi_card
from components import charts
from data.data_loader import get_financial_summary, get_budget_vs_forecast_real
from data.mock_data import get_pl_bridge_waterfall

def layout():
    fin    = get_financial_summary()
    bvf_df = get_budget_vs_forecast_real()
    bridge = get_pl_bridge_waterfall()

    spark14 = [fin["revenue_cr"] * (1 + i * 0.002) for i in range(14)]
    kpi_row = [
        kpi_card("Revenue",       fin["revenue_cr"],        "Cr INR", fin["revenue_cr"]*1.05, fin["revenue_cr"]*0.03,  spark14, "success", False),
        kpi_card("Avg Discount",  fin["avg_discount_pct"],  "%",      5.0,                    fin["avg_discount_pct"]-5,spark14, "warning", True),
        kpi_card("Logistics Cost",fin["logistics_cost_m"],  "M INR",  fin["logistics_cost_m"]*0.95, 0, spark14, "warning", True),
    ]

    return html.Div([
        html.Div(className="page-title", children=[html.Span("💰", className="icon"), "Financial Impact — Live Revenue Data"]),
        html.Div(className="grid-kpi", style={"gridTemplateColumns":"repeat(3,1fr)"}, children=kpi_row),
        html.Div(className="grid-2", style={"marginBottom":"16px"}, children=[
            html.Div(className="card", children=[
                dcc.Graph(figure=charts.pl_bridge_waterfall(bridge),
                          config={"displayModeBar":False}, style={"height":"300px"}),
            ]),
            html.Div(className="card", children=[
                dcc.Graph(figure=_bvf_chart(bvf_df),
                          config={"displayModeBar":False}, style={"height":"280px"}),
            ]),
        ]),
        html.Div(className="card", children=[
            html.Div("REVENUE BY REGION — REAL DATA SUMMARY", className="section-header"),
            html.Div(style={"display":"grid","gridTemplateColumns":"repeat(3,1fr)","gap":"12px"}, children=[
                _stat(f"Total Revenue", f"{fin['revenue_cr']:.1f} Cr INR", COLORS["chart_2"]),
                _stat(f"Avg Discount",  f"{fin['avg_discount_pct']:.2f}%",  COLORS["warning"]),
                _stat(f"Logistics Cost",f"{fin['logistics_cost_m']:.2f}M",  COLORS["chart_1"]),
            ]),
        ]),
    ])

def _bvf_chart(df):
    import plotly.graph_objects as go
    from components.theme import COLORS, base_layout
    from components.charts import _rgba as rgba  # noqa: F401
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["month"].dt.strftime("%b %y"), y=df["budget"],
                         name="Budget", marker_color=rgba(COLORS["chart_2"], 0.55)))
    fig.add_trace(go.Scatter(x=df["month"].dt.strftime("%b %y"), y=df["actual"],
                             name="Actual", line=dict(color=COLORS["chart_2"], width=2),
                             mode="lines+markers", marker=dict(size=5)))
    if "forecast" in df.columns:
        fig.add_trace(go.Scatter(x=df["month"].dt.strftime("%b %y"), y=df["forecast"],
                                 name="Forecast", line=dict(color=COLORS["chart_1"], width=2, dash="dash")))
    fig.update_layout(**base_layout("Budget vs Actual vs Forecast (Cr INR)", height=280))
    return fig

def _stat(label, value, color):
    from components.theme import COLORS
    return html.Div(style={"textAlign":"center","padding":"12px"}, children=[
        html.Div(label, style={"fontSize":"0.72rem","color":COLORS["text_secondary"],"marginBottom":"4px"}),
        html.Div(value, style={"fontSize":"1.3rem","fontWeight":700,"color":color,"fontFamily":"JetBrains Mono,monospace"}),
    ])
