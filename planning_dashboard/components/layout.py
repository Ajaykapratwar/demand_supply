"""
layout.py  ─  Shell layout: login page, top nav, sidebar, main, copilot.
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.theme import COLORS

# Real regions from dataset
REAL_REGIONS = ["North", "South", "East", "West", "Central"]
# AC Types from dataset
REAL_CATEGORIES = ["Split", "Window", "Portable", "Cassette", "Tower", "Central"]

NAV_ITEMS = [
    ("executive",      "📊", "Executive Summary"),
    ("operational",    "⚙️", "Operational Planning"),
    ("forecast",       "📈", "Forecast Analytics"),
    ("inventory",      "📦", "Inventory Optimization"),
    ("capacity",       "🏭", "Capacity Planning"),
    ("financial",      "💰", "Financial Impact"),
    ("risk",           "🛡️", "Risk Monitoring"),
    ("sustainability", "🌱", "Sustainability"),
    ("regional",       "🗺️", "Regional Planning"),
]

# ── Login Page ─────────────────────────────────────────────────────────────────
def login_page() -> html.Div:
    return html.Div(id="login-page", style={
        "minHeight": "100vh", "display": "flex", "alignItems": "center",
        "justifyContent": "center",
        "background": f"linear-gradient(135deg, {COLORS['background']} 0%, #0d1b2a 100%)",
    }, children=[
        html.Div(style={
            "background": COLORS["card"], "border": f"1px solid {COLORS['border']}",
            "borderRadius": "16px", "padding": "48px 40px", "width": "380px",
            "boxShadow": "0 24px 80px rgba(0,0,0,0.5)",
        }, children=[
            # Logo
            html.Div(style={"textAlign": "center", "marginBottom": "32px"}, children=[
                html.Div("⚡", style={"fontSize": "2.5rem", "marginBottom": "8px"}),
                html.H1("DemandIQ", style={"color": COLORS["primary"], "fontSize": "1.8rem",
                                            "fontWeight": 800, "margin": 0, "letterSpacing": "-0.02em"}),
                html.P("AI-Powered Planning Dashboard",
                       style={"color": COLORS["text_secondary"], "fontSize": "0.82rem", "margin": "4px 0 0"}),
            ]),
            # Error message
            html.Div(id="login-error", style={"marginBottom": "16px"}),
            # Username
            html.Div(style={"marginBottom": "16px"}, children=[
                html.Label("Username", style={"fontSize": "0.76rem", "color": COLORS["text_secondary"],
                                               "display": "block", "marginBottom": "6px", "fontWeight": 600}),
                dcc.Input(id="login-username", type="text", placeholder="scmanager",
                          value="scmanager", style={
                    "width": "100%", "background": COLORS["surface"],
                    "border": f"1px solid {COLORS['border']}", "borderRadius": "8px",
                    "padding": "10px 14px", "color": COLORS["text_primary"],
                    "fontSize": "0.9rem", "outline": "none", "boxSizing": "border-box",
                }),
            ]),
            # Password
            html.Div(style={"marginBottom": "24px"}, children=[
                html.Label("Password", style={"fontSize": "0.76rem", "color": COLORS["text_secondary"],
                                               "display": "block", "marginBottom": "6px", "fontWeight": 600}),
                dcc.Input(id="login-password", type="password", placeholder="••••••",
                          value="sc123", style={
                    "width": "100%", "background": COLORS["surface"],
                    "border": f"1px solid {COLORS['border']}", "borderRadius": "8px",
                    "padding": "10px 14px", "color": COLORS["text_primary"],
                    "fontSize": "0.9rem", "outline": "none", "boxSizing": "border-box",
                }),
            ]),
            # Login button
            html.Button("Sign In →", id="login-btn", n_clicks=0, style={
                "width": "100%", "padding": "12px", "background": COLORS["primary"],
                "color": "#fff", "border": "none", "borderRadius": "8px",
                "fontSize": "0.92rem", "fontWeight": 700, "cursor": "pointer",
                "letterSpacing": "0.02em",
            }),
            # Default credentials hint
            html.Div(style={"marginTop": "20px", "padding": "12px", "background": COLORS["surface"],
                            "borderRadius": "8px", "border": f"1px solid {COLORS['border']}"}, children=[
                html.P("Default Credentials", style={"fontSize": "0.7rem", "fontWeight": 700,
                       "color": COLORS["text_secondary"], "margin": "0 0 6px", "textTransform": "uppercase"}),
                html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "4px"}, children=[
                    _cred_row("SC Manager", "scmanager / sc123"),
                    _cred_row("Admin",      "admin / admin123"),
                ]),
            ]),
        ]),
    ])

def _cred_row(role, cred):
    return html.Div(style={"fontSize": "0.72rem"}, children=[
        html.Span(role + ": ", style={"color": COLORS["text_secondary"]}),
        html.Span(cred, style={"color": COLORS["primary"], "fontFamily": "JetBrains Mono,monospace"}),
    ])

# ── Sidebar ────────────────────────────────────────────────────────────────────
def sidebar(role: str = "SC Manager") -> html.Div:
    role_badge_color = COLORS["primary"] if role == "Admin" else COLORS["chart_2"]
    items = [
        html.Div(style={"padding": "12px 16px", "borderBottom": f"1px solid {COLORS['border']}",
                         "marginBottom": "8px"}, children=[
            html.Div("⚡ DemandIQ", style={"fontWeight": 800, "fontSize": "1rem", "color": COLORS["primary"],
                                             "marginBottom": "4px"}),
            html.Div(role, style={"fontSize": "0.7rem", "background": role_badge_color + "22",
                                   "color": role_badge_color, "padding": "2px 8px",
                                   "borderRadius": "4px", "display": "inline-block", "fontWeight": 600}),
        ]),
        html.Div("PLANNING VIEWS", className="sidebar-section"),
    ]
    for page_id, icon, label in NAV_ITEMS:
        items.append(html.Div(
            id=f"nav-{page_id}", className="nav-item",
            children=[html.Span(icon, className="nav-icon"), html.Span(label)],
            n_clicks=0,
        ))
    items.append(html.Div(style={"position": "absolute", "bottom": "12px", "left": "12px", "right": "12px"}, children=[
        html.Button("← Logout", id="logout-btn", n_clicks=0, style={
            "width": "100%", "background": "transparent", "border": f"1px solid {COLORS['border']}",
            "color": COLORS["text_secondary"], "padding": "8px", "borderRadius": "6px",
            "cursor": "pointer", "fontSize": "0.76rem",
        }),
    ]))
    return html.Div(id="sidebar", style={"position": "relative"}, children=items)


# ── Top Nav ────────────────────────────────────────────────────────────────────
def top_nav() -> html.Div:
    return html.Div(id="top-nav", children=[
        html.Div(style={"display": "flex", "alignItems": "center", "gap": "6px"}, children=[
            html.Span("⚡", style={"color": COLORS["primary"]}),
            html.Span("DemandIQ", style={"fontWeight": 700, "color": COLORS["primary"]}),
            html.Span(" | Planning Dashboard",
                      style={"color": COLORS["text_secondary"], "fontWeight": 400, "fontSize": "0.82rem"}),
        ], className="brand"),
        # Horizon buttons
        html.Div([
            html.Button("Operational", id="btn-op",  className="horizon-btn active"),
            html.Button("Tactical",    id="btn-tac", className="horizon-btn"),
            html.Button("Strategic",   id="btn-str", className="horizon-btn"),
        ], style={"display": "flex", "gap": "6px"}),
        html.Div(className="nav-sep"),
        # Global filters
        dcc.Dropdown(
            id="filter-region",
            options=[{"label": r, "value": r} for r in REAL_REGIONS],
            value=None, placeholder="All Regions", multi=True, clearable=True,
            style={"width": "180px", "fontSize": "0.8rem"},
        ),
        dcc.Dropdown(
            id="filter-category",
            options=[{"label": c, "value": c} for c in REAL_CATEGORIES],
            value=None, placeholder="All AC Types", multi=True, clearable=True,
            style={"width": "180px", "fontSize": "0.8rem"},
        ),
        html.Div(id="nav-alert-badge", children=[
            html.Span("⚠ 3 Alerts", className="nav-badge"),
        ]),
        html.Div(id="nav-user-display",
                 children=[html.Span("👤 SC Manager", className="nav-user")]),
    ])


# ── Copilot ────────────────────────────────────────────────────────────────────
def copilot_panel() -> html.Div:
    return html.Div(id="copilot-panel", children=[
        html.Div(["✨ ", "AI COPILOT"], className="copilot-title"),
        html.Div(id="copilot-narrative", children=[
            html.Div(className="copilot-msg", children=[
                html.Span("[AI Generated] ", style={"color": COLORS["accent"],
                                                     "fontWeight": 600, "fontSize": "0.68rem"}),
                html.Span(
                    "Fill rate 88.3% vs 95% target — check North & South regions. "
                    "Model MAPE = 14.9% (XGBoost P50 on test set). "
                    "CO2 from logistics is the primary Scope 3 driver.",
                    style={"fontSize": "0.8rem", "color": COLORS["text_secondary"]}
                ),
            ]),
        ]),
        html.Div(style={"marginTop": "12px"}, children=[
            html.P("Ask a question:", style={"fontSize": "0.72rem",
                                              "color": COLORS["text_secondary"], "marginBottom": "6px"}),
            dcc.Textarea(id="copilot-input", placeholder="e.g. Why is fill rate low in North?",
                         className="copilot-query", style={"height": "70px"}),
            html.Button("Ask →", id="copilot-submit", style={
                "marginTop": "6px", "width": "100%",
                "background": COLORS["primary"] + "22",
                "border": f"1px solid {COLORS['primary']}55",
                "color": COLORS["primary"], "padding": "6px 12px",
                "borderRadius": "6px", "cursor": "pointer",
                "fontSize": "0.8rem", "fontFamily": "Inter, sans-serif",
            }),
        ]),
        html.Div(id="copilot-response", style={"marginTop": "12px"}),
        html.Div(style={"marginTop": "16px"}, children=[
            html.P("RECENT ALERTS", style={"fontSize": "0.68rem", "fontWeight": 600,
                                            "letterSpacing": "0.06em",
                                            "color": COLORS["text_secondary"], "marginBottom": "8px"}),
            _alert_item("🔴", "North fill rate 82% — critical", "critical"),
            _alert_item("🟡", "South DOS 52d — overstock risk", "warning"),
            _alert_item("🔴", "Supplier backorder spike East", "critical"),
            _alert_item("🟡", "Forecast MAPE 14.9% approaching 15%", "warning"),
        ]),
    ])

def _alert_item(icon, text, level):
    color = COLORS["danger"] if level == "critical" else COLORS["warning"]
    return html.Div(style={"display": "flex", "gap": "8px", "padding": "7px 0",
                           "borderBottom": f"1px solid {COLORS['border']}",
                           "fontSize": "0.76rem"}, children=[
        html.Span(icon), html.Span(text, style={"color": color}),
    ])


# ── App Shell ──────────────────────────────────────────────────────────────────
def app_layout(page_content) -> html.Div:
    return html.Div(id="root-container", children=[
        # Login overlay (shown when not authenticated)
        html.Div(id="login-overlay", children=[login_page()]),
        # Main dashboard (hidden until logged in)
        html.Div(id="dashboard-shell", style={"display": "none"}, children=[
            top_nav(),
            html.Div(id="app-layout", children=[
                sidebar(),
                html.Div(id="main-content", children=[page_content]),
                copilot_panel(),
            ]),
        ]),
        # Stores
        dcc.Store(id="active-page-store", data="executive"),
        dcc.Store(id="global-filter-store", data={
            "horizon": "operational", "region": [], "category": [], "scenario": None,
        }),
        dcc.Store(id="auth-store", data={"authenticated": False, "role": None, "username": None}),
    ])
