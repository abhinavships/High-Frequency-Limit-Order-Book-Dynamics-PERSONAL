import numpy as np
import pandas as pd
import sys
import os
from itertools import product

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from strategy.avellaneda_stoikov import AvellanedaStoikovMarketMaker
from backtesting.engine import BacktestEngine

def run_grid_search():
    print("Starting Parameter Optimization (Grid Search)...")
    
    # Define parameter grid
    gammas = [0.01, 0.1, 0.5, 1.0]
    ks = [0.5, 1.5, 5.0]
    windows = [1000] # Simulation steps
    
    results = []
    
    for gamma, k in product(gammas, ks):
        engine = BacktestEngine(initial_capital=100000)
        strategy = AvellanedaStoikovMarketMaker(gamma=gamma, k=k, T=1.0)
        
        # Simulation
        mid_price = 100.0
        prices = [mid_price]
        for _ in range(1000):
            prices.append(prices[-1] + np.random.normal(0, 0.05))
            
        for i in range(1000):
            current_time = pd.Timestamp.now() + pd.Timedelta(seconds=i)
            time_left = max(0, 1.0 - i/1000)
            
            quotes = strategy.quote(prices[i], engine.inventory, sigma=2.0, time_left=time_left)
            
            # Simple fill probability
            prob_fill = np.exp(-k * quotes['spread'] / 2)
            
            if np.random.rand() < prob_fill:
                engine.process_fill('buy', quotes['bid'], 1, current_time)
            if np.random.rand() < prob_fill:
                engine.process_fill('sell', quotes['ask'], 1, current_time)
                
        metrics = engine.calculate_metrics()
        results.append({
            'gamma': gamma,
            'k': k,
            'sharpe': metrics['sharpe'],
            'total_return': metrics['total_return'],
            'max_dd': metrics['max_drawdown'],
            'final_inventory': engine.inventory
        })
        print(f"Tested gamma={gamma}, k={k}: Sharpe={metrics['sharpe']:.2f}")
        
    # Find best parameters
    df_results = pd.DataFrame(results)
    best_sharpe = df_results.loc[df_results['sharpe'].idxmax()]
    
    print("\noptimization Results:")
    print(df_results.sort_values(by='sharpe', ascending=False))
    print("\nBest Parameters:")
    print(best_sharpe)
    
    # Save results
    df_results.to_csv('optimization_results.csv', index=False)
    print("Results saved to optimization_results.csv")

if __name__ == "__main__":
    run_grid_search()
