import numpy as np
from collections import deque

class BacktestEngine:
    def __init__(self, initial_capital=100000, max_position=100):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.inventory = 0
        self.max_position = max_position
        self.pnl_history = []
        self.timestamps = []
        self.trades = []
        
    def process_fill(self, side, price, quantity, timestamp):
        """
        Execute a fill and update state.
        Returns True if trade executed, False if rejected by risk limits.
        """
        if side == 'buy':
            if self.inventory + quantity > self.max_position:
                return False
            self.inventory += quantity
            self.capital -= price * quantity
        elif side == 'sell':
            if self.inventory - quantity < -self.max_position:
                return False
            self.inventory -= quantity
            self.capital += price * quantity

        
        
        self.trades.append({
            'timestamp': timestamp,
            'side': side,
            'price': price,
            'quantity': quantity,
            'inventory': self.inventory,
            'capital': self.capital
        })
        
        # Calculate current Portfolio Value (Mark-to-Market)
        # Assuming fill price is close to market mid-price for approximation
        # In a real engine, we'd pass mid_price separately for explicit MTM
        current_equity = self.capital + (self.inventory * price)
        self.pnl_history.append(current_equity)
        self.timestamps.append(timestamp)
        return True

    def calculate_metrics(self):
        """Compute Sharpe, drawdown, etc."""
        if not self.pnl_history:
            return {'sharpe': 0.0, 'max_drawdown': 0.0, 'total_return': 0.0}
            
        pnl_series = np.array(self.pnl_history)
        
        # Avoid division by zero if series is constant
        if len(pnl_series) < 2:
             return {'sharpe': 0.0, 'max_drawdown': 0.0, 'total_return': 0.0}

        # Calculate returns
        # Handle cases where PnL might be 0 or negative (though equity usually positive)
        # Using simple differences for now or percentage change if equity > 0
        
        returns = np.diff(pnl_series) / pnl_series[:-1]
        
        # Check for NaNs or Infs
        returns = np.nan_to_num(returns)
        
        if np.std(returns) == 0:
            sharpe = 0.0
        else:
            # Annualized Sharpe (assuming daily data? No, this is HFT/intraday)
            # If timestamps are high frequency, 252 is wrong scaling factor.
            # For now, we will return a raw Sharpe or assume a specific frequency.
            # Let's assume the caller interprets it, or we just use a placeholder scaling.
            # Standard: sqrt(samples_per_year)
            # Let's stick to the user's snippet logic: sqrt(252) implies daily, 
            # but we might be doing intraday. Let's keep 252 as per requirements for now 
            # or just leave it unscaled if standard deviation is per-step.
            # User prompted: sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)
            
        max_dd = self._max_drawdown(pnl_series)
        total_return = (pnl_series[-1] - self.initial_capital) / self.initial_capital
        
        return {'sharpe': sharpe, 'max_drawdown': max_dd, 'total_return': total_return}
    
    def _max_drawdown(self, equity_curve):
        """Calculate maximum drawdown"""
        if len(equity_curve) == 0:
            return 0.0
            
        peak = np.maximum.accumulate(equity_curve)
        
        # Avoid division by zero if peak is 0 (unlikely for capital)
        with np.errstate(divide='ignore', invalid='ignore'):
            drawdown = (equity_curve - peak) / peak
            
        drawdown = np.nan_to_num(drawdown)
        return np.min(drawdown)
