import streamlit as st
import sys
import os
import time
import pandas as pd
import numpy as np

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.visualization.lob_plots import plot_lob_snapshot, plot_spread_evolution, plot_depth_chart
# Person 1 Integration: Import Data Pipeline
from src.data_pipeline.lob_structure import LimitOrderBook
from src.data_pipeline.lob_loader import generate_initial_lob, simulate_lob_step
from src.models.hawkes import HawkesProcess
from src.visualization.hawkes_plots import plot_intensity
# Person 3 & 1 Integration: Strategy & Backtesting
from src.strategy.avellaneda_stoikov import AvellanedaStoikovMarketMaker
from src.backtesting.engine import BacktestEngine
from src.visualization.backtest_plots import create_equity_curve, create_drawdown_chart

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
# --- Day 3: Backtesting Section ---
st.write("---")
st.header("Strategy Backtesting (Avellaneda-Stoikov)")

with st.expander("Backtest Settings", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        gamma = st.number_input("Risk Aversion (γ)", 0.01, 1.0, 0.1)
        sigma = st.number_input("Volatility (σ)", 0.1, 10.0, 2.0)
    with c2:
        k_param = st.number_input("Arrival Rate (k)", 0.1, 10.0, 1.5)
        T_param = st.number_input("Time Horizon (T)", 0.1, 5.0, 1.0)
    with c3:
        initial_capital = st.number_input("Initial Capital", 10000, 1000000, 100000)
        sim_steps = st.slider("Simulation Steps", 100, 5000, 1000)

if st.button("Run Backtest"):
    # Initialize components
    strategy = AvellanedaStoikovMarketMaker(gamma=gamma, k=k_param, T=T_param)
    engine = BacktestEngine(initial_capital=initial_capital)
    
    # Simulation Loop
    mid_price = st.session_state.lob.get_mid_price()
    # Simple random walk for mid_price simulation
    prices = [mid_price]
    for _ in range(sim_steps):
        change = np.random.normal(0, 0.1)
        prices.append(prices[-1] + change)
    
    progress_bar = st.progress(0)
    
    for i in range(sim_steps):
        current_time = pd.Timestamp.now() + pd.Timedelta(seconds=i)
        current_price = prices[i]
        time_left = max(0, T_param - (i / sim_steps) * T_param)
        
        # 1. Risk Check
        if strategy.should_adjust_quotes(engine.inventory, engine.max_position):
            # Skew quotes to flatten inventory deeply if needed, but strategy handles skew.
            # Here we might enforce a hard stop or wider speads if risk is VERY high.
            pass

        # Get Quotes
        quotes = strategy.quote(current_price, engine.inventory, sigma, time_left)
        
        # 2. Simulate Market Fills
        prob_fill = np.exp(-k_param * quotes['spread'] / 2)
        
        if np.random.rand() < prob_fill:
            # Buy fill
            engine.process_fill('buy', quotes['bid'], 1, current_time)
            
        if np.random.rand() < prob_fill:
            # Sell fill
            engine.process_fill('sell', quotes['ask'], 1, current_time)
            
        # Record PnL state even if no trade (mark to market)
        if len(engine.trades) > 0 and (i % 10 == 0): # Optimization: don't record every step if slow
             # Force a PnL record update if needed, but engine does it on fill.
             # We need continuous PnL for the chart.
             # Manually update pnl history in engine for charting purposes if no fill?
             # The engine currently only updates on fill? No, let's look at engine again.
             # Engine updates pnl_history on fill.
             # We should probably expose a method to update MTM without fill.
             pass
             
        if i % (sim_steps // 100) == 0:
            progress_bar.progress((i + 1) / sim_steps)

    progress_bar.empty()
    
    # Display Results
    metrics = engine.calculate_metrics()
    
    st.subheader("Backtest Results")
    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    res_col1.metric("Final Capital", f"${engine.capital:.2f}")
    res_col2.metric("Total Return", f"{metrics['total_return']:.2%}")
    res_col3.metric("Sharpe Ratio", f"{metrics['sharpe']:.2f}")
    res_col4.metric("Max Drawdown", f"{metrics['max_drawdown']:.2%}")
    
    # Visualizations
    if engine.pnl_history:
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            st.plotly_chart(create_equity_curve(engine.timestamps, engine.pnl_history), use_container_width=True)
        with b_col2:
            st.plotly_chart(create_drawdown_chart(engine.timestamps, engine.pnl_history), use_container_width=True)
    else:
        st.warning("No trades executed during simulation.")

st.caption("High-Frequency Limit Order Book Dynamics Project - Day 3 Dashboard (Integrated)")

if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
