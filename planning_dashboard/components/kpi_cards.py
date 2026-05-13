"""
kpi_cards.py  ─  Reusable KPI card component (blueprint §6.8)

Each card: title, value, unit, target, delta (arrow + %), sparkline, status dot.
"""
import plotly.graph_objects as go
from dash import html, dcc
from components.theme import COLORS, STATUS_COLOR, base_layout


def _hex_to_rgba(hex_color: str, alpha: float = 0.12) -> str:
    """Convert 6-digit hex → rgba() string."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def sparkline_fig(data: list, color: str) -> go.Figure:
    fill_color = _hex_to_rgba(color) if color.startswith("#") else color
    fig = go.Figure(go.Scatter(
        y=data, mode="lines",
        line=dict(color=color, width=1.5, shape="spline"),
        fill="tozeroy",
        fillcolor=fill_color,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0), height=40,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


def kpi_card(
    label: str,
    value: float,
    unit: str,
    target: float,
    delta: float,
    sparkline_data: list,
    status: str = "success",   # success | warning | danger
    delta_invert: bool = False, # True for "lower is better" metrics (MAPE, stockout)
) -> html.Div:
    """
    Blueprint §6.8 compliant KPI card.
    delta_invert=True: negative delta is green (improvement for cost/error metrics).
    """
    color = STATUS_COLOR.get(status, COLORS["primary"])

    if delta == 0:
        delta_cls = "kpi-delta neu"
        delta_icon = "→"
    elif delta > 0:
        delta_cls = "kpi-delta pos" if not delta_invert else "kpi-delta neg"
        delta_icon = "▲"
    else:
        delta_cls = "kpi-delta neg" if not delta_invert else "kpi-delta pos"
        delta_icon = "▼"

    return html.Div(className="kpi-card", children=[
        # Status dot + label
        html.Div(style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}, children=[
            html.Span(className=f"status-dot {status}"),
            html.Span(label, className="kpi-label"),
        ]),
        # Value + unit
        html.Div(style={"display": "flex", "alignItems": "baseline", "gap": "4px"}, children=[
            html.Span(f"{value:,.1f}", className="kpi-value",
                      style={"color": color}),
            html.Span(unit, className="kpi-unit"),
        ]),
        # Target + delta
        html.Div(style={"display": "flex", "justifyContent": "space-between",
                        "marginTop": "4px"}, children=[
            html.Span(f"Target: {target:,.1f} {unit}", className="kpi-target"),
            html.Span(f"{delta_icon} {abs(delta):.1f}%", className=delta_cls),
        ]),
        # Sparkline
        dcc.Graph(figure=sparkline_fig(sparkline_data, color),
                  config={"displayModeBar": False},
                  style={"marginTop": "8px", "height": "40px"}),
    ])
