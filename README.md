# WTI/Brent Statistical Arbitrage Strategy

**Quantitative research project: Implementation of a mean-reversion strategy on energy futures spreads.**

## Project Overview
This repository contains a systematic algorithmic trading strategy exploiting the statistical co-integration between **WTI (NYMEX)** and **Brent (ICE)** Crude Oil futures. The project demonstrates a full quantitative pipeline, from raw data ingestion and synchronization to risk-adjusted performance analysis.

## Technical Highlights
* **Data Engineering and Synchronization:** The framework implements a custom alignment logic to handle asynchronous trading calendars. By reconciling NYMEX and ICE exchange holidays, the backtest eliminates data stale-pricing bias.
* **Mean-Reversion Engine:** Signals are generated via a dynamic Z-Score calculated on a rolling lookback window. This normalizes the spread volatility and identifies statistically significant entry and exit points.
* **Robustness vs. Overfitting:** Parameter selection (window size and thresholds) was conducted using stability cluster analysis rather than raw historical optimization. This ensures higher generalization capabilities on unseen data.
* **Risk Management:** A hard statistical stop-loss is integrated at $|Z| > 3.5$ to protect the portfolio against structural regime shifts or geopolitical shocks.

## Out-of-Sample Results (Jan 2024 - Feb 2026)
The model was validated on strictly unseen data to confirm its predictive power:
* **Sharpe Ratio:** 2.17
* **Net PnL per Barrel:** $14.60 (inclusive of estimated transaction costs)
* **Execution Logic:** Entry at $|Z| > 1.9$, Mean-reversion exit at $|Z| < 0.5$.



## Technology Stack
* **Language:** Python 3.x
* **Data Science Libraries:** Pandas (data manipulation), NumPy (vectorized computations), yfinance (market data), Matplotlib (visualization).
* **Research Documentation:** Technical note authored in LaTeX for academic-grade presentation.

## Repository Structure
* `main.py`: Full Python script including data cleaning, backtesting engine, and performance visualization.
* `DEBOVE_Augustin_WTI_Brent_Arbitrage.pdf`: Detailed research paper covering the mathematical framework, methodology, and critical analysis.
* `requirements.txt`: List of Python dependencies required to reproduce the results.

---
**Contact:** Augustin Debove
