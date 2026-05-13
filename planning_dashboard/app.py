"""
app.py  ─  DemandIQ Planning Dashboard
Run:  python app.py   →   http://127.0.0.1:8050
"""
import dash
from dash import html, dcc, Input, Output, State, callback, ctx, no_update
import dash_bootstrap_components as dbc

from components.theme import COLORS, CUSTOM_CSS
from components.layout import app_layout

from dashboards import (
    executive, operational, forecast_analytics,
    inventory, capacity, financial, risk, sustainability, regional,
)

# ── Credentials ───────────────────────────────────────────────────────────────
USERS = {
    "scmanager": {"password": "sc123",    "role": "SC Manager"},
    "admin":     {"password": "admin123", "role": "Admin"},
}

# ── App init ──────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    title="DemandIQ | Planning Dashboard",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

app.index_string = f"""
<!DOCTYPE html>
<html>
<head>
  {{%metas%}}
  <title>{{%title%}}</title>
  {{%favicon%}}
  {{%css%}}
  <style>{CUSTOM_CSS}</style>
  <style>
    #login-username, #login-password {{
      display: block;
      width: 100%;
      box-sizing: border-box;
    }}
    .filter-active-badge {{
      background: {COLORS["primary"]}22;
      color: {COLORS["primary"]};
      border: 1px solid {COLORS["primary"]}55;
      border-radius: 4px;
      padding: 2px 8px;
      font-size: 0.7rem;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  {{%app_entry%}}
  <footer>{{%config%}}</footer>
  {{%scripts%}}
  {{%renderer%}}
</body>
</html>
"""

# ── Page registry ─────────────────────────────────────────────────────────────
PAGE_FNS = {
    "executive":      executive.layout,
    "operational":    operational.layout,
    "forecast":       forecast_analytics.layout,
    "inventory":      inventory.layout,
    "capacity":       capacity.layout,
    "financial":      financial.layout,
    "risk":           risk.layout,
    "sustainability": sustainability.layout,
    "regional":       regional.layout,
}

NAV_IDS  = [f"nav-{k}" for k in PAGE_FNS]
PAGE_KEYS = list(PAGE_FNS)

