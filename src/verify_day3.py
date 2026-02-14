import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from strategy.avellaneda_stoikov import AvellanedaStoikovMarketMaker
from backtesting.engine import BacktestEngine
from visualization.backtest_plots import create_equity_curve, create_drawdown_chart

def test_strategy():
    print("Testing Avellaneda-Stoikov Strategy...")
    strategy = AvellanedaStoikovMarketMaker(gamma=0.1, k=1.5, T=1.0)
    
    mid_price = 100.0
    inventory = 0
    sigma = 2.0
    time_left = 1.0
    
    quotes = strategy.quote(mid_price, inventory, sigma, time_left)
    print(f"Quotes (Inv=0): {quotes}")
    
    # Test inventory skew
    inventory = 50
    quotes_skewed = strategy.quote(mid_price, inventory, sigma, time_left)
    print(f"Quotes (Inv=50): {quotes_skewed}")
    
    assert quotes_skewed['bid'] < quotes['bid'], "Bid should be lower with positive inventory"
    assert quotes_skewed['ask'] < quotes['ask'], "Ask should be lower with positive inventory"
    print("Strategy test passed.")

def test_engine():
    print("\nTesting Backtest Engine...")
    engine = BacktestEngine(initial_capital=100000)
    
    start_time = datetime.now()
    
    # Simulate some trades
    engine.process_fill('buy', 100.0, 10, start_time)
    print(f"After Buy: Inv={engine.inventory}, Cap={engine.capital}")
    
    engine.process_fill('sell', 101.0, 10, start_time + timedelta(seconds=1))
    print(f"After Sell: Inv={engine.inventory}, Cap={engine.capital}")
    
    metrics = engine.calculate_metrics()
    print(f"Metrics: {metrics}")
    
    assert metrics['total_return'] > 0, "Should have positive return"
    print("Engine test passed.")

def test_visualization():
    print("\nTesting Visualization...")
    # Mock data
    timestamps = [datetime.now() + timedelta(minutes=i) for i in range(10)]
    equity = [100000 + i*10 + np.random.randn()*5 for i in range(10)]
    
    fig_equity = create_equity_curve(timestamps, equity)
    fig_dd = create_drawdown_chart(timestamps, equity)
    
    print("Visualization objects created successfully.")

if __name__ == "__main__":
    test_strategy()
    test_engine()
    test_visualization()
