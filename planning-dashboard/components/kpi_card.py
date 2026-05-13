"""components/kpi_card.py — Blueprint §6.8 KPI card template"""
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go
from config import COLORS, apply_dark_layout, hex_to_rgba


def _mini_sparkline(trend_data: list, color: str) -> dcc.Graph:
    fig = go.Figure(go.Scatter(
        y=trend_data, mode="lines",
        line=dict(color=color, width=1.5),
        fill="tozeroy", fillcolor=hex_to_rgba(color, 0.13),
        hoverinfo="skip",
    ))
    apply_dark_layout(fig, height=40, margin=dict(l=0, r=0, t=0, b=0))
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(showlegend=False)
    return dcc.Graph(figure=fig, config={"displayModeBar": False},
                     style={"height": "40px"})


_STATUS_COLOR = {
    "success": COLORS["success"],
    "warning": COLORS["warning"],
    "danger":  COLORS["danger"],
    "info":    COLORS["info"],
}


def kpi_card(title: str, value: str, target: str, delta: str,
             trend: list, status: str = "success", id_suffix: str = "") -> dbc.Card:
    """Blueprint §6.8: metric title · current value · target · delta · sparkline · status dot."""
    color = _STATUS_COLOR.get(status, COLORS["info"])
    delta_positive = not delta.startswith("-")
    delta_color = COLORS["success"] if delta_positive else COLORS["danger"]
    delta_icon = "▲" if delta_positive else "▼"

    return dbc.Card([
        dbc.CardBody([
            # Status dot + title row
            html.Div([
                html.Span("●", style={"color": color, "fontSize": "0.7rem", "marginRight": "6px"}),
                html.Span(title.upper(),
                          style={"fontSize": "0.72rem", "fontWeight": "600",
                                 "letterSpacing": "0.08em", "color": COLORS["text_secondary"]}),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "4px"}),

            # KPI value
            html.Div(value, style={
                "fontSize": "2.4rem", "fontWeight": "700", "color": COLORS["text_primary"],
                "lineHeight": "1.1", "marginBottom": "4px",
            }),

            # Target + delta row
            html.Div([
                html.Span(f"Target: {target}",
                          style={"fontSize": "0.78rem", "color": COLORS["text_secondary"]}),
                html.Span(f"  {delta_icon} {delta}",
                          style={"fontSize": "0.78rem", "color": delta_color,
                                 "fontWeight": "600", "marginLeft": "8px"}),
            ], style={"marginBottom": "8px"}),

            # Sparkline
            _mini_sparkline(trend, color),
        ], style={"padding": "14px 16px"}),
    ],
    style={
        "backgroundColor": COLORS["card"],
        "border": f"1px solid {COLORS['border']}",
        "borderRadius": "10px",
        "boxShadow": f"0 2px 12px rgba(0,0,0,0.3)",
        "transition": "transform 0.15s, box-shadow 0.15s",
    })


def kpi_row(kpi_list: list, cols: int = 3) -> html.Div:
    """Lay out a list of kpi_card() dicts into a responsive Bootstrap row."""
    cards = [kpi_card(**k, id_suffix=str(i)) for i, k in enumerate(kpi_list)]
    width = max(12 // cols, 2)
    return dbc.Row([
        dbc.Col(c, xs=12, sm=6, md=width, className="mb-3")
        for c in cards
    ])
