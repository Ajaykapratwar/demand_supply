"""pages/capacity.py — Dashboard 5: Capacity Planning"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page, callback, Input, Output
import pandas as pd

from config import COLORS, LEGEND_STYLE, apply_dark_layout
from components.kpi_card import kpi_row
from components.copilot import narrative_card
from components.scenario_controls import ScenarioSlider
from components.charts import density_plot
from data.data_loader import get_capacity_utilization, get_capacity_load_profile, get_capacity_gantt, get_production_kpis

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
    return html.Div(dcc.Graph(figure=fig, config={"displayModeBar": False}), className="col-span-3 chart-card")

layout = html.Div([
    html.Div([
        html.Div([
            html.H5("Capacity Planning", style={
                "color": COLORS["text_primary"], "fontWeight": "700",
                "fontSize": "1.1rem", "margin": "0", "letterSpacing": "-0.01em",
            }),
            html.Div("Plant utilization gauges · 12-week load profile · Production schedule",
                     style={"color": COLORS["text_secondary"], "fontSize": "0.8rem", "marginTop": "2px"}),
        ]),
    ], style={"display": "flex", "justifyContent": "space-between",
              "alignItems": "center", "marginBottom": "20px"}),
    dcc.Loading(
        id="loading-capacity",
        type="dot",
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
    prod_kpis = get_production_kpis(region, category)  # §11.1

    gauges = [_util_gauge(cap.iloc[i]) for i in range(len(cap))]

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
        duration_ms = (pd.to_datetime(row["finish"]) - pd.to_datetime(row["start"])).total_seconds() * 1000
        _gantt_fig.add_trace(go.Bar(
            x=[duration_ms], y=[row["plant"]], orientation="h",
            base=row["start"], name=row["task"],
            marker_color=_PLANT_COLOR.get(row["plant"], COLORS["chart_4"]),
            text=row["task"], textposition="inside", insidetextanchor="middle",
            hovertemplate=f"<b>{row['task']}</b><br>{row['start'].strftime('%Y-%m-%d')} → {row['finish'].strftime('%Y-%m-%d')}<extra></extra>",
        ))

    min_date = gantt["start"].min() - pd.Timedelta(days=1)
    max_date = gantt["finish"].max() + pd.Timedelta(days=1)
    apply_dark_layout(_gantt_fig, title="Production Schedule — Gantt View", height=240,
                      barmode="stack", showlegend=False,
                      xaxis=dict(type="date", gridcolor=COLORS["border"], range=[min_date, max_date]))

    # §11.1 — Production KPI labels
    prod_labels = {"oee": "OEE", "fpy": "First Pass Yield", "schedule_adh": "Schedule Adh.",
                   "throughput": "Throughput", "utilization": "Avg Utilization"}
    prod_formatted = {prod_labels.get(k, k): v for k, v in prod_kpis.items()}

    # §13 — Narrative for capacity
    oee_val = prod_kpis["oee"]["value"]
    util_val = prod_kpis["utilization"]["value"]
    narrative = (
        f"**OEE at {oee_val:.1f}%** vs 85% target "
        f"({'✕ below' if oee_val < 65 else '⚠ near-threshold' if oee_val < 85 else '✓ on-track'}). "
        f"**Avg utilization {util_val:.1f}%** "
        f"({'🔴 over-loaded' if util_val > 95 else '⚠ above comfort zone' if util_val > 85 else '✓ healthy'}). "
        f"Review gantt for WH-East bottleneck."
    )

    return html.Div([
        # §14.1 narrative
        narrative_card(narrative, dashboard_id="capacity"),

        # §11.1 Production KPI row
        html.Div([
            html.Span("Production KPIs", style={
                "fontSize": "0.68rem", "fontWeight": "700", "letterSpacing": "0.09em",
                "color": COLORS["text_secondary"], "textTransform": "uppercase",
            }),
        ], style={"marginBottom": "10px"}),
        kpi_row(prod_formatted, cols=5),

        html.Div([
            html.Span("Scenario: Demand Surge", style={
                "fontSize": "0.68rem", "fontWeight": "700", "letterSpacing": "0.09em",
                "color": COLORS["text_secondary"], "textTransform": "uppercase",
            }),
        ], style={"marginBottom": "8px", "marginTop": "12px"}),
        html.Div([
            html.Div(
                ScenarioSlider(
                    slider_id="capacity-demand-surge",
                    label="Demand Surge (%)",
                    min_val=0, max_val=50, default=10, step=5,
                    marks={0: "0%", 10: "+10%", 25: "+25%", 50: "+50%"},
                ), className="col-span-6 chart-card"
            )
        ], className="dashboard-grid mb-4"),

        html.Div([
            html.Span("Plant Utilization", style={
                "fontSize": "0.68rem", "fontWeight": "700", "letterSpacing": "0.09em",
                "color": COLORS["text_secondary"], "textTransform": "uppercase",
            }),
        ], style={"marginBottom": "10px"}),
        html.Div(gauges, className="dashboard-grid mb-4"),
        html.Div([
            html.Div(dcc.Graph(figure=_load_fig,  config={"displayModeBar": False}), className="col-span-7 chart-card"),
            html.Div(dcc.Graph(figure=_gantt_fig, config={"displayModeBar": False}), className="col-span-5 chart-card"),
        ], className="dashboard-grid mb-4"),
        html.Div([
            html.Div(dcc.Graph(figure=density_plot({"Utilization": cap["utilization"].tolist()}, title="Plant Utilization Density Distribution"), config={"displayModeBar": False}), className="col-span-12 chart-card")
        ], className="dashboard-grid mb-4"),
    ], className="page-wrapper")

