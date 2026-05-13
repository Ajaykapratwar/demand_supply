"""dashboards/capacity.py — Dashboard 5: Capacity Planning (LIVE)"""
import numpy as np
from dash import html, dcc
from components.theme import COLORS
from components import charts
from data.data_loader import get_capacity_utilization, get_capacity_load_profile

def layout():
    plants  = get_capacity_utilization()
    load_df = get_capacity_load_profile()

    gauge_cards = [
        html.Div(className="card", style={"padding":"8px"}, children=[
            dcc.Graph(figure=charts.capacity_gauge(p["utilization"], p["plant"], p["oee"]),
                      config={"displayModeBar":False}, style={"height":"180px"}),
        ]) for p in plants
    ]

    avg_util = sum(p["utilization"] for p in plants) / len(plants)
    critical = sum(1 for p in plants if p["utilization"] > 0.92)

    return html.Div([
        html.Div(className="page-title", children=[html.Span("🏭", className="icon"), "Capacity Planning — Warehouse Utilization (Live)"]),
        html.Div(style={"display":"flex","gap":"12px","marginBottom":"16px","flexWrap":"wrap"}, children=[
            _pill("Avg Utilization", f"{avg_util:.0%}", COLORS["primary"]),
            _pill("Regions >92%",    str(critical),     COLORS["danger"]),
            _pill("Total Regions",   str(len(plants)),  COLORS["text_secondary"]),
        ]),
        html.Div(style={"display":"grid","gridTemplateColumns":f"repeat({len(plants)},1fr)","gap":"12px","marginBottom":"16px"},
                 children=gauge_cards),
        html.Div(className="card", children=[
            dcc.Graph(figure=charts.capacity_load_profile(load_df),
                      config={"displayModeBar":False}, style={"height":"300px"}),
        ]),
    ])

def _pill(label, value, color):
    return html.Div(style={"background":COLORS["card"],"border":f"1px solid {COLORS['border']}",
                           "borderRadius":"8px","padding":"10px 16px","display":"flex","flexDirection":"column","gap":"2px"}, children=[
        html.Span(label, style={"fontSize":"0.68rem","color":COLORS["text_secondary"],"textTransform":"uppercase"}),
        html.Span(value, style={"fontSize":"1.4rem","fontWeight":700,"fontFamily":"JetBrains Mono,monospace","color":color}),
    ])
