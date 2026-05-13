"""
layout.py  ─  Shell layout: top nav, sidebar, main content, copilot panel.
All 9 dashboard views wired to sidebar nav.
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.theme import COLORS

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


def sidebar() -> html.Div:
    items = [
        html.Div("PLANNING VIEWS", className="sidebar-section",
                 style={"marginTop": "8px"}),
    ]
    for page_id, icon, label in NAV_ITEMS:
        items.append(
            html.Div(
                id=f"nav-{page_id}",
                className="nav-item",
                children=[
                    html.Span(icon, className="nav-icon"),
                    html.Span(label),
                ],
                **{"data-page": page_id},
                n_clicks=0,
            )
        )
    return html.Div(id="sidebar", children=items)


def top_nav() -> html.Div:
    return html.Div(id="top-nav", children=[
        html.Div([
            html.Span("⚡", style={"color": COLORS["primary"], "marginRight": "4px"}),
            html.Span("DemandIQ", style={"fontWeight": 700, "color": COLORS["primary"]}),
            html.Span(" | Planning Dashboard", style={"color": COLORS["text_secondary"],
                                                       "fontWeight": 400, "fontSize": "0.82rem"}),
        ], className="brand"),
        html.Div([
            html.Button("Operational", id="btn-op",  className="horizon-btn active",
                        **{"data-horizon": "operational"}),
            html.Button("Tactical",    id="btn-tac", className="horizon-btn",
                        **{"data-horizon": "tactical"}),
            html.Button("Strategic",   id="btn-str", className="horizon-btn",
                        **{"data-horizon": "strategic"}),
        ], style={"display": "flex", "gap": "6px"}),
        html.Div(className="nav-sep"),
        # Global filters
        dcc.Dropdown(
            id="filter-region",
            options=[{"label": r, "value": r} for r in ["APAC", "EMEA", "NA", "LATAM"]],
            value=None, placeholder="All Regions", multi=True,
            style={"width": "160px", "fontSize": "0.8rem"},
        ),
        dcc.Dropdown(
            id="filter-category",
            options=[{"label": c, "value": c}
                     for c in ["Electronics", "Apparel", "FMCG", "Pharma", "Automotive"]],
            value=None, placeholder="All Categories", multi=True,
            style={"width": "170px", "fontSize": "0.8rem"},
        ),
        html.Span("⚠ 3 Alerts", className="nav-badge"),
        html.Span("👤 SC Manager", className="nav-user"),
    ])


def copilot_panel() -> html.Div:
    from components.theme import COLORS
    return html.Div(id="copilot-panel", children=[
        html.Div(["✨ ", "AI COPILOT"], className="copilot-title"),
        html.Div(id="copilot-narrative", children=[
            html.Div(className="copilot-msg", children=[
                html.Span("[AI Generated] ", style={"color": COLORS["accent"],
                                                     "fontWeight": 600, "fontSize": "0.68rem"}),
                html.Span(
                    "OTIF at 93.4% vs 95% target — APAC stockout risk is the primary "
                    "action item. Inventory dos in EMEA is 45 days (overstock). "
                    "Recommend redistributing 12K units EMEA→LATAM by EOW.",
                    style={"fontSize": "0.8rem", "color": COLORS["text_secondary"]}
                ),
            ]),
        ]),
        html.Div(style={"marginTop": "12px"}, children=[
            html.P("Ask a question:", style={"fontSize": "0.72rem",
                                              "color": COLORS["text_secondary"],
                                              "marginBottom": "6px"}),
            dcc.Textarea(
                id="copilot-input",
                placeholder="e.g. Why is APAC fill rate low?",
                className="copilot-query",
                style={"height": "70px"},
            ),
            html.Button("Ask →", id="copilot-submit",
                        style={"marginTop": "6px", "width": "100%",
                               "background": COLORS["primary"] + "22",
                               "border": f"1px solid {COLORS['primary']}55",
                               "color": COLORS["primary"],
                               "padding": "6px 12px", "borderRadius": "6px",
                               "cursor": "pointer", "fontSize": "0.8rem",
                               "fontFamily": "Inter, sans-serif"}),
        ]),
        html.Div(id="copilot-response", style={"marginTop": "12px"}),
        # Recent alerts
        html.Div(style={"marginTop": "16px"}, children=[
            html.P("RECENT ALERTS", style={"fontSize": "0.68rem", "fontWeight": 600,
                                            "letterSpacing": "0.06em",
                                            "color": COLORS["text_secondary"],
                                            "marginBottom": "8px"}),
            _alert_item("🔴", "SKU-0003 APAC stockout in 7d", "critical"),
            _alert_item("🟡", "EMEA DOS 45d — overstock risk", "warning"),
            _alert_item("🔴", "SUP-07 reliability < 70%",       "critical"),
            _alert_item("🟡", "Forecast bias drift +7.2%",       "warning"),
        ]),
    ])


def _alert_item(icon: str, text: str, level: str) -> html.Div:
    color = COLORS["danger"] if level == "critical" else COLORS["warning"]
    return html.Div(style={
        "display": "flex", "gap": "8px", "padding": "7px 0",
        "borderBottom": f"1px solid {COLORS['border']}",
        "fontSize": "0.76rem",
    }, children=[
        html.Span(icon),
        html.Span(text, style={"color": color}),
    ])


def app_layout(page_content: html.Div) -> html.Div:
    """Outer shell wrapping sidebar + main + copilot."""
    return html.Div([
        top_nav(),
        html.Div(id="app-layout", children=[
            sidebar(),
            html.Div(id="main-content", children=[page_content]),
            copilot_panel(),
        ]),
        # State store for active page
        dcc.Store(id="active-page-store", data="executive"),
        dcc.Store(id="global-filter-store", data={
            "horizon": "operational",
            "region": [],
            "category": [],
            "scenario": None,
        }),
    ])
