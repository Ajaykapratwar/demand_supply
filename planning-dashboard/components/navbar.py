"""components/navbar.py — Sidebar + Topbar layout components"""
import dash_bootstrap_components as dbc
from dash import dcc, html
from config import COLORS, NAV_ITEMS, HORIZONS, REGIONS, CATEGORIES
from components.insight_feed import insight_feed_layout
from components.collaboration import get_presence_indicators

_LABEL_STYLE = {
    "color": "var(--text-2)",
    "fontSize": "11px",
    "fontWeight": "600",
    "letterSpacing": "0.05em",
    "textTransform": "uppercase",
    "marginBottom": "6px",
}

_NAV_ICONS = {
    "/":               "bi-grid-1x2",
    "/operational":    "bi-sliders",
    "/forecast":       "bi-graph-up-arrow",
    "/inventory":      "bi-box-seam",
    "/capacity":       "bi-building",
    "/financial":      "bi-currency-dollar",
    "/risk":           "bi-shield-check",
    "/sustainability": "bi-tree",
    "/regional":       "bi-globe2",
}

def build_sidebar():
    return html.Div([
        # ── Brand ──────────────────────────────────────────
        html.Div([
            html.A([
                html.Div(style={
                    "width": "28px", "height": "28px",
                    "background": "linear-gradient(135deg, var(--primary), var(--accent))",
                    "borderRadius": "var(--radius-sm)",
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                    "marginRight": "10px", "flexShrink": "0",
                }, children=html.Span("P", style={
                    "color": "#fff", "fontWeight": "800", "fontSize": "14px", "lineHeight": "1",
                })),
                html.Div([
                    html.Span("PlanIQ", style={
                        "fontWeight": "700", "fontSize": "16px",
                        "color": "var(--text-1)", "letterSpacing": "-0.01em",
                    }),
                ]),
            ], href="/", style={"textDecoration": "none", "display": "flex", "alignItems": "center"})
        ], style={"padding": "20px"}),

        # ── Nav Section ────────────────────────────────────────
        html.Div("Navigation", style={**_LABEL_STYLE, "padding": "10px 20px"}),
        html.Div([
            dbc.NavLink(
                [
                    html.I(
                        className=f"bi {_NAV_ICONS.get(item['href'], 'bi-circle')}",
                        style={"fontSize": "15px", "width": "20px", "flexShrink": "0"},
                    ),
                    html.Span(item["label"], style={"fontSize": "13px"}),
                ],
                href=item["href"],
                active="exact",
                className="nav-link"
            )
            for item in NAV_ITEMS
        ]),

        html.Hr(style={"borderColor": "var(--border)", "margin": "20px 20px"}),

        # ── Team Presence ──────────────────────────────────────
        html.Div("Team", style={**_LABEL_STYLE, "padding": "0 20px"}),
        html.Div(
            get_presence_indicators(),
            style={"padding": "0 20px 10px"}
        ),

        html.Hr(style={"borderColor": "var(--border)", "margin": "10px 20px"}),

        # ── AI Collaboration Mode ──────────────────────────────
        html.Div("AI Mode", style={**_LABEL_STYLE, "padding": "0 20px"}),
        html.Div([
            dcc.RadioItems(
                options=[
                    {'label': ' Analyst', 'value': 'analyst'},
                    {'label': ' Decision Maker', 'value': 'decision_maker'},
                    {'label': ' Coach', 'value': 'coach'},
                ],
                value='decision_maker',
                id='ai-collaboration-mode',
                labelStyle={
                    'display': 'flex', 'alignItems': 'center',
                    'color': 'var(--text-2)',
                    'marginBottom': '10px',
                    'fontSize': '13px',
                    'cursor': 'pointer',
                },
                inputStyle={"marginRight": "8px", "cursor": "pointer"},
            )
        ], style={"padding": "10px 20px"}),

        html.Hr(style={"borderColor": "var(--border)", "margin": "10px 20px 20px"}),

        # ── Live Insights ──────────────────────────────────────
        html.Div("Live Insights", style={**_LABEL_STYLE, "padding": "0 20px"}),
        html.Div(insight_feed_layout(), style={
            "padding": "0 12px", "overflowY": "auto", "flex": "1",
        }),
    ], id="sidebar")


