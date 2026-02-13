import sys
import os
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from backtesting.engine import BacktestEngine

def test_risk_limits():
    print("Testing Risk Limits...")
    # Initialize engine with small max position
    engine = BacktestEngine(initial_capital=100000, max_position=5)
    
    start_time = datetime.now()
    
    # Buy 5 (Allowed)
    print("Buying 5...")
    success = engine.process_fill('buy', 100.0, 5, start_time)
    print(f"Buy 5 Success: {success}, Inventory: {engine.inventory}")
    assert success == True
    assert engine.inventory == 5
    
    # Buy 1 more (Should Fail)
    print("Buying 1 more (Should Fail)...")
    success = engine.process_fill('buy', 100.0, 1, start_time)
    print(f"Buy 1 Success: {success}, Inventory: {engine.inventory}")
    assert success == False
    assert engine.inventory == 5
    
    # Sell 5 (Allowed)
    print("Selling 5...")
    success = engine.process_fill('sell', 100.0, 5, start_time)
    print(f"Sell 5 Success: {success}, Inventory: {engine.inventory}")
    assert success == True
    assert engine.inventory == 0
    
    # Sell 6 (Should Fail - limit is 5, so -5 is max short)
    print("Selling 6 (Should Fail)...")
    success = engine.process_fill('sell', 100.0, 6, start_time)
    print(f"Sell 6 Success: {success}, Inventory: {engine.inventory}")
    assert success == False
    assert engine.inventory == 0
    
    # Sell 5 (Allowed)
    print("Selling 5...")
    success = engine.process_fill('sell', 100.0, 5, start_time)
    print(f"Sell 5 Success: {success}, Inventory: {engine.inventory}")
    assert success == True
    assert engine.inventory == -5
    
    print("Risk Limits Test Passed.")

if __name__ == "__main__":
    test_risk_limits()
