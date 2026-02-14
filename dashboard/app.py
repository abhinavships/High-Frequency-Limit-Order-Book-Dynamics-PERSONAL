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
# Person 4: Microstructure & Analysis
from src.models.microstructure import calculate_ofi_step, calculate_vpin, estimate_price_impact
from src.analysis.sensitivity import run_sensitivity_analysis

st.set_page_config(page_title="LOB Analyzer", layout="wide")

st.title("Limit Order Book Dynamics & Market Microstructure")

# Initialize Session State
if 'lob' not in st.session_state:
    st.session_state.lob = generate_initial_lob(mid_price=100.0, depth=50)
if 'spread_history' not in st.session_state:
    st.session_state.spread_history = []
if 'timestamp_history' not in st.session_state:
    st.session_state.timestamp_history = []
# Microstructure Metrics History
if 'ofi_history' not in st.session_state:
    st.session_state.ofi_history = []
if 'vpin_history' not in st.session_state:
    st.session_state.vpin_history = []
if 'price_history' not in st.session_state:
    st.session_state.price_history = []
if 'volume_history' not in st.session_state:
    st.session_state.volume_history = []

# Sidebar
st.sidebar.header("Settings")
stock_symbol = st.sidebar.selectbox("Select Stock", ["RELIANCE", "TCS", "INFY", "MOCK-DATA"])
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 60, 2)
auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=False)

# Navigation
page = st.sidebar.radio("Navigate", ["Dashboard", "Backtest & Sensitivity", "Technical Report"])

if page == "Dashboard":
    # Simulate Data Update
    if auto_refresh or st.button("Manual Refresh"):
        prev_lob = st.session_state.lob
        st.session_state.lob = simulate_lob_step(st.session_state.lob)
        
        # Calculate Metrics
        current_time = pd.Timestamp.now()
        spread = st.session_state.lob.get_spread()
        mid_price = st.session_state.lob.get_mid_price()
        
        # OFI
        ofi = calculate_ofi_step(prev_lob, st.session_state.lob)
        
        # VPIN (Simplified for real-time)
        # We need trade volume, here we simulate it or derive from LOB changes (limited accuracy without trade tape)
        # For demo, we use random trade volume logic or LOB volume delta
        trade_vol = np.abs(np.random.normal(100, 20)) # Mock trade volume for VPIN demo
        price_change = mid_price - (st.session_state.price_history[-1] if st.session_state.price_history else mid_price)
        
        # Store for VPIN calc (needs window)
        st.session_state.price_history.append(mid_price)
        st.session_state.volume_history.append(trade_vol)
        
        if len(st.session_state.price_history) > 50:
             prices = pd.Series(st.session_state.price_history[-50:])
             volumes = pd.Series(st.session_state.volume_history[-50:])
             sigma = prices.pct_change().std()
             v_buy, v_sell = calculate_vpin(volumes, prices.diff(), sigma) # This returns vectors
             # VPIN is aggregated metric
             vpin_val = (np.abs(v_buy - v_sell).sum()) / (v_buy + v_sell).sum()
             st.session_state.vpin_history.append(vpin_val)
        else:
             st.session_state.vpin_history.append(0.5) # Default neutral

        if spread:
            st.session_state.spread_history.append(spread)
            st.session_state.timestamp_history.append(current_time)
            st.session_state.ofi_history.append(ofi)
            
            # Keep history manageable
            if len(st.session_state.spread_history) > 100:
                st.session_state.spread_history.pop(0)
                st.session_state.timestamp_history.pop(0)
                st.session_state.ofi_history.pop(0)
                st.session_state.vpin_history.pop(0)

    # Layout
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Order Book Snapshot")
        depth_bids, depth_asks = st.session_state.lob.get_depth(levels=20)
        lob_data = {
            'bids': pd.DataFrame(list(depth_bids.items()), columns=['price', 'volume']),
            'asks': pd.DataFrame(list(depth_asks.items()), columns=['price', 'volume'])
        }
        fig_lob = plot_lob_snapshot(lob_data) 
        st.plotly_chart(fig_lob, use_container_width=True)

    with col2:
        st.subheader("Spread Evolution")
        fig_spread = plot_spread_evolution(st.session_state.timestamp_history, st.session_state.spread_history)
        st.plotly_chart(fig_spread, use_container_width=True)

    st.subheader("Microstructure Indicators")
    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        st.markdown("**Order Flow Imbalance (OFI)**")
        st.line_chart(pd.Series(st.session_state.ofi_history, name="OFI").tail(100))
        
    with m_col2:
        st.markdown("**VPIN (Flow Toxicity)**")
        st.line_chart(pd.Series(st.session_state.vpin_history, name="VPIN").tail(100))
        
    # Stats
    st.write("---")
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("Mid Price", f"{st.session_state.lob.get_mid_price():.2f}")
    with m_col2:
        st.metric("Spread", f"{st.session_state.lob.get_spread():.2f}")
    with m_col3:
        st.metric("Recent Volatility", f"{st.session_state.lob.get_volatility():.4f}")

