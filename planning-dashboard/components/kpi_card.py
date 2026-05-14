"""components/kpi_card.py — Modern minimalist KPI card"""
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go
from config import COLORS, apply_dark_layout, hex_to_rgba


def _mini_sparkline(trend_data: list, color: str) -> dcc.Graph:
    fig = go.Figure(go.Scatter(
        y=trend_data, mode="lines",
        line=dict(color=color, width=1.5),
        fill="tozeroy", fillcolor=hex_to_rgba(color, 0.1),
        hoverinfo="skip",
    ))
    apply_dark_layout(fig, height=36, margin=dict(l=0, r=0, t=0, b=0))
    fig.update_xaxes(visible=False, fixedrange=True, showgrid=False)
    fig.update_yaxes(visible=False, fixedrange=True, showgrid=False)
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return dcc.Graph(figure=fig, config={"displayModeBar": False},
                     style={"height": "36px"})


_STATUS_COLOR = {
    "success": COLORS["success"],
    "warning": COLORS["warning"],
    "danger":  COLORS["danger"],
    "info":    COLORS["primary"],
}
_STATUS_ICON = {"success": "bi-arrow-up-short", "warning": "bi-dash", "danger": "bi-arrow-down-short", "info": "bi-circle-fill"}
_RELIABILITY_COLOR = {"high": COLORS["success"], "medium": COLORS["warning"], "low": COLORS["danger"]}
_RELIABILITY_LABEL = {"high": "HIGH", "medium": "MED", "low": "LOW"}


def kpi_card(title: str, value: str, target: str, delta: str,
             trend: list, status: str = "success", id_suffix: str = "",
             ai_generated: bool = False, reliability: str = "high") -> html.Div:
    """Modern minimalist KPI card with sparkline."""
    color = _STATUS_COLOR.get(status, COLORS["primary"])
    delta_positive = not delta.startswith("-")
    delta_color = COLORS["success"] if delta_positive else COLORS["danger"]
    rel_color = _RELIABILITY_COLOR.get(reliability, COLORS["primary"])
    rel_label = _RELIABILITY_LABEL.get(reliability, reliability.upper())

    # Top accent line color set via border-top
    return html.Div([
        # ── Top bar: title + badges ───────────────────────────
        html.Div([
            html.Span(title.upper(), style={
                "fontSize": "0.67rem", "fontWeight": "700",
                "letterSpacing": "0.09em", "color": COLORS["text_secondary"],
                "flex": "1",
            }),
            html.Div([
                # Reliability badge
                html.Span(rel_label, style={
                    "fontSize": "0.58rem", "fontWeight": "700", "color": rel_color,
                    "border": f"1px solid {rel_color}",
                    "borderRadius": "3px", "padding": "1px 5px", "marginRight": "5px",
                    "opacity": "0.85",
                }),
                # Ask Copilot / AI badge
                html.Div(
                    html.I(className="bi bi-stars", style={"fontSize": "0.8rem"}),
                    id={"type": "kpi-copilot-btn", "index": title},
                    title="Ask Copilot",
                    style={
                        "color": COLORS["accent"], "cursor": "pointer",
                        "padding": "2px 4px", "borderRadius": "4px",
                        "transition": "background 0.15s",
                    }
                ) if not ai_generated else html.Span("✨", style={
                    "fontSize": "0.75rem", "color": COLORS["accent"],
                }),
            ], style={"display": "flex", "alignItems": "center"}),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "10px"}),

        # ── KPI Value ─────────────────────────────────────────
        html.Div(value, style={
            "fontSize": "1.9rem", "fontWeight": "700", "color": COLORS["text_primary"],
            "lineHeight": "1", "marginBottom": "6px",
            "fontFamily": "'JetBrains Mono', 'Fira Code', monospace",
            "letterSpacing": "-0.02em",
        }),

        # ── Delta + Target ────────────────────────────────────
        html.Div([
            html.Span([
                html.I(className=f"bi {'bi-arrow-up-short' if delta_positive else 'bi-arrow-down-short'}",
                       style={"fontSize": "0.9rem"}),
                f" {delta}",
            ], style={
                "fontSize": "0.8rem", "color": delta_color,
                "fontWeight": "600", "marginRight": "10px",
                "display": "inline-flex", "alignItems": "center",
            }),
            html.Span(f"vs {target}", style={
                "fontSize": "0.75rem", "color": COLORS["text_secondary"],
            }),
        ], style={"marginBottom": "10px", "display": "flex", "alignItems": "center"}),

        # ── Sparkline ─────────────────────────────────────────
        _mini_sparkline(trend, color),

        # Status indicator line at bottom
        html.Div(style={
            "position": "absolute", "bottom": "0", "left": "0", "right": "0",
            "height": "3px",
            "background": color,
            "opacity": "0.8",
        }),

    ], className="kpi-card")


def kpi_row(kpi_list, cols: int = 3) -> html.Div:
    """Lay out KPI cards into a strict CSS Grid to ensure equal heights and no overlap.

    Accepts either:
    - list of dicts: {title, value, target, delta, trend, status}
    - dict of dicts: {label: {value, target, delta, unit, status, spark}}
    """
    if isinstance(kpi_list, dict):
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
                "ai_generated": kpi.get("ai_generated", False),
                "reliability": kpi.get("reliability", "high")
            })
        kpi_list = normalised

    cards = [kpi_card(**k, id_suffix=str(i)) for i, k in enumerate(kpi_list)]
    return html.Div(cards, className="kpi-grid mb-4")
