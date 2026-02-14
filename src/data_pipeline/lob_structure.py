import collections
import time

class LimitOrderBook:
    def __init__(self):
        # Using dicts for O(1) access: price -> volume
        self.bids = collections.defaultdict(int)  # price -> quantity
        self.asks = collections.defaultdict(int)  # price -> quantity
        self.timestamp = None
        
        # Track best bid/ask for fast access
        self.best_bid = 0.0
        self.best_ask = float('inf')
        
        # Statistics tracking
        self.mid_prices = collections.deque(maxlen=100) # For volatility
        self.flow_imbalance = collections.deque(maxlen=100) # For OFI

    def add_order(self, side, price, quantity, timestamp=None):
        """
        Adds a limit order to the book.
        side: 'buy' or 'sell'
        """
        self.timestamp = timestamp or time.time()
        
        if side == 'buy':
            self.bids[price] += quantity
            if price > self.best_bid:
                self.best_bid = price
        elif side == 'sell':
            self.asks[price] += quantity
            if price < self.best_ask:
                self.best_ask = price
        
        # simple tracking after update
        mp = self.get_mid_price()
        if mp:
            self.mid_prices.append(mp)

    def cancel_order(self, side, price, quantity, timestamp=None):
        """
        Cancels (removes) quantity from an order.
        """
        self.timestamp = timestamp or time.time()
        
        if side == 'buy':
            if price in self.bids:
                self.bids[price] -= quantity
                if self.bids[price] <= 0:
                    del self.bids[price]
                    # Update best bid if needed
                    if price == self.best_bid:
                        self.best_bid = max(self.bids.keys()) if self.bids else 0.0
        elif side == 'sell':
            if price in self.asks:
                self.asks[price] -= quantity
                if self.asks[price] <= 0:
                    del self.asks[price]
                    # Update best ask if needed
                    if price == self.best_ask:
                        self.best_ask = min(self.asks.keys()) if self.asks else float('inf')
        
        # simple tracking after update
        mp = self.get_mid_price()
        if mp:
            self.mid_prices.append(mp)

    def get_mid_price(self):
        if self.best_bid > 0 and self.best_ask < float('inf'):
            return (self.best_bid + self.best_ask) / 2
        return None

    def get_spread(self):
        if self.best_bid > 0 and self.best_ask < float('inf'):
            return self.best_ask - self.best_bid
        return None

    def get_volatility(self):
        """Standard deviation of recent mid-prices."""
        import statistics
        if len(self.mid_prices) < 2:
            return 0.0
        return statistics.stdev(self.mid_prices)

    def get_ofi(self):
        """
        Order Flow Imbalance (OFI) - Simplified for Day 1.
        Ideally compares e_n to e_{n-1}. 
        Here we return a placeholder or simple logic.
        """
        # Real OFI requires tracking depth changes at best limits.
        # For Day 1, we'll return a basic buy/sell volume ratio of top level.
        best_bid_vol = self.bids.get(self.best_bid, 0)
        best_ask_vol = self.asks.get(self.best_ask, 0)
        
        if best_bid_vol + best_ask_vol == 0:
            return 0
        return (best_bid_vol - best_ask_vol) / (best_bid_vol + best_ask_vol)

    def get_mid_price(self):
        if self.best_bid > 0 and self.best_ask < float('inf'):
            return (self.best_bid + self.best_ask) / 2
        return None

    def get_spread(self):
        if self.best_bid > 0 and self.best_ask < float('inf'):
            return self.best_ask - self.best_bid
        return None

    def get_depth(self, levels=5):
        """
        Returns top `levels` of bids and asks.
        Returns: ({price: vol}, {price: vol})
        """
        # Sort bids descending
        sorted_bids = sorted(self.bids.items(), key=lambda x: x[0], reverse=True)[:levels]
        # Sort asks ascending
        sorted_asks = sorted(self.asks.items(), key=lambda x: x[0])[:levels]
        
        return dict(sorted_bids), dict(sorted_asks)
