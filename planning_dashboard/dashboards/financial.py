"""dashboards/financial.py  ─  Dashboard 6: Financial Impact"""
from dash import html, dcc
from components.theme import COLORS
from components.kpi_cards import kpi_card
from components import charts
from data.mock_data import (
    get_financial_kpis, get_pl_bridge_waterfall, get_budget_vs_forecast,
)

FIN_CONFIG = [
    ("revenue",        "Total Revenue",    "$M",  False, [128+i*0.3 for i in range(14)]),
    ("gross_margin",   "Gross Margin",     "%",   False, [33+i*0.05 for i in range(14)]),
    ("inventory_cost", "Inventory Cost",   "$M",  True,  [4.4-i*0.01 for i in range(14)]),
    ("logistics_cost", "Logistics Cost",   "$M",  True,  [8.9-i*0.02 for i in range(14)]),
    ("expediting_cost","Expediting Cost",  "$M",  True,  [1.2-i*0.02 for i in range(14)]),
]


def layout() -> html.Div:
    fin     = get_financial_kpis()
    bridge  = get_pl_bridge_waterfall()
    bvf_df  = get_budget_vs_forecast()

    kpi_row = [
        kpi_card(
            label=label, value=fin[k]["value"], unit=unit,
            target=fin[k]["target"], delta=fin[k]["delta"],
            sparkline_data=spark, status="success", delta_invert=invert,
        )
        for k, label, unit, invert, spark in FIN_CONFIG
    ]

    # Scenario P&L impact table
    scenario_pl = [
        {"scenario": "Base Plan",          "revenue": 128.4, "margin": 34.2, "inv_cost": 4.2, "log_cost": 8.7},
        {"scenario": "Demand Surge +30%",  "revenue": 142.1, "margin": 31.8, "inv_cost": 5.8, "log_cost": 10.2},
        {"scenario": "Supply Disruption",  "revenue": 119.3, "margin": 28.4, "inv_cost": 5.1, "log_cost": 11.5},
        {"scenario": "Best Case",          "revenue": 133.6, "margin": 36.1, "inv_cost": 3.9, "log_cost": 8.1},
        {"scenario": "Sustainability Opt.","revenue": 129.2, "margin": 33.8, "inv_cost": 4.3, "log_cost": 8.5},
    ]

    return html.Div([
        html.Div(className="page-title", children=[
            html.Span("💰", className="icon"), "Financial Impact",
        ]),
        html.Div(className="grid-kpi", style={"gridTemplateColumns": "repeat(5, 1fr)"},
                 children=kpi_row),

        html.Div(className="grid-2", style={"marginBottom": "16px"}, children=[
            html.Div(className="card", children=[
                dcc.Graph(figure=charts.pl_bridge_waterfall(bridge),
                          config={"displayModeBar": False}, style={"height": "300px"}),
            ]),
            html.Div(className="card", children=[
                dcc.Graph(figure=charts.budget_vs_forecast_chart(bvf_df),
                          config={"displayModeBar": False}, style={"height": "280px"}),
            ]),
        ]),

        # Scenario P&L table
        html.Div(className="card", children=[
            html.Div("SCENARIO P&L COMPARISON ($M)", className="section-header"),
            html.Table(className="scenario-table", style={"width": "100%"}, children=[
                html.Thead(html.Tr([
                    html.Th(h) for h in
                    ["Scenario", "Revenue", "Gross Margin %", "Inventory Cost", "Logistics Cost"]
                ])),
                html.Tbody([
                    html.Tr(
                        className="active-row" if s["scenario"] == "Base Plan" else "",
                        children=[
                            html.Td(s["scenario"]),
                            html.Td(f"${s['revenue']:.1f}M",
                                    style={"color": COLORS["chart_2"] if s["revenue"] >= 128.4
                                           else COLORS["danger"]}),
                            html.Td(f"{s['margin']:.1f}%",
                                    style={"color": COLORS["success"] if s["margin"] >= 34.2
                                           else COLORS["warning"]}),
                            html.Td(f"${s['inv_cost']:.1f}M",
                                    style={"color": COLORS["success"] if s["inv_cost"] <= 4.2
                                           else COLORS["danger"]}),
                            html.Td(f"${s['log_cost']:.1f}M",
                                    style={"color": COLORS["success"] if s["log_cost"] <= 8.7
                                           else COLORS["danger"]}),
                        ]
                    )
                    for s in scenario_pl
                ]),
            ]),
        ]),
    ])
