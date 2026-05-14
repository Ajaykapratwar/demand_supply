"""pages/executive.py — Dashboard 1: Executive Summary"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page, callback, Input, Output
import pandas as pd

from components.kpi_card import kpi_row
from components import charts
from components.copilot import narrative_card, ai_recommendation_card
from config import COLORS, apply_dark_layout, ALERT_THRESHOLDS
from data.data_loader import get_executive_kpis, get_plan_vs_actual, get_action_queue, get_scenario_comparison

register_page(__name__, path="/", name="Executive Summary")

def layout(**kwargs):
    return html.Div(id="executive-page-content")

@callback(
    Output("executive-page-content", "children"),
    Input("global-filter-store", "data"),
)
def update_executive_page(filter_data):
    filter_data = filter_data or {}
    region = filter_data.get("region", "Global")
    category = filter_data.get("category", "All")
    horizon = filter_data.get("horizon", "Tactical")

    kpis = get_executive_kpis(region=region, category=category)
    pva_df = get_plan_vs_actual(region=region, category=category)
    queue = get_action_queue(region=region, category=category)
    scenario_df = get_scenario_comparison(region=region, category=category)

    kpi_labels = {
        "otif": "OTIF", "fill_rate": "Fill Rate", "stockout_rate": "Stockout Rate",
        "mape": "Forecast MAPE", "dos": "Days of Supply", "revenue": "Revenue",
        "r2": "Model R²", "co2": "Carbon (tCO2)"
    }
    formatted_kpis = {kpi_labels.get(k, k): v for k, v in kpis.items()}

    pva_fig = charts.plan_vs_actual_chart(pva_df)
    scenario_fig = charts.scenario_radar(scenario_df)

    # Priority color map
    def _priority_color(priority):
        return {
            "CRITICAL": COLORS["danger"],
            "HIGH": COLORS["warning"],
            "MEDIUM": COLORS["primary"],
        }.get(priority, COLORS["text_secondary"])

    def _risk_badge(r):
        color = _priority_color(r["priority"])
        return html.Div([
            # Header
            html.Div([
                html.Div(style={
                    "width": "8px", "height": "8px", "borderRadius": "50%",
                    "background": color, "marginRight": "8px", "flexShrink": "0",
                    "boxShadow": f"0 0 6px {color}",
                }),
                html.Span(f"{r['sku']} — {r['region']}", style={
                    "fontWeight": "600", "fontSize": "0.82rem", "color": COLORS["text_primary"],
                    "flex": "1",
                }),
                html.Span(r["priority"], style={
                    "color": color, "fontSize": "0.62rem", "fontWeight": "700",
                    "border": f"1px solid {color}", "borderRadius": "4px",
                    "padding": "2px 7px", "letterSpacing": "0.04em",
                }),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
            html.Div(r["issue"], style={"fontSize": "0.78rem", "color": COLORS["text_secondary"], "marginBottom": "6px"}),
            html.Div(f"→ {r['action']}", style={"fontSize": "0.75rem", "color": color, "fontWeight": "500"}),
            # Progress bar
            html.Div([
                html.Div(style={
                    "height": "3px",
                    "width": "100%" if r["priority"] == "CRITICAL" else "75%" if r["priority"] == "HIGH" else "50%",
                    "background": color,
                    "borderRadius": "99px",
                }),
            ], style={"background": COLORS["border"], "borderRadius": "99px", "marginTop": "10px", "overflow": "hidden"}),
        ], style={
            "background": COLORS["card"],
            "border": f"1px solid {COLORS['border']}",
            "borderLeft": f"3px solid {color}",
            "borderRadius": "8px",
            "padding": "14px 16px",
            "transition": "all 0.18s ease",
        })

    thr = ALERT_THRESHOLDS["executive"]
    svc_status = "danger" if kpis["fill_rate"]["value"] < thr["service_level_red"] else "success"
    kpis["fill_rate"]["status"] = svc_status

    narrative_text = (
        f"**Fill Rate** at **{kpis['fill_rate']['value']:.1f}%** vs 98% target "
        f"({'✕ below' if kpis['fill_rate']['value'] < thr['service_level_red'] else '✓ on-track'} threshold). "
        f"**Stockout rate** {kpis['stockout_rate']['value']:.2f}% — review action queue below. "
        f"**Forecast R²** = {kpis['r2']['value']:.3f} (target ≥0.91). "
        f"Carbon at {kpis['co2']['value']:.0f} tCO₂."
    )

    return html.Div([
        # ── Page Header ────────────────────────────────────────
        html.Div([
            html.Div([
                html.H5("Executive Summary", style={
                    "color": COLORS["text_primary"], "fontWeight": "700",
                    "fontSize": "1.1rem", "margin": "0", "letterSpacing": "-0.01em",
                }),
                html.Div(f"Real-time cross-functional KPI overview · {horizon} Horizon", style={
                    "color": COLORS["text_secondary"], "fontSize": "0.8rem", "marginTop": "2px",
                }),
            ]),
            # Timestamp
            html.Div([
                html.I(className="bi bi-clock",
                       style={"color": COLORS["text_secondary"], "fontSize": "0.78rem", "marginRight": "5px"}),
                html.Span("Updated just now", style={"color": COLORS["text_secondary"], "fontSize": "0.78rem"}),
            ], style={"display": "flex", "alignItems": "center"}),
        ], style={
            "display": "flex", "justifyContent": "space-between", "alignItems": "center",
            "marginBottom": "20px",
        }),

        # ── AI Narrative ───────────────────────────────────────
        narrative_card(narrative_text, dashboard_id="executive"),

        # ── KPI Row ────────────────────────────────────────────
        kpi_row(formatted_kpis, cols=4),

        # ── Charts Row ─────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("Plan vs Actual", style={
                        "fontSize": "0.78rem", "fontWeight": "600",
                        "color": COLORS["text_secondary"], "letterSpacing": "0.04em",
                    }),
                ], style={"padding": "14px 16px 0", "marginBottom": "-4px"}),
                dcc.Graph(figure=pva_fig, config={"displayModeBar": False}),
            ], md=8, className="mb-3", style={
                "background": COLORS["card"], "border": f"1px solid {COLORS['border']}",
                "borderRadius": "10px", "overflow": "hidden",
                "marginRight": "0",
            }),
            dbc.Col([
                html.Div([
                    html.Span("Scenario Radar", style={
                        "fontSize": "0.78rem", "fontWeight": "600",
                        "color": COLORS["text_secondary"], "letterSpacing": "0.04em",
                    }),
                ], style={"padding": "14px 16px 0", "marginBottom": "-4px"}),
                dcc.Graph(figure=scenario_fig, config={"displayModeBar": False}),
            ], md=4, className="mb-3", style={
                "background": COLORS["card"], "border": f"1px solid {COLORS['border']}",
                "borderRadius": "10px", "overflow": "hidden",
            }),
        ], className="g-3"),

        # ── Action Queue ───────────────────────────────────────
        html.Div([
            html.Span("Action Queue", style={
                "fontSize": "0.68rem", "fontWeight": "700", "letterSpacing": "0.09em",
                "color": COLORS["text_secondary"], "textTransform": "uppercase",
            }),
            html.Span(f"{len(queue)} active", style={
                "fontSize": "0.65rem", "color": COLORS["danger"],
                "background": "rgba(239,68,68,0.1)", "border": "1px solid rgba(239,68,68,0.25)",
                "borderRadius": "99px", "padding": "2px 9px", "fontWeight": "600",
                "marginLeft": "10px",
            }),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "12px", "marginTop": "4px"}),
        dbc.Row([dbc.Col(_risk_badge(r), md=4, className="mb-3") for r in queue]),

        # ── AI Recommendations ─────────────────────────────────
        html.Div([
            html.I(className="bi bi-lightning-charge-fill",
                   style={"color": COLORS["primary"], "fontSize": "0.75rem", "marginRight": "7px"}),
            html.Span("AI Recommendations", style={
                "fontSize": "0.68rem", "fontWeight": "700", "letterSpacing": "0.09em",
                "color": COLORS["text_secondary"], "textTransform": "uppercase",
            }),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "12px", "marginTop": "8px"}),

        dbc.Row([
            dbc.Col(ai_recommendation_card(
                "Increase safety stock by 12% in North region to reduce stockout risk from 3.8% to 1.2%.",
                "+1.4 pp OTIF, -$280K stockout cost", confidence=0.82), md=4),
            dbc.Col(ai_recommendation_card(
                "Shift production from WH-East (101% loaded) to WH-West (62% loaded) — cost neutral.",
                "-14 overtime hours, +0.8 pp schedule adherence", confidence=0.76), md=4),
            dbc.Col(ai_recommendation_card(
                "Defer 3 low-margin Portable SKUs in South to free 320 capacity hours for high-margin Split units.",
                "+$180K margin, no service impact", confidence=0.71), md=4),
        ], className="g-3"),
    ])
