from dash import dcc, html
import plotly.graph_objects as go
import config

def shap_waterfall_chart(base_value, features, final_value, title="Feature Importance (SHAP)"):
    """
    Creates a SHAP-style waterfall chart using Plotly to explain KPI outcomes.
    
    Args:
        base_value (float): The expected or baseline value.
        features (list of dicts): List containing feature names and their impact values.
                                  e.g. [{"name": "Temperature", "impact": 15}, {"name": "Promo", "impact": -5}]
        final_value (float): The final predicted value.
        title (str): Chart title.
    """
    
    # Prepare data for Plotly Waterfall
    x_data = ["Base Value"] + [f["name"] for f in features] + ["Final Prediction"]
    
    # Plotly expects 'relative' for intermediate steps and 'total' for start/end
    measure = ["absolute"] + ["relative"] * len(features) + ["total"]
    
    # Values
    y_data = [base_value] + [f["impact"] for f in features] + [final_value]
    
    # Format labels
    text = [f"{val:+.1f}" if i > 0 and i < len(y_data)-1 else f"{val:.1f}" for i, val in enumerate(y_data)]
    
    fig = go.Figure(go.Waterfall(
        name = "20", orientation = "v",
        measure = measure,
        x = x_data,
        textposition = "outside",
        text = text,
        y = y_data,
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
        increasing = {"marker":{"color":"#2ECC71"}}, # Green for positive impact
        decreasing = {"marker":{"color":"#E74C3C"}}, # Red for negative impact
        totals = {"marker":{"color":"#3498DB"}}      # Blue for totals
    ))
    
    fig.update_layout(
        title=title,
        waterfallgap=0.3,
        margin=dict(l=40, r=40, t=40, b=40),
        height=300
    )
    
    # Apply dark layout if configured
    if hasattr(config, 'apply_dark_layout'):
        fig = config.apply_dark_layout(fig)
        
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def lime_feature_bars(features, title="LIME Feature Weights"):
    """
    Alternative Explainability chart: A horizontal bar chart for LIME weights.
    """
    features_sorted = sorted(features, key=lambda x: abs(x['impact']), reverse=False)
    
    y_data = [f["name"] for f in features_sorted]
    x_data = [f["impact"] for f in features_sorted]
    colors = ['#2ECC71' if val > 0 else '#E74C3C' for val in x_data]
    
    fig = go.Figure(go.Bar(
        x=x_data,
        y=y_data,
        orientation='h',
        marker_color=colors
    ))
    
    fig.update_layout(
        title=title,
        margin=dict(l=40, r=40, t=40, b=40),
        height=250,
        xaxis_title="Impact on Prediction"
    )
    
    if hasattr(config, 'apply_dark_layout'):
        fig = config.apply_dark_layout(fig)
        
    return dcc.Graph(figure=fig, config={'displayModeBar': False})
