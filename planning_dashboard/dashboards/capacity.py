"""dashboards/capacity.py  ─  Dashboard 5: Capacity Planning"""
from dash import html, dcc
from components.theme import COLORS
from components import charts
from data.mock_data import get_capacity_utilization, get_capacity_load_profile


def layout() -> html.Div:
    plants   = get_capacity_utilization()
    load_df  = get_capacity_load_profile()

    gauge_cards = [
        html.Div(className="card", style={"padding": "8px"}, children=[
            dcc.Graph(
                figure=charts.capacity_gauge(p["utilization"], p["plant"], p["oee"]),
                config={"displayModeBar": False},
                style={"height": "180px"},
            ),
        ])
        for p in plants
    ]

    # Summary stats strip
    avg_util = sum(p["utilization"] for p in plants) / len(plants)
    critical = sum(1 for p in plants if p["utilization"] > 0.92)

    return html.Div([
        html.Div(className="page-title", children=[
            html.Span("🏭", className="icon"), "Capacity Planning",
        ]),

        # Summary strip
        html.Div(style={
            "display": "flex", "gap": "12px", "marginBottom": "16px", "flexWrap": "wrap",
        }, children=[
            _stat_pill("Avg Utilization", f"{avg_util:.0%}", COLORS["primary"]),
            _stat_pill("Plants Critical (>92%)", str(critical), COLORS["danger"]),
            _stat_pill("Total Plants", str(len(plants)), COLORS["text_secondary"]),
            _stat_pill("Avg OEE", f"{sum(p['oee'] for p in plants)/len(plants):.0%}", COLORS["chart_2"]),
        ]),

        # Gauge row
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "12px",
                   "marginBottom": "16px"},
            children=gauge_cards,
        ),

        # Load profile chart
        html.Div(className="card", style={"marginBottom": "16px"}, children=[
            dcc.Graph(figure=charts.capacity_load_profile(load_df),
                      config={"displayModeBar": False}, style={"height": "300px"}),
        ]),

        # Gantt-style table placeholder
        html.Div(className="card", children=[
            html.Div("PLANNED PRODUCTION SCHEDULE (SIMPLIFIED GANTT)", className="section-header"),
            _gantt_table(plants),
        ]),
    ])


def _stat_pill(label: str, value: str, color: str) -> html.Div:
    return html.Div(style={
        "background": COLORS["card"],
        "border": f"1px solid {COLORS['border']}",
        "borderRadius": "8px", "padding": "10px 16px",
        "display": "flex", "flexDirection": "column", "gap": "2px",
    }, children=[
        html.Span(label, style={"fontSize": "0.68rem", "color": COLORS["text_secondary"],
                                "textTransform": "uppercase", "letterSpacing": "0.05em"}),
        html.Span(value, style={"fontSize": "1.4rem", "fontWeight": 700,
                                "fontFamily": "JetBrains Mono, monospace", "color": color}),
    ])


def _gantt_table(plants: list) -> html.Table:
    weeks = ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"]
    import numpy as np
    rng = np.random.default_rng(7)
    rows = []
    for p in plants:
        util_vals = (p["utilization"] * 100 + rng.normal(0, 3, len(weeks))).clip(50, 100)
        cells = [html.Td(p["plant"],
                         style={"fontSize": "0.8rem", "color": COLORS["text_primary"],
                                "padding": "8px 10px", "whiteSpace": "nowrap"})]
        for val in util_vals:
            color = (COLORS["danger"] if val > 92 else
                     COLORS["warning"] if val > 80 else COLORS["success"])
            cells.append(html.Td(
                f"{val:.0f}%",
                style={
                    "background": color + "22",
                    "color": color,
                    "textAlign": "center",
                    "padding": "6px 8px",
                    "fontSize": "0.78rem",
                    "fontFamily": "JetBrains Mono, monospace",
                    "fontWeight": 600,
                    "border": f"1px solid {COLORS['border']}33",
                }
            ))
        rows.append(html.Tr(cells))

    header = html.Tr([
        html.Th("Plant", style={"padding": "8px 10px", "fontSize": "0.7rem",
                                "textTransform": "uppercase", "color": COLORS["text_secondary"],
                                "fontWeight": 600, "textAlign": "left"}),
        *[html.Th(w, style={"padding": "8px", "fontSize": "0.7rem", "textAlign": "center",
                            "color": COLORS["text_secondary"]}) for w in weeks],
    ])
    return html.Table(
        style={"width": "100%", "borderCollapse": "collapse"},
        children=[html.Thead(header), html.Tbody(rows)],
    )
