import plotly.graph_objects as go
import numpy as np

def create_equity_curve(timestamps, equity_values):
    """
    Create an Equity Curve chart.
    
    Args:
        timestamps (list): List of timestamps.
        equity_values (list): List of equity values (PnL history).
        
    Returns:
        plotly.graph_objects.Figure
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timestamps, 
        y=equity_values, 
        mode='lines', 
        name='Equity',
        line=dict(color='#00ff00', width=2)
    ))
    
    fig.update_layout(
        title='Strategy Equity Curve',
        xaxis_title='Time',
        yaxis_title='Account Equity ($)',
        template='plotly_dark',
        height=400
    )
    return fig

def create_drawdown_chart(timestamps, equity_values):
    """
    Create a Drawdown chart.
    
    Args:
        timestamps (list): List of timestamps.
        equity_values (list): List of equity values.
    
    Returns:
        plotly.graph_objects.Figure
    """
    equity_array = np.array(equity_values)
    if len(equity_array) == 0:
         peak = np.array([])
         drawdown = np.array([])
    else:
        peak = np.maximum.accumulate(equity_array)
        with np.errstate(divide='ignore', invalid='ignore'):
            drawdown = (equity_array - peak) / peak
        drawdown = np.nan_to_num(drawdown)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timestamps, 
        y=drawdown, 
        mode='lines', 
        name='Drawdown',
        fill='tozeroy',
        line=dict(color='#ff0000', width=1)
    ))
    
    fig.update_layout(
        title='Strategy Drawdown',
        xaxis_title='Time',
        yaxis_title='Drawdown (%)',
        template='plotly_dark',
        height=400,
        yaxis=dict(tickformat='.1%')
    )
    return fig
