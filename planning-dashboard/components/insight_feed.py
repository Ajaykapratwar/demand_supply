from dash import html
import dash_bootstrap_components as dbc
from config import COLORS


def generate_insights():
    """
    Simulates "Rule + LLM" generated insights based on current dashboard data.
    In a real implementation, this would call the LLM backend or Rules Engine.
    """
    return [
        {
            "time": "10 min ago",
            "type": "Risk",
            "message": "Supplier ACME Corp designated Critical Risk. Consider alternative sourcing.",
            "color": COLORS["danger"],
            "dot_color": COLORS["danger"],
            "icon": "bi-shield-exclamation",
        },
        {
            "time": "1 hr ago",
            "type": "Approval",
            "message": "Rules Engine auto-approved 14 replenishment orders — saved 2.5 hrs.",
            "color": COLORS["success"],
            "dot_color": COLORS["success"],
            "icon": "bi-check-circle",
        },
        {
            "time": "3 hrs ago",
            "type": "Forecast",
            "message": "Conformal recalibration triggered for APAC — quantile coverage < 90%.",
            "color": COLORS["warning"],
            "dot_color": COLORS["warning"],
            "icon": "bi-graph-down",
        },
        {
            "time": "1 day ago",
            "type": "Simulation",
            "message": "Digital Twin: +15% bullwhip effect if lead times extend 2 days.",
            "color": COLORS["primary"],
            "dot_color": COLORS["primary"],
            "icon": "bi-cpu",
        },
    ]


def insight_feed_layout():
    """Returns the UI layout for the Automated Insight Feed."""
    insights = generate_insights()

    items = []
    for ins in insights:
        items.append(
            html.Div([
                # Icon dot
                html.Div(style={
                    "width": "7px", "height": "7px", "borderRadius": "50%",
                    "background": ins["dot_color"],
                    "marginRight": "9px", "marginTop": "3px",
                    "flexShrink": "0",
                    "boxShadow": f"0 0 5px {ins['dot_color']}",
                }),
                html.Div([
                    html.Div([
                        html.Span(ins["type"], style={
                            "fontSize": "0.68rem", "fontWeight": "700",
                            "color": ins["color"], "letterSpacing": "0.05em",
                            "textTransform": "uppercase", "marginRight": "6px",
                        }),
                        html.Span(ins["time"], style={
                            "fontSize": "0.63rem", "color": COLORS["text_secondary"],
                        }),
                    ], style={"marginBottom": "3px"}),
                    html.Div(ins["message"], style={
                        "fontSize": "0.77rem", "color": COLORS["text_secondary"],
                        "lineHeight": "1.45",
                    }),
                ], style={"flex": "1", "minWidth": "0"}),
            ], style={
                "display": "flex",
                "padding": "10px 10px",
                "borderRadius": "7px",
                "marginBottom": "4px",
                "background": "rgba(255,255,255,0.02)",
                "border": f"1px solid {COLORS['border']}",
                "transition": "all 0.15s",
                "cursor": "default",
            }, className="insight-item")
        )

    return html.Div([
        html.Div(items),
    ], className="insight-feed-container", style={"maxHeight": "360px", "overflowY": "auto"})
