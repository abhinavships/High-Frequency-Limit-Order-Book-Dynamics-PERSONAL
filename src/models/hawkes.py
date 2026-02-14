import numpy as np
from scipy.optimize import minimize

class HawkesProcess:
    def __init__(self, mu=1.0, alpha=0.5, beta=1.0):
        self.mu = mu      # baseline intensity
        self.alpha = alpha  # excitation
        self.beta = beta   # decay
    
    def intensity(self, t, event_times):
        """Calculate intensity at time t given past events"""
        intensity = self.mu
        # Filter events that happened before t
        past_events = event_times[event_times < t]
        if len(past_events) > 0:
            intensity += np.sum(self.alpha * np.exp(-self.beta * (t - past_events)))
        return intensity
    
    def log_likelihood(self, event_times):
        """Compute log-likelihood for MLE"""
        if len(event_times) == 0:
            return 0
            
        T = event_times[-1]
        
        # Log of intensity at each event
        log_sum = 0
        for i, ti in enumerate(event_times):
            # For efficiency in loop, could optimize, but keeping simple for now
            # Only consider events strictly before ti
            lam = self.intensity(ti, event_times[:i])
            if lam <= 0: return -np.inf # Safety check
            log_sum += np.log(lam)
        
        # Compensator integral
        # Integral of lambda(t) from 0 to T
        # = pixel_integral(mu) + sum_over_events(integral_of_excitation)
        # alpha * exp(-beta*(t-ti)) -> integral is (alpha/beta) * (1 - exp(-beta*(T-ti)))
        
        compensator = self.mu * T
        for ti in event_times:
            compensator += (self.alpha / self.beta) * (1 - np.exp(-self.beta * (T - ti)))
        
        return log_sum - compensator
    
    def fit(self, event_times):
        """Estimate parameters via MLE"""
        def neg_log_likelihood(params):
            mu, alpha, beta = params
            # Constraints
            if mu <= 0 or alpha < 0 or beta <= 0:
                return np.inf
            # Stationarity check: alpha < beta is often required for stability, 
            # though locally we might just enforce bounds
            
            self.mu, self.alpha, self.beta = mu, alpha, beta
            return -self.log_likelihood(event_times)
        
        # Initial guess
        x0 = [max(0.1, self.mu), max(0.1, self.alpha), max(0.1, self.beta)]
        
        result = minimize(neg_log_likelihood, 
                         x0=x0,
                         bounds=[(0.01, None), (0, None), (0.01, None)],
                         method='L-BFGS-B')
        
        if result.success:
            self.mu, self.alpha, self.beta = result.x
            
        return result

    def simulate(self, T_max):
        """
        Simulate Hawkes process using Ogata's Thinning Algorithm.
        Returns: numpy array of event times
        """
        events = []
        t = 0
        
        # Current intensity upper bound
        # Initially just mu, but technically should be calculated dynamically
        # For Ogata's, we need lambda(t) which is max possible intensity immediately
        
        while t < T_max:
            # Calculate current intensity to get an upper bound for the next step
            # We can use the current intensity at t as a bound because it decays
            # UNLESS a new event happens. But we are looking for the next event.
            # So lambda(s) <= lambda(t) + alpha (if event happens) - wait.
            # Between events, intensity is decreasing (decaying).
            # So lambda(t) is the upper bound for any s > t until next event.
            
            current_intensity = self.intensity(t, np.array(events))
            
            # Generate candidate inter-arrival time
            # Using homogeneous Poisson process with rate = current_intensity (upper bound)
            # Actually, standard algorithm:
            # 1. lambda_bar = lambda(t)
            # 2. s ~ Exp(lambda_bar)
            # 3. accept with probability lambda(t+s) / lambda_bar
            
            # Use a slightly loose upper bound to avoiding re-calculating too often if needed,
            # but here exact lambda(t) is fine as it's the max for [t, infinity) absent new events.
            lambda_star = current_intensity
            
            if lambda_star <= 0: # Should not happen with mu > 0
                lambda_star = 0.0001
                
            w = -np.log(np.random.rand()) / lambda_star
            t += w
            
            if t >= T_max:
                break
                
            # Rejection sampling
            lambda_t = self.intensity(t, np.array(events))
            
            if np.random.rand() < lambda_t / lambda_star:
                events.append(t)
                
        return np.array(events)
