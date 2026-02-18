import sys
import os
import pandas as pd
import numpy as np
import itertools
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.strategy.avellaneda_stoikov import AvellanedaStoikovMarketMaker
from src.backtesting.engine import BacktestEngine
from src.data_pipeline.lob_loader import generate_initial_lob

def run_sensitivity_analysis():
    print("Starting Sensitivity Analysis...")
    
    # Parameters to vary
    gamma_values = [0.01, 0.05, 0.1, 0.5, 1.0]
    k_values = [0.5, 1.0, 1.5, 2.0]
    
    results = []
    
    total_iterations = len(gamma_values) * len(k_values)
    count = 0
    
    for gamma, k in itertools.product(gamma_values, k_values):
        count += 1
        print(f"[{count}/{total_iterations}] Testing gamma={gamma}, k={k}...")
        
        # Setup Backtest
        strategy = AvellanedaStoikovMarketMaker(gamma=gamma, k=k, T=1.0)
        engine = BacktestEngine(initial_capital=100000)
        
        # Simulation Loop (simplified for speed)
        mid_price = 100.0
        prices = [mid_price]
        sim_steps = 1000
        
        # Simple price path
        np.random.seed(42) # Ensure reproducibility
        for _ in range(sim_steps):
            change = np.random.normal(0, 0.1)
            prices.append(prices[-1] + change)
            
        for i in range(sim_steps):
            current_time = pd.Timestamp.now() + pd.Timedelta(seconds=i)
            current_price = prices[i]
            time_left = max(0, 1.0 - (i / sim_steps) * 1.0)
            
            # Get Quotes
            quotes = strategy.quote(current_price, engine.inventory, sigma=2.0, time_left=time_left)
            
            # Simulate Fill
            prob_fill = np.exp(-k * quotes['spread'] / 2)
            
            if np.random.rand() < prob_fill:
                engine.process_fill('buy', quotes['bid'], 1, current_time)
            if np.random.rand() < prob_fill:
                engine.process_fill('sell', quotes['ask'], 1, current_time)
                
        # Calculate Metrics
        metrics = engine.calculate_metrics()
        results.append({
            'gamma': gamma,
            'k': k,
            'sharpe_ratio': metrics['sharpe'],
            'total_return': metrics['total_return'],
            'max_drawdown': metrics['max_drawdown']
        })
        
    # Convert to DataFrame
    df_results = pd.DataFrame(results)
    
    # Save results
    output_path = os.path.join(os.path.dirname(__file__), 'sensitivity_results.csv')
    df_results.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")
    
    # Generate Heatmap
    pivot_table = df_results.pivot(index='gamma', columns='k', values='sharpe_ratio')
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot_table, annot=True, cmap='RdYlGn', fmt='.2f')
    plt.title('Sharpe Ratio Sensitivity to Risk Aversion (gamma) and Arrival Rate (k)')
    plt.xlabel('Arrival Rate (k)')
    plt.ylabel('Risk Aversion (gamma)')
    
    plot_path = os.path.join(os.path.dirname(__file__), 'sensitivity_heatmap.png')
    plt.savefig(plot_path)
    print(f"Heatmap saved to {plot_path}")
    
    return df_results

if __name__ == "__main__":
    run_sensitivity_analysis()
