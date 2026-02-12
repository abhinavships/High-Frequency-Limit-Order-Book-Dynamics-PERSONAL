import plotly.graph_objects as go
import numpy as np
import pandas as pd

def plot_intensity(hawkes_model, event_times, t_max=None, resolution=200):
    """
    Plot the intensity function of a Hawkes process.
    
    Args:
        hawkes_model: Instance of HawkesProcess class
        event_times: list or array of event timestamps
        t_max: end time for plot. If None, max(event_times) + buffer
        resolution: number of points to plot
    """
    if len(event_times) == 0:
        return go.Figure().update_layout(title="No events to plot intensity")
        
    if t_max is None:
        t_max = event_times[-1] * 1.1
        
    t_values = np.linspace(0, t_max, resolution)
    lambda_values = [hawkes_model.intensity(t, event_times) for t in t_values]
    
    fig = go.Figure()
    
    # Plot Intensity Function
    fig.add_trace(go.Scatter(
        x=t_values,
        y=lambda_values,
        mode='lines',
        name='Intensity λ(t)',
        line=dict(color='blue')
    ))
    
    # Plot Events as markers on the x-axis (or rug plot)
    # We'll put them at y=0 or slightly above
    fig.add_trace(go.Scatter(
        x=event_times,
        y=np.zeros_like(event_times),
        mode='markers',
        name='Events',
        marker=dict(symbol='line-ns-open', size=10, color='red', line=dict(width=2))
    ))
    
    fig.update_layout(
        title=f'Hawkes Process Intensity (μ={hawkes_model.mu:.2f}, α={hawkes_model.alpha:.2f}, β={hawkes_model.beta:.2f})',
        xaxis_title='Time',
        yaxis_title='Intensity',
        template='plotly_white'
    )
    
    return fig
