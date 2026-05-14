import dash_bootstrap_components as dbc
from dash import html, dcc
import random

def get_presence_indicators():
    """
    Returns a UI component showing active users on the dashboard.
    As requested, this mocks real-time presence without WebSockets.
    """
    from config import COLORS
    _AVATARS = [
        {"initials": "JD", "name": "John Doe (Demand Planner)", "color": "#3b82f6"},
        {"initials": "SK", "name": "Sarah Khan (Supply Planner)", "color": "#10b981"},
        {"initials": "AL", "name": "Alex Lee (Exec)",           "color": "#8b5cf6"},
    ]
    return html.Div([
        dcc.Interval(id="presence-interval", interval=10000, n_intervals=0),
        html.Div([
            html.Div([
                html.Div(a["initials"], title=a["name"], style={
                    "width": "24px", "height": "24px", "borderRadius": "50%",
                    "background": a["color"],
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                    "fontSize": "0.6rem", "fontWeight": "700", "color": "#fff",
                    "marginRight": "8px", "cursor": "default",
                    "border": f"1px solid {COLORS['border']}",
                }),
                html.Span(a["name"], style={"fontSize": "0.75rem", "color": COLORS["text_secondary"]})
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"})
            for a in _AVATARS
        ], id="presence-container", style={
            "display": "flex", "flexDirection": "column",
            "padding": "5px 0"
        })
    ])

def sop_wizard_modal():
    """
    Guided S&OP Wizard: A modal stepping through the monthly S&OP cycle.
    """
    return html.Div([
        dcc.Store(id="sop-step-store", data=1),
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Executive S&OP Cycle - May 2026")),
            dbc.ModalBody(id="sop-modal-body"),
            dbc.ModalFooter([
                dbc.Button("Previous Step", id="sop-prev", color="secondary", className="me-auto"),
                dbc.Button("Save & Next Step", id="sop-next", color="primary")
            ])
        ], id="sop-modal", is_open=False, size="lg", centered=True)
    ])

def register_collaboration_callbacks(app):
    from dash.dependencies import Input, Output, State
    import dash
    
    @app.callback(
        Output("sop-modal", "is_open"),
        Input("launch-sop-wizard-btn", "n_clicks"),
        State("sop-modal", "is_open")
    )
    def toggle_modal(n, is_open):
        if n:
            return not is_open
        return is_open
        
    @app.callback(
        Output("sop-step-store", "data"),
        Input("sop-prev", "n_clicks"),
        Input("sop-next", "n_clicks"),
        State("sop-step-store", "data")
    )
    def change_step(prev_clicks, next_clicks, current_step):
        ctx = dash.callback_context
        if not ctx.triggered:
            return current_step
        trigger = ctx.triggered[0]["prop_id"]
        if "sop-next" in trigger:
            return min(4, current_step + 1)
        elif "sop-prev" in trigger:
            return max(1, current_step - 1)
        return current_step
        
    @app.callback(
        Output("sop-modal-body", "children"),
        Input("sop-step-store", "data")
    )
    def update_sop_body(step):
        titles = ["1. Demand", "2. Supply", "3. Pre-S&OP", "4. Exec"]
        content = []
        if step == 1:
            content = [
                html.H5("Step 1: Demand Review", className="text-success"),
                html.P("Reviewing baseline forecast vs consensus demand plan."),
            ]
        elif step == 2:
            content = [
                html.H5("Step 2: Supply Review", className="text-primary"),
                html.P("Evaluating capacity constraints and raw material availability."),
            ]
        elif step == 3:
            content = [
                html.H5("Step 3: Pre-S&OP Reconciliation", className="text-warning"),
                html.P("Reviewing unconstrained demand against capacity constraints. Financial impact scenarios generated."),
                dbc.Alert([
                    html.I(className="bi bi-exclamation-triangle-fill me-2"),
                    "Capacity shortfall identified in EU region. Simulated margin impact: -$1.2M."
                ], color="warning"),
                dbc.Checklist(
                    options=[
                        {"label": "Review Demand Shaping Options", "value": 1},
                        {"label": "Review Alternative Sourcing (Spot Market)", "value": 2},
                        {"label": "Approve Financial Gap for Exec S&OP", "value": 3},
                    ],
                    value=[1], id="sop-checklist", switch=True,
                )
            ]
        else:
            content = [
                html.H5("Step 4: Executive S&OP", className="text-secondary"),
                html.P("Final sign-off on the constrained operating plan."),
                dbc.Alert("All exceptions have been cleared. Ready for execution.", color="success")
            ]
            
        progress = dbc.Progress([
            dbc.Progress(value=25, color="success", bar=True, label="1. Demand", style={"opacity": 1.0 if step >= 1 else 0.5}),
            dbc.Progress(value=25, color="primary", bar=True, label="2. Supply", style={"opacity": 1.0 if step >= 2 else 0.5}),
            dbc.Progress(value=25, color="warning", bar=True, label="3. Pre-S&OP", striped=(step==3), animated=(step==3), style={"opacity": 1.0 if step >= 3 else 0.5}),
            dbc.Progress(value=25, color="secondary", bar=True, label="4. Exec", style={"opacity": 1.0 if step >= 4 else 0.5}),
        ], className="mb-4", style={"height": "30px"})
        
        return [progress] + content

    # Mocking presence update
    @app.callback(
        Output("presence-container", "style"),
        Input("presence-interval", "n_intervals")
    )
    def update_presence(n):
        return {"opacity": 1.0}
