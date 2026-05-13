"""pages/executive.py — Dashboard 1: Executive Summary"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page, callback, Input, Output
import pandas as pd

from components.kpi_card import kpi_row
from components import charts
from config import COLORS, apply_dark_layout
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
    
    # Format KPIs for kpi_row
    kpi_labels = {
        "otif": "OTIF", "fill_rate": "Fill Rate", "stockout_rate": "Stockout Rate",
        "mape": "Forecast MAPE", "dos": "Days of Supply", "revenue": "Revenue",
        "r2": "Model R²", "co2": "Carbon (tCO2)"
    }
    formatted_kpis = {kpi_labels.get(k, k): v for k, v in kpis.items()}
    
    # PVA Chart & Scenario Radar
    pva_fig = charts.plan_vs_actual_chart(pva_df)
    scenario_fig = charts.scenario_radar(scenario_df)
    
    # Action Queue / Risk Strip
    def _risk_badge(r):
        color = {"CRITICAL": COLORS["danger"], "HIGH": COLORS["warning"], "MEDIUM": COLORS["primary"]}.get(r["priority"], COLORS["text_secondary"])
        return dbc.Card(dbc.CardBody([
            html.Div([
                html.Span("●", style={"color": color, "marginRight": "6px"}),
                html.Span(r["sku"] + " - " + r["region"], style={"fontWeight": "600", "fontSize": "0.82rem", "color": COLORS["text_primary"]}),
                html.Span(r["priority"], style={"color": color, "fontSize": "0.7rem", "fontWeight": "700",
                                            "border": f"1px solid {color}", "borderRadius": "4px",
                                            "padding": "1px 6px", "marginLeft": "8px"}),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "4px"}),
            html.Div(r["issue"], style={"fontSize": "0.76rem", "color": COLORS["text_secondary"]}),
            html.Div("→ " + r["action"], style={"fontSize": "0.72rem", "color": color, "marginTop": "4px"}),
            dbc.Progress(value=100 if r["priority"] == "CRITICAL" else 75 if r["priority"] == "HIGH" else 50,
                         color="danger" if r["priority"]=="CRITICAL" else "warning" if r["priority"]=="HIGH" else "primary",
                         style={"height": "4px", "marginTop": "6px", "backgroundColor": COLORS["border"]}),
        ], style={"padding": "10px 14px"}),
        style={"backgroundColor": COLORS["surface"], "border": f"1px solid {color}44", "borderRadius": "8px"})

    return html.Div([
        html.H5("Executive Summary", style={"color": COLORS["text_primary"], "fontWeight": "700", "marginBottom": "4px"}),
        html.Div(f"Real-time cross-functional KPI overview — {horizon} Horizon",
                 style={"color": COLORS["text_secondary"], "fontSize": "0.83rem", "marginBottom": "20px"}),
        
        # AI Brief
        html.Div(style={"marginBottom": "16px", "backgroundColor": COLORS["card"], "padding": "15px", "borderRadius": "8px", "border": f"1px solid {COLORS['border']}"}, children=[
            html.Div("[AI GENERATED]", style={"fontSize": "0.7rem", "color": COLORS["primary"], "fontWeight": "700", "marginBottom": "6px", "letterSpacing": "0.05em"}),
            html.P(
                f"Fill rate at {kpis['fill_rate']['value']:.1f}% vs 98% target. "
                f"Model R²={kpis['r2']['value']:.3f} on test set (target ≥0.91). "
                f"Stockout rate {kpis['stockout_rate']['value']:.2f}% — review action queue below.",
                style={"fontSize": "0.85rem", "color": COLORS["text_primary"], "margin": "0", "lineHeight": "1.5"}
            ),
        ]),

        kpi_row(formatted_kpis, cols=4),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=pva_fig, config={"displayModeBar": False}), md=8, className="mb-3"),
            dbc.Col(dcc.Graph(figure=scenario_fig, config={"displayModeBar": False}), md=4, className="mb-3"),
        ]),
        html.Div("ACTION QUEUE — LIVE ANOMALIES", style={"fontSize": "0.72rem", "fontWeight": "700",
                 "letterSpacing": "0.08em", "color": COLORS["text_secondary"], "marginBottom": "10px"}),
        dbc.Row([dbc.Col(_risk_badge(r), md=4, className="mb-2") for r in queue]),
    ])

