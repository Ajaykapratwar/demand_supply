import dash_bootstrap_components as dbc
from dash import html, dcc
import random

def get_presence_indicators():
    """
    Returns a UI component showing active users on the dashboard.
    As requested, this mocks real-time presence without WebSockets.
    """
    return html.Div([
        # Hidden interval component to simulate real-time updates if needed
        dcc.Interval(id="presence-interval", interval=10000, n_intervals=0),
        
        html.Div([
            html.Span("Active Now: ", className="text-muted small me-2"),
            # Mock Avatars
            html.Span("JD", className="badge rounded-pill bg-primary me-1", title="John Doe (Demand Planner)"),
            html.Span("SK", className="badge rounded-pill bg-success me-1", title="Sarah Khan (Supply Planner)"),
            html.Span("AL", className="badge rounded-pill bg-info me-1", title="Alex Lee (Exec)"),
            
            # Simulated blinking "live" dot
            html.Span(className="spinner-grow spinner-grow-sm text-danger ms-2", style={"width": "10px", "height": "10px"})
        ], id="presence-container", className="d-flex align-items-center bg-dark p-2 rounded border border-secondary")
    ])

def sop_wizard_modal():
    """
    Guided S&OP Wizard: A modal stepping through the monthly S&OP cycle.
    """
    return html.Div([
        dbc.Button("Launch S&OP Wizard", id="open-sop-wizard", color="outline-info", className="w-100 mb-3"),
        
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Executive S&OP Cycle - May 2026")),
            dbc.ModalBody([
                dbc.Progress([
                    dbc.Progress(value=25, color="success", bar=True, label="1. Demand"),
                    dbc.Progress(value=25, color="primary", bar=True, label="2. Supply"),
                    dbc.Progress(value=25, color="warning", bar=True, label="3. Pre-S&OP", striped=True, animated=True),
                    dbc.Progress(value=25, color="secondary", bar=True, label="4. Exec", style={"opacity": 0.5}),
                ], className="mb-4", style={"height": "30px"}),
                
                html.H5("Step 3: Pre-S&OP Reconciliation", className="text-info"),
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
                    value=[1],
                    id="sop-checklist",
                    switch=True,
                )
            ]),
            dbc.ModalFooter([
                dbc.Button("Previous Step", id="sop-prev", color="secondary", className="me-auto"),
                dbc.Button("Save & Next Step", id="sop-next", color="primary")
            ])
        ], id="sop-modal", is_open=False, size="lg", centered=True)
    ])

def register_collaboration_callbacks(app):
    from dash.dependencies import Input, Output, State
    
    @app.callback(
        Output("sop-modal", "is_open"),
        Input("open-sop-wizard", "n_clicks"),
        State("sop-modal", "is_open")
    )
    def toggle_modal(n, is_open):
        if n:
            return not is_open
        return is_open
    
    # Mocking presence update
    @app.callback(
        Output("presence-container", "style"),
        Input("presence-interval", "n_intervals")
    )
    def update_presence(n):
        # Just a dummy callback to show how it would be wired
        # In a real app, this would poll an endpoint for active sessions
        return {"opacity": 1.0}
