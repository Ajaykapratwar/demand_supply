"""dashboards/risk.py — Dashboard 7: Risk Monitoring (LIVE + FIXED)"""
import numpy as np
import pandas as pd
from dash import html, dcc, Input, Output, callback
from components.theme import COLORS
from components.charts import risk_score_gauge, risk_probability_impact_matrix, _rgba
from data.data_loader import get_supplier_risk

RISK_COLORS = {
    "low":      COLORS["success"],
    "medium":   COLORS["warning"],
    "high":     COLORS["danger"],
    "critical": "#ff3333",
}

# ── Static risk event data (augments real supplier risk) ─────────────────────
RISK_EVENTS = pd.DataFrame([
    {"risk": "Supplier Concentration", "probability": 0.70, "impact": 0.90, "category": "Supply"},
    {"risk": "Port Disruption",        "probability": 0.40, "impact": 0.80, "category": "Logistics"},
    {"risk": "Demand Spike +40%",      "probability": 0.50, "impact": 0.60, "category": "Demand"},
    {"risk": "Currency Volatility",    "probability": 0.60, "impact": 0.40, "category": "Financial"},
    {"risk": "Regulatory Change",      "probability": 0.30, "impact": 0.70, "category": "Compliance"},
    {"risk": "Quality Defect Rate",    "probability": 0.25, "impact": 0.50, "category": "Quality"},
    {"risk": "IT System Failure",      "probability": 0.20, "impact": 0.80, "category": "Operational"},
])

MITIGATIONS = [
    {"risk": "Supplier Concentration", "action": "Dual-source affected SKUs",         "owner": "Procurement", "status": "In Progress"},
    {"risk": "Port Disruption",        "action": "Pre-position 15 DOS buffer at DC",  "owner": "Logistics",   "status": "Planned"},
    {"risk": "Demand Spike",           "action": "Activate flex capacity contract",   "owner": "Operations",  "status": "Approved"},
]


def layout(regions=None, categories=None):
    suppliers = get_supplier_risk()

    # Apply region filter if set
    if regions:
        suppliers = suppliers[suppliers["supplier"].isin(regions)]
    if suppliers.empty:
        suppliers = get_supplier_risk()  # fallback to all

    top4 = suppliers.nlargest(min(4, len(suppliers)), "risk_score")
    composite = round(suppliers["risk_score"].mean(), 3)
    high_risk_count = int((suppliers["risk_score"] > 0.5).sum())

    return html.Div([
        html.Div(className="page-title", children=[
            html.Span("🛡️", className="icon"), "Risk Monitoring — Live Supplier Scorecard",
        ]),

        # Summary KPI strip
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(4,1fr)",
                        "gap": "12px", "marginBottom": "16px"}, children=[
            _kpi_pill("Composite Risk Score", f"{composite:.3f}",
                      COLORS["danger"] if composite > 0.5 else COLORS["warning"]),
            _kpi_pill("High-Risk Regions", str(high_risk_count),
                      COLORS["danger"] if high_risk_count > 1 else COLORS["success"]),
            _kpi_pill("Regions Monitored", str(len(suppliers)), COLORS["primary"]),
            _kpi_pill("Mitigation Actions", "3 Active", COLORS["chart_2"]),
        ]),

        # Supplier gauges
        html.Div(style={"display": "grid",
                        "gridTemplateColumns": f"repeat({max(1,len(top4))},1fr)",
                        "gap": "12px", "marginBottom": "16px"},
                 children=[
            html.Div(className="card", style={"padding": "8px"}, children=[
                dcc.Graph(
                    figure=risk_score_gauge(float(row["risk_score"]), str(row["supplier"])),
                    config={"displayModeBar": False},
                    style={"height": "160px"},
                ),
            ]) for _, row in top4.iterrows()
        ]),

        # Matrix + table
        html.Div(className="grid-2", style={"marginBottom": "16px"}, children=[
            html.Div(className="card", children=[
                dcc.Graph(
                    figure=risk_probability_impact_matrix(RISK_EVENTS),
                    config={"displayModeBar": False},
                    style={"height": "320px"},
                ),
            ]),
            html.Div(className="card", children=[
                html.Div("REGION RISK SCORECARD — LIVE", className="section-header"),
                html.Div(style={"overflowX": "auto"}, children=[
                    html.Table(style={"width": "100%", "borderCollapse": "collapse"}, children=[
                        html.Thead(html.Tr([
                            html.Th(h, style={
                                "padding": "8px 10px", "fontSize": "0.7rem",
                                "textTransform": "uppercase", "color": COLORS["text_secondary"],
                                "textAlign": "left", "borderBottom": f"1px solid {COLORS['border']}",
                                "whiteSpace": "nowrap",
                            }) for h in ["Region", "Risk Score", "Fill Rate", "Backorder %", "Category"]
                        ])),
                        html.Tbody([_risk_table_row(row) for _, row in suppliers.iterrows()]),
                    ]),
                ]),
            ]),
        ]),

        # Mitigations
        html.Div(className="card", children=[
            html.Div("MITIGATION ACTIONS", className="section-header"),
            *[_mitigation_row(m) for m in MITIGATIONS],
        ]),

        # Risk trend chart
        html.Div(className="card", style={"marginTop": "16px"}, children=[
            dcc.Graph(
                id="risk-trend-chart",
                figure=_risk_trend_fig(suppliers),
                config={"displayModeBar": False},
                style={"height": "240px"},
            ),
        ]),
    ])


