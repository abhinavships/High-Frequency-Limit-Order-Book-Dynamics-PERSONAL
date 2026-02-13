import numpy as np

class AvellanedaStoikovMarketMaker:
    def __init__(self, gamma=0.1, k=1.5, T=1.0):
        """
        Initialize the Avellaneda-Stoikov Market Maker.
        
        Args:
            gamma (float): Risk aversion parameter.
            k (float): Order arrival rate parameter.
            T (float): Time horizon (normalized).
        """
        self.gamma = gamma
        self.k = k
        self.T = T
    
    def reservation_price(self, mid_price, inventory, sigma, time_left):
        """
        Calculate reservation price r(t).
        r(t) = s(t) - q(t) * gamma * sigma^2 * (T - t)
        """
        return mid_price - inventory * self.gamma * (sigma**2) * time_left
    
    def optimal_spread(self, sigma, time_left):
        """
        Calculate optimal bid-ask spread delta.
        delta = gamma * sigma^2 * (T - t) + (2 / gamma) * ln(1 + gamma / k)
        """
        # Avoid division by zero if gamma is extremely small, though default is 0.1
        if self.gamma < 1e-9:
            return 0.0
        
        spread = self.gamma * (sigma**2) * time_left + (2 / self.gamma) * np.log(1 + self.gamma / self.k)
        return max(0.0, spread) # Ensure spread is non-negative
    
    def quote(self, mid_price, inventory, sigma, time_left):
        """
        Generate bid and ask quotes.
        
        Returns:
            dict: {'bid': float, 'ask': float, 'reservation': float, 'spread': float}
        """
        r = self.reservation_price(mid_price, inventory, sigma, time_left)
        delta = self.optimal_spread(sigma, time_left)
        
        bid_price = r - delta / 2
        ask_price = r + delta / 2
        
        return {
            'bid': bid_price, 
            'ask': ask_price, 
            'reservation': r, 
            'spread': delta
        }
    
    def should_adjust_quotes(self, current_inventory, max_inventory):
        """
        Inventory risk check.
        Returns True if inventory exposure is too high (> 80% of max).
        """
        if max_inventory <= 0:
            return False
        return abs(current_inventory) > 0.8 * max_inventory
