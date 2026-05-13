"""dashboards/regional.py  ─  Dashboard 9: Regional Planning"""
from dash import html, dcc, Input, Output, callback
from components.theme import COLORS
from components import charts
from data.mock_data import get_regional_kpis, get_region_vs_plan, get_safety_stock_simulation

REGIONS = ["APAC", "EMEA", "NA", "LATAM"]


def layout() -> html.Div:
    reg_df  = get_regional_kpis()
    rvp_df  = get_region_vs_plan()

    return html.Div([
        html.Div(className="page-title", children=[
            html.Span("🗺️", className="icon"), "Regional Planning",
        ]),

        # Regional KPI scorecards
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)",
                   "gap": "12px", "marginBottom": "16px"},
            children=[_region_card(row) for _, row in reg_df.iterrows()],
        ),

        # Region vs Plan bar chart
        html.Div(className="card", style={"marginBottom": "16px"}, children=[
            dcc.Graph(figure=charts.regional_bar_chart(rvp_df),
                      config={"displayModeBar": False}, style={"height": "300px"}),
        ]),

        html.Div(className="grid-2", children=[
            # Local scenario sliders
            html.Div(className="card", children=[
                html.Div("LOCAL SCENARIO SLIDERS", className="section-header"),
                html.Div(style={"marginBottom": "12px"}, children=[
                    html.Label("Demand Surge Factor",
                               style={"fontSize": "0.78rem", "color": COLORS["text_secondary"],
                                      "display": "block", "marginBottom": "6px"}),
                    dcc.Slider(id="reg-demand-surge", min=0.8, max=1.5, step=0.05, value=1.0,
                               marks={0.8: "−20%", 1.0: "Base", 1.3: "+30%", 1.5: "+50%"},
                               tooltip={"placement": "bottom", "always_visible": True}),
                ]),
                html.Div(style={"marginBottom": "12px"}, children=[
                    html.Label("Target Service Level",
                               style={"fontSize": "0.78rem", "color": COLORS["text_secondary"],
                                      "display": "block", "marginBottom": "6px"}),
                    dcc.Slider(id="reg-service-level", min=85, max=99, step=0.5, value=95,
                               marks={85: "85%", 90: "90%", 95: "95%", 99: "99%"},
                               tooltip={"placement": "bottom", "always_visible": True}),
                ]),
                html.Div(id="reg-sim-output"),
            ]),

            # Plan attainment table
            html.Div(className="card", children=[
                html.Div("PLAN ATTAINMENT BY REGION", className="section-header"),
                html.Table(style={"width": "100%", "borderCollapse": "collapse"}, children=[
                    html.Thead(html.Tr([
                        html.Th(h, style={"padding": "8px 10px", "fontSize": "0.7rem",
                                          "textTransform": "uppercase",
                                          "color": COLORS["text_secondary"],
                                          "textAlign": "left",
                                          "borderBottom": f"1px solid {COLORS['border']}"})
                        for h in ["Region", "Revenue $M", "OTIF %", "Fill Rate %",
                                  "DOS", "Plan Attain."]
                    ])),
                    html.Tbody([
                        _attainment_row(row) for _, row in reg_df.iterrows()
                    ]),
                ]),
            ]),
        ]),
    ])


def _region_card(row) -> html.Div:
    otif_color = (COLORS["success"] if row["otif"] >= 95 else
                  COLORS["warning"] if row["otif"] >= 90 else COLORS["danger"])
    return html.Div(className="card", children=[
        html.Div(style={"display": "flex", "justifyContent": "space-between",
                        "marginBottom": "10px"}, children=[
            html.Span(row["region"],
                      style={"fontSize": "0.9rem", "fontWeight": 700,
                             "color": COLORS["text_primary"]}),
            html.Span(f"${row['revenue_m']:.1f}M",
                      style={"fontSize": "0.88rem", "color": COLORS["chart_2"],
                             "fontWeight": 600, "fontFamily": "JetBrains Mono, monospace"}),
        ]),
        *[_mini_stat(label, val, color) for label, val, color in [
            ("OTIF",       f"{row['otif']:.1f}%",       otif_color),
            ("Fill Rate",  f"{row['fill_rate']:.1f}%",  COLORS["chart_1"]),
            ("DOS",        f"{row['dos']:.0f} days",     COLORS["text_secondary"]),
            ("Plan Att.",  f"{row['plan_attainment']:.0f}%",
             COLORS["success"] if row["plan_attainment"] >= 95 else COLORS["warning"]),
        ]],
    ])


