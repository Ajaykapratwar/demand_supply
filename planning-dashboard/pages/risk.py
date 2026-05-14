"""pages/risk.py — Dashboard 7: Risk Monitoring"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page, callback, Input, Output
import pandas as pd

from components.kpi_card import kpi_row
from components.copilot import narrative_card
from components.charts import tornado_chart, supplier_network_graph
from config import COLORS, LEGEND_STYLE, apply_dark_layout
from data.data_loader import (
    get_risk_kpis, get_risk_probability_impact, get_mitigation_actions,
    get_service_kpis, get_kpi_interdependencies, get_supplier_network,
)

register_page(__name__, path="/risk", name="Risk Monitoring")

layout = html.Div([
    html.H5("Risk Monitoring", style={"color": COLORS["text_primary"], "fontWeight": "700", "marginBottom": "4px"}),
    html.Div("Composite risk score • Probability × impact matrix • Mitigation actions",
             style={"color": COLORS["text_secondary"], "fontSize": "0.83rem", "marginBottom": "20px"}),
    dcc.Loading(
        id="loading-risk",
        type="default",
        color=COLORS["primary"],
        children=html.Div(id="risk-content")
    )
])

@callback(
    Output("risk-content", "children"),
    Input("global-filter-store", "data")
)
def update_risk_page(filter_data):
    filter_data = filter_data or {}
    region   = filter_data.get("region", "Global")
    category = filter_data.get("category", "All")

    _kpis  = get_risk_kpis(region, category)
    _pi    = get_risk_probability_impact(region, category)
    _mit   = get_mitigation_actions(region, category)
    _svc   = get_service_kpis(region, category)          # §11.5
    _deps  = get_kpi_interdependencies("otif")            # §12

    # §12 interdependency chips for OTIF
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

    # §14.1 narrative
    comp_risk = _kpis["composite_risk"]["value"]
    otif_val  = _svc["otif"]["value"]
    ret_val   = _svc["returns_rate"]["value"]
    narrative = (
        f"**Composite Risk {comp_risk:.2f}** "
        f"({'🔴 HIGH — immediate action required' if comp_risk >= 0.6 else '🟡 MODERATE' if comp_risk >= 0.3 else '🟢 LOW'}). "
        f"**OTIF {otif_val:.1f}%** vs 95% target. "
        f"**Returns rate {ret_val:.2f}%** "
        f"({'⚠ above 2% threshold' if ret_val > 2 else '✓ within target'})."
    )

    _gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number", value=comp_risk,
        title={"text": "Composite Risk Score", "font": {"color": COLORS["text_secondary"], "size": 12}},
        number={"font": {"color": COLORS["danger"], "size": 32}},
        gauge={"axis": {"range": [0, 1], "tickcolor": COLORS["text_secondary"],
                        "tickfont": {"color": COLORS["text_secondary"]}},
               "bar": {"color": COLORS["danger"]},
               "steps": [{"range": [0.0, 0.3], "color": "rgba(63,185,80,0.27)"},
                         {"range": [0.3, 0.6], "color": "rgba(255,170,0,0.27)"},
                         {"range": [0.6, 1.0], "color": "rgba(218,54,51,0.27)"}],
               "threshold": {"line": {"color": "white", "width": 2}, "value": 0.5},
               "bgcolor": COLORS["surface"], "bordercolor": COLORS["border"]},
    ))
    apply_dark_layout(_gauge_fig, height=240, margin=dict(l=20, r=20, t=60, b=20))

    _cat_color = {"Supply": COLORS["danger"], "Demand": COLORS["warning"],
                  "Operational": COLORS["primary"], "External": COLORS["accent"]}
    _pi_fig = go.Figure()
    for cat, color in _cat_color.items():
        mask = _pi["category"] == cat
        _pi_fig.add_trace(go.Scatter(
            x=_pi.loc[mask, "probability"], y=_pi.loc[mask, "impact"],
            mode="markers+text", name=cat,
            text=_pi.loc[mask, "risk"], textposition="top center",
            textfont=dict(color=COLORS["text_secondary"], size=9),
            marker=dict(color=color, size=14, opacity=0.85, line=dict(color=COLORS["border"], width=1)),
        ))
    _pi_fig.add_hline(y=0.5, line_dash="dot", line_color=COLORS["border"], line_width=1)
    _pi_fig.add_vline(x=0.5, line_dash="dot", line_color=COLORS["border"], line_width=1)
    _pi_fig.add_shape(type="rect", x0=0.5, y0=0.5, x1=1.0, y1=1.0,
                       fillcolor="rgba(218,54,51,0.08)", line=dict(color=COLORS["danger"], width=1, dash="dot"))
    apply_dark_layout(_pi_fig, title="Risk Probability × Impact Matrix", height=310,
                      xaxis=dict(title="Probability", range=[0, 1], gridcolor=COLORS["border"]),
                      yaxis=dict(title="Impact", range=[0, 1.05], gridcolor=COLORS["border"]),
                      legend=dict(**LEGEND_STYLE, orientation="h", y=1.08))

    _mit_fig = go.Figure(go.Table(
        header=dict(values=list(_mit.columns), fill_color=COLORS["surface"],
                    font=dict(color=COLORS["primary"], size=11), align="left",
                    line_color=COLORS["border"], height=32),
        cells=dict(values=[_mit[c].tolist() for c in _mit.columns],
                   fill_color=[[COLORS["card"], COLORS["surface"]]*5],
                   font=dict(color=COLORS["text_primary"], size=11),
                   align="left", line_color=COLORS["border"], height=28),
    ))
    apply_dark_layout(_mit_fig, title="Mitigation Action Table", height=200, margin=dict(l=0, r=0, t=40, b=0))

    # §11.5 service KPI labels
    svc_labels = {"otif": "OTIF", "fill_rate": "Fill Rate",
                  "returns_rate": "Returns Rate", "perfect_order": "Perfect Order"}
    svc_fmt = {svc_labels.get(k, k): v for k, v in _svc.items()}

    return html.Div([
        # §14.1 AI Narrative
        narrative_card(narrative, dashboard_id="risk"),

        # §11.5 Service KPI row
        html.Div("SERVICE LEVEL KPIs", style={"fontSize": "0.72rem", "fontWeight": "700",
                 "letterSpacing": "0.08em", "color": COLORS["text_secondary"], "marginBottom": "8px"}),
        kpi_row(svc_fmt, cols=4),

        # §12 OTIF interdependency strip
        html.Div(
            [html.Span("OTIF interdependencies: ",
                       style={"fontSize": "0.72rem", "color": COLORS["text_secondary"], "marginRight": "8px"})]
            + dep_chips,
            style={"marginBottom": "16px"},
        ),

        kpi_row(_kpis, cols=4),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=_gauge_fig, config={"displayModeBar": False}), md=4, className="mb-3"),
            dbc.Col(dcc.Graph(figure=_pi_fig,    config={"displayModeBar": False}), md=8, className="mb-3"),
        ]),
        dbc.Row([dbc.Col(dcc.Graph(figure=_mit_fig, config={"displayModeBar": False}), className="mb-3")]),
        dbc.Row([dbc.Col(dcc.Graph(figure=tornado_chart(
            {
                "Supplier Default": {"downside": -15.0, "upside": 25.0},
                "Transport Delay": {"downside": -5.0, "upside": 12.0},
                "Demand Spike": {"downside": -20.0, "upside": 35.0},
                "FX Fluctuation": {"downside": -8.0, "upside": 8.0},
                "Labor Strike": {"downside": -12.0, "upside": 18.0}
            },
            title="Risk Sensitivity Analysis (EBITDA Impact %)"
        ), config={"displayModeBar": False}), className="mb-3")]),
        dbc.Row([dbc.Col(dcc.Graph(figure=supplier_network_graph(*get_supplier_network(region=region)), config={"displayModeBar": False}), className="mb-3")]),
    ])

