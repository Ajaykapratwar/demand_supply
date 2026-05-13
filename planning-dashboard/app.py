"""app.py — PlanIQ Dashboard entry point (Plotly Dash, blueprint §6.5)

Layout shell (blueprint §3.6):
  [Top Nav] → [Left Sidebar | Main Content | Right Copilot Panel]
"""
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback, ctx, no_update

from config import COLORS, USERS
from components.navbar import build_navbar, build_sidebar
from components.copilot import build_copilot_panel, _CANNED_RESPONSES, _response_card

# ── App Init ──────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="PlanIQ — AI Planning Dashboard",
    update_title=None,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server   # for production WSGI deployment

# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div([
    # Global filter state store (blueprint §3.6 GlobalFilterState)
    dcc.Store(id="global-filter-store", storage_type="memory", data={
        "horizon":      "Tactical (1-12m)",
        "region":       "Global",
        "category":     "All",
        "scenario":     None,
    }),
    dcc.Store(id="copilot-open-store", data=True),
    dcc.Store(id="auth-store", storage_type="memory", data={"authenticated": False, "role": None, "username": None}),

    # Login Overlay
    html.Div(id="login-overlay", style={"display": "flex", "justifyContent": "center", "alignItems": "center", "height": "100vh", "backgroundColor": COLORS["background"]}, children=[
        html.Div(style={"padding": "40px", "backgroundColor": COLORS["surface"], "borderRadius": "12px", "width": "400px", "boxShadow": "0 8px 32px rgba(0,0,0,0.5)"}, children=[
            html.H3("PlanIQ Login", style={"color": COLORS["text_primary"], "marginBottom": "24px"}),
            dbc.Input(id="login-username", placeholder="Username (e.g. scmanager)", type="text", style={"marginBottom": "16px", "backgroundColor": COLORS["background"], "color": COLORS["text_primary"], "border": "none"}),
            dbc.Input(id="login-password", placeholder="Password (e.g. sc123)", type="password", style={"marginBottom": "24px", "backgroundColor": COLORS["background"], "color": COLORS["text_primary"], "border": "none"}),
            dbc.Button("Login", id="login-btn", color="primary", style={"width": "100%", "marginBottom": "16px"}),
            html.Div(id="login-error", style={"marginTop": "16px"}),
        ])
    ]),

    # Dashboard Shell
    html.Div(id="dashboard-shell", style={"display": "none"}, children=[
        # Top Nav
    build_navbar(),

    # Body
    html.Div([
        # Left Sidebar
        build_sidebar(),

        # Main content
        html.Div(
            dash.page_container,
            id="page-content",
            style={
                "backgroundColor": COLORS["background"],
                "flex": "1",
                "overflowY": "auto",
                "padding": "24px 28px",
                "minHeight": "calc(100vh - 60px)",
            },
        ),

        # Right Copilot panel
        html.Div(
            id="copilot-wrapper",
            children=build_copilot_panel(),
            style={"display": "flex"},
        ),
    ], style={
        "display": "flex",
        "flex": "1",
        "overflow": "hidden",
        "height": "calc(100vh - 60px)",
    }),

        # Copilot FAB toggle
        dbc.Button(
            "🤖", id="copilot-toggle-btn", color="primary", size="sm",
            style={
                "position": "fixed", "right": "16px", "bottom": "24px", "zIndex": "999",
                "borderRadius": "50%", "width": "48px", "height": "48px",
                "fontSize": "1.3rem", "boxShadow": "0 4px 16px rgba(88,166,255,0.4)",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
            },
        ),
    ])
], style={"backgroundColor": COLORS["background"], "fontFamily": "Inter, sans-serif"})


# ── Callbacks ─────────────────────────────────────────────────────────────────

