"""
dashboards/executive.py  ─  Dashboard 1: Executive Summary
KPI cards, plan vs actual, scenario comparison table, risk strip, AI brief.
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.theme import COLORS
from components.kpi_cards import kpi_card
from components import charts
from data.mock_data import (
    get_executive_kpis, get_kpi_sparklines,
    get_plan_vs_actual, get_scenarios,
)

KPI_CONFIG = {
    "otif":           ("OTIF",             "%",    False),
    "fill_rate":      ("Fill Rate",        "%",    False),
    "mape":           ("Forecast MAPE",    "%",    True),   # lower=better
    "stockout_rate":  ("Stockout Rate",    "%",    True),
    "dos":            ("Days of Supply",   "days", True),
    "inventory_cost": ("Inventory Cost",   "$M",   True),
    "total_revenue":  ("Total Revenue",    "$M",   False),
    "carbon_scope2":  ("Carbon Scope 2",   "tCO2", True),
}


def layout() -> html.Div:
    kpis      = get_executive_kpis()
    sparklines = get_kpi_sparklines()
    pva_df    = get_plan_vs_actual()
    scenarios = get_scenarios()

    # Build KPI card grid
    kpi_cards = []
    for key, (label, unit, invert) in KPI_CONFIG.items():
        k = kpis[key]
        kpi_cards.append(
            kpi_card(
                label=label,
                value=k["value"], unit=unit,
                target=k["target"],
                delta=k["delta"],
                sparkline_data=sparklines[key],
                status=k["status"],
                delta_invert=invert,
            )
        )

    return html.Div([
        html.Div(className="page-title", children=[
            html.Span("📊", className="icon"),
            "Executive Summary",
            html.Span("Tactical Horizon · All Regions",
                      style={"fontSize": "0.75rem", "color": COLORS["text_secondary"],
                             "fontWeight": 400, "marginLeft": "12px"}),
        ]),

        # AI Brief
        html.Div(className="ai-brief", style={"marginBottom": "16px"}, children=[
            html.Div("[AI GENERATED]", className="ai-badge"),
            html.P(
                "OTIF at 93.4% (−1.6pp vs target): driven by APAC stockout risk on SKU-0003 "
                "(7-day horizon) and EMEA supply delay from SUP-07. "
                "Top opportunity: redistribute 12K units from overstock EMEA DCs (45 DOS) "
                "to LATAM before Q3 peak, yielding est. +$180K margin recovery. "
                "Primary risk: copper price index +10% in 30d threatens landed cost for "
                "Electronics category — activate hedge or dual-source by week 3."
            ),
        ]),

        # KPI Cards
        html.Div(className="grid-kpi", children=kpi_cards),

        # Charts row
        html.Div(className="grid-2", style={"marginBottom": "16px"}, children=[
            html.Div(className="card", children=[
                dcc.Graph(
                    figure=charts.plan_vs_actual_chart(pva_df),
                    config={"displayModeBar": False},
                    style={"height": "280px"},
                ),
            ]),
            html.Div(className="card", children=[
                dcc.Graph(
                    figure=charts.scenario_radar(scenarios),
                    config={"displayModeBar": False},
                    style={"height": "300px"},
                ),
            ]),
        ]),

        # Scenario comparison table
        html.Div(className="card", style={"marginBottom": "16px"}, children=[
            html.Div("SCENARIO COMPARISON", className="section-header"),
            html.Table(className="scenario-table", children=[
                html.Thead(html.Tr([
                    html.Th("Scenario"),
                    html.Th("Cost Impact"),
                    html.Th("Service Δ"),
                    html.Th("Carbon Δ"),
                    html.Th("Inventory Δ"),
                ])),
                html.Tbody([
                    html.Tr(
                        className="active-row" if s["name"] == "Base Plan" else "",
                        children=[
                            html.Td(s["name"]),
                            html.Td(
                                f"+${s['cost_delta']:,.0f}" if s["cost_delta"] >= 0
                                else f"-${abs(s['cost_delta']):,.0f}",
                                className="val-pos" if s["cost_delta"] > 0 else
                                ("val-neg" if s["cost_delta"] < 0 else ""),
                            ),
                            html.Td(
                                f"{s['service_delta']:+.1f}%",
                                style={"color": COLORS["success"] if s["service_delta"] > 0
                                       else (COLORS["danger"] if s["service_delta"] < 0
                                             else COLORS["text_primary"])},
                            ),
                            html.Td(f"{s['carbon_delta']:+.0f} tCO2"),
                            html.Td(f"{s['inventory_delta']:+,.0f} units"),
                        ]
                    )
                    for s in scenarios
                ]),
            ]),
        ]),
    ])
