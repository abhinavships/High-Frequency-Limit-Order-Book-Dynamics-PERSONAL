import sys
import os
import pandas as pd
import plotly.graph_objects as go

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.data_pipeline.lob_structure import LimitOrderBook
    from src.data_pipeline.lob_loader import generate_initial_lob, simulate_lob_step
    from src.visualization.lob_plots import plot_lob_snapshot, plot_spread_evolution, plot_depth_chart
    print("Imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def validate_integration():
    print("Initializing LOB...")
    lob = generate_initial_lob(mid_price=100.0, depth=20)
    
    print("Simulating 10 steps...")
    for _ in range(10):
        lob = simulate_lob_step(lob)
    
    print("Fetching depth and adapting data...")
    depth_bids, depth_asks = lob.get_depth(levels=10)
    lob_data = {
        'bids': pd.DataFrame(list(depth_bids.items()), columns=['price', 'volume']),
        'asks': pd.DataFrame(list(depth_asks.items()), columns=['price', 'volume'])
    }
    
    print("Checking dataframes...")
    if lob_data['bids'].empty or lob_data['asks'].empty:
        print("Warning: Bids or Asks dataframe is empty.")
    else:
        print("Dataframes populated.")

    print("Generating LOB Snapshot Plot...")
    fig1 = plot_lob_snapshot(lob_data)
    if not isinstance(fig1, go.Figure):
        print("Error: plot_lob_snapshot failed.")
        sys.exit(1)
        
    print("Generating Depth Chart...")
    fig2 = plot_depth_chart(lob_data)
    if not isinstance(fig2, go.Figure):
        print("Error: plot_depth_chart failed.")
        sys.exit(1)
        
    print("Generating Statistics...")
    mid = lob.get_mid_price()
    spread = lob.get_spread()
    vol = lob.get_volatility()
    ofi = lob.get_ofi()
    
    print(f"Mid: {mid}, Spread: {spread}, Volatility: {vol}, OFI: {ofi}")
    
    if mid is None or spread is None:
        print("Error: Mid price or spread calculation failed.")
        sys.exit(1)
        
    print("\nIntegration Validation Passed!")

if __name__ == "__main__":
    validate_integration()
