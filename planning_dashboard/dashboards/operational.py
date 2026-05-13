"""
dashboards/operational.py  ─  Dashboard 2: Operational Planning
Supply-demand balance heatmap, inventory DOS gauges, action queue.
"""
from dash import html, dcc
from components.theme import COLORS
from components import charts
from data.mock_data import (
    get_supply_demand_balance, get_inventory_dos_gauges, get_action_queue,
)

PRIORITY_COLORS = {
    "CRITICAL": COLORS["danger"],
    "HIGH":     COLORS["warning"],
    "MEDIUM":   COLORS["primary"],
}


def layout() -> html.Div:
    sd_df  = get_supply_demand_balance()
    gauges = get_inventory_dos_gauges()
    queue  = get_action_queue()

    gauge_graphs = [
        html.Div(className="card", style={"padding": "8px"}, children=[
            dcc.Graph(
                figure=charts.inventory_dos_gauge(g["dos"], g["target"], g["region"]),
                config={"displayModeBar": False},
                style={"height": "170px"},
            ),
        ])
        for g in gauges
    ]

    action_items = []
    for item in queue:
        color = PRIORITY_COLORS.get(item["priority"], COLORS["primary"])
        action_items.append(
            html.Div(className="action-item", children=[
                html.Div(children=[
                    html.Span(item["priority"], className=f"priority-badge {item['priority']}"),
                    html.Span(f" {item['sku']} · {item['region']}",
                              style={"fontSize": "0.78rem", "color": COLORS["text_secondary"],
                                     "marginLeft": "6px"}),
                ]),
                html.Div(style={"flex": 1}, children=[
                    html.Div(item["issue"], className="action-text"),
                    html.Div(f"→ {item['action']}", className="action-sub"),
                ]),
                html.Button("Resolve", style={
                    "background": "none",
                    "border": f"1px solid {COLORS['border']}",
                    "color": COLORS["text_secondary"],
                    "padding": "3px 10px", "borderRadius": "5px",
                    "cursor": "pointer", "fontSize": "0.74rem",
                    "fontFamily": "Inter, sans-serif",
                }),
            ])
        )

    return html.Div([
        html.Div(className="page-title", children=[
            html.Span("⚙️", className="icon"),
            "Operational Planning",
        ]),

        # Supply-demand heatmap
        html.Div(className="card", style={"marginBottom": "16px"}, children=[
            dcc.Graph(
                figure=charts.supply_demand_heatmap(sd_df),
                config={"displayModeBar": False},
                style={"height": "220px"},
            ),
        ]),

        # DOS gauges
        html.Div(className="card", style={"marginBottom": "16px"}, children=[
            html.Div("INVENTORY DAYS OF SUPPLY BY REGION", className="section-header"),
            html.Div(style={"display": "grid",
                            "gridTemplateColumns": "repeat(4, 1fr)", "gap": "10px"},
                     children=gauge_graphs),
        ]),

        # Action queue
        html.Div(className="card", children=[
            html.Div(style={"display": "flex", "justifyContent": "space-between",
                            "alignItems": "center", "marginBottom": "12px"}, children=[
                html.Div("ACTION QUEUE", className="section-header",
                         style={"margin": "0", "border": "none"}),
                html.Span(f"{len(queue)} open items",
                          style={"fontSize": "0.72rem", "color": COLORS["text_secondary"]}),
            ]),
            html.Div(action_items),
        ]),
    ])
