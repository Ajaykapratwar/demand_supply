"""app.py — PlanIQ Dashboard entry point (Plotly Dash, blueprint §6.5)

Layout shell (blueprint §3.6):
  [Top Nav] → [Left Sidebar | Main Content | Right Copilot Panel]
"""
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback

from config import COLORS
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
        "businessUnit": "All",
        "scenario":     None,
    }),
    dcc.Store(id="copilot-open-store", data=True),

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
], style={"backgroundColor": COLORS["background"], "fontFamily": "Inter, sans-serif"})


# ── Callbacks ─────────────────────────────────────────────────────────────────

@callback(
    Output("global-filter-store", "data"),
    Input("filter-horizon", "value"),
    Input("filter-region", "value"),
    Input("filter-bu", "value"),
    State("global-filter-store", "data"),
    prevent_initial_call=True,
)
def update_global_store(horizon, region, bu, current):
    current.update({"horizon": horizon, "region": region, "businessUnit": bu})
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
    ctx = dash.callback_context
    if not ctx.triggered:
        return [_response_card(_CANNED_RESPONSES["default"])]

    trigger = ctx.triggered[0]["prop_id"]
    if "stockout" in trigger:
        resp = _CANNED_RESPONSES["stockout"]
    elif "forecast" in trigger:
        resp = _CANNED_RESPONSES["forecast"]
    elif "scenario" in trigger:
        resp = _CANNED_RESPONSES["scenario"]
    elif query:
        # Keyword matching for free-text queries
        q = query.lower()
        if any(w in q for w in ["stock", "shortage", "out"]):
            resp = _CANNED_RESPONSES["stockout"]
        elif any(w in q for w in ["forecast", "accuracy", "mape", "wape"]):
            resp = _CANNED_RESPONSES["forecast"]
        elif any(w in q for w in ["scenario", "surge", "demand", "simulate"]):
            resp = _CANNED_RESPONSES["scenario"]
        else:
            resp = _CANNED_RESPONSES["default"]
    else:
        resp = _CANNED_RESPONSES["default"]

    return [_response_card(resp)]


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
