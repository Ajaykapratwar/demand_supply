"""pages/operational.py — Dashboard 2: Operational Planning"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page, callback, Input, Output
import pandas as pd

from config import COLORS, apply_dark_layout
from data.data_loader import get_supply_demand_balance, get_inventory_dos_gauges, get_action_queue

register_page(__name__, path="/operational", name="Operational Planning")

# DOS Gauges
_STATUS_COLOR = {"success": COLORS["success"], "warning": COLORS["warning"], "danger": COLORS["danger"]}

def _dos_gauge(row):
    color = _STATUS_COLOR[row["status"]]
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=row["dos"],
        title={"text": row["region"], "font": {"color": COLORS["text_secondary"], "size": 11}},
        number={"suffix": "d", "font": {"color": color, "size": 22}},
        gauge={"axis": {"range": [0, 60], "tickcolor": COLORS["text_secondary"],
                        "tickfont": {"color": COLORS["text_secondary"]}},
               "bar": {"color": color}, "bgcolor": COLORS["surface"], "bordercolor": COLORS["border"],
               "threshold": {"line": {"color": COLORS["primary"], "width": 2}, "value": row["target"]}},
    ))
    apply_dark_layout(fig, height=160, margin=dict(l=10, r=10, t=40, b=10))
    return dcc.Graph(figure=fig, config={"displayModeBar": False})

# Action queue
_PRIORITY_COLOR = {"CRITICAL": COLORS["danger"], "HIGH": COLORS["warning"], "MEDIUM": COLORS["info"]}

def _action_row(row):
    color = _PRIORITY_COLOR.get(row["priority"], COLORS["info"])
    return dbc.ListGroupItem([
        html.Div([
            html.Span(row["priority"], style={"color": color, "fontSize": "0.7rem", "fontWeight": "700",
                      "border": f"1px solid {color}", "borderRadius": "4px",
                      "padding": "1px 7px", "marginRight": "10px", "whiteSpace": "nowrap"}),
            html.Span(row["action"], style={"fontSize": "0.83rem", "color": COLORS["text_primary"], "flex": "1"}),
            html.Span(row["issue"], style={"fontSize": "0.76rem", "color": COLORS["text_secondary"],
                      "marginLeft": "12px", "whiteSpace": "nowrap"}),
            html.Span(row["region"], style={"fontSize": "0.76rem", "color": color, "fontWeight": "600",
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


def layout(**kwargs):
    return html.Div(id="operational-page-content")


@callback(
    Output("operational-page-content", "children"),
    Input("global-filter-store", "data"),
)
def update_operational_page(filter_data):
    filter_data = filter_data or {}
    region = filter_data.get("region", "Global")
    category = filter_data.get("category", "All")
    
    # Load live data
    bal_df = get_supply_demand_balance(region=region, category=category)
    dos_data = get_inventory_dos_gauges(region=region, category=category)
    queue = get_action_queue(region=region, category=category)
    
    # Process balance for heatmap
    if not bal_df.empty:
        bal_df['week'] = bal_df['date'].dt.strftime('W%V')
        bal_pivot = bal_df.pivot(index='region', columns='week', values='gap').fillna(0)
    else:
        bal_pivot = pd.DataFrame(columns=["W01"], index=["Region"])

    # Heatmap
    heatmap_fig = go.Figure(go.Heatmap(
        z=bal_pivot.values, x=bal_pivot.columns.tolist(), y=bal_pivot.index.tolist(),
        colorscale=[[0.0, COLORS["danger"]], [0.4, COLORS["warning"]],
                    [0.6, "#ffffff"], [0.8, COLORS["success"]], [1.0, "#1a6640"]],
        zmin=-10000, zmax=10000,
        colorbar=dict(title=dict(text="Units Gap", font=dict(color=COLORS["text_secondary"])),
                      tickfont=dict(color=COLORS["text_secondary"])),
        hovertemplate="Region: %{y}<br>Week: %{x}<br>Balance: %{z:.0f} units<extra></extra>",
    ))
    apply_dark_layout(heatmap_fig, title="Supply-Demand Balance (units: + surplus / − gap)", height=330,
                      xaxis=dict(title="Week", gridcolor=COLORS["border"]),
                      yaxis=dict(title="Region", gridcolor=COLORS["border"]))

    return html.Div([
        # Page Header
        html.Div([
            html.Div([
                html.H5("Operational Planning", style={
                    "color": COLORS["text_primary"], "fontWeight": "700",
                    "fontSize": "1.1rem", "margin": "0", "letterSpacing": "-0.01em",
                }),
                html.Div(f"Short-horizon demand-supply balance · Inventory status · Exception queue",
                         style={"color": COLORS["text_secondary"], "fontSize": "0.8rem", "marginTop": "2px"}),
            ]),
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center",
                  "marginBottom": "20px"}),

        dbc.Row([dbc.Col(html.Div([
            html.Div(style={"padding": "14px 16px 0", "marginBottom": "-4px"}, children=[
                html.Span("Supply–Demand Balance", style={
                    "fontSize": "0.78rem", "fontWeight": "600",
                    "color": COLORS["text_secondary"], "letterSpacing": "0.04em",
                }),
            ]),
            dcc.Graph(figure=heatmap_fig, config={"displayModeBar": False}),
        ], style={"background": COLORS["card"], "border": f"1px solid {COLORS['border']}",
                  "borderRadius": "10px", "overflow": "hidden"}), className="mb-3")]),

        html.Div([
            html.Span("Inventory Days-of-Supply by Region", style={
                "fontSize": "0.68rem", "fontWeight": "700", "letterSpacing": "0.09em",
                "color": COLORS["text_secondary"], "textTransform": "uppercase",
            }),
        ], style={"marginBottom": "10px"}),
        dbc.Row([dbc.Col(_dos_gauge(r), xs=6, sm=4, md=2, className="mb-2") for r in dos_data],
                className="mb-4"),

        html.Div([
            html.Span("Exception Action Queue", style={
                "fontSize": "0.68rem", "fontWeight": "700", "letterSpacing": "0.09em",
                "color": COLORS["text_secondary"], "textTransform": "uppercase",
            }),
            html.Span(f"{len(queue)} items", style={
                "fontSize": "0.65rem", "color": COLORS["primary"],
                "background": "rgba(59,130,246,0.1)", "border": "1px solid rgba(59,130,246,0.25)",
                "borderRadius": "99px", "padding": "2px 9px", "fontWeight": "600",
                "marginLeft": "10px",
            }),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "10px"}),
        dbc.ListGroup([_action_row(r) for r in queue]),
    ])
