"""pages/capacity.py — Dashboard 5: Capacity Planning"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page

from config import COLORS, LEGEND_STYLE, apply_dark_layout
from data.mock_data import capacity_utilization, load_profile, gantt_data

register_page(__name__, path="/capacity", name="Capacity Planning")

_cap  = capacity_utilization()
_load = load_profile()
_gantt = gantt_data()

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

_load_fig = go.Figure()
plant_colors = [COLORS["chart_1"], COLORS["chart_2"], COLORS["chart_3"]]
for i, plant in enumerate([c for c in _load.columns if c != "week"]):
    _load_fig.add_trace(go.Bar(x=_load["week"], y=_load[plant], name=plant,
                               marker_color=plant_colors[i], opacity=0.88))
_load_fig.add_hline(y=100, line_dash="dash", line_color=COLORS["danger"], line_width=1.5,
                    annotation_text="100% capacity", annotation_font_color=COLORS["danger"])
apply_dark_layout(_load_fig, title="12-Week Load Profile (% of capacity)", height=270,
                  barmode="group", yaxis=dict(title="Utilization %", gridcolor=COLORS["border"]),
                  legend=dict(**LEGEND_STYLE, orientation="h", y=1.08))

_PLANT_COLOR = {"Plant-MX": COLORS["chart_1"], "Plant-DE": COLORS["chart_2"], "Plant-CN": COLORS["chart_3"]}
_gantt_fig = go.Figure()
for _, row in _gantt.iterrows():
    _gantt_fig.add_trace(go.Bar(
        x=[(row["finish"], row["start"])], y=[row["plant"]], orientation="h",
        base=row["start"], name=row["task"],
        marker_color=_PLANT_COLOR.get(row["plant"], COLORS["chart_4"]),
        text=row["task"], textposition="inside", insidetextanchor="middle",
        hovertemplate=f"<b>{row['task']}</b><br>{row['start']} → {row['finish']}<extra></extra>",
    ))
apply_dark_layout(_gantt_fig, title="Production Schedule — Gantt View (June 2024)", height=240,
                  barmode="stack", showlegend=False,
                  xaxis=dict(type="date", gridcolor=COLORS["border"]))

layout = html.Div([
    html.H5("Capacity Planning", style={"color": COLORS["text_primary"], "fontWeight": "700", "marginBottom": "4px"}),
    html.Div("Plant utilization gauges • 12-week load profile • Production schedule",
             style={"color": COLORS["text_secondary"], "fontSize": "0.83rem", "marginBottom": "20px"}),
    html.Div("PLANT UTILIZATION", style={"fontSize": "0.72rem", "fontWeight": "700",
             "letterSpacing": "0.08em", "color": COLORS["text_secondary"], "marginBottom": "8px"}),
    dbc.Row([dbc.Col(_util_gauge(_cap.iloc[i]), xs=6, sm=3, className="mb-2") for i in range(len(_cap))],
            className="mb-3"),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=_load_fig,  config={"displayModeBar": False}), md=7, className="mb-3"),
        dbc.Col(dcc.Graph(figure=_gantt_fig, config={"displayModeBar": False}), md=5, className="mb-3"),
    ]),
])
