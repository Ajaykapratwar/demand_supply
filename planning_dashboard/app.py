"""
app.py  ─  DemandIQ Planning Dashboard
AI-Powered Demand-Supply & Matching Planning Dashboard (blueprint v1.0)

Run:  python app.py
Open: http://127.0.0.1:8050
"""
import dash
from dash import html, dcc, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc

from components.theme import COLORS, CUSTOM_CSS
from components.layout import app_layout

# ── Import all 9 dashboards ───────────────────────────────────────────────────
from dashboards import (
    executive, operational, forecast_analytics,
    inventory, capacity, financial, risk, sustainability, regional,
)

# ─────────────────────────────────────────────────────────────────────────────
# App initialisation
# ─────────────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    title="DemandIQ | Planning Dashboard",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description",
         "content": "AI-Powered Demand-Supply & Matching Planning Dashboard"},
    ],
)
server = app.server   # WSGI entry-point for production

# Inject custom CSS as a <style> block
app.index_string = f"""
<!DOCTYPE html>
<html>
<head>
  {{%metas%}}
  <title>{{%title%}}</title>
  {{%favicon%}}
  {{%css%}}
  <style>{CUSTOM_CSS}</style>
</head>
<body>
  {{%app_entry%}}
  <footer>{{%config%}}</footer>
  {{%scripts%}}
  {{%renderer%}}
</body>
</html>
"""

# ─────────────────────────────────────────────────────────────────────────────
# Page registry
# ─────────────────────────────────────────────────────────────────────────────
PAGES = {
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

NAV_IDS = [
    "nav-executive", "nav-operational", "nav-forecast",
    "nav-inventory", "nav-capacity", "nav-financial",
    "nav-risk", "nav-sustainability", "nav-regional",
]

PAGE_KEYS = [
    "executive", "operational", "forecast",
    "inventory", "capacity", "financial",
    "risk", "sustainability", "regional",
]

# ─────────────────────────────────────────────────────────────────────────────
# Root layout
# ─────────────────────────────────────────────────────────────────────────────
app.layout = app_layout(executive.layout())


# ─────────────────────────────────────────────────────────────────────────────
# Callbacks
# ─────────────────────────────────────────────────────────────────────────────

@app.callback(
    Output("main-content", "children"),
    Output("active-page-store", "data"),
    *[Output(nav_id, "className") for nav_id in NAV_IDS],
    *[Input(nav_id, "n_clicks") for nav_id in NAV_IDS],
    State("active-page-store", "data"),
    prevent_initial_call=True,
)
def navigate(*args):
    """Switch dashboard view when sidebar item clicked."""
    n_clicks_list = args[:len(NAV_IDS)]
    active_page   = args[-1]

    triggered = ctx.triggered_id
    if not triggered:
        page = active_page or "executive"
    else:
        # "nav-executive" → "executive"
        page = triggered.replace("nav-", "")

    content = PAGES.get(page, executive.layout)()
    classes = [
        "nav-item active" if pk == page else "nav-item"
        for pk in PAGE_KEYS
    ]
    return (content, page, *classes)


@app.callback(
    Output("copilot-response", "children"),
    Input("copilot-submit", "n_clicks"),
    State("copilot-input", "value"),
    prevent_initial_call=True,
)
def copilot_query(n_clicks: int, query: str):
    """Simulate AI copilot response (template-based fallback per §5.8)."""
    if not query:
        return dash.no_update

    # Rule-based responses matching common query intents
    q = query.lower().strip()
    if "apac" in q and ("fill" in q or "low" in q):
        response = ("APAC fill rate is 94.8% vs 98% target. Root cause: "
                    "SUP-07 reliability dropped to 68% (lead time +10d). "
                    "Recommend: activate backup SUP-03 immediately. "
                    "Expected recovery: +2.1pp fill rate in 14 days.")
    elif "stockout" in q or "sku-000" in q.lower():
        response = ("SKU-0003 (APAC) has 7-day stockout horizon. "
                    "On-hand: 420 units. Daily demand: 60 units. "
                    "Nearest supply: PO #4421 ETA +12 days. "
                    "→ Expedite PO or transfer 300 units from EMEA DC.")
    elif "mape" in q or "forecast" in q:
        response = ("Portfolio MAPE = 17.8% (target 15%). "
                    "Worst segments: Automotive +28%, Electronics +22%. "
                    "FVA shows planner overrides added +1.6pp on Apparel. "
                    "→ Re-calibrate Apparel promo uplift model.")
    elif "carbon" in q or "emission" in q or "sustainab" in q:
        response = ("Scope 2 emissions 1,840 tCO2e — 2.2% above target. "
                    "Transportation is largest contributor (32%). "
                    "Solar PV at Plant-A on track for 240 tCO2e reduction by Q4. "
                    "→ Accelerate modal shift rail initiative to close gap.")
    elif "scenario" in q or "surge" in q or "demand surge" in q:
        response = ("Demand Surge +30% scenario: total cost +$450K, "
                    "service level −2.1%, carbon +120 tCO2e. "
                    "Flex capacity contract at Plant-B can absorb 18% of surge. "
                    "→ Pre-position 15 DOS buffer in APAC DC.")
    elif "risk" in q or "supplier" in q:
        response = ("Highest risk: SUP-07 (score 0.91/critical). "
                    "Key drivers: reliability 68%, OTD 72%, single-source for SKU-0003. "
                    "SHAP: reliability (42%), concentration_risk (38%), lead_time_cv (20%). "
                    "→ Dual-source with SUP-05 within 30 days.")
    else:
        response = (f"Query received: '{query}'. "
                    "For best results, ask about: fill rate, stockouts, MAPE, "
                    "scenarios, carbon emissions, or supplier risk.")

    return html.Div(className="copilot-msg", children=[
        html.Div(style={"display": "flex", "justifyContent": "space-between",
                        "marginBottom": "6px"}, children=[
            html.Span("[AI Generated]",
                      style={"color": COLORS["accent"], "fontWeight": 600,
                             "fontSize": "0.68rem"}),
            html.Span("Template Mode",
                      style={"color": COLORS["text_secondary"], "fontSize": "0.66rem"}),
        ]),
        html.P(response, style={"fontSize": "0.78rem", "color": COLORS["text_secondary"],
                                "lineHeight": "1.55"}),
    ])


@app.callback(
    Output("btn-op",  "className"),
    Output("btn-tac", "className"),
    Output("btn-str", "className"),
    Output("global-filter-store", "data"),
    Input("btn-op",  "n_clicks"),
    Input("btn-tac", "n_clicks"),
    Input("btn-str", "n_clicks"),
    State("global-filter-store", "data"),
    prevent_initial_call=True,
)
def set_horizon(n_op, n_tac, n_str, store):
    """Highlight active horizon button and update store."""
    triggered = ctx.triggered_id
    horizon_map = {"btn-op": "operational", "btn-tac": "tactical", "btn-str": "strategic"}
    horizon = horizon_map.get(triggered, "operational")
    store["horizon"] = horizon
    return (
        "horizon-btn active" if horizon == "operational" else "horizon-btn",
        "horizon-btn active" if horizon == "tactical"    else "horizon-btn",
        "horizon-btn active" if horizon == "strategic"   else "horizon-btn",
        store,
    )


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  DemandIQ Planning Dashboard  ·  v1.0")
    print("  Blueprint: §6.5 Plotly Dash stack")
    print("  http://127.0.0.1:8050")
    print("="*60 + "\n")
    app.run(debug=False, host="127.0.0.1", port=8050)
