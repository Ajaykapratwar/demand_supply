from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

def approval_drawer_layout():
    """
    Returns the layout for the Approval Drawer (Offcanvas).
    This component slides out from the right side of the screen.
    """
    return html.Div([
        # Button to trigger the drawer
        dbc.Button(
            [html.I(className="bi bi-inboxes-fill me-2"), "Pending Approvals", dbc.Badge("3", color="danger", className="ms-1")],
            id="open-approval-drawer",
            color="primary",
            className="mb-3",
            style={"position": "fixed", "right": "20px", "bottom": "20px", "zIndex": 1000}
        ),
        
        # The Drawer (Offcanvas)
        dbc.Offcanvas(
            html.Div([
                html.H5("Pending Actions", className="text-muted mb-4"),
                
                # Item 1: Auto-Approved
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Replenishment: WH-North", className="card-title"),
                        html.P("Value: $45,000 | Risk: Low", className="card-text small text-muted"),
                        dbc.Alert("Auto-Approved by Rules Engine", color="success", style={"padding": "0.5rem"}),
                    ])
                ], className="mb-3 bg-dark text-light border-success"),
                
                # Item 2: Needs Review
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Supplier Contract Renewal: ACME Corp", className="card-title"),
                        html.P("Value: $250,000 | Risk: High", className="card-text small text-muted"),
                        dbc.Alert("Flagged by Fuzzy Logic (High Risk)", color="warning", style={"padding": "0.5rem"}),
                        html.Div([
                            dbc.Button("Approve", color="success", size="sm", className="me-2"),
                            dbc.Button("Reject", color="danger", size="sm")
                        ], className="mt-2")
                    ])
                ], className="mb-3 bg-dark text-light border-warning"),
                
                # Item 3: Escalated
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Emergency Freight: Air Cargo", className="card-title"),
                        html.P("Margin Impact: -4% | Value: $120k", className="card-text small text-muted"),
                        dbc.Alert("Escalated: Margin Threshold Exceeded", color="danger", style={"padding": "0.5rem"}),
                        dbc.Button("Review Details", color="primary", size="sm", className="mt-2")
                    ])
                ], className="mb-3 bg-dark text-light border-danger")
                
            ]),
            id="approval-drawer",
            title="Workflow Inbox",
            is_open=False,
            placement="end",
            className="bg-dark text-light"
        )
    ])

def register_approval_callbacks(app):
    """
    Registers the callback to open/close the approval drawer.
    """
    @app.callback(
        Output("approval-drawer", "is_open"),
        Input("open-approval-drawer", "n_clicks"),
        [State("approval-drawer", "is_open")],
    )
    def toggle_drawer(n1, is_open):
        if n1:
            return not is_open
        return is_open
