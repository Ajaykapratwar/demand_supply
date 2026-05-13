"""
components/charts.py  ─  Centralized Plotly chart factory.
"""
import plotly.graph_objects as go
import pandas as pd
from config import COLORS, LEGEND_STYLE, apply_dark_layout, hex_to_rgba

# A list of colors for the radar chart scenarios
CHART_COLORS = [
    COLORS["primary"],
    COLORS["warning"],
    COLORS["danger"],
    COLORS["success"],
    COLORS["info"]
]

def plan_vs_actual_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    x_col = "date" if "date" in df.columns else ("week" if "week" in df.columns else df.columns[0])
    fig.add_trace(go.Scatter(x=df[x_col], y=df["plan"], name="Plan",
        line=dict(color=COLORS["primary"], width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=df[x_col], y=df["actual"], name="Actual",
        line=dict(color=COLORS["success"], width=2),
        fill="tonexty", fillcolor=hex_to_rgba(COLORS["success"], 0.1)))
    apply_dark_layout(fig, title="Plan vs Actual — Demand Units", height=260,
                      legend=dict(**LEGEND_STYLE, orientation="h", y=1.12))
    return fig


def scenario_radar(df: pd.DataFrame) -> go.Figure:
    """
    Takes the scenario_comparison() DataFrame and generates a radar chart.
    Metrics: Total Cost, Service Level, Carbon, Inventory, Risk (optional, mock added).
    """
    # Assuming columns are: Scenario, Total Cost ($M), Service Level (%), Carbon (tCO₂e), Inventory ($M)
    metrics = ["Cost Impact", "Service Level", "Carbon", "Inventory"]
    fig = go.Figure()

    for i, row in df.iterrows():
        # Normalize values roughly for visual comparison (0-12 scale)
        cost_norm = row["Total Cost ($M)"] / 5.0
        service_norm = row["Service Level (%)"] / 10.0
        carbon_norm = row["Carbon (tCO₂e)"] / 120.0
        inventory_norm = row["Inventory ($M)"] / 2.0
        
        vals = [cost_norm, service_norm, carbon_norm, inventory_norm]
        vals.append(vals[0])  # Close the radar loop
        
        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=metrics + [metrics[0]],
            fill="toself",
            name=row["Scenario"],
            line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=1.5),
            fillcolor=hex_to_rgba(CHART_COLORS[i % len(CHART_COLORS)], 0.13),
            opacity=0.85,
        ))

    apply_dark_layout(fig, title="Scenario Radar", height=300)
    fig.update_layout(
        polar=dict(
            bgcolor=COLORS["card"],
            radialaxis=dict(visible=True, range=[0, 12],
                            gridcolor=COLORS["border"],
                            tickfont=dict(color=COLORS["text_secondary"], size=9)),
            angularaxis=dict(gridcolor=COLORS["border"],
                             tickfont=dict(color=COLORS["text_secondary"])),
        ),
    )
    return fig