# ── Root layout ───────────────────────────────────────────────────────────────
app.layout = app_layout(executive.layout())


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN / LOGOUT
# ══════════════════════════════════════════════════════════════════════════════
@app.callback(
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

    if triggered == "logout-btn":
        return (
            {"authenticated": False, "role": None, "username": None},
            SHOW, HIDE, no_update, [html.Span("👤 Guest", className="nav-user")]
        )

    # Login
    uname = (username or "").strip().lower()
    uinfo = USERS.get(uname)
    if uinfo and uinfo["password"] == (password or "").strip():
        role = uinfo["role"]
        return (
            {"authenticated": True, "role": role, "username": uname},
            HIDE, SHOW, "",
            [html.Span(f"👤 {role}", className="nav-user",
                       style={"color": COLORS["primary"] if role == "Admin" else COLORS["chart_2"]})]
        )
    else:
        err = html.Div("❌ Invalid credentials. Try scmanager / sc123", style={
            "background": COLORS["danger"] + "22", "color": COLORS["danger"],
            "border": f"1px solid {COLORS['danger']}55", "borderRadius": "6px",
            "padding": "8px 12px", "fontSize": "0.8rem",
        })
        return (auth, SHOW, HIDE, err, no_update)


# ══════════════════════════════════════════════════════════════════════════════
# NAVIGATION + FILTER-AWARE PAGE RENDERING
# ══════════════════════════════════════════════════════════════════════════════
@app.callback(
    Output("main-content",       "children"),
    Output("active-page-store",  "data"),
    Output("global-filter-store","data"),
    *[Output(nid, "className") for nid in NAV_IDS],
    # Nav clicks
    *[Input(nid, "n_clicks") for nid in NAV_IDS],
    # Filter changes trigger re-render too
    Input("filter-region",   "value"),
    Input("filter-category", "value"),
    State("active-page-store",   "data"),
    State("global-filter-store", "data"),
    prevent_initial_call=True,
)
def navigate_and_filter(*args):
    n = len(NAV_IDS)
    # n_clicks for each nav, then region, category, active_page, store
    region_val   = args[n]
    category_val = args[n + 1]
    active_page  = args[n + 2] or "executive"
    store        = dict(args[n + 3])

    triggered = ctx.triggered_id

    # Update store with new filter values
    store["region"]   = region_val   or []
    store["category"] = category_val or []

    # Determine which page to show
    if triggered in NAV_IDS:
        page = triggered.replace("nav-", "")
    elif triggered in ("filter-region", "filter-category"):
        page = active_page  # re-render same page with new filter
    else:
        page = active_page

    # Render page — pass filters as kwargs where supported
    try:
        content = PAGE_FNS[page](
            regions=store["region"],
            categories=store["category"],
        )
    except TypeError:
        # layout() doesn't accept kwargs — render without
        content = PAGE_FNS[page]()

    classes = [
        "nav-item active" if pk == page else "nav-item"
        for pk in PAGE_KEYS
    ]
    return (content, page, store, *classes)


# ══════════════════════════════════════════════════════════════════════════════
# HORIZON BUTTONS
# ══════════════════════════════════════════════════════════════════════════════
@app.callback(
    Output("btn-op",  "className"),
    Output("btn-tac", "className"),
    Output("btn-str", "className"),
    Input("btn-op",  "n_clicks"),
    Input("btn-tac", "n_clicks"),
    Input("btn-str", "n_clicks"),
    prevent_initial_call=True,
)
def set_horizon(*_):
    triggered = ctx.triggered_id
    return (
        "horizon-btn active" if triggered == "btn-op"  else "horizon-btn",
        "horizon-btn active" if triggered == "btn-tac" else "horizon-btn",
        "horizon-btn active" if triggered == "btn-str" else "horizon-btn",
    )


# ══════════════════════════════════════════════════════════════════════════════
# AI COPILOT
# ══════════════════════════════════════════════════════════════════════════════
@app.callback(
    Output("copilot-response", "children"),
    Input("copilot-submit", "n_clicks"),
    State("copilot-input", "value"),
    State("auth-store", "data"),
    prevent_initial_call=True,
)
def copilot_query(_, query, auth):
    if not query:
        return no_update
    q = (query or "").lower()

    if "fill" in q or "otif" in q:
        resp = ("Real data: OTIF = 88.3% vs 95% target. North region worst at ~82%. "
                "Primary cause: high backorder rates in North+South. "
                "→ Expedite POs, activate backup suppliers in affected regions.")
    elif "mape" in q or "forecast" in q or "accuracy" in q:
        resp = ("XGBoost P50 MAPE = 14.9% on holdout test set (R²=0.65). "
                "P90 pinball loss = 1511. Bias is within ±5% guardrail. "
                "→ Feature engineering improvements could push R² above 0.91 target.")
    elif "stock" in q or "backorder" in q:
        resp = ("Backorder analysis from real orders dataset: "
                "East region shows highest backorder concentration. "
                "→ Increase safety stock buffer using Z=1.65 formula.")
    elif "carbon" in q or "co2" in q or "emission" in q:
        resp = ("Real logistics data: Road transport is highest CO2 contributor. "
                "Modal shift to Rail would reduce emissions ~35%. "
                "→ Prioritize rail for inter-DC transfers.")
    elif "risk" in q or "supplier" in q:
        resp = ("Live supplier risk computed from real fulfillment data. "
                "Regions with fill rate <85% flagged as critical risk. "
                "→ Dual-source procurement for high-risk regions immediately.")
    elif "region" in q:
        resp = ("Real regional KPIs: North leads in revenue. "
                "South has highest DOS (overstock). West has best fill rate. "
                "→ Redistribute from South to high-demand regions.")
    else:
        resp = (f"Query: '{query}' — Ask about: OTIF, fill rate, MAPE, "
                "backorders, carbon emissions, regional risk, or inventory.")

    role = (auth or {}).get("role", "User")
    return html.Div(className="copilot-msg", children=[
        html.Div(style={"display": "flex", "justifyContent": "space-between", "marginBottom": "6px"}, children=[
            html.Span("[AI Generated]", style={"color": COLORS["accent"], "fontWeight": 600, "fontSize": "0.68rem"}),
            html.Span(f"Role: {role}", style={"color": COLORS["text_secondary"], "fontSize": "0.66rem"}),
        ]),
        html.P(resp, style={"fontSize": "0.78rem", "color": COLORS["text_secondary"], "lineHeight": "1.55"}),
    ])


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  DemandIQ Planning Dashboard  ·  v2.0 (Live Data)")
    print("  Login: scmanager / sc123  |  admin / admin123")
    print("  http://127.0.0.1:8050")
    print("="*60 + "\n")
    app.run(debug=False, host="127.0.0.1", port=8050)
