"""app.py — PlanIQ Dashboard entry point (Plotly Dash, blueprint §6.5)

Layout shell (blueprint §3.6):
  [Top Nav] → [Left Sidebar | Main Content | Right Copilot Panel]
"""
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback, ctx, no_update, MATCH, ALL

from config import COLORS, USERS
from components.navbar import build_topbar, build_sidebar
from components.copilot import build_copilot_panel, _CANNED_RESPONSES, _response_card
from components.approval_drawer import approval_drawer_layout, register_approval_callbacks
from components.collaboration import get_presence_indicators, sop_wizard_modal, register_collaboration_callbacks
from components.insight_feed import insight_feed_layout
from services.briefing_generator import trigger_executive_briefing
import requests
import datetime
import os

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
        html.Div(style={
            "padding": "40px",
            "backgroundColor": COLORS["surface"],
            "borderRadius": "14px",
            "width": "380px",
            "border": f"1px solid {COLORS['border']}",
            "boxShadow": "0 24px 64px rgba(0,0,0,0.6)",
        }, children=[
            # Logo
            html.Div([
                html.Div(style={
                    "width": "40px", "height": "40px", "borderRadius": "10px",
                    "background": "linear-gradient(135deg, #3b82f6, #8b5cf6)",
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                    "marginRight": "12px",
                }, children=html.Span("P", style={"color": "#fff", "fontWeight": "800", "fontSize": "1.2rem"})),
                html.Div([
                    html.Div("PlanIQ", style={"fontWeight": "800", "fontSize": "1.1rem", "color": COLORS["text_primary"], "letterSpacing": "-0.01em"}),
                    html.Div("AI Planning Dashboard", style={"fontSize": "0.75rem", "color": COLORS["text_secondary"]}),
                ]),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "32px"}),

            html.Div("Username", style={"fontSize": "0.72rem", "fontWeight": "700", "color": COLORS["text_secondary"], "letterSpacing": "0.07em", "textTransform": "uppercase", "marginBottom": "6px"}),
            dbc.Input(id="login-username", placeholder="e.g. scmanager", type="text",
                      style={"marginBottom": "16px", "backgroundColor": COLORS["card"],
                             "color": COLORS["text_primary"], "border": f"1px solid {COLORS['border']}",
                             "borderRadius": "7px", "fontSize": "0.85rem", "padding": "10px 14px"}),
            html.Div("Password", style={"fontSize": "0.72rem", "fontWeight": "700", "color": COLORS["text_secondary"], "letterSpacing": "0.07em", "textTransform": "uppercase", "marginBottom": "6px"}),
            dbc.Input(id="login-password", placeholder="e.g. sc123", type="password",
                      style={"marginBottom": "24px", "backgroundColor": COLORS["card"],
                             "color": COLORS["text_primary"], "border": f"1px solid {COLORS['border']}",
                             "borderRadius": "7px", "fontSize": "0.85rem", "padding": "10px 14px"}),
            dbc.Button([html.I(className="bi bi-box-arrow-in-right", style={"marginRight": "8px"}), "Sign In"],
                       id="login-btn", color="primary",
                       style={"width": "100%", "fontWeight": "700", "borderRadius": "7px",
                              "padding": "10px", "fontSize": "0.88rem"}),
            html.Div(id="login-error", style={"marginTop": "14px"}),
        ])
    ]),

    # Dashboard Shell
    html.Div(id="dashboard-shell", style={"display": "none"}, children=[
        html.Div(id="app-shell", children=[
            # Left Sidebar
            build_sidebar(),
            
            # Main Area
            html.Div(id="main-area", children=[
                # Top Navbar
                build_topbar(),
                
                # UI overlays (Modals, Drawers)
                sop_wizard_modal(),
                approval_drawer_layout(),
                
                # Body Content
                html.Div(id="page-content", children=[
                    dash.page_container,
                ]),

                # Download components
                dcc.Download(id="download-briefing-pdf"),
                html.Div(id="email-toast-container", style={"position": "fixed", "top": "80px", "right": "20px", "zIndex": "9999"}),
            ]),
            
            # Right Copilot Panel (slides out inside main-area or app-shell)
            html.Div(
                id="copilot-wrapper",
                children=build_copilot_panel(),
                style={"display": "none", "height": "100vh"},
            ),
        ]),

        # Copilot FAB toggle
        dbc.Button(
            html.I(className="bi bi-stars"),
            id="copilot-toggle-btn", color="primary", size="sm",
            style={
                "position": "fixed", "right": "24px", "bottom": "24px", "zIndex": "999",
                "borderRadius": "50%", "width": "48px", "height": "48px",
                "fontSize": "18px",
                "background": "linear-gradient(135deg, var(--primary), var(--accent))",
                "border": "none",
                "boxShadow": "0 4px 20px rgba(79, 110, 247, 0.4)",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
                "padding": "0",
            },
        ),
    ])
], id="root-container")


# ── Callbacks ─────────────────────────────────────────────────────────────────

