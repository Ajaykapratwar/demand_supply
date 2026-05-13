"""dashboards/risk.py  ─  Dashboard 7: Risk Monitoring"""
from dash import html, dcc
from components.theme import COLORS
from components import charts
from data.mock_data import get_risk_scores, get_risk_matrix, get_mitigation_actions

RISK_COLORS = {
    "low":      COLORS["success"],
    "medium":   COLORS["warning"],
    "high":     COLORS["danger"],
    "critical": "#ff0000",
}


def layout() -> html.Div:
    suppliers = get_risk_scores()
    matrix_df = get_risk_matrix()
    actions   = get_mitigation_actions()

    # Top-risk supplier gauges (top 4 by score)
    top4 = suppliers.nlargest(4, "risk_score")
    gauge_cards = [
        html.Div(className="card", style={"padding": "8px"}, children=[
            dcc.Graph(
                figure=charts.risk_score_gauge(row["risk_score"], row["supplier"]),
                config={"displayModeBar": False},
                style={"height": "160px"},
            ),
        ])
        for _, row in top4.iterrows()
    ]

    # Supplier risk table
    tbl_rows = []
    for _, row in suppliers.iterrows():
        cat_color = RISK_COLORS.get(row["risk_category"], COLORS["text_secondary"])
        tbl_rows.append(html.Tr([
            html.Td(row["supplier"], style={"padding": "8px 10px", "fontSize": "0.82rem"}),
            html.Td(f"{row['risk_score']:.2f}",
                    style={"fontFamily": "JetBrains Mono, monospace", "fontWeight": 700,
                           "color": RISK_COLORS.get(row["risk_category"], COLORS["text_primary"]),
                           "padding": "8px"}),
            html.Td(f"{row['reliability']:.0%}",
                    style={"padding": "8px", "fontSize": "0.82rem"}),
            html.Td(f"{row['on_time_rate']:.0%}",
                    style={"padding": "8px", "fontSize": "0.82rem"}),
            html.Td(html.Span(row["risk_category"].upper(),
                              style={"background": cat_color + "22", "color": cat_color,
                                     "padding": "2px 8px", "borderRadius": "4px",
                                     "fontSize": "0.68rem", "fontWeight": 700}),
                    style={"padding": "8px"}),
        ]))

    return html.Div([
        html.Div(className="page-title", children=[
            html.Span("🛡️", className="icon"), "Risk Monitoring",
        ]),

        # Top-risk gauges
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)",
                   "gap": "12px", "marginBottom": "16px"},
            children=gauge_cards,
        ),

        html.Div(className="grid-2", style={"marginBottom": "16px"}, children=[
            # P×I matrix
            html.Div(className="card", children=[
                dcc.Graph(figure=charts.risk_probability_impact_matrix(matrix_df),
                          config={"displayModeBar": False}, style={"height": "320px"}),
            ]),
            # Supplier table
            html.Div(className="card", children=[
                html.Div("SUPPLIER RISK SCORECARD", className="section-header"),
                html.Table(style={"width": "100%", "borderCollapse": "collapse"}, children=[
                    html.Thead(html.Tr([
                        html.Th(h, style={"padding": "8px 10px", "fontSize": "0.7rem",
                                          "textTransform": "uppercase", "textAlign": "left",
                                          "color": COLORS["text_secondary"],
                                          "borderBottom": f"1px solid {COLORS['border']}"})
                        for h in ["Supplier", "Risk Score", "Reliability", "OTD 90d", "Category"]
                    ])),
                    html.Tbody(tbl_rows),
                ]),
            ]),
        ]),

        # Mitigation actions
        html.Div(className="card", children=[
            html.Div("ACTIVE MITIGATION ACTIONS", className="section-header"),
            *[_mitigation_row(a) for a in actions],
        ]),
    ])


def _mitigation_row(action: dict) -> html.Div:
    status_color = {
        "In Progress": COLORS["warning"],
        "Planned":     COLORS["primary"],
        "Approved":    COLORS["success"],
    }.get(action["status"], COLORS["text_secondary"])

    return html.Div(style={
        "display": "grid",
        "gridTemplateColumns": "2fr 3fr 1fr 1fr 1fr",
        "gap": "12px", "padding": "10px 0",
        "borderBottom": f"1px solid {COLORS['border']}",
        "alignItems": "center",
    }, children=[
        html.Span(action["risk"],
                  style={"fontSize": "0.82rem", "color": COLORS["text_primary"],
                         "fontWeight": 500}),
        html.Span(action["action"],
                  style={"fontSize": "0.79rem", "color": COLORS["text_secondary"]}),
        html.Span(action["owner"],
                  style={"fontSize": "0.76rem", "color": COLORS["text_secondary"]}),
        html.Span(action["due"],
                  style={"fontSize": "0.76rem", "color": COLORS["text_secondary"],
                         "fontFamily": "JetBrains Mono, monospace"}),
        html.Span(action["status"],
                  style={"background": status_color + "22", "color": status_color,
                         "padding": "2px 8px", "borderRadius": "4px",
                         "fontSize": "0.7rem", "fontWeight": 600,
                         "textAlign": "center"}),
    ])
