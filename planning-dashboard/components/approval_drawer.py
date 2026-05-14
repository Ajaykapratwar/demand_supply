from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

def approval_drawer_layout():
    """
    Returns the layout for the Approval Drawer (Offcanvas).
    This component slides out from the right side of the screen.
    """
    from config import COLORS
    return html.Div([
        # Toast Container for Notifications
        html.Div(id="toast-container", style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999}),
        
        # FAB trigger button
        dbc.Button(
            [html.I(className="bi bi-inboxes-fill me-2"), "Pending Approvals",
             dbc.Badge("3", color="danger", className="ms-1")],
            id="open-approval-drawer",
            color="primary",
            size="sm",
            style={
                "marginLeft": "32px", "marginTop": "24px", "marginBottom": "-10px",
                "fontSize": "0.8rem", "fontWeight": "600",
                "position": "relative", "zIndex": "10"
            }
        ),

        # The Drawer
        dbc.Offcanvas(
            html.Div([
                html.Div("Pending Actions", style={
                    "fontSize": "0.68rem", "fontWeight": "700",
                    "color": COLORS["text_secondary"], "letterSpacing": "0.09em",
                    "textTransform": "uppercase", "marginBottom": "16px",
                }),

                # Item 1: Auto-Approved
                html.Div([
                    html.Div([
                        html.Div(style={"width": "6px", "height": "6px", "borderRadius": "50%",
                                        "background": "var(--success)", "marginRight": "8px", "flexShrink": "0"}),
                        html.Span("Increase EU Safety Stock by 15%", style={"fontSize": "0.85rem", "fontWeight": "600", "color": COLORS["text_primary"]}),
                    ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}),
                    html.Div("Risk: Low", style={"fontSize": "0.75rem", "color": COLORS["text_secondary"], "marginBottom": "8px"}),
                    html.Span("✓ Auto-Approved by Rules Engine", style={"fontSize": "0.75rem", "color": COLORS["success"], "fontWeight": "600"}),
                ], style={"background": "var(--card)", "border": "1px solid var(--border)",
                          "borderLeft": "3px solid var(--success)", "borderRadius": "8px",
                          "padding": "12px 14px", "marginBottom": "10px"}),

                # Item 2: Needs Review
                html.Div([
                    html.Div([
                        html.Div(style={"width": "6px", "height": "6px", "borderRadius": "50%",
                                        "background": "var(--warning)", "marginRight": "8px", "flexShrink": "0"}),
                        html.Span("Expedite SKU003 Air Freight", style={"fontSize": "0.85rem", "fontWeight": "600", "color": COLORS["text_primary"]}),
                    ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}),
                    html.Div("Cost Impact: +$120k", style={"fontSize": "0.75rem", "color": COLORS["text_secondary"], "marginBottom": "10px"}),
                    html.Div([
                        dbc.Button("Approve", id="btn-approve-1", color="success", size="sm",
                                   style={"marginRight": "8px", "fontSize": "0.75rem", "borderRadius": "5px"}),
                        dbc.Button("Reject", id="btn-reject-1", color="danger", size="sm",
                                   style={"fontSize": "0.75rem", "borderRadius": "5px"}),
                    ]),
                ], style={"background": "var(--card)", "border": "1px solid var(--border)",
                          "borderLeft": "3px solid var(--warning)", "borderRadius": "8px",
                          "padding": "12px 14px", "marginBottom": "10px"}),

                # Item 3: Escalated
                html.Div([
                    html.Div([
                        html.Div(style={"width": "6px", "height": "6px", "borderRadius": "50%",
                                        "background": "var(--danger)", "marginRight": "8px", "flexShrink": "0"}),
                        html.Span("Supplier Default: Battery Pack (NA)", style={"fontSize": "0.85rem", "fontWeight": "600", "color": COLORS["text_primary"]}),
                    ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}),
                    html.Div("Margin Impact: -4% · Escalated", style={"fontSize": "0.75rem", "color": COLORS["danger"], "marginBottom": "10px"}),
                    dbc.Button("Review Details", id="btn-review-1", color="primary", size="sm",
                               style={"fontSize": "0.75rem", "borderRadius": "5px"}),
                ], style={"background": "var(--card)", "border": "1px solid var(--border)",
                          "borderLeft": "3px solid var(--danger)", "borderRadius": "8px",
                          "padding": "12px 14px", "marginBottom": "10px"}),

            ]),
            id="approval-drawer",
            title="Workflow Inbox",
            is_open=False,
            placement="end",
            style={"backgroundColor": "var(--surface)", "color": "var(--text-1)",
                   "borderLeft": "1px solid var(--border)", "width": "360px"},
        )
    ])

def register_approval_callbacks(app):
    """
    Registers the callback to open/close the approval drawer and handle actions.
    """
    import dash
    @app.callback(
        Output("approval-drawer", "is_open"),
        Input("open-approval-drawer", "n_clicks"),
        [State("approval-drawer", "is_open")],
    )
    def toggle_drawer(n1, is_open):
        if n1:
            return not is_open
        return is_open

    @app.callback(
        Output("toast-container", "children"),
        Input("btn-approve-1", "n_clicks"),
        Input("btn-reject-1", "n_clicks"),
        Input("btn-review-1", "n_clicks"),
        prevent_initial_call=True
    )
    def handle_actions(approve, reject, review):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update
            
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "btn-approve-1":
            return dbc.Toast(
                [html.P("Action 'Expedite SKU003 Air Freight' has been approved.", className="mb-0")],
                header="Action Approved",
                icon="success",
                duration=4000,
                is_open=True,
            )
        elif trigger_id == "btn-reject-1":
            return dbc.Toast(
                [html.P("Action 'Expedite SKU003 Air Freight' has been rejected.", className="mb-0")],
                header="Action Rejected",
                icon="danger",
                duration=4000,
                is_open=True,
            )
        elif trigger_id == "btn-review-1":
            return dbc.Toast(
                [html.P("Opening detailed review for Supplier Default...", className="mb-0")],
                header="Review Mode",
                icon="info",
                duration=4000,
                is_open=True,
            )
            
        return dash.no_update
