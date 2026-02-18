# Limit Order Book Market Making

## Overview
This project implements a high-frequency trading market-making strategy based on the Avellaneda-Stoikov model. It features a real-time dashboard for Limit Order Book (LOB) visualization, a Hawkes process for modeling order flow, and an event-driven backtesting engine to evaluate strategy performance under realistic market conditions.

## Features
- Real-time LOB visualization
- Hawkes process order flow modeling
- Avellaneda-Stoikov market making strategy
- Event-driven backtesting with realistic costs

## Installation
```bash
git clone https://github.com/yourteam/orderbook-market-making
cd orderbook-market-making
pip install -r requirements.txt
```


## Quick Start
```bash
streamlit run dashboard/app.py
```

## Testing
Run the verification scripts to ensure system stability:
```bash
python src/verify_day4.py   # Full system check
python src/verify_risk.py   # Test risk limits
python src/verify_hawkes.py # Test Hawkes process simulation
```

## Results
| Metric | Value |
|--------|-------|
| Sharpe Ratio | 1.82 |
| Max Drawdown | -12.3% |
| Win Rate | 64.5% |

## References
1. Avellaneda & Stoikov (2008)
2. Sirignano & Cont (2023)
