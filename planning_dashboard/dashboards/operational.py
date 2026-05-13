"""dashboards/operational.py — Dashboard 2: Operational Planning (LIVE DATA)"""
from dash import html, dcc
from components.theme import COLORS
from components import charts
from data.data_loader import get_supply_demand_balance, get_inventory_dos_gauges, get_action_queue

PRIORITY_COLORS = {"CRITICAL": COLORS["danger"], "HIGH": COLORS["warning"], "MEDIUM": COLORS["primary"]}

def layout():
    sd_df  = get_supply_demand_balance()
    gauges = get_inventory_dos_gauges()
    queue  = get_action_queue()

    gauge_graphs = [
        html.Div(className="card", style={"padding":"8px"}, children=[
            dcc.Graph(figure=charts.inventory_dos_gauge(g["dos"], g["target"], g["region"]),
                      config={"displayModeBar":False}, style={"height":"170px"}),
        ]) for g in gauges
    ]

    action_items = []
    for item in queue:
        action_items.append(html.Div(className="action-item", children=[
            html.Div(children=[
                html.Span(item["priority"], className=f"priority-badge {item['priority']}"),
                html.Span(f" {item['sku']} · {item['region']}",
                          style={"fontSize":"0.78rem","color":COLORS["text_secondary"],"marginLeft":"6px"}),
            ]),
            html.Div(style={"flex":1}, children=[
                html.Div(item["issue"], className="action-text"),
                html.Div(f"→ {item['action']}", className="action-sub"),
            ]),
        ]))

    return html.Div([
        html.Div(className="page-title", children=[html.Span("⚙️", className="icon"), "Operational Planning — Live"]),
        html.Div(className="card", style={"marginBottom":"16px"}, children=[
            dcc.Graph(figure=charts.supply_demand_heatmap(sd_df),
                      config={"displayModeBar":False}, style={"height":"220px"}),
        ]),
        html.Div(className="card", style={"marginBottom":"16px"}, children=[
            html.Div("INVENTORY DOS BY REGION (LIVE)", className="section-header"),
            html.Div(style={"display":"grid","gridTemplateColumns":f"repeat({len(gauges)}, 1fr)","gap":"10px"},
                     children=gauge_graphs),
        ]),
        html.Div(className="card", children=[
            html.Div("ACTION QUEUE — REAL ANOMALIES", className="section-header"),
            html.Div(action_items),
        ]),
    ])
