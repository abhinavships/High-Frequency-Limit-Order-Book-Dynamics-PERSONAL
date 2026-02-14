import plotly.graph_objects as go
import pandas as pd
import numpy as np

def generate_mock_lob_data():
    """Generates mock LOB data for testing visualization."""
    # Mid price around 100
    mid_price = 100
    
    # Generate Bids (Buy orders) - Prices < Mid Price
    # Prices descending from just below mid
    bids_prices = np.sort(np.random.uniform(mid_price - 1, mid_price - 0.05, 20))[::-1]
    bids_volumes = np.random.randint(10, 100, 20)
    
    # Generate Asks (Sell orders) - Prices > Mid Price
    # Prices ascending from just above mid
    asks_prices = np.sort(np.random.uniform(mid_price + 0.05, mid_price + 1, 20))
    asks_volumes = np.random.randint(10, 100, 20)
    
    return {
        'bids': pd.DataFrame({'price': bids_prices, 'volume': bids_volumes}),
        'asks': pd.DataFrame({'price': asks_prices, 'volume': asks_volumes})
    }

def plot_lob_snapshot(lob_data=None, levels=10):
    """
    Create bid-ask ladder visualization (Order Book Snapshot).
    
    Args:
        lob_data (dict): Dictionary with 'bids' and 'asks' DataFrames. 
                         If None, generates mock data.
        levels (int): Number of price levels to show.
    """
    if lob_data is None:
        lob_data = generate_mock_lob_data()

    bids = lob_data['bids'].head(levels)
    asks = lob_data['asks'].head(levels)

    fig = go.Figure()

    # Bids (Green)
    fig.add_trace(go.Bar(
        x=bids['price'],
        y=bids['volume'],
        name='Bids',
        marker_color='green'
    ))

    # Asks (Red)
    fig.add_trace(go.Bar(
        x=asks['price'],
        y=asks['volume'],
        name='Asks',
        marker_color='red'
    ))

    fig.update_layout(
        title='Limit Order Book Snapshot',
        xaxis_title='Price',
        yaxis_title='Volume',
        barmode='overlay',
        bargap=0.1
    )
    
    return fig

def plot_depth_chart(lob_data=None):
    """
    Create Cumulative Depth Chart.
    
    Args:
        lob_data (dict): Dictionary with 'bids' and 'asks' DataFrames.
                         If None, generates mock data.
    """
    if lob_data is None:
        lob_data = generate_mock_lob_data()

    bids = lob_data['bids'].sort_values('price', ascending=False)
    asks = lob_data['asks'].sort_values('price', ascending=True)

    # Calculate cumulative volume
    bids['cumulative_volume'] = bids['volume'].cumsum()
    asks['cumulative_volume'] = asks['volume'].cumsum()

    fig = go.Figure()

    # Bids Area (Green) - Filled
    fig.add_trace(go.Scatter(
        x=bids['price'],
        y=bids['cumulative_volume'],
        name='Bids Depth',
        mode='lines',
        fill='tozeroy',
        line=dict(color='green'),
        fillcolor='rgba(0, 255, 0, 0.2)' # Semi-transparent green
    ))

    # Asks Area (Red) - Filled
    fig.add_trace(go.Scatter(
        x=asks['price'],
        y=asks['cumulative_volume'],
        name='Asks Depth',
        mode='lines',
        fill='tozeroy',
        line=dict(color='red'),
        fillcolor='rgba(255, 0, 0, 0.2)' # Semi-transparent red
    ))

    fig.update_layout(
        title='Market Depth Chart',
        xaxis_title='Price',
        yaxis_title='Cumulative Volume',
        template='plotly_dark' # Optional: Dark theme looks cool for financial apps
    )
    
    return fig

def plot_spread_evolution(timestamps=None, spreads=None):
    """
    Time series of bid-ask spread.
    
    Args:
        timestamps (list): List of timestamps.
        spreads (list): List of spread values.
    """
    if timestamps is None or spreads is None:
        # Mock data: Time series over last 5 minutes
        timestamps = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='3S')
        # Simulate mean-reverting spread
        spreads = np.abs(np.random.normal(0.05, 0.02, 100))

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=spreads,
        mode='lines',
        name='Spread',
        line=dict(color='blue')
    ))

    fig.update_layout(
        title='Bid-Ask Spread Evolution',
        xaxis_title='Time',
        yaxis_title='Spread',
        template='plotly_white'
    )

    return fig
