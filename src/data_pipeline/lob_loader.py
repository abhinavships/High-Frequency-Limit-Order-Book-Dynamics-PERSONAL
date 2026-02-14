import random
import time
from src.data_pipeline.lob_structure import LimitOrderBook

def load_nse_data(filepath):
    """Load NSE tick data and convert to LOB snapshots"""
    # Placeholder for real data loading logic
    pass

def simulate_lob_step(lob: LimitOrderBook, mid_price=100.0, volatility=0.5):
    """
    Simulates a single step of LOB dynamics (add/cancel) updates.
    Returns the updated lob object.
    """
    # Simple simulation parameters
    tick_size = 0.05
    
    # Decide side
    side = 'buy' if random.random() < 0.5 else 'sell'
    
    # Decide action (add or cancel)
    action = 'add' if random.random() < 0.7 else 'cancel'
    
    # Determine price
    # Central limit order book tendency: most activity near spread
    offset = int(random.expovariate(1.0 / (volatility * 10))) * tick_size
    
    best_bid = lob.best_bid if lob.best_bid > 0 else mid_price - tick_size
    best_ask = lob.best_ask if lob.best_ask < float('inf') else mid_price + tick_size
    
    if side == 'buy':
        # Buy orders typically at or below best bid, or slightly improving
        base_price = best_bid
        price = round(base_price + (random.choice([-1, 0, 1]) * offset), 2)
        if price >= best_ask: price = best_ask - tick_size # Avoid crossing for now
    else:
        # Sell orders typically at or above best ask
        base_price = best_ask
        price = round(base_price + (random.choice([-1, 0, 1]) * offset), 2)
        if price <= best_bid: price = best_bid + tick_size # Avoid crossing
        
    quantity = random.randint(1, 100)
    
    if action == 'add':
        lob.add_order(side, price, quantity)
    elif action == 'cancel':
        # Can only cancel if order exists
        if side == 'buy' and price in lob.bids:
            # logic to ensure we don't cancel more than exists, 
            # lob_structure handles negative check, but let's be cleaner
            curr_qty = lob.bids[price]
            cancel_qty = min(quantity, curr_qty)
            lob.cancel_order(side, price, cancel_qty)
        elif side == 'sell' and price in lob.asks:
            curr_qty = lob.asks[price]
            cancel_qty = min(quantity, curr_qty)
            lob.cancel_order(side, price, cancel_qty)
            
    return lob

def generate_initial_lob(mid_price=100.0, depth=20):
    """Generates a populated LimitOrderBook to start with."""
    lob = LimitOrderBook()
    
    # Initialize some bids
    for i in range(depth):
        price = round(mid_price - (i * 0.05) - 0.05, 2)
        qty = random.randint(10, 100)
        lob.add_order('buy', price, qty)
        
    # Initialize some asks
    for i in range(depth):
        price = round(mid_price + (i * 0.05) + 0.05, 2)
        qty = random.randint(10, 100)
        lob.add_order('sell', price, qty)
        
    return lob