# Register new component callbacks
register_approval_callbacks(app)
register_collaboration_callbacks(app)

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
    SHOW = {"display": "flex", "flexDirection": "column"}
    HIDE = {"display": "none"}
    SHOW_FLEX = {"display": "flex", "justifyContent": "center", "alignItems": "center", "height": "100vh"}

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
    Input({"type": "kpi-copilot-btn", "index": ALL}, "n_clicks"),
    State("copilot-open-store", "data"),
    prevent_initial_call=True,
)
def toggle_copilot(toggle_n, kpi_n_clicks, is_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update
    
    trigger = ctx.triggered[0]["prop_id"]
    
    # If triggered by a KPI button, always open the drawer
    if "kpi-copilot-btn" in trigger:
        return {"display": "flex"}, True
        
    new_open = not is_open
    display_style = {"display": "flex"} if new_open else {"display": "none"}
    return display_style, new_open

@callback(
    Output("copilot-response-area", "children"),
    Input("copilot-ask-btn", "n_clicks"),
    Input("quick-stockout", "n_clicks"),
    Input("quick-forecast", "n_clicks"),
    Input("quick-scenario", "n_clicks"),
    Input({"type": "kpi-copilot-btn", "index": ALL}, "n_clicks"),
    State("copilot-input", "value"),
    State("global-filter-store", "data"),
    State("ai-collaboration-mode", "value"),
    prevent_initial_call=True,
)
def handle_copilot_query(ask_clicks, stockout_clicks, forecast_clicks, scenario_clicks, kpi_clicks, query, filter_store, ai_mode):
    ctx = dash.callback_context
    if not ctx.triggered:
        return [_response_card(_CANNED_RESPONSES["default"])]

    trigger = ctx.triggered[0]["prop_id"]
    active_q = query
    if "stockout" in trigger:
        active_q = "What is the stockout risk?"
    elif "forecast" in trigger:
        active_q = "What is the forecast accuracy?"
    elif "scenario" in trigger:
        active_q = "Run demand surge +20% scenario"
    elif "kpi-copilot-btn" in trigger:
        import json
        try:
            kpi_index = json.loads(trigger.split(".")[0])["index"]
            KPI_COPILOT_PROMPTS = {
              "EVA":              "Explain our current Economic Value Added and what's driving it.",
              "ROIC":             "What is our Return on Invested Capital and how does it compare to target?",
              "Cash-to-Cash":     "Show me cash-to-cash cycle trend and what's causing any variance.",
              "Gross Margin":     "Why did gross margin change this period? Break down the key drivers.",
              "Carrying Cost":    "What is our inventory carrying cost and where are the biggest overstock risks?",
              "Logistics % Rev":  "Show our supply chain cost as % of sales vs industry benchmark.",
            }
            active_q = KPI_COPILOT_PROMPTS.get(kpi_index, f"Explain the current status of {kpi_index}.")
        except:
            pass
        
    if not active_q:
        return [_response_card(_CANNED_RESPONSES["default"])]
        
    # Call the backend Copilot API (Now connected to Groq)
    try:
        from data.data_loader import get_executive_kpis
        import requests
        
        region = filter_store.get("region", "Global")
        kpis = get_executive_kpis(region=region, category="All")
            
        context_str = f"Here is the current HVAC dashboard data for Region: {region}:\n"
        for k, v in kpis.items():
            context_str += f"- {k}: {v.get('value')} {v.get('unit', '')} (Target: {v.get('target')})\n"
            
        role_instructions = {
            "analyst": "You are a deeply analytical Data Analyst. Focus strictly on numbers, trends, statistical variances, and root causes. Be extremely detailed with figures.",
            "decision_maker": "You are a strategic Executive Decision Maker. Focus on bottom-line impact, risks, and high-level actionable recommendations. Be concise and business-focused.",
            "coach": "You are a helpful Supply Chain Coach. Explain the concepts behind the metrics, ask guiding questions to the user, and suggest what they should look into next to improve their skills."
        }
        persona = role_instructions.get(ai_mode, role_instructions["decision_maker"])
            
        groq_payload = {
            "model": "llama-3.3-70b-versatile", 
            "messages": [
                {"role": "system", "content": f"{persona} Provide concise, insightful answers based on the provided data context. Keep responses under 4 sentences."},
                {"role": "user", "content": f"Context:\n{context_str}\n\nUser query: {active_q}"}
            ]
        }
        
        headers = {
            
            "Authorization": f"Bearer {os.environ.get('GROQ_API_KEY', '')}",
            "Content-Type": "application/json"
        }
        
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=groq_payload, timeout=15)
        
        if res.status_code == 200:
            data = res.json()
            reply = data["choices"][0]["message"]["content"]
            model_used = data["model"]
            resp = {
                "text": f"{reply}\n\n*Tools used: Live Dashboard Data*\n*Model: {model_used}*",
                "badge_color": COLORS["primary"]
            }
        else:
            resp = {
                "text": f"Error connecting to AI: {res.text}",
                "badge_color": COLORS["danger"]
            }
            
    except Exception as e:
        resp = {
            "text": f"Backend Error: {str(e)}",
            "badge_color": COLORS["danger"]
        }
        
    return [_response_card(resp)]


