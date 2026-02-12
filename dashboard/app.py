import streamlit as st
import sys
import os
import time
import pandas as pd

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.visualization.lob_plots import plot_lob_snapshot, plot_spread_evolution, plot_depth_chart
# Person 1 Integration: Import Data Pipeline
from src.data_pipeline.lob_structure import LimitOrderBook
from src.data_pipeline.lob_loader import generate_initial_lob, simulate_lob_step
from src.models.hawkes import HawkesProcess
from src.visualization.hawkes_plots import plot_intensity

st.set_page_config(page_title="LOB Analyzer", layout="wide")

st.title("Limit Order Book Dynamics Analysis")

# Initialize Session State for LOB
if 'lob' not in st.session_state:
    st.session_state.lob = generate_initial_lob(mid_price=100.0, depth=50)
if 'spread_history' not in st.session_state:
    st.session_state.spread_history = []
if 'timestamp_history' not in st.session_state:
    st.session_state.timestamp_history = []

# Sidebar
st.sidebar.header("Settings")
stock_symbol = st.sidebar.selectbox("Select Stock", ["RELIANCE", "TCS", "INFY", "MOCK-DATA"])
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 60, 2)
auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=False)
st.sidebar.info(f"Viewing data for: {stock_symbol}")

st.sidebar.markdown("---")
st.sidebar.header("Hawkes Process Settings")
show_hawkes = st.sidebar.checkbox("Show Hawkes Analysis", value=False)
if show_hawkes:
    h_mu = st.sidebar.slider("Base Intensity (μ)", 0.1, 5.0, 1.0)
    h_alpha = st.sidebar.slider("Excitation (α)", 0.0, 2.0, 0.5)
    h_beta = st.sidebar.slider("Decay (β)", 0.1, 5.0, 1.0)
    
    if st.sidebar.button("Run Hawkes Simulation"):
        hp = HawkesProcess(mu=h_mu, alpha=h_alpha, beta=h_beta)
        st.session_state.hawkes_events = hp.simulate(T_max=100)
        st.session_state.hawkes_model = hp

# Simulate Data Update (Person 1 Logic)
if auto_refresh or st.button("Manual Refresh"):
    st.session_state.lob = simulate_lob_step(st.session_state.lob)
    
    # Update histories
    current_time = pd.Timestamp.now()
    spread = st.session_state.lob.get_spread()
    if spread:
        st.session_state.spread_history.append(spread)
        st.session_state.timestamp_history.append(current_time)
        
        # Keep history manageable
        if len(st.session_state.spread_history) > 100:
            st.session_state.spread_history.pop(0)
            st.session_state.timestamp_history.pop(0)

# Prepare Data for Plots (Adapter)
# lob_plots expects a dict with 'bids' and 'asks' DataFrames
depth_bids, depth_asks = st.session_state.lob.get_depth(levels=20)

lob_data = {
    'bids': pd.DataFrame(list(depth_bids.items()), columns=['price', 'volume']),
    'asks': pd.DataFrame(list(depth_asks.items()), columns=['price', 'volume'])
}

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Order Book Snapshot")
    fig_lob = plot_lob_snapshot(lob_data) 
    st.plotly_chart(fig_lob, use_container_width=True)

with col2:
    st.subheader("Spread Analytics")
    fig_spread = plot_spread_evolution(st.session_state.timestamp_history, st.session_state.spread_history)
    st.plotly_chart(fig_spread, use_container_width=True)

st.subheader("Market Depth")
fig_depth = plot_depth_chart(lob_data)
st.plotly_chart(fig_depth, use_container_width=True)

# Metrics Section (Person 1 Statistics)
st.write("---")
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.metric("Mid Price", f"{st.session_state.lob.get_mid_price():.2f}")
with m_col2:
    st.metric("Spread", f"{st.session_state.lob.get_spread():.2f}")
with m_col3:
    st.metric("Recent Volatility", f"{st.session_state.lob.get_volatility():.4f}")

if show_hawkes and 'hawkes_events' in st.session_state:
    st.write("---")
    st.header("Hawkes Process Analysis")
    
    # Calculate fit if not already done (optional, for now just show ground truth vs simulation)
    # But task says "Plot intensity function"
    
    fig_hawkes = plot_intensity(st.session_state.hawkes_model, st.session_state.hawkes_events)
    st.plotly_chart(fig_hawkes, use_container_width=True)
    
    st.caption(f"Simulated {len(st.session_state.hawkes_events)} events over T=100.")

st.write("---")
st.caption("High-Frequency Limit Order Book Dynamics Project - Day 1 Dashboard (Integrated)")

if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
