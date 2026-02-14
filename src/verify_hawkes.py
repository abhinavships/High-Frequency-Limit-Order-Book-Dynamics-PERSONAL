
import sys
import os
import numpy as np

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.hawkes import HawkesProcess
from src.visualization.hawkes_plots import plot_intensity

def test_hawkes_simulation():
    print("Testing Hawkes Simulation...")
    hp = HawkesProcess(mu=1.0, alpha=0.5, beta=1.0)
    events = hp.simulate(T_max=100)
    print(f"Generated {len(events)} events.")
    
    if len(events) == 0:
        print("WARNING: No events generated.")
    else:
        print(f"First 5 events: {events[:5]}")
        
    # Test Intensity Calculation
    print("Testing Intensity Calculation...")
    t = 50
    lambda_t = hp.intensity(t, events)
    print(f"Intensity at t={t}: {lambda_t}")
    
    # Test Fitting (basic sanity check)
    print("Testing Fitting...")
    if len(events) > 10:
        result = hp.fit(events)
        print(f"Fitted parameters: mu={hp.mu}, alpha={hp.alpha}, beta={hp.beta}")
    
    print("Hawkes Test Completed.")

if __name__ == "__main__":
    test_hawkes_simulation()
