import numpy as np
import pandas as pd
from scipy.stats import norm

def calculate_ofi_step(prev_lob, curr_lob):
    """
    Calculate Order Flow Imbalance (OFI) step from two LOB states.
    
    OFI(t) = e_b * q_b - e_a * q_a
    where e_b = 1 if P_b(t) > P_b(t-1)
                0 if P_b(t) == P_b(t-1)
               -1 if P_b(t) < P_b(t-1)
    """
    # Bid side
    if curr_lob.bids and prev_lob.bids:
        curr_best_bid = max(curr_lob.bids.keys())
        prev_best_bid = max(prev_lob.bids.keys())
        curr_bid_vol = curr_lob.bids[curr_best_bid]
        prev_bid_vol = prev_lob.bids[prev_best_bid]
        
        if curr_best_bid > prev_best_bid:
            ofi_bid = curr_bid_vol
        elif curr_best_bid < prev_best_bid:
            ofi_bid = -prev_bid_vol
        else:
            ofi_bid = curr_bid_vol - prev_bid_vol
    else:
        ofi_bid = 0

    # Ask side
    if curr_lob.asks and prev_lob.asks:
        curr_best_ask = min(curr_lob.asks.keys())
        prev_best_ask = min(prev_lob.asks.keys())
        curr_ask_vol = curr_lob.asks[curr_best_ask]
        prev_ask_vol = prev_lob.asks[prev_best_ask]
        
        if curr_best_ask > prev_best_ask:
            ofi_ask = -prev_ask_vol
        elif curr_best_ask < prev_best_ask:
            ofi_ask = curr_ask_vol
        else:
            ofi_ask = curr_ask_vol - prev_ask_vol
    else:
        ofi_ask = 0
            
    return ofi_bid - ofi_ask

def calculate_vpin(volume, price_change, sigma, window=50):
    """
    Calculate Volume-Synchronized Probability of Informed Trading (VPIN).
    VPIN = |V_buy - V_sell| / (V_buy + V_sell)
    """
    # Bulk Volume Classification (BVC)
    # V_buy = V * N( (P - P_prev) / sigma )
    if sigma == 0:
        sigma = 1e-6
        
    z = price_change / sigma
    prob_buy = norm.cdf(z)
    
    v_buy = volume * prob_buy
    v_sell = volume * (1 - prob_buy)
    
    return v_buy, v_sell 

def estimate_price_impact(trade_size, price_change):
    """
    Simple linear price impact model:
    Delta P = lambda * Q
    Returns lambda (impact coefficient).
    """
    if trade_size == 0:
        return 0.0
    return price_change / trade_size
