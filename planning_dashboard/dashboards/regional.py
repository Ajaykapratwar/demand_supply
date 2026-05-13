"""dashboards/regional.py — Dashboard 9: Regional Planning (LIVE)"""
from dash import html, dcc, Input, Output, callback
from components.theme import COLORS
from components import charts
from data.data_loader import get_regional_kpis, get_region_vs_plan
from data.mock_data import get_safety_stock_simulation

def layout():
    reg_df = get_regional_kpis()
    rvp_df = get_region_vs_plan()

    return html.Div([
        html.Div(className="page-title", children=[html.Span("🗺️","icon"), "Regional Planning — Live KPIs"]),
        html.Div(style={"display":"grid","gridTemplateColumns":f"repeat({len(reg_df)},1fr)","gap":"12px","marginBottom":"16px"},
                 children=[_region_card(row) for _, row in reg_df.iterrows()]),
        html.Div(className="card", style={"marginBottom":"16px"}, children=[
            dcc.Graph(figure=charts.regional_bar_chart(rvp_df),
                      config={"displayModeBar":False}, style={"height":"300px"}),
        ]),
        html.Div(className="grid-2", children=[
            html.Div(className="card", children=[
                html.Div("SAFETY STOCK SIMULATOR", className="section-header"),
                html.Div(style={"marginBottom":"12px"}, children=[
                    html.Label("Target Service Level", style={"fontSize":"0.78rem","color":COLORS["text_secondary"],"display":"block","marginBottom":"6px"}),
                    dcc.Slider(id="reg-service-level", min=85, max=99, step=0.5, value=95,
                               marks={85:"85%",90:"90%",95:"95%",99:"99%"},
                               tooltip={"placement":"bottom","always_visible":True}),
                ]),
                html.Div(id="reg-sim-output"),
            ]),
            html.Div(className="card", children=[
                html.Div("PLAN ATTAINMENT BY REGION — LIVE", className="section-header"),
                html.Table(style={"width":"100%","borderCollapse":"collapse"}, children=[
                    html.Thead(html.Tr([html.Th(h, style={"padding":"8px 10px","fontSize":"0.7rem","textTransform":"uppercase",
                                                           "color":COLORS["text_secondary"],"textAlign":"left",
                                                           "borderBottom":f"1px solid {COLORS['border']}"})
                                        for h in ["Region","Revenue (Cr)","OTIF %","DOS","Stockout%","Plan Att."]])),
                    html.Tbody([_att_row(row) for _, row in reg_df.iterrows()]),
                ]),
            ]),
        ]),
    ])

def _region_card(row):
    c = COLORS["success"] if row["otif"] >= 90 else COLORS["warning"] if row["otif"] >= 85 else COLORS["danger"]
    return html.Div(className="card", children=[
        html.Div(style={"display":"flex","justifyContent":"space-between","marginBottom":"8px"}, children=[
            html.Span(row["region"], style={"fontSize":"0.9rem","fontWeight":700,"color":COLORS["text_primary"]}),
            html.Span(f"{row['revenue_cr']:.1f} Cr", style={"fontSize":"0.88rem","color":COLORS["chart_2"],"fontWeight":600,"fontFamily":"JetBrains Mono,monospace"}),
        ]),
        *[html.Div(style={"display":"flex","justifyContent":"space-between","padding":"3px 0","borderBottom":f"1px solid {COLORS['border']}33"}, children=[
            html.Span(lbl, style={"fontSize":"0.72rem","color":COLORS["text_secondary"]}),
            html.Span(val, style={"fontSize":"0.78rem","fontWeight":600,"color":col,"fontFamily":"JetBrains Mono,monospace"}),
          ]) for lbl, val, col in [
            ("OTIF", f"{row['otif']:.1f}%", c),
            ("DOS",  f"{row['dos']:.0f}d",  COLORS["text_secondary"]),
            ("SO%",  f"{row['stockout_pct']:.2f}%", COLORS["danger"] if row["stockout_pct"]>2 else COLORS["success"]),
          ]
        ],
    ])

def _att_row(row):
    att = row["plan_attainment"]
    ac  = COLORS["success"] if att>=95 else COLORS["warning"] if att>=88 else COLORS["danger"]
    return html.Tr([
        html.Td(row["region"], style={"padding":"8px 10px","fontSize":"0.82rem","fontWeight":500}),
        html.Td(f"{row['revenue_cr']:.1f}", style={"padding":"8px","fontFamily":"JetBrains Mono,monospace","fontSize":"0.82rem"}),
        html.Td(f"{row['otif']:.1f}%",      style={"padding":"8px","fontSize":"0.82rem"}),
        html.Td(f"{row['dos']:.0f}d",       style={"padding":"8px","fontSize":"0.82rem"}),
        html.Td(f"{row['stockout_pct']:.2f}%",style={"padding":"8px","fontSize":"0.82rem"}),
        html.Td(html.Span(f"{att:.0f}%", style={"background":ac+"22","color":ac,"padding":"2px 8px",
                          "borderRadius":"4px","fontSize":"0.78rem","fontWeight":700}), style={"padding":"8px"}),
    ], style={"borderBottom":f"1px solid {COLORS['border']}55"})

@callback(Output("reg-sim-output","children"), Input("reg-service-level","value"))
def update_sim(sl):
    sim = get_safety_stock_simulation(sl / 100)
    rows = [("Service Level",f"{sim['service_level']:.1f}%",COLORS["primary"]),
            ("Safety Stock",f"{sim['safety_stock']:,.0f} u",COLORS["chart_2"]),
            ("Reorder Point",f"{sim['reorder_point']:,.0f} u",COLORS["chart_1"]),
            ("Working Capital",f"${sim['working_capital_usd']:,.0f}",COLORS["chart_3"]),
            ("Stockout Risk",f"{sim['stockout_prob']:.2f}%",COLORS["danger"])]
    return html.Div(style={"marginTop":"12px"}, children=[
        html.Div(style={"display":"flex","justifyContent":"space-between","padding":"8px 0","borderBottom":f"1px solid {COLORS['border']}"}, children=[
            html.Span(l, style={"fontSize":"0.8rem","color":COLORS["text_secondary"]}),
            html.Span(v, style={"fontSize":"0.86rem","fontWeight":700,"color":c,"fontFamily":"JetBrains Mono,monospace"}),
        ]) for l, v, c in rows
    ])