def build_topbar():
    return html.Div([
        # ── Left: Global Filters ──────────────────────────────────
        html.Div([
            # Horizon
            html.Div([
                html.Div("Horizon", className="filter-label"),
                dcc.Dropdown(
                    id="filter-horizon",
                    options=[{"label": h, "value": h} for h in HORIZONS],
                    value=HORIZONS[1],
                    clearable=False,
                    searchable=False,
                    className="topbar-dropdown"
                ),
            ], style={"width": "160px"}),

            # Region
            html.Div([
                html.Div("Region", className="filter-label"),
                dcc.Dropdown(
                    id="filter-region",
                    options=[{"label": r, "value": r} for r in REGIONS],
                    value="Global",
                    clearable=False,
                    searchable=False,
                    className="topbar-dropdown"
                ),
            ], style={"width": "160px"}),

            # Category
            html.Div([
                html.Div("Category", className="filter-label"),
                dcc.Dropdown(
                    id="filter-category",
                    options=[{"label": b, "value": b} for b in CATEGORIES],
                    value="All",
                    clearable=False,
                    searchable=False,
                    className="topbar-dropdown"
                ),
            ], style={"width": "160px"}),

            # Scenario pill
            html.Div([
                html.Div(style={
                    "width": "8px", "height": "8px", "borderRadius": "50%",
                    "background": "var(--success)",
                    "marginRight": "8px", "flexShrink": "0",
                }),
                html.Span("Base Plan Active", style={
                    "color": "var(--success)", "fontSize": "13px", "fontWeight": "600",
                }),
            ], style={"display": "flex", "alignItems": "center",
                      "background": "rgba(22, 163, 74, 0.1)",
                      "border": "1px solid rgba(22, 163, 74, 0.2)",
                      "borderRadius": "var(--radius-lg)", "padding": "6px 14px", "marginLeft": "16px"}),
        ], className="topbar-filters", style={"display": "flex", "alignItems": "center"}),

        # ── Right: User + Actions ────────────────────────────
        html.Div([
            # Launch S&OP Wizard Button
            dbc.Button(
                [html.I(className="bi bi-magic"), " Launch S&OP Wizard"],
                id="launch-sop-wizard-btn",
                color="primary",
                className="btn-primary",
                size="sm",
                style={"marginRight": "12px"}
            ),

            # Export PDF Button
            dbc.Button(
                [html.I(className="bi bi-file-earmark-pdf"), " Export PDF"],
                id="btn-export-pdf",
                color="secondary",
                outline=True,
                size="sm",
                style={"marginRight": "12px", "color": "var(--text-1)", "borderColor": "var(--border)"}
            ),

            # Email Report Button
            dbc.Button(
                [html.I(className="bi bi-envelope-paper"), " Email Alert"],
                id="btn-email-alert",
                color="warning",
                outline=True,
                size="sm",
                style={"marginRight": "16px", "color": "var(--warning)", "borderColor": "var(--warning)"}
            ),

            # Theme Toggle
            html.Button(
                html.I(className="bi bi-moon-stars", id="theme-icon"),
                id="theme-toggle-btn",
                className="theme-toggle"
            ),

            # Notification bell
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Notifications", header=True, style={"color": "var(--text-1)", "fontWeight": "700"}),
                    dbc.DropdownMenuItem([
                        html.I(className="bi bi-exclamation-triangle text-danger me-2"),
                        "Critical: EU Region Safety Stock depleted"
                    ], href="/inventory", style={"color": "var(--text-2)", "backgroundColor": "transparent"}),
                    dbc.DropdownMenuItem([
                        html.I(className="bi bi-exclamation-circle text-warning me-2"),
                        "Warning: Supplier lead time extending (SKU003)"
                    ], href="/risk", style={"color": "var(--text-2)", "backgroundColor": "transparent"}),
                    dbc.DropdownMenuItem([
                        html.I(className="bi bi-info-circle text-info me-2"),
                        "System: Model recalibration complete"
                    ], href="/forecast", style={"color": "var(--text-2)", "backgroundColor": "transparent"}),
                ],
                nav=True,
                in_navbar=True,
                label=html.Div([
                    html.I(className="bi bi-bell", style={"fontSize": "18px"}),
                    html.Span("3", style={
                        "position": "absolute", "top": "0px", "right": "0px",
                        "fontSize": "10px", "fontWeight": "700", "color": "#fff",
                        "background": "var(--danger)", "borderRadius": "50%",
                        "width": "16px", "height": "16px",
                        "display": "flex", "alignItems": "center", "justifyContent": "center",
                    }),
                ], style={"position": "relative", "padding": "4px 8px"}),
                toggle_style={"background": "transparent", "border": "none", "color": "var(--text-2)", "boxShadow": "none", "padding": "0"},
                align_end=True,
                className="notification-dropdown"
            ),

            html.Div(style={"width": "1px", "height": "24px", "background": "var(--border)", "margin": "0 8px"}),

            # User chip
            html.Div([
                html.Div(style={
                    "width": "32px", "height": "32px", "borderRadius": "50%",
                    "background": "linear-gradient(135deg, var(--primary), var(--accent))",
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                    "marginRight": "10px", "flexShrink": "0",
                }, children=html.Span("U", style={"color": "#fff", "fontSize": "13px", "fontWeight": "700"})),
                html.Div([
                    html.Div("SC Manager", id="nav-user-display", style={"fontSize": "13px", "color": "var(--text-1)", "fontWeight": "600", "lineHeight": "1"}),
                    html.Div("Admin", style={"fontSize": "11px", "color": "var(--text-2)", "marginTop": "2px"}),
                ]),
            ], style={"display": "flex", "alignItems": "center"}),

            # Logout
            html.Button(
                html.I(className="bi bi-box-arrow-right"),
                id="logout-btn",
                style={
                    "background": "transparent", "border": "none", "color": "var(--text-2)",
                    "fontSize": "18px", "cursor": "pointer", "padding": "8px", "marginLeft": "8px",
                }
            )
        ], className="topbar-actions", style={"display": "flex", "alignItems": "center", "flexWrap": "nowrap", "minWidth": "max-content", "gap": "4px"}),

    ], id="topbar")
