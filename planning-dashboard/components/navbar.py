"""components/navbar.py — Top nav bar + horizon/region dropdowns"""
import dash_bootstrap_components as dbc
from dash import dcc, html
from config import COLORS, NAV_ITEMS, HORIZONS, REGIONS, CATEGORIES
from components.insight_feed import insight_feed_layout


_DROPDOWN_STYLE = {
    "backgroundColor": COLORS["surface"],
    "color": COLORS["text_primary"],
    "border": f"1px solid {COLORS['border']}",
    "borderRadius": "6px",
    "fontSize": "0.82rem",
    "minWidth": "160px",
}

_LABEL_STYLE = {
    "color": COLORS["text_secondary"],
    "fontSize": "0.72rem",
    "fontWeight": "600",
    "letterSpacing": "0.06em",
    "marginBottom": "2px",
}


def build_navbar():
    return dbc.Navbar(
        dbc.Container([
            # Brand
            html.A([
                html.Span("◆ ", style={"color": COLORS["primary"], "fontSize": "1.1rem"}),
                html.Span("PlanIQ", style={
                    "fontWeight": "800", "fontSize": "1.15rem",
                    "color": COLORS["text_primary"], "letterSpacing": "0.04em",
                }),
                html.Span(" Dashboard", style={
                    "fontWeight": "400", "fontSize": "0.85rem",
                    "color": COLORS["text_secondary"], "marginLeft": "4px",
                }),
            ], href="/", style={"textDecoration": "none", "display": "flex", "alignItems": "center"}),

            # Global filters
            html.Div([
                # Horizon
                html.Div([
                    html.Div("HORIZON", style=_LABEL_STYLE),
                    dcc.Dropdown(
                        id="filter-horizon",
                        options=[{"label": h, "value": h} for h in HORIZONS],
                        value=HORIZONS[1],
                        clearable=False,
                        style=_DROPDOWN_STYLE,
                        className="dark-dropdown",
                    ),
                ], style={"marginRight": "16px"}),

                # Region
                html.Div([
                    html.Div("REGION", style=_LABEL_STYLE),
                    dcc.Dropdown(
                        id="filter-region",
                        options=[{"label": r, "value": r} for r in REGIONS],
                        value="Global",
                        clearable=False,
                        style=_DROPDOWN_STYLE,
                        className="dark-dropdown",
                    ),
                ], style={"marginRight": "16px"}),

                # Category
                html.Div([
                    html.Div("CATEGORY", style=_LABEL_STYLE),
                    dcc.Dropdown(
                        id="filter-category",
                        options=[{"label": b, "value": b} for b in CATEGORIES],
                        value="All",
                        clearable=False,
                        style=_DROPDOWN_STYLE,
                        className="dark-dropdown",
                    ),
                ], style={"marginRight": "24px"}),

                # Scenario indicator
                html.Div([
                    html.Span("⬡ ", style={"color": COLORS["accent"]}),
                    html.Span("Base Plan Active",
                              style={"color": COLORS["accent"], "fontSize": "0.8rem", "fontWeight": "600"}),
                ], style={"display": "flex", "alignItems": "center"}),

            ], style={"display": "flex", "alignItems": "flex-end", "flexWrap": "wrap", "gap": "4px"}),

            # Right: user + notifications
            html.Div([
                html.Span("🔔", style={"fontSize": "1.1rem", "cursor": "pointer",
                                        "color": COLORS["text_secondary"], "marginRight": "16px"}),
                html.Span("👤 SC Manager", id="nav-user-display",
                          style={"fontSize": "0.82rem", "color": COLORS["text_secondary"], "marginRight": "12px"}),
                dbc.Button("Logout", id="logout-btn", size="sm", color="secondary", outline=True),
            ], style={"display": "flex", "alignItems": "center"}),

        ], fluid=True, style={"display": "flex", "justifyContent": "space-between",
                               "alignItems": "flex-end", "flexWrap": "wrap", "gap": "8px"}),
        color=COLORS["surface"],
        dark=True,
        style={
            "borderBottom": f"1px solid {COLORS['border']}",
            "padding": "10px 0",
            "position": "sticky", "top": "0", "zIndex": "1000",
        },
    )


def build_sidebar():
    return html.Div([
        html.Div("DASHBOARDS", style={
            **_LABEL_STYLE, "padding": "16px 16px 8px",
        }),
        html.Div([
            dbc.NavLink(
                [html.Span(item["icon"], style={"marginRight": "8px", "fontSize": "0.95rem"}),
                 html.Span(item["label"], style={"fontSize": "0.83rem"})],
                href=item["href"],
                active="exact",
                style={"color": COLORS["text_secondary"], "padding": "8px 16px",
                       "borderRadius": "6px", "display": "flex", "alignItems": "center"},
            )
            for item in NAV_ITEMS
        ]),
        
        # Human-AI Collaboration Modes
        html.Div("AI MODE", style={**_LABEL_STYLE, "padding": "24px 16px 8px", "marginTop": "auto"}),
        html.Div([
            dcc.RadioItems(
                options=[
                    {'label': ' Analyst (Push)', 'value': 'analyst'},
                    {'label': ' Decision Maker (Pull)', 'value': 'decision_maker'},
                    {'label': ' Coach (Feedback)', 'value': 'coach'}
                ],
                value='decision_maker',
                id='ai-collaboration-mode',
                labelStyle={'display': 'block', 'color': COLORS['text_secondary'], 'marginBottom': '8px', 'fontSize': '0.85rem'},
                inputStyle={"marginRight": "8px"}
            )
        ], style={"padding": "0 16px"}),
        
        # Automated Insight Feed
        html.Div("LIVE INSIGHTS", style={**_LABEL_STYLE, "padding": "24px 16px 8px"}),
        html.Div(insight_feed_layout(), style={"padding": "0 8px", "overflowY": "auto", "flex": "1"})
        
    ], style={
        "backgroundColor": COLORS["surface"],
        "borderRight": f"1px solid {COLORS['border']}",
        "minHeight": "100vh",
        "width": "280px", # Increased width for feed
        "flexShrink": "0",
        "paddingTop": "8px",
        "display": "flex",
        "flexDirection": "column"
    })
