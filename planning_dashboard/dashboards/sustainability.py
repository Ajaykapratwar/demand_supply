"""dashboards/sustainability.py — Dashboard 8: Sustainability (LIVE CO2 DATA)"""
from dash import html, dcc
from components.theme import COLORS
from components.kpi_cards import kpi_card
from components import charts
from data.data_loader import get_sustainability_summary, get_co2_trend
from data.mock_data import get_pareto_scatter

def layout():
    sus   = get_sustainability_summary()
    trend = get_co2_trend()
    prt   = get_pareto_scatter()

    total = sus["total_tco2"]
    by_mode = sus["by_mode"]

    breakdown = [{"source": r["source"], "tco2e": r["tco2e"]} for _, r in by_mode.iterrows()]
    sbti_pct = 62

    spark = [total * (1 - i*0.003) for i in range(14)]
    kpi_row = [
        kpi_card("Total CO2",   total,  "tCO2", total*0.9, -(total*0.1), spark, "warning", True),
        kpi_card("Renewable %", 34.0,   "%",    50.0,       -16.0,        spark, "warning", False),
        kpi_card("SBTi Prog.", sbti_pct,"%",   100.0,      -38.0,        spark, "warning", False),
    ]

    return html.Div([
        html.Div(className="page-title", children=[html.Span("🌱","icon"), "Sustainability — Live Logistics CO2"]),
        html.Div(style={"background":COLORS["card"],"border":f"1px solid {COLORS['chart_2']}44",
                        "borderRadius":"10px","padding":"12px 16px","marginBottom":"16px"}, children=[
            html.Div(style={"display":"flex","justifyContent":"space-between","marginBottom":"8px"}, children=[
                html.Span("SBTi Progress — 1.5°C Aligned Target",
                          style={"fontSize":"0.82rem","fontWeight":600,"color":COLORS["text_primary"]}),
                html.Span(f"{sbti_pct}% toward 2030 target",
                          style={"fontSize":"0.8rem","color":COLORS["chart_2"],"fontWeight":600}),
            ]),
            html.Div(style={"height":"8px","borderRadius":"4px","background":COLORS["border"],"overflow":"hidden"}, children=[
                html.Div(style={"width":f"{sbti_pct}%","height":"100%",
                                "background":f"linear-gradient(90deg,{COLORS['chart_2']},{COLORS['primary']})",
                                "borderRadius":"4px"}),
            ]),
        ]),
        html.Div(className="grid-kpi", style={"gridTemplateColumns":"repeat(3,1fr)"}, children=kpi_row),
        html.Div(className="grid-2", style={"marginBottom":"16px"}, children=[
            html.Div(className="card", children=[
                dcc.Graph(figure=charts.emissions_donut(breakdown),
                          config={"displayModeBar":False}, style={"height":"300px"}),
            ]),
            html.Div(className="card", children=[
                dcc.Graph(figure=_trend_chart(trend),
                          config={"displayModeBar":False}, style={"height":"300px"}),
            ]),
        ]),
        html.Div(className="card", children=[
            dcc.Graph(figure=charts.pareto_cost_carbon(prt),
                      config={"displayModeBar":False}, style={"height":"320px"}),
        ]),
    ])

def _trend_chart(df):
    import plotly.graph_objects as go
    from components.theme import COLORS, base_layout
    fig = go.Figure(go.Scatter(
        x=df["date"], y=df["tco2"], name="CO2 Emissions",
        line=dict(color=COLORS["chart_2"], width=2),
        fill="tozeroy", fillcolor="rgba(63,185,80,0.10)",
    ))
    fig.update_layout(**base_layout("Weekly CO2 Emissions (tCO2) — Logistics", height=300))
    return fig