@callback(
    Output("download-briefing-pdf", "data"),
    Input("btn-export-pdf", "n_clicks"),
    State("global-filter-store", "data"),
    prevent_initial_call=True,
)
def export_dashboard_report(n_clicks, filter_data):
    if not n_clicks:
        return no_update
    
    # Prepare context data for the report
    region = filter_data.get("region", "Global") if filter_data else "Global"
    category = filter_data.get("category", "All") if filter_data else "All"
    
    from data.data_loader import get_executive_kpis, get_financial_summary, get_forecast_accuracy_kpis
    
    context = {
        "timestamp": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
        "region": region,
        "category": category,
        "exec_kpis": get_executive_kpis(region, category),
        "fin_kpis": get_financial_summary(region, category),
        "fcst_kpis": get_forecast_accuracy_kpis(region, category),
    }
    
    success, filepath = trigger_executive_briefing(context)
    
    if success:
        return dcc.send_file(filepath)
    return no_update


@callback(
    Output("email-toast-container", "children"),
    Input("btn-email-alert", "n_clicks"),
    State("global-filter-store", "data"),
    prevent_initial_call=True,
)
def send_email_alert(n_clicks, filter_data):
    if not n_clicks:
        return no_update
        
    region = filter_data.get("region", "Global") if filter_data else "Global"
    category = filter_data.get("category", "All") if filter_data else "All"
    
    from data.data_loader import get_executive_kpis, get_financial_summary, get_forecast_accuracy_kpis, get_action_queue
    from services.email_service import send_alert_email
    
    # Check for critical alerts to include in email body
    queue = get_action_queue(region, category)
    critical_alerts = [item for item in queue if item.get("priority") == "CRITICAL"]
    
    body = f"PlanIQ Dashboard Alert for {region} - {category}\n\n"
    if critical_alerts:
        body += "CRITICAL ALERTS DETECTED:\n"
        for alert in critical_alerts:
            body += f"- {alert['sku']}: {alert['issue']} -> {alert['action']}\n"
    else:
        body += "No critical alerts at this time.\n"
        
    body += "\nPlease find the fully detailed KPI report attached.\n\nPlanIQ Automated System"
    
    context = {
        "timestamp": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
        "region": region,
        "category": category,
        "exec_kpis": get_executive_kpis(region, category),
        "fin_kpis": get_financial_summary(region, category),
        "fcst_kpis": get_forecast_accuracy_kpis(region, category),
    }
    
    success, filepath = trigger_executive_briefing(context)
    
    if success:
        email_sent, msg = send_alert_email("hufeh9299@gmail.com", f"PlanIQ Alert - {region}", body, filepath)
        
        icon = "bi-check-circle text-success" if email_sent else "bi-exclamation-circle text-danger"
        header = "Email Sent" if email_sent else "Email Failed"
        
        return dbc.Toast(
            [html.P(msg, className="mb-0")],
            id="email-toast",
            header=html.Div([html.I(className=f"bi {icon} me-2"), header]),
            is_open=True,
            dismissable=True,
            duration=4000,
            icon="primary" if email_sent else "danger",
            style={"position": "fixed", "top": "66px", "right": "10px", "width": 350, "zIndex": 9999}
        )
    
    return dbc.Toast(
        [html.P("Failed to generate report for email.", className="mb-0")],
        id="email-toast",
        header=html.Div([html.I(className="bi bi-exclamation-circle text-danger me-2"), "Error"]),
        is_open=True,
        dismissable=True,
        duration=4000,
        icon="danger",
        style={"position": "fixed", "top": "66px", "right": "10px", "width": 350, "zIndex": 9999}
    )


import threading
import time

def automated_alert_job():
    # Wait 15 seconds after app starts to simulate a background system check
    time.sleep(15)
    from data.data_loader import get_executive_kpis, get_financial_summary, get_forecast_accuracy_kpis, get_action_queue
    from services.email_service import send_alert_email
    
    region = "Global"
    category = "All"
    queue = get_action_queue(region, category)
    critical_alerts = [item for item in queue if item.get("priority") == "CRITICAL"]
    
    if critical_alerts:
        print("[Automated System] Critical conditions detected. Generating automated email alert...")
        body = f"AUTOMATED SYSTEM ALERT - {region}\n\nCRITICAL CONDITIONS DETECTED:\n"
        for alert in critical_alerts:
            body += f"- {alert['sku']}: {alert['issue']} -> {alert['action']}\n"
        
        body += "\nDetailed KPI report is attached. Please review immediately.\n\nPlanIQ Background Monitor"
        
        context = {
            "timestamp": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
            "region": region,
            "category": category,
            "exec_kpis": get_executive_kpis(region, category),
            "fin_kpis": get_financial_summary(region, category),
            "fcst_kpis": get_forecast_accuracy_kpis(region, category),
        }
        
        success, filepath = trigger_executive_briefing(context)
        if success:
            email_sent, _ = send_alert_email("hufeh9299@gmail.com", "URGENT: PlanIQ Automated Critical Alert", body, filepath)
            if email_sent:
                print("[Automated System] Automated alert email sent successfully.")

# Start the automated background monitor
threading.Thread(target=automated_alert_job, daemon=True).start()

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
