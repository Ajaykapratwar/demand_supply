"""dashboards/inventory.py  ─  Dashboard 4: Inventory Optimization"""
from dash import html, dcc, Input, Output, callback
from components.theme import COLORS
from components import charts
from data.mock_data import (
    get_inventory_geo_data, get_service_vs_inventory_scatter, get_safety_stock_simulation,
)


def layout() -> html.Div:
    geo_df     = get_inventory_geo_data()
    scatter_df = get_service_vs_inventory_scatter()
    sim        = get_safety_stock_simulation(0.95)

    return html.Div([
        html.Div(className="page-title", children=[
            html.Span("📦", className="icon"), "Inventory Optimization",
        ]),

        # Geo map
        html.Div(className="card", style={"marginBottom": "16px"}, children=[
            dcc.Graph(figure=charts.inventory_geo_scatter(geo_df),
                      config={"displayModeBar": False}, style={"height": "320px"}),
        ]),

        html.Div(className="grid-2", children=[
            # Scatter: service level vs safety stock
            html.Div(className="card", children=[
                dcc.Graph(figure=charts.service_vs_inventory_scatter(scatter_df),
                          config={"displayModeBar": False}, style={"height": "300px"}),
            ]),

            # What-if simulator
            html.Div(className="card", children=[
                html.Div("SAFETY STOCK SIMULATOR (WHAT-IF)", className="section-header"),
                html.Div(style={"marginBottom": "12px"}, children=[
                    html.Label("Target Service Level",
                               style={"fontSize": "0.78rem", "color": COLORS["text_secondary"],
                                      "marginBottom": "6px", "display": "block"}),
                    dcc.Slider(
                        id="sl-service-level",
                        min=85, max=99, step=0.5, value=95,
                        marks={85: "85%", 90: "90%", 95: "95%", 99: "99%"},
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                ]),
                html.Div(id="sim-output", children=_sim_cards(sim)),
            ]),
        ]),
    ])


def _sim_cards(sim: dict) -> list:
    rows = [
        ("Service Level",     f"{sim['service_level']:.1f}%", COLORS["primary"]),
        ("Safety Stock",      f"{sim['safety_stock']:,.0f} units", COLORS["chart_2"]),
        ("Reorder Point",     f"{sim['reorder_point']:,.0f} units", COLORS["chart_1"]),
        ("Working Capital",   f"${sim['working_capital_usd']:,.0f}", COLORS["chart_3"]),
        ("Stockout Risk",     f"{sim['stockout_prob']:.2f}%", COLORS["danger"]),
    ]
    return [
        html.Div(style={
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "center", "padding": "10px 0",
            "borderBottom": f"1px solid {COLORS['border']}",
        }, children=[
            html.Span(label, style={"fontSize": "0.8rem",
                                    "color": COLORS["text_secondary"]}),
            html.Span(value, style={"fontSize": "0.92rem", "fontWeight": 700,
                                    "fontFamily": "JetBrains Mono, monospace",
                                    "color": color}),
        ])
        for label, value, color in rows
    ]


@callback(
    Output("sim-output", "children"),
    Input("sl-service-level", "value"),
)
def update_sim(service_level: float) -> list:
    sim = get_safety_stock_simulation(service_level / 100)
    return _sim_cards(sim)
