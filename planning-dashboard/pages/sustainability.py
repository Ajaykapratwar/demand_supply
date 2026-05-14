"""pages/sustainability.py — Dashboard 8: Sustainability"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page, callback, Input, Output
import pandas as pd

from components.kpi_card import kpi_row
from config import COLORS, LEGEND_STYLE, apply_dark_layout
from data.data_loader import get_sustainability_kpis, get_emissions_breakdown, get_cost_vs_carbon_pareto

register_page(__name__, path="/sustainability", name="Sustainability")

layout = html.Div([
    html.Div([
        html.Div([
            html.H5("Sustainability", style={
                "color": COLORS["text_primary"], "fontWeight": "700",
                "fontSize": "1.1rem", "margin": "0", "letterSpacing": "-0.01em",
            }),
            html.Div("Carbon KPIs · Emissions breakdown · Cost vs Carbon Pareto",
                     style={"color": COLORS["text_secondary"], "fontSize": "0.8rem", "marginTop": "2px"}),
        ]),
    ], style={"display": "flex", "justifyContent": "space-between",
              "alignItems": "center", "marginBottom": "20px"}),
    dcc.Loading(
        id="loading-sustainability",
        type="dot",
        color=COLORS["primary"],
        children=html.Div(id="sustainability-content")
    )
])

@callback(
    Output("sustainability-content", "children"),
    Input("global-filter-store", "data")
)
def update_sustainability_page(filter_data):
    filter_data = filter_data or {}
    region = filter_data.get("region", "Global")
    category = filter_data.get("category", "All")

    _kpis = get_sustainability_kpis(region, category)
    _emissions = get_emissions_breakdown(region, category)
    _pareto = get_cost_vs_carbon_pareto(region, category)

    _EMIT_COLORS = [COLORS["chart_1"], COLORS["chart_2"], COLORS["chart_3"],
                    COLORS["chart_4"], COLORS["chart_5"], COLORS["accent"]]
    _donut_fig = go.Figure(go.Pie(
        labels=_emissions["category"], values=_emissions["tco2e"], hole=0.52,
        marker=dict(colors=_EMIT_COLORS, line=dict(color=COLORS["border"], width=1)),
        textinfo="label+percent",
        textfont=dict(color=COLORS["text_primary"], size=11),
        hovertemplate="<b>%{label}</b><br>%{value:,} tCO₂e<br>%{percent}<extra></extra>",
    ))
    total_emissions = int(_emissions["tco2e"].sum()) if not _emissions.empty else 0
    _donut_fig.add_annotation(text=f"<b>{total_emissions:,}</b><br>tCO₂e", x=0.5, y=0.5, showarrow=False,
                               font=dict(color=COLORS["text_primary"], size=13))
    apply_dark_layout(_donut_fig, title="Emissions by Category (tCO₂e)", height=310,
                      showlegend=True, legend=dict(**LEGEND_STYLE, orientation="v", x=1.02))

    _pareto_fig = go.Figure(go.Scatter(
        x=_pareto["carbon"], y=_pareto["cost_usd"], mode="markers+text",
        text=_pareto["scenario"], textposition="top center",
        textfont=dict(color=COLORS["text_secondary"], size=10),
        marker=dict(color=_pareto["carbon"],
                    colorscale=[[0, COLORS["success"]], [0.5, COLORS["warning"]], [1, COLORS["danger"]]],
                    size=14, opacity=0.9, line=dict(color=COLORS["border"], width=1),
                    colorbar=dict(title="tCO₂e", tickfont=dict(color=COLORS["text_secondary"]))),
        hovertemplate="<b>%{text}</b><br>Cost: $%{y:.1f}M<br>Carbon: %{x:,} tCO₂e<extra></extra>",
    ))
    apply_dark_layout(_pareto_fig, title="Cost vs Carbon Pareto Frontier", height=310,
                      xaxis=dict(title="Carbon (tCO₂e)", gridcolor=COLORS["border"]),
                      yaxis=dict(title="Total Cost ($M)", gridcolor=COLORS["border"]),
                      showlegend=False)

    _progress_card = dbc.Card([
        dbc.CardBody([
            html.Div("SBTi TARGET PROGRESS", style={"fontSize": "0.72rem", "fontWeight": "700",
                     "letterSpacing": "0.08em", "color": COLORS["text_secondary"], "marginBottom": "12px"}),
            *[html.Div([
                html.Div([html.Span(label, style={"fontSize": "0.82rem", "color": COLORS["text_primary"]}),
                          html.Span(f"{pct}%", style={"fontSize": "0.82rem", "color": COLORS["success"],
                                                       "fontWeight": "700", "marginLeft": "auto"})],
                         style={"display": "flex", "marginBottom": "4px"}),
                dbc.Progress(value=pct, color="success" if pct > 50 else "warning",
                             style={"height": "8px", "marginBottom": "12px", "backgroundColor": COLORS["border"]}),
            ]) for label, pct in [
                ("Scope 1 Reduction", 62), ("Scope 2 Reduction (RE)", 34),
                ("Scope 3 Engagement", 48), ("SBTi 2030 Milestone", 55),
            ]],
        ]),
    ], style={"backgroundColor": COLORS["card"], "border": f"1px solid {COLORS['border']}", "borderRadius": "10px"})

    return html.Div([
        kpi_row(_kpis, cols=3),
        html.Div([
            html.Div(dcc.Graph(figure=_donut_fig,  config={"displayModeBar": False}), className="col-span-5 chart-card"),
            html.Div(dcc.Graph(figure=_pareto_fig, config={"displayModeBar": False}), className="col-span-4 chart-card"),
            html.Div(_progress_card, className="col-span-3 chart-card"),
        ], className="dashboard-grid mb-4"),
    ], className="page-wrapper")