@callback(
    Output("auth-store",       "data"),
    Output("login-overlay",    "style"),
    Output("dashboard-shell",  "style"),
    Output("login-error",      "children"),
    Output("nav-user-display", "children"),
    Input("login-btn",  "n_clicks"),
    Input("logout-btn", "n_clicks"),
    State("login-username", "value"),
    State("login-password", "value"),
    State("auth-store", "data"),
    prevent_initial_call=True,
)
def handle_auth(login_clicks, logout_clicks, username, password, auth):
    triggered = ctx.triggered_id
    SHOW = {"display": "block"}
    HIDE = {"display": "none"}
    SHOW_FLEX = {"display": "flex", "justifyContent": "center", "alignItems": "center", "height": "100vh", "backgroundColor": COLORS["background"]}

    if triggered == "logout-btn":
        return (
            {"authenticated": False, "role": None, "username": None},
            SHOW_FLEX, HIDE, no_update, [html.Span("👤 Guest")]
        )

    uname = (username or "").strip().lower()
    uinfo = USERS.get(uname)
    if uinfo and uinfo["password"] == (password or "").strip():
        role = uinfo["role"]
        return (
            {"authenticated": True, "role": role, "username": uname},
            HIDE, SHOW, "",
            [html.Span(f"👤 {role}")]
        )
    else:
        err = html.Div("❌ Invalid credentials. Try scmanager / sc123", style={
            "background": "#ff4d4d22", "color": "#ff4d4d",
            "border": "1px solid #ff4d4d55", "borderRadius": "6px",
            "padding": "8px 12px", "fontSize": "0.8rem",
        })
        return (auth, SHOW_FLEX, HIDE, err, no_update)


@callback(
    Output("global-filter-store", "data"),
    Input("filter-horizon", "value"),
    Input("filter-region", "value"),
    Input("filter-category", "value"),
    State("global-filter-store", "data"),
    prevent_initial_call=True,
)
def update_global_store(horizon, region, category, current):
    current.update({"horizon": horizon, "region": region, "category": category})
    return current


@callback(
    Output("copilot-wrapper", "style"),
    Output("copilot-open-store", "data"),
    Input("copilot-toggle-btn", "n_clicks"),
    State("copilot-open-store", "data"),
    prevent_initial_call=True,
)
def toggle_copilot(n, is_open):
    new_open = not is_open
    display_style = {"display": "flex"} if new_open else {"display": "none"}
    return display_style, new_open


@callback(
    Output("copilot-response-area", "children"),
    Input("copilot-ask-btn", "n_clicks"),
    Input("quick-stockout", "n_clicks"),
    Input("quick-forecast", "n_clicks"),
    Input("quick-scenario", "n_clicks"),
    State("copilot-input", "value"),
    prevent_initial_call=True,
)
def handle_copilot_query(ask_clicks, stockout_clicks, forecast_clicks, scenario_clicks, query):
    import requests
    ctx = dash.callback_context
    if not ctx.triggered:
        return [_response_card(_CANNED_RESPONSES["default"])]

    trigger = ctx.triggered[0]["prop_id"]
    query_text = ""
    
    if "stockout" in trigger:
        query_text = "What is the current stockout risk?"
    elif "forecast" in trigger:
        query_text = "How is the forecast accuracy?"
    elif "scenario" in trigger:
        query_text = "Run demand surge scenario (+20%)"
    elif query:
        query_text = query
    else:
        return [_response_card(_CANNED_RESPONSES["default"])]
        
    try:
        # Call the new Financial Copilot endpoint
        resp = requests.post("http://localhost:8000/copilot/chat", json={
            "user_message": query_text,
            "active_dashboard": "Dashboard 6",
            "active_scenario": "Baseline",
            "user_role": "CFO",
            "region_filter": "GLOBAL"
        }, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            llm_text = data.get("response", "")
            citations = data.get("citations", [])
            model_used = data.get("model_used", "cache")
            
            # Format the response
            formatted_text = f"{llm_text}\n\n**Citations:** {', '.join(citations)}\n**Model:** {model_used}"
            
            return [_response_card({
                "text": formatted_text,
                "badge_color": COLORS["success"]
            })]
    except Exception as e:
        print(f"Backend error: {e}")
        
    # Fallback to canned responses if backend fails
    if any(w in query_text.lower() for w in ["stock", "shortage", "out"]):
        return [_response_card(_CANNED_RESPONSES["stockout"])]
    elif any(w in query_text.lower() for w in ["forecast", "accuracy", "mape", "wape"]):
        return [_response_card(_CANNED_RESPONSES["forecast"])]
    elif any(w in query_text.lower() for w in ["scenario", "surge", "demand", "simulate"]):
        return [_response_card(_CANNED_RESPONSES["scenario"])]
        
    return [_response_card({
        "text": f"Copilot backend unavailable. Raw input: {query_text}",
        "badge_color": COLORS["danger"]
    })]


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
