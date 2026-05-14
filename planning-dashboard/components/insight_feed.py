from dash import html
import dash_bootstrap_components as dbc
from datetime import datetime

def generate_insights():
    """
    Simulates "Rule + LLM" generated insights based on current dashboard data.
    In a real implementation, this would call the LLM backend or Rules Engine.
    """
    insights = [
        {
            "time": "10 Mins Ago",
            "type": "Risk",
            "message": "Supplier ACME Corp designated as Critical Risk by Fuzzy Logic Engine. Consider alternative sourcing.",
            "color": "danger",
            "icon": "bi-shield-exclamation"
        },
        {
            "time": "1 Hour Ago",
            "type": "Approval",
            "message": "Rules Engine auto-approved 14 low-value replenishment orders saving 2.5 hours of manual review.",
            "color": "success",
            "icon": "bi-check-circle"
        },
        {
            "time": "3 Hours Ago",
            "type": "Forecast",
            "message": "Conformal recalibration triggered for APAC region due to quantile coverage dropping below 90%.",
            "color": "warning",
            "icon": "bi-graph-down"
        },
        {
            "time": "1 Day Ago",
            "type": "Simulation",
            "message": "Digital Twin simulation suggests a 15% increase in bullwhip effect if lead times extend by 2 days.",
            "color": "info",
            "icon": "bi-cpu"
        }
    ]
    return insights

def insight_feed_layout():
    """
    Returns the UI layout for the Automated Insight Feed.
    """
    insights = generate_insights()
    
    feed_items = []
    for insight in insights:
        item = dbc.ListGroupItem(
            [
                html.Div([
                    html.I(className=f"bi {insight['icon']} text-{insight['color']} fs-4 me-3"),
                    html.Div([
                        html.Div(insight['type'], className="fw-bold text-light"),
                        html.Div(insight['message'], className="small text-muted mb-1"),
                        html.Small(insight['time'], className=f"text-{insight['color']} fw-bold")
                    ], className="flex-grow-1")
                ], className="d-flex w-100")
            ],
            className="bg-dark border-secondary mb-2 rounded"
        )
        feed_items.append(item)
        
    return html.Div([
        html.H5([html.I(className="bi bi-lightning-charge-fill text-warning me-2"), "Live Insights"], className="text-light mb-3"),
        dbc.ListGroup(feed_items, flush=True)
    ], className="insight-feed-container", style={"maxHeight": "400px", "overflowY": "auto"})
