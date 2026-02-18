# Technical Report: High-Frequency Limit Order Book Dynamics

## 1. Introduction
This project implements a comprehensive analysis of Limit Order Book (LOB) dynamics, featuring real-time visualization, Hawkes process modeling for order flow, and an Avellaneda-Stoikov market-making strategy.

## 2. Methodology

### 2.1 Limit Order Book Simulation
We simulate the LOB using a dual-queue structure (Bids and Asks). Order arrivals and cancellations are simulated to generate realistic spread and depth dynamics.

### 2.2 Hawkes Process for Order Flow
We model the arrival of market orders using a univariate Hawkes process, a self-exciting point process where the intensity function is given by:

$$ \lambda(t) = \mu + \sum_{t_i < t} \alpha e^{-\beta(t - t_i)} $$

- $\mu$: Base intensity (exogenous arrivals)
- $\alpha$: Excitation parameter (endogenous feedback)
- $\beta$: Decay rate (memory duration)

This captures the "clustering" of trades observed in high-frequency data.

### 2.3 Microstructure Metrics

#### Order Flow Imbalance (OFI)
OFI measures the net buying/selling pressure at the best bid/ask quotes:
$$ OFI_t = e_b q_b - e_a q_a $$
where $q$ is volume and $e$ indicates price direction (+1 for increase, -1 for decrease).

#### VPIN (Volume-Synchronized Probability of Informed Trading)
VPIN estimates the toxicity of order flow (likelihood of informed trading):
$$ VPIN = \frac{\sum |V_{\text{buy}} - V_{\text{sell}}|}{\sum (V_{\text{buy}} + V_{\text{sell}})} $$
High VPIN values indicate a higher probability of adverse selection risk.

### 2.4 Avellaneda-Stoikov Market Making Strategy
The strategy determines optimal bid and ask quotes to maximize utility while penalizing inventory risk.

**Reservation Price:**
$$ r(t) = s(t) - q \gamma \sigma^2 (T-t) $$
- $s(t)$: Mid-price
- $q$: Current inventory
- $\gamma$: Risk aversion
- $\sigma$: Volatility
- $T-t$: Time remaining

**Optimal Spread:**
$$ \delta + \delta = \gamma \sigma^2 (T-t) + \frac{2}{\gamma} \ln(1 + \frac{\gamma}{k}) $$

## 3. Implementation Details
- **Dashboard**: Built with Streamlit and Plotly for real-time interactivity.
- **Backtesting**: Event-driven engine simulating fills based on probability density functions derived from order book depth.
- **Sensitivity Analysis**: Grid search over Risk Aversion ($\gamma$) and Arrival Rate ($k$) to optimize Sharpe Ratio.

## 4. Results
(See Sensitivity Analysis in Dashboard for latest results)

## 5. References
1. Avellaneda, M., & Stoikov, S. (2008). High-frequency trading in a limit order book.
2. Cont, R., Kukanov, A., & Stoikov, S. (2014). The price impact of order book events.
