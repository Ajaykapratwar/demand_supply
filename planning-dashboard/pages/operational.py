"""pages/operational.py — Dashboard 2: Operational Planning"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page

from config import COLORS, apply_dark_layout
from data.mock_data import supply_demand_balance, inventory_dos, action_queue

register_page(__name__, path="/operational", name="Operational Planning")

_bal   = supply_demand_balance()
_dos   = inventory_dos()
_queue = action_queue()

# Heatmap
_heatmap_fig = go.Figure(go.Heatmap(
    z=_bal.values, x=_bal.columns.tolist(), y=_bal.index.tolist(),
    colorscale=[[0.0, COLORS["danger"]], [0.4, COLORS["warning"]],
                [0.6, "#ffffff"], [0.8, COLORS["success"]], [1.0, "#1a6640"]],
    zmin=-35, zmax=55,
    colorbar=dict(title="Units", tickfont=dict(color=COLORS["text_secondary"]),
                  titlefont=dict(color=COLORS["text_secondary"])),
    hovertemplate="SKU: %{y}<br>Week: %{x}<br>Balance: %{z:.0f} units<extra></extra>",
))
apply_dark_layout(_heatmap_fig, title="Supply-Demand Balance (units: + surplus / − gap)", height=330,
                  xaxis=dict(title="Week", gridcolor=COLORS["border"]),
                  yaxis=dict(title="SKU", gridcolor=COLORS["border"]))

# DOS Gauges
_STATUS_COLOR = {"success": COLORS["success"], "warning": COLORS["warning"], "danger": COLORS["danger"]}

def _dos_gauge(row):
    color = _STATUS_COLOR[row["status"]]
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=row["dos_current"],
        title={"text": row["location"], "font": {"color": COLORS["text_secondary"], "size": 11}},
        number={"suffix": "d", "font": {"color": color, "size": 22}},
        gauge={"axis": {"range": [0, 60], "tickcolor": COLORS["text_secondary"],
                        "tickfont": {"color": COLORS["text_secondary"]}},
               "bar": {"color": color}, "bgcolor": COLORS["surface"], "bordercolor": COLORS["border"],
               "threshold": {"line": {"color": COLORS["primary"], "width": 2}, "value": row["dos_target"]}},
    ))
    apply_dark_layout(fig, height=160, margin=dict(l=10, r=10, t=40, b=10))
    return dcc.Graph(figure=fig, config={"displayModeBar": False})

# Action queue
_PRIORITY_COLOR = {"P1": COLORS["danger"], "P2": COLORS["warning"], "P3": COLORS["info"]}

def _action_row(row):
    color = _PRIORITY_COLOR.get(row["Priority"], COLORS["info"])
    return dbc.ListGroupItem([
        html.Div([
            html.Span(row["Priority"], style={"color": color, "fontSize": "0.7rem", "fontWeight": "700",
                      "border": f"1px solid {color}", "borderRadius": "4px",
                      "padding": "1px 7px", "marginRight": "10px", "whiteSpace": "nowrap"}),
            html.Span(row["Action"], style={"fontSize": "0.83rem", "color": COLORS["text_primary"], "flex": "1"}),
            html.Span(row["Owner"], style={"fontSize": "0.76rem", "color": COLORS["text_secondary"],
                      "marginLeft": "12px", "whiteSpace": "nowrap"}),
            html.Span(row["Due"], style={"fontSize": "0.76rem", "color": color, "fontWeight": "600",
                      "marginLeft": "10px", "marginRight": "12px", "whiteSpace": "nowrap"}),
            html.Button("Resolve", style={
                "background": "none",
                "border": f"1px solid {COLORS['border']}",
                "color": COLORS["text_secondary"],
                "padding": "3px 10px", "borderRadius": "5px",
                "cursor": "pointer", "fontSize": "0.74rem",
                "fontFamily": "Inter, sans-serif",
            }),
        ], style={"display": "flex", "alignItems": "center"}),
    ], style={"backgroundColor": COLORS["card"], "border": f"1px solid {COLORS['border']}",
               "borderRadius": "6px", "marginBottom": "4px", "padding": "10px 14px"})

layout = html.Div([
    html.H5("Operational Planning", style={"color": COLORS["text_primary"], "fontWeight": "700", "marginBottom": "4px"}),
    html.Div("Short-horizon demand-supply balance • Inventory status • Exception queue",
             style={"color": COLORS["text_secondary"], "fontSize": "0.83rem", "marginBottom": "20px"}),
    dbc.Row([dbc.Col(dcc.Graph(figure=_heatmap_fig, config={"displayModeBar": False}), className="mb-3")]),
    html.Div("INVENTORY DAYS-OF-SUPPLY BY LOCATION", style={"fontSize": "0.72rem", "fontWeight": "700",
             "letterSpacing": "0.08em", "color": COLORS["text_secondary"], "marginBottom": "8px"}),
    dbc.Row([dbc.Col(_dos_gauge(_dos.iloc[i]), xs=6, sm=4, md=2, className="mb-2") for i in range(len(_dos))],
            className="mb-3"),
    html.Div("EXCEPTION ACTION QUEUE", style={"fontSize": "0.72rem", "fontWeight": "700",
             "letterSpacing": "0.08em", "color": COLORS["text_secondary"], "marginBottom": "8px"}),
    dbc.ListGroup([_action_row(_queue.iloc[i]) for i in range(len(_queue))]),
])
