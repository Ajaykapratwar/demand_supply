"""dashboards/sustainability.py  ─  Dashboard 8: Sustainability"""
from dash import html, dcc
from components.theme import COLORS
from components.kpi_cards import kpi_card
from components import charts
from data.mock_data import (
    get_sustainability_kpis, get_emissions_breakdown, get_pareto_scatter,
)

SUS_CONFIG = [
    ("scope1",          "Scope 1 Emissions",  "tCO2e", True),
    ("scope2",          "Scope 2 Emissions",  "tCO2e", True),
    ("scope3",          "Scope 3 Emissions",  "tCO2e", True),
    ("carbon_intensity","Carbon Intensity",   "kg/unit",True),
    ("renewable_pct",   "Renewable Energy",   "%",     False),
]


def layout() -> html.Div:
    sus    = get_sustainability_kpis()
    breakdown = get_emissions_breakdown()
    pareto_df = get_pareto_scatter()

    sparkline_dummy = [sus["scope2"]["value"] - i * 10 for i in range(14)]

    kpi_row = [
        kpi_card(
            label=label,
            value=sus[k]["value"], unit=unit,
            target=sus[k]["target"], delta=sus[k]["delta"],
            sparkline_data=[sus[k]["value"] - i * abs(sus[k]["delta"]) * 0.1
                            for i in range(14)],
            status="warning", delta_invert=invert,
        )
        for k, label, unit, invert in SUS_CONFIG
    ]

    # SBTi progress bar
    sbti_pct = 68   # % toward SBTi target

    return html.Div([
        html.Div(className="page-title", children=[
            html.Span("🌱", className="icon"), "Sustainability",
        ]),

        # SBTi progress banner
        html.Div(style={
            "background": COLORS["card"],
            "border": f"1px solid {COLORS['chart_2']}44",
            "borderRadius": "10px", "padding": "12px 16px",
            "marginBottom": "16px",
        }, children=[
            html.Div(style={"display": "flex", "justifyContent": "space-between",
                            "marginBottom": "8px"}, children=[
                html.Span("SBTi Progress — 1.5°C Aligned Target",
                          style={"fontSize": "0.82rem", "fontWeight": 600,
                                 "color": COLORS["text_primary"]}),
                html.Span(f"{sbti_pct}% toward 2030 target",
                          style={"fontSize": "0.8rem", "color": COLORS["chart_2"],
                                 "fontWeight": 600}),
            ]),
            html.Div(style={
                "height": "8px", "borderRadius": "4px",
                "background": COLORS["border"],
                "overflow": "hidden",
            }, children=[
                html.Div(style={
                    "width": f"{sbti_pct}%", "height": "100%",
                    "background": f"linear-gradient(90deg, {COLORS['chart_2']}, {COLORS['primary']})",
                    "borderRadius": "4px",
                    "transition": "width 0.5s ease",
                }),
            ]),
        ]),

        html.Div(className="grid-kpi", style={"gridTemplateColumns": "repeat(5, 1fr)"},
                 children=kpi_row),

        html.Div(className="grid-2", style={"marginBottom": "16px"}, children=[
            html.Div(className="card", children=[
                dcc.Graph(figure=charts.emissions_donut(breakdown),
                          config={"displayModeBar": False}, style={"height": "300px"}),
            ]),
            html.Div(className="card", children=[
                dcc.Graph(figure=charts.pareto_cost_carbon(pareto_df),
                          config={"displayModeBar": False}, style={"height": "320px"}),
            ]),
        ]),

        # Emission reduction initiatives
        html.Div(className="card", children=[
            html.Div("EMISSION REDUCTION INITIATIVES", className="section-header"),
            *[_initiative_row(i) for i in _initiatives()],
        ]),
    ])


def _initiatives() -> list:
    return [
        {"initiative": "Solar PV at Plant-A", "scope": "Scope 2",
         "reduction": "−240 tCO2e/yr", "status": "Active",   "progress": 85},
        {"initiative": "Modal shift Rail→Road", "scope": "Scope 3",
         "reduction": "−180 tCO2e/yr", "status": "Planned",  "progress": 30},
        {"initiative": "Supplier green audit",  "scope": "Scope 3",
         "reduction": "−350 tCO2e/yr", "status": "In Review","progress": 55},
        {"initiative": "EV fleet pilot (EMEA)", "scope": "Scope 1",
         "reduction": "−90 tCO2e/yr",  "status": "Active",   "progress": 60},
    ]


def _initiative_row(item: dict) -> html.Div:
    status_color = {
        "Active":    COLORS["success"],
        "Planned":   COLORS["primary"],
        "In Review": COLORS["warning"],
    }.get(item["status"], COLORS["text_secondary"])

    return html.Div(style={
        "display": "grid",
        "gridTemplateColumns": "3fr 1fr 1fr 1fr 2fr",
        "gap": "12px", "padding": "10px 0",
        "borderBottom": f"1px solid {COLORS['border']}",
        "alignItems": "center",
    }, children=[
        html.Span(item["initiative"],
                  style={"fontSize": "0.82rem", "color": COLORS["text_primary"]}),
        html.Span(item["scope"],
                  style={"fontSize": "0.76rem", "color": COLORS["text_secondary"]}),
        html.Span(item["reduction"],
                  style={"fontSize": "0.82rem", "color": COLORS["chart_2"],
                         "fontWeight": 600, "fontFamily": "JetBrains Mono, monospace"}),
        html.Span(item["status"],
                  style={"background": status_color + "22", "color": status_color,
                         "padding": "2px 8px", "borderRadius": "4px",
                         "fontSize": "0.7rem", "fontWeight": 600}),
        # Progress bar
        html.Div(style={"display": "flex", "alignItems": "center", "gap": "8px"}, children=[
            html.Div(style={
                "flex": 1, "height": "6px", "borderRadius": "3px",
                "background": COLORS["border"], "overflow": "hidden",
            }, children=[
                html.Div(style={
                    "width": f"{item['progress']}%", "height": "100%",
                    "background": status_color, "borderRadius": "3px",
                }),
            ]),
            html.Span(f"{item['progress']}%",
                      style={"fontSize": "0.72rem", "color": COLORS["text_secondary"],
                             "fontFamily": "JetBrains Mono, monospace", "minWidth": "32px"}),
        ]),
    ])
