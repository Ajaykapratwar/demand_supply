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
# §17 color-blind-safe icon paired with each status
_STATUS_ICON = {"success": "✓", "warning": "⚠", "danger": "✕", "info": "●"}

# §16.3 / §17 ReliabilityBadge
_RELIABILITY_COLOR = {"high": COLORS["success"], "medium": COLORS["warning"], "low": COLORS["danger"]}
_RELIABILITY_LABEL = {"high": "HIGH", "medium": "MED", "low": "LOW"}


def kpi_card(title: str, value: str, target: str, delta: str,
             trend: list, status: str = "success", id_suffix: str = "",
             ai_generated: bool = False, reliability: str = "high") -> dbc.Card:
    """Blueprint §17.6 8-field KPI card: title · value · target · delta · sparkline · status dot · AI badge · reliability badge."""
    color = _STATUS_COLOR.get(status, COLORS["info"])
    icon  = _STATUS_ICON.get(status, "●")
    delta_positive = not delta.startswith("-")
    delta_color = COLORS["success"] if delta_positive else COLORS["danger"]
    delta_icon = "▲" if delta_positive else "▼"
    rel_color = _RELIABILITY_COLOR.get(reliability, COLORS["info"])
    rel_label = _RELIABILITY_LABEL.get(reliability, reliability.upper())

    return dbc.Card([
        dbc.CardBody([
            # Row 1: Status dot+icon + title + badges
            html.Div([
                html.Span(f"{icon}", style={"color": color, "fontSize": "0.75rem",
                                            "marginRight": "5px", "fontWeight": "700"}),
                html.Span(title.upper(),
                          style={"fontSize": "0.72rem", "fontWeight": "600",
                                 "letterSpacing": "0.08em", "color": COLORS["text_secondary"],
                                 "flex": "1"}),
                # §17 ReliabilityBadge
                html.Span(rel_label, style={
                    "fontSize": "0.6rem", "fontWeight": "700", "color": rel_color,
                    "border": f"1px solid {rel_color}", "borderRadius": "3px",
                    "padding": "0px 4px", "marginLeft": "4px",
                }),
                # §17 AI badge
                *([
                    html.Span("✨", title="AI Generated", style={
                        "fontSize": "0.8rem", "marginLeft": "4px",
                        "color": COLORS["accent"], "cursor": "default",
                    })
                ] if ai_generated else []),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "4px"}),

            # Row 2: KPI value
            html.Div(value, style={
                "fontSize": "2.4rem", "fontWeight": "700", "color": COLORS["text_primary"],
                "lineHeight": "1.1", "marginBottom": "4px",
                "fontFamily": "'JetBrains Mono', monospace",
            }),

            # Row 3: Target + delta
            html.Div([
                html.Span(f"Target: {target}",
                          style={"fontSize": "0.78rem", "color": COLORS["text_secondary"]}),
                html.Span(f"  {delta_icon} {delta}",
                          style={"fontSize": "0.78rem", "color": delta_color,
                                 "fontWeight": "600", "marginLeft": "8px"}),
            ], style={"marginBottom": "8px"}),

            # Row 4: Sparkline
            _mini_sparkline(trend, color),
        ], style={"padding": "14px 16px"}),
    ],
    style={
        "backgroundColor": COLORS["card"],
        "border": f"1px solid {COLORS['border']}",
        "borderRadius": "10px",
        "boxShadow": "0 2px 12px rgba(0,0,0,0.3)",
        "transition": "transform 0.15s, box-shadow 0.15s",
    })


def kpi_row(kpi_list, cols: int = 3) -> html.Div:
    """Lay out KPI cards into a responsive Bootstrap row.

    Accepts either:
    - list of dicts: {title, value, target, delta, trend, status}
    - dict of dicts: {label: {value, target, delta, unit, status, spark}} as
      returned by every data_loader KPI function.
    """
    if isinstance(kpi_list, dict):
        # Normalise data_loader format → kpi_card kwargs
        normalised = []
        for label, kpi in kpi_list.items():
            v = kpi.get("value", 0) or 0
            t = kpi.get("target", 0) or 0
            d = kpi.get("delta", 0) or 0
            u = kpi.get("unit", "")
            normalised.append({
                "title":  label,
                "value":  f"{v:,.2f}{u}" if isinstance(v, float) else f"{v}{u}",
                "target": f"{t:,.2f}{u}" if isinstance(t, float) else f"{t}{u}",
                "delta":  f"{d:+.2f}{u}" if isinstance(d, (int, float)) else str(d),
                "trend":  kpi.get("spark", [v] * 14),
                "status": kpi.get("status", "info"),
            })
        kpi_list = normalised

    cards = [kpi_card(**k, id_suffix=str(i)) for i, k in enumerate(kpi_list)]
    width = max(12 // cols, 2)
    return dbc.Row([
        dbc.Col(c, xs=12, sm=6, md=width, className="mb-3")
        for c in cards
    ])
