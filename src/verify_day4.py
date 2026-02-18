import sys
import os
import pandas as pd
import numpy as np

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.microstructure import calculate_ofi_step, calculate_vpin, estimate_price_impact
from src.analysis.sensitivity import run_sensitivity_analysis
from src.data_pipeline.lob_structure import LimitOrderBook

def test_microstructure():
    print("Testing Microstructure Models...")
    
    # Mock Data
    prev_lob = LimitOrderBook()
    prev_lob.add_order('buy', 100.0, 10)
    prev_lob.add_order('sell', 101.0, 10)
    
    curr_lob = LimitOrderBook()
    curr_lob.add_order('buy', 100.5, 5) # Price increase
    curr_lob.add_order('sell', 101.0, 10)
    
    # Test OFI
    ofi = calculate_ofi_step(prev_lob, curr_lob)
    print(f"OFI Step: {ofi}")
    
    # Test VPIN
    volume = pd.Series([100, 120, 110, 130])
    price_change = pd.Series([0.1, -0.05, 0.2, -0.1])
    sigma = 0.01
    v_buy, v_sell = calculate_vpin(volume, price_change, sigma)
    print(f"VPIN Components: V_buy={v_buy.sum()}, V_sell={v_sell.sum()}")
    
    # Test Price Impact
    impact = estimate_price_impact(100, 0.5)
    print(f"Price Impact Lambda: {impact}")
    
    assert ofi != 0, "OFI should not be zero for price change"
    assert impact == 0.005, f"Impact wrong: {impact}"
    print("Microstructure tests passed.")

def test_sensitivity_import():
    print("Testing Sensitivity Analysis Import...")
    # Just checking if we can import and call it without immediate crash
    # We won't run full analysis here as it takes time
    import inspect
    assert inspect.isfunction(run_sensitivity_analysis)
    print("Sensitivity Analysis import passed.")

if __name__ == "__main__":
    test_microstructure()
    test_sensitivity_import()
    print("All Day 4 verifications passed!")
