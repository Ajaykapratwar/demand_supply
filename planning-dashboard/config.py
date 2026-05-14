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

# ── Blueprint v2.0 §13 — Per-dashboard alert thresholds (configurable) ──────
ALERT_THRESHOLDS = {
    "executive": {
        "service_level_red":   92.0,   # % below → red
        "risk_score_red":       0.70,   # > → red
        "cost_delta_yellow":    5.0,    # % vs plan → yellow
        "cost_delta_red":      10.0,    # % vs plan → red
    },
    "forecast": {
        "wape_red":            25.0,    # % on A-class → red
        "coverage_low":        75.0,    # % below → calibration warning
        "coverage_high":       85.0,    # % above → calibration warning
    },
    "capacity": {
        "utilization_burn":    95.0,    # % sustained → burnout risk
        "oee_red":             65.0,    # % below → review
        "fpy_red":             95.0,    # % below → quality investigation
    },
    "financial": {
        "margin_delta_red":    -2.0,    # pp vs plan → red
        "cash_to_cash_warn":   10.0,    # days over target → warning
    },
    "risk": {
        "composite_p1":         0.75,   # > → P1 incident
    },
    "sustainability": {
        "sbti_off_red":         5.0,    # % off trajectory → red
    },
    "inventory": {
        "dos_over":             2.0,    # × target → overstock flag
        "dos_under":            0.5,    # × target → stockout risk flag
    },
    "regional": {
        "fill_rate_red":       92.0,    # % below → red overlay
    },
}

# ── Blueprint v2.0 §18.2 — Industry KPI Benchmarks (CPG/Retail defaults) ─────
INDUSTRY_BENCHMARKS = {
    "forecast_wape":        {"p25": 15.0, "p50": 20.0, "p75": 25.0},
    "otif":                {"p25": 95.0, "p50": 96.5, "p75": 98.0},
    "inventory_turns":     {"p25":  8.0, "p50": 10.0, "p75": 12.0},
    "dos_finished_goods":  {"p25": 30.0, "p50": 37.5, "p75": 45.0},
    "fill_rate":           {"p25": 95.0, "p50": 96.5, "p75": 98.0},
    "cash_to_cash":        {"p25": 30.0, "p50": 45.0, "p75": 60.0},
    "logistics_pct_sales": {"p25":  4.0, "p50":  6.5, "p75":  9.0},
    "oee":                 {"p25": 60.0, "p50": 67.5, "p75": 75.0},
}

# ── Blueprint v2.0 §13 — AI recommendation phrasing templates ─────────────────
AI_RECOMMENDATION_TEMPLATES = {
    "safety_stock_increase":
        "Increase safety stock by {pct}% in {region} to reduce stockout risk from {p_old}% to {p_new}%.",
    "production_shift":
        "Shift production from {plant_a} to {plant_b} to improve OTIF by {delta_pp} pp with {cost_delta}% cost change.",
    "sku_defer":
        "Defer {sku_count} low-margin SKUs in {region} to free {capacity_hrs} capacity hours for high-margin lines.",
    "inventory_rebalance":
        "Rebalance {qty} units from {dc_a} (overstock) to {dc_b} (understock); saves {usd} carrying cost; raises fill rate by {pp} pp.",
    "freight_mode_switch":
        "Switching {sku_count} SKUs from air to ocean saves {usd}/quarter; service impact +{days} lead time.",
    "supplier_alternate":
        "Supplier {x} reliability dropped {pp} pp; recommend qualifying alternate supplier {y} (lead time +{days}, cost +{pct}%).",
    "carbon_mode_switch":
        "Switch {lanes} from air to rail; reduces Scope 3 by {tco2} tCO₂e; service impact: +{days} extra lead time.",
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
