"""pages/financial.py — Dashboard 6: Financial Impact"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page, callback, Input, Output
import pandas as pd

from components.kpi_card import kpi_row
from components.copilot import narrative_card
from config import COLORS, LEGEND_STYLE, apply_dark_layout
from data.data_loader import (
    get_financial_summary, get_scenario_pl_bridge, get_budget_vs_forecast_real,
    get_financial_extended_kpis, get_kpi_interdependencies,
)

register_page(__name__, path="/financial", name="Financial Impact")

layout = html.Div([
    html.Div([
        html.Div([
            html.H5("Financial Impact", style={
                "color": COLORS["text_primary"], "fontWeight": "700",
                "fontSize": "1.1rem", "margin": "0", "letterSpacing": "-0.01em",
            }),
            html.Div("Revenue/margin KPIs · Scenario P&L bridge · Budget vs forecast",
                     style={"color": COLORS["text_secondary"], "fontSize": "0.8rem", "marginTop": "2px"}),
        ]),
    ], style={"display": "flex", "justifyContent": "space-between",
              "alignItems": "center", "marginBottom": "20px"}),
    dcc.Loading(
        id="loading-financial",
        type="dot",
        color=COLORS["primary"],
        children=html.Div(id="financial-content")
    )
])

@callback(
    Output("financial-content", "children"),
    Input("global-filter-store", "data")
)
def update_financial_page(filter_data):
    filter_data = filter_data or {}
    region   = filter_data.get("region", "Global")
    category = filter_data.get("category", "All")

    _kpis   = get_financial_summary(region, category)
    _bridge = get_scenario_pl_bridge(region, category)
    _bvf    = get_budget_vs_forecast_real(region, category)
    _ext    = get_financial_extended_kpis(region, category)   # §11.3
    _deps   = get_kpi_interdependencies("inventory_turns")     # §12

    # §12 interdependency chips
    dep_chips = []
    for d in _deps:
        c = COLORS["warning"] if d["type"] == "trade_off" else COLORS["success"]
        dep_chips.append(html.Span(
            f"{'⇄' if d['type'] == 'trade_off' else '↑↑'} {d['kpi']} ({d['strength']:+.2f})",
            title=d["note"],
            style={"backgroundColor": f"{c}1a", "border": f"1px solid {c}55",
                   "borderRadius": "12px", "padding": "2px 10px",
                   "fontSize": "0.72rem", "color": c,
                   "marginRight": "6px", "display": "inline-block"},
        ))

    ext_labels = {"eva": "EVA", "roic": "ROIC", "logistics_pct": "Logistics % Rev",
                  "cost_per_order": "Cost/Order", "cash_to_cash": "Cash-to-Cash", "carrying_cost": "Carrying Cost"}
    ext_fmt = {ext_labels.get(k, k): v for k, v in _ext.items()}

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
    if "actual" in _bvf.columns:
        _act = _bvf.dropna(subset=["actual"])
        _bvf_fig.add_trace(go.Scatter(x=_act["month"], y=_act["actual"], name="Actual",
                                       mode="lines+markers", line=dict(color=COLORS["success"], width=2),
                                       marker=dict(size=5)))
    apply_dark_layout(_bvf_fig, title="Budget vs Forecast vs Actual ($M)", height=280,
                      yaxis=dict(title="Revenue $M", gridcolor=COLORS["border"]),
                      legend=dict(**LEGEND_STYLE, orientation="h", y=1.08), barmode="group")

    # §14.1 narrative
    eva_val  = _ext["eva"]["value"]
    roic_val = _ext["roic"]["value"]
    log_pct  = _ext["logistics_pct"]["value"]
    narrative = (
        f"**EVA {eva_val:+.1f} $M** "
        f"({'✓ value creation' if eva_val > 0 else '✕ destroying value'}). "
        f"**ROIC {roic_val:.1f}%** vs 15% hurdle rate. "
        f"**Logistics cost {log_pct:.1f}% of revenue** "
        f"({'⚠ above 6.5% benchmark' if log_pct > 6.5 else '✓ within benchmark'})."
    )

    return html.Div([
        # §14.1 AI Narrative
        narrative_card(narrative, dashboard_id="financial"),

        # §11.3 Extended financial KPIs
        html.Div([
            html.Span("Extended Financial KPIs", style={
                "fontSize": "0.68rem", "fontWeight": "700", "letterSpacing": "0.09em",
                "color": COLORS["text_secondary"], "textTransform": "uppercase",
            }),
        ], style={"marginBottom": "10px"}),
        kpi_row(ext_fmt, cols=6),

        # §12 Interdependency strip
        html.Div(
            [html.Span("Inventory Turns trade-offs: ",
                       style={"fontSize": "0.72rem", "color": COLORS["text_secondary"], "marginRight": "8px"})]
            + dep_chips,
            style={"marginBottom": "16px"},
        ),

        # Core KPIs (revenue / margin)
        kpi_row(_kpis, cols=3),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=_bridge_fig, config={"displayModeBar": False}), md=6, className="mb-3"),
            dbc.Col(dcc.Graph(figure=_bvf_fig,    config={"displayModeBar": False}), md=6, className="mb-3"),
        ]),
    ])

