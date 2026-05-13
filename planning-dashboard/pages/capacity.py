"""pages/capacity.py — Dashboard 5: Capacity Planning"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page, callback, Input, Output
import pandas as pd

from config import COLORS, LEGEND_STYLE, apply_dark_layout
from data.data_loader import get_capacity_utilization, get_capacity_load_profile, get_capacity_gantt

register_page(__name__, path="/capacity", name="Capacity Planning")

def _util_gauge(row):
    u = row["utilization"]
    color = COLORS["danger"] if u > 90 else COLORS["warning"] if u > 80 else COLORS["success"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=u,
        title={"text": row["plant"], "font": {"color": COLORS["text_secondary"], "size": 11}},
        number={"suffix": "%", "font": {"color": color, "size": 24}},
        gauge={"axis": {"range": [0, 110], "tickcolor": COLORS["text_secondary"],
                        "tickfont": {"color": COLORS["text_secondary"]}},
               "bar": {"color": color},
               "steps": [{"range": [0, 70],  "color": "rgba(63,185,80,0.2)"},
                         {"range": [70, 90], "color": "rgba(255,170,0,0.2)"},
                         {"range": [90, 110],"color": "rgba(218,54,51,0.2)"}],
               "threshold": {"line": {"color": "white", "width": 2}, "value": 100},
               "bgcolor": COLORS["surface"], "bordercolor": COLORS["border"]},
    ))
    apply_dark_layout(fig, height=180, margin=dict(l=10, r=10, t=50, b=10))
    return dcc.Graph(figure=fig, config={"displayModeBar": False})

layout = html.Div([
    html.H5("Capacity Planning", style={"color": COLORS["text_primary"], "fontWeight": "700", "marginBottom": "4px"}),
    html.Div("Plant utilization gauges • 12-week load profile • Production schedule",
             style={"color": COLORS["text_secondary"], "fontSize": "0.83rem", "marginBottom": "20px"}),
    dcc.Loading(
        id="loading-capacity",
        type="default",
        color=COLORS["primary"],
        children=html.Div(id="capacity-content")
    )
])

@callback(
    Output("capacity-content", "children"),
    Input("global-filter-store", "data")
)
def update_capacity_page(filter_data):
    filter_data = filter_data or {}
    region = filter_data.get("region", "Global")
    category = filter_data.get("category", "All")

    cap = get_capacity_utilization(region, category)
    load = get_capacity_load_profile(region, category)
    gantt = get_capacity_gantt(region, category)

    gauges = [dbc.Col(_util_gauge(cap.iloc[i]), xs=6, sm=3, className="mb-2") for i in range(len(cap))]

    _load_fig = go.Figure()
    plant_colors = [COLORS["chart_1"], COLORS["chart_2"], COLORS["chart_3"], COLORS["chart_4"], COLORS["chart_5"], COLORS["info"], COLORS["success"]]
    plants = [c for c in load.columns if c != "week"]
    for i, plant in enumerate(plants):
        color = plant_colors[i % len(plant_colors)]
        _load_fig.add_trace(go.Bar(x=load["week"], y=load[plant], name=plant,
                                   marker_color=color, opacity=0.88))
    _load_fig.add_hline(y=100, line_dash="dash", line_color=COLORS["danger"], line_width=1.5,
                        annotation_text="100% capacity", annotation_font_color=COLORS["danger"])
    apply_dark_layout(_load_fig, title="12-Week Load Profile (% of capacity)", height=270,
                      barmode="group", yaxis=dict(title="Utilization %", gridcolor=COLORS["border"]),
                      legend=dict(**LEGEND_STYLE, orientation="h", y=1.08))

    _gantt_fig = go.Figure()
    _PLANT_COLOR = {p: plant_colors[i % len(plant_colors)] for i, p in enumerate(plants)}
    for _, row in gantt.iterrows():
        # For plotly date xaxis, base is datetime, x is duration in milliseconds
        duration_ms = (pd.to_datetime(row["finish"]) - pd.to_datetime(row["start"])).total_seconds() * 1000
        _gantt_fig.add_trace(go.Bar(
            x=[duration_ms], y=[row["plant"]], orientation="h",
            base=row["start"], name=row["task"],
            marker_color=_PLANT_COLOR.get(row["plant"], COLORS["chart_4"]),
            text=row["task"], textposition="inside", insidetextanchor="middle",
            hovertemplate=f"<b>{row['task']}</b><br>{row['start'].strftime('%Y-%m-%d')} → {row['finish'].strftime('%Y-%m-%d')}<extra></extra>",
        ))
    
    # Compute gantt x-axis range
    min_date = gantt["start"].min() - pd.Timedelta(days=1)
    max_date = gantt["finish"].max() + pd.Timedelta(days=1)

    apply_dark_layout(_gantt_fig, title=f"Production Schedule — Gantt View", height=240,
                      barmode="stack", showlegend=False,
                      xaxis=dict(type="date", gridcolor=COLORS["border"], range=[min_date, max_date]))

    return html.Div([
        html.Div("PLANT UTILIZATION", style={"fontSize": "0.72rem", "fontWeight": "700",
                 "letterSpacing": "0.08em", "color": COLORS["text_secondary"], "marginBottom": "8px"}),
        dbc.Row(gauges, className="mb-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=_load_fig,  config={"displayModeBar": False}), md=7, className="mb-3"),
            dbc.Col(dcc.Graph(figure=_gantt_fig, config={"displayModeBar": False}), md=5, className="mb-3"),
        ]),
    ])
