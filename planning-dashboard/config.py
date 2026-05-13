# config.py — Blueprint §6.6 color palette + §6.7 typography constants

COLORS = {
    "background":     "#0d1117",
    "surface":        "#161b22",
    "card":           "#1c2128",
    "border":         "#30363d",
    "primary":        "#58a6ff",
    "success":        "#3fb950",
    "warning":        "#d29922",
    "danger":         "#f85149",
    "info":           "#58a6ff",
    "text_primary":   "#e6edf3",
    "text_secondary": "#8b949e",
    "accent":         "#bc8cff",
    "chart_1":        "#58a6ff",
    "chart_2":        "#3fb950",
    "chart_3":        "#d29922",
    "chart_4":        "#f85149",
    "chart_5":        "#bc8cff",
}

# Shared Plotly layout defaults (dark theme)
PLOT_LAYOUT = dict(
    paper_bgcolor=COLORS["card"],
    plot_bgcolor=COLORS["surface"],
    font=dict(color=COLORS["text_primary"], family="Inter, sans-serif", size=12),
    margin=dict(l=40, r=20, t=40, b=40),
)

# Shared axis style helper
AXIS_STYLE = dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"],
                  tickfont=dict(color=COLORS["text_secondary"]),
                  title_font=dict(color=COLORS["text_secondary"]))

# Shared legend style
LEGEND_STYLE = dict(bgcolor=COLORS["card"], bordercolor=COLORS["border"],
                    borderwidth=1, font=dict(color=COLORS["text_secondary"]))


def hex_to_rgba(hex_color: str, alpha: float = 0.15) -> str:
    """Convert 6-char hex to rgba string. Plotly 5.x rejects 8-char hex."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def apply_dark_layout(fig, title="", height=300, margin=None, **kwargs):
    """Apply dark theme to a figure. Use this instead of spreading PLOT_LAYOUT."""
    m = margin or dict(l=40, r=20, t=40, b=40)
    fig.update_layout(
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["surface"],
        font=dict(color=COLORS["text_primary"], family="Inter, sans-serif", size=12),
        margin=m,
        title=dict(text=title, font=dict(color=COLORS["text_primary"], size=13)),
        height=height,
        **kwargs,
    )
    fig.update_xaxes(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"],
                     tickfont=dict(color=COLORS["text_secondary"]))
    fig.update_yaxes(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"],
                     tickfont=dict(color=COLORS["text_secondary"]))
    return fig

# Blueprint §6.7 typography
TYPOGRAPHY = {
    "kpi_value_size": "2.6rem",
    "kpi_title_size": "0.72rem",
    "body_size": "0.875rem",
    "header_weight": "700",
    "header_spacing": "0.08em",
}

# Planning horizons
HORIZONS = ["Operational (0-4w)", "Tactical (1-12m)", "Strategic (12-36m+)"]

# Credentials
USERS = {
    "scmanager": {"password": "sc123",    "role": "SC Manager"},
    "admin":     {"password": "admin123", "role": "Admin"},
}

# Regions (from data_loader.py)
REGIONS = ["Global", "North", "South", "East", "West", "Central"]

# Categories (replacing Business Units)
CATEGORIES = ["All", "Split", "Window", "Portable", "Cassette", "Tower", "Central"]

# Dashboard nav items
NAV_ITEMS = [
    {"label": "Executive Summary",    "href": "/",                  "icon": "📊"},
    {"label": "Operational Planning", "href": "/operational",       "icon": "⚙️"},
    {"label": "Forecast Analytics",   "href": "/forecast",          "icon": "📈"},
    {"label": "Inventory Optimization","href": "/inventory",        "icon": "🗄️"},
    {"label": "Capacity Planning",    "href": "/capacity",          "icon": "🏭"},
    {"label": "Financial Impact",     "href": "/financial",         "icon": "💰"},
    {"label": "Risk Monitoring",      "href": "/risk",              "icon": "🛡️"},
    {"label": "Sustainability",       "href": "/sustainability",     "icon": "🌱"},
    {"label": "Regional Planning",    "href": "/regional",          "icon": "🌍"},
]
