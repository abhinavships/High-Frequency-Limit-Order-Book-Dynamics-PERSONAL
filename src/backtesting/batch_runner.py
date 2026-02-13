import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from strategy.avellaneda_stoikov import AvellanedaStoikovMarketMaker
from backtesting.engine import BacktestEngine

def run_batch_backtest():
    print("Starting Comprehensive Batch Backtest...")
    
    stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']
    results = []
    
    # Parameters
    gamma = 0.1
    k = 1.5
    sim_steps = 1000
    
    for stock in stocks:
        print(f"Testing on {stock}...")
        engine = BacktestEngine(initial_capital=100000)
        strategy = AvellanedaStoikovMarketMaker(gamma=gamma, k=k)
        
        # Simulate check
        mid_price = 100 + np.random.randn() * 10
        prices = [mid_price]
        
        # Volatility specific to stock (simulated)
        sigma = np.random.uniform(1.0, 5.0)
        
        for _ in range(sim_steps):
            prices.append(prices[-1] + np.random.normal(0, 0.1))
            
        for i in range(sim_steps):
            current_time = pd.Timestamp.now() + pd.Timedelta(seconds=i)
            time_left = max(0, 1.0 - i/sim_steps)
            
            quotes = strategy.quote(prices[i], engine.inventory, sigma=sigma, time_left=time_left)
            
            prob_fill = np.exp(-k * quotes['spread'] / 2)
            
            if np.random.rand() < prob_fill:
                 engine.process_fill('buy', quotes['bid'], 1, current_time)
            if np.random.rand() < prob_fill:
                 engine.process_fill('sell', quotes['ask'], 1, current_time)
                 
        metrics = engine.calculate_metrics()
        results.append({
            'Stock': stock,
            'Total Return': f"{metrics['total_return']:.2%}",
            'Sharpe': f"{metrics['sharpe']:.2f}",
            'Max Drawdown': f"{metrics['max_drawdown']:.2%}",
            'Final Inv': engine.inventory
        })
        
    df_res = pd.DataFrame(results)
    print("\nBatch Backtest Results:")
    print(df_res)
    
    # Save
    df_res.to_csv('batch_backtest_results.csv', index=False)
    print("Results saved to batch_backtest_results.csv")

if __name__ == "__main__":
    run_batch_backtest()