elif page == "Backtest & Sensitivity":
    st.header("Strategy Backtesting & Sensitivity Analysis")
    
    tab1, tab2 = st.tabs(["Single Backtest", "Sensitivity Analysis"])
    
    with tab1:
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
            strategy = AvellanedaStoikovMarketMaker(gamma=gamma, k=k_param, T=T_param)
            engine = BacktestEngine(initial_capital=initial_capital)
            
            mid_price = 100.0
            prices = [mid_price]
            # Generate price path
            for _ in range(sim_steps):
                prices.append(prices[-1] + np.random.normal(0, 0.1))
                
            progress_bar = st.progress(0)
            for i in range(sim_steps):
                current_time = pd.Timestamp.now() + pd.Timedelta(seconds=i)
                current_price = prices[i]
                time_left = max(0, T_param - (i/sim_steps)*T_param)
                
                quotes = strategy.quote(current_price, engine.inventory, sigma, time_left)
                prob_fill = np.exp(-k_param * quotes['spread'] / 2)
                
                if np.random.rand() < prob_fill: engine.process_fill('buy', quotes['bid'], 1, current_time)
                if np.random.rand() < prob_fill: engine.process_fill('sell', quotes['ask'], 1, current_time)
                
                if i % (sim_steps // 100) == 0: progress_bar.progress((i+1)/sim_steps)
            progress_bar.empty()
            
            metrics = engine.calculate_metrics()
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Final Capital", f"${engine.capital:.2f}")
            col2.metric("Total Return", f"{metrics['total_return']:.2%}")
            col3.metric("Sharpe Ratio", f"{metrics['sharpe']:.2f}")
            col4.metric("Max Drawdown", f"{metrics['max_drawdown']:.2%}")
            
            if engine.pnl_history:
                st.plotly_chart(create_equity_curve(engine.timestamps, engine.pnl_history), use_container_width=True)
                st.plotly_chart(create_drawdown_chart(engine.timestamps, engine.pnl_history), use_container_width=True)
    
    with tab2:
        st.subheader("Sensitivity Analysis (Grid Search)")
        st.write("Varies Gamma (Risk Aversion) and K (Order Arrival Rate) to find optimal Sharpe Ratio.")
        
        if st.button("Run Sensitivity Analysis"):
            with st.spinner("Running batch simulations..."):
                df_results = run_sensitivity_analysis()
                st.success("Analysis Complete!")
                st.dataframe(df_results)
                
                # Plot Heatmap
                try:
                    import plotly.express as px
                    pivot = df_results.pivot(index='gamma', columns='k', values='sharpe_ratio')
                    fig = px.imshow(pivot, 
                                    labels=dict(x="Arrival Rate (k)", y="Risk Aversion (gamma)", color="Sharpe Ratio"),
                                    x=pivot.columns, y=pivot.index,
                                    title="Sharpe Ratio Heatmap",
                                    color_continuous_scale="RdYlGn")
                    st.plotly_chart(fig)
                except Exception as e:
                    st.error(f"Could not plot heatmap: {e}")

elif page == "Technical Report":
    st.markdown("## Technical Report")
    st.info("Technical Report is located in `docs/technical_report.md`")
    if os.path.exists("./docs/technical_report.md"):
        with open("./docs/technical_report.md", "r") as f:
            st.markdown(f.read())
    else:
        st.warning("Report not found.")

if auto_refresh:
    time.sleep(refresh_rate)
    st.experimental_rerun()