def _mini_stat(label: str, value: str, color: str) -> html.Div:
    return html.Div(style={
        "display": "flex", "justifyContent": "space-between",
        "padding": "4px 0", "borderBottom": f"1px solid {COLORS['border']}33",
    }, children=[
        html.Span(label, style={"fontSize": "0.72rem", "color": COLORS["text_secondary"]}),
        html.Span(value, style={"fontSize": "0.78rem", "fontWeight": 600,
                                "color": color, "fontFamily": "JetBrains Mono, monospace"}),
    ])


def _attainment_row(row) -> html.Tr:
    att = row["plan_attainment"]
    att_color = (COLORS["success"] if att >= 98 else
                 COLORS["warning"] if att >= 90 else COLORS["danger"])
    return html.Tr([
        html.Td(row["region"], style={"padding": "8px 10px", "fontSize": "0.82rem",
                                      "fontWeight": 500}),
        html.Td(f"${row['revenue_m']:.1f}M", style={"padding": "8px",
                "fontFamily": "JetBrains Mono, monospace", "fontSize": "0.82rem"}),
        html.Td(f"{row['otif']:.1f}%", style={"padding": "8px", "fontSize": "0.82rem"}),
        html.Td(f"{row['fill_rate']:.1f}%", style={"padding": "8px", "fontSize": "0.82rem"}),
        html.Td(f"{row['dos']:.0f}d", style={"padding": "8px", "fontSize": "0.82rem"}),
        html.Td(
            html.Span(f"{att:.0f}%",
                      style={"background": att_color + "22", "color": att_color,
                             "padding": "2px 8px", "borderRadius": "4px",
                             "fontSize": "0.78rem", "fontWeight": 700,
                             "fontFamily": "JetBrains Mono, monospace"}),
            style={"padding": "8px"},
        ),
    ], style={"borderBottom": f"1px solid {COLORS['border']}55"})


@callback(
    Output("reg-sim-output", "children"),
    Input("reg-demand-surge",   "value"),
    Input("reg-service-level",  "value"),
)
def update_regional_sim(surge: float, sl: float) -> html.Div:
    sim = get_safety_stock_simulation(sl / 100)
    adj_ss  = sim["safety_stock"]  * surge
    adj_wc  = sim["working_capital_usd"] * surge
    adj_rop = sim["reorder_point"] * surge

    rows = [
        ("Demand Factor",    f"×{surge:.2f}",             COLORS["primary"]),
        ("Adj Safety Stock", f"{adj_ss:,.0f} units",      COLORS["chart_2"]),
        ("Adj Reorder Pt.",  f"{adj_rop:,.0f} units",     COLORS["chart_1"]),
        ("Working Capital",  f"${adj_wc:,.0f}",           COLORS["chart_3"]),
        ("Stockout Risk",    f"{sim['stockout_prob']:.2f}%",COLORS["danger"]),
    ]
    return html.Div(style={"marginTop": "12px"}, children=[
        html.Div(style={
            "display": "flex", "justifyContent": "space-between",
            "padding": "8px 0", "borderBottom": f"1px solid {COLORS['border']}",
        }, children=[
            html.Span(label, style={"fontSize": "0.8rem", "color": COLORS["text_secondary"]}),
            html.Span(value, style={"fontSize": "0.86rem", "fontWeight": 700,
                                    "color": color, "fontFamily": "JetBrains Mono, monospace"}),
        ])
        for label, value, color in rows
    ])