def _kpi_pill(label, value, color):
    return html.Div(style={
        "background": COLORS["card"], "border": f"1px solid {COLORS['border']}",
        "borderRadius": "10px", "padding": "14px 16px",
    }, children=[
        html.Div(label, style={"fontSize": "0.7rem", "color": COLORS["text_secondary"],
                               "textTransform": "uppercase", "marginBottom": "4px"}),
        html.Div(value, style={"fontSize": "1.4rem", "fontWeight": 700, "color": color,
                               "fontFamily": "JetBrains Mono, monospace"}),
    ])


def _risk_table_row(row):
    cat   = str(row.get("risk_category", "low"))
    color = RISK_COLORS.get(cat, COLORS["text_secondary"])
    fill  = row.get("fill_rate", 0)
    bk    = row.get("backorder_pct", 0)
    score = float(row.get("risk_score", 0))
    return html.Tr(style={"borderBottom": f"1px solid {COLORS['border']}55"}, children=[
        html.Td(str(row["supplier"]),  style={"padding": "8px 10px", "fontSize": "0.82rem", "fontWeight": 500}),
        html.Td(f"{score:.3f}",        style={"padding": "8px", "fontFamily": "JetBrains Mono,monospace",
                                              "fontWeight": 700, "color": color}),
        html.Td(f"{fill:.2%}",         style={"padding": "8px", "fontSize": "0.82rem"}),
        html.Td(f"{bk:.2%}",           style={"padding": "8px", "fontSize": "0.82rem"}),
        html.Td(html.Span(cat.upper(), style={
            "background": color + "22", "color": color, "padding": "2px 8px",
            "borderRadius": "4px", "fontSize": "0.68rem", "fontWeight": 700,
        }), style={"padding": "8px"}),
    ])


def _mitigation_row(m):
    sc = {"In Progress": COLORS["warning"], "Planned": COLORS["primary"], "Approved": COLORS["success"]}
    color = sc.get(m["status"], COLORS["text_secondary"])
    return html.Div(style={
        "display": "grid", "gridTemplateColumns": "2fr 3fr 1fr 1fr",
        "gap": "12px", "padding": "10px 0", "borderBottom": f"1px solid {COLORS['border']}",
        "alignItems": "center",
    }, children=[
        html.Span(m["risk"],   style={"fontSize": "0.82rem", "color": COLORS["text_primary"], "fontWeight": 500}),
        html.Span(m["action"], style={"fontSize": "0.79rem", "color": COLORS["text_secondary"]}),
        html.Span(m["owner"],  style={"fontSize": "0.76rem", "color": COLORS["text_secondary"]}),
        html.Span(m["status"], style={
            "background": color + "22", "color": color, "padding": "2px 8px",
            "borderRadius": "4px", "fontSize": "0.7rem", "fontWeight": 600, "textAlign": "center",
        }),
    ])


def _risk_trend_fig(suppliers):
    import plotly.graph_objects as go
    from components.theme import base_layout
    import numpy as np

    fig = go.Figure()
    weeks = list(range(1, 13))
    for _, row in suppliers.iterrows():
        base = float(row["risk_score"])
        trend = np.clip(base + np.random.default_rng(abs(hash(str(row["supplier"]))) % 2**32).normal(0, 0.05, 12), 0, 1)
        color = RISK_COLORS.get(str(row.get("risk_category","low")), COLORS["text_secondary"])
        fig.add_trace(go.Scatter(
            x=weeks, y=trend.tolist(),
            name=str(row["supplier"]),
            line=dict(color=color, width=2),
            mode="lines",
        ))
    fig.add_hline(y=0.7, line_dash="dash", line_color=COLORS["danger"],   line_width=1,
                  annotation_text="Critical 0.7", annotation_font_color=COLORS["danger"])
    fig.add_hline(y=0.4, line_dash="dash", line_color=COLORS["warning"],  line_width=1,
                  annotation_text="High 0.4", annotation_font_color=COLORS["warning"])
    fig.update_layout(**base_layout("Risk Score Trend — 12 Weeks", height=240))
    return fig
