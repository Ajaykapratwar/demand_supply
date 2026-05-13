"""dashboards/forecast_analytics.py  ─  Dashboard 3: Forecast Analytics"""
from dash import html, dcc
from components.theme import COLORS
from components.kpi_cards import kpi_card
from components import charts
from data.mock_data import (
    get_forecast_accuracy_kpis, get_forecast_vs_actual,
    get_fva_waterfall, get_bias_by_category,
)

ACC_CONFIG = {
    "mape":    ("MAPE",         "%",  True,  "warning"),
    "wape":    ("WAPE",         "%",  True,  "success"),
    "bias":    ("Bias",         "%",  False, "success"),
    "fva":     ("FVA Score",    "pp", False, "success"),
    "p90_cov": ("P90 Coverage", "%",  False, "success"),
}


def layout() -> html.Div:
    acc    = get_forecast_accuracy_kpis()
    fva_df = get_forecast_vs_actual()
    fva_w  = get_fva_waterfall()
    bias_df = get_bias_by_category()

    sparkline_dummy = [acc[k]["value"] + i * 0.05 for i in range(14)]

    kpi_row = [
        kpi_card(
            label=label, value=acc[k]["value"], unit=unit,
            target=0.0, delta=acc[k]["delta"],
            sparkline_data=sparkline_dummy,
            status=acc[k]["status"], delta_invert=invert,
        )
        for k, (label, unit, invert, _) in ACC_CONFIG.items()
    ]

    return html.Div([
        html.Div(className="page-title", children=[
            html.Span("📈", className="icon"), "Forecast Analytics",
        ]),
        html.Div(className="grid-kpi", style={"gridTemplateColumns": "repeat(5, 1fr)"},
                 children=kpi_row),

        # Forecast vs Actual chart
        html.Div(className="card", style={"marginBottom": "16px"}, children=[
            dcc.Graph(figure=charts.forecast_vs_actual_chart(fva_df),
                      config={"displayModeBar": False}, style={"height": "300px"}),
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="card", children=[
                dcc.Graph(figure=charts.fva_waterfall(fva_w),
                          config={"displayModeBar": False}, style={"height": "280px"}),
            ]),
            html.Div(className="card", children=[
                dcc.Graph(figure=charts.bias_by_category_chart(bias_df),
                          config={"displayModeBar": False}, style={"height": "260px"}),
                html.Div(style={"padding": "4px 8px", "marginTop": "4px"}, children=[
                    html.Div(className="ai-badge", children="[AI GENERATED]",
                             style={"display": "inline-block", "marginRight": "6px"}),
                    html.Span(
                        "Apparel bias at +6.2% indicates systematic over-forecasting — "
                        "likely driven by promo calendar misalignment. "
                        "Recommend re-running promo uplift calibration.",
                        style={"fontSize": "0.76rem", "color": COLORS["text_secondary"]},
                    ),
                ]),
            ]),
        ]),
    ])
