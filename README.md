# WTI-Brent Statistical Arbitrage

This project is a personal implementation of a mean-reversion strategy on the **WTI/Brent spread**. [cite_start]I decided to build this framework to bridge the gap between my Mathematics/CS background and my growing interest in energy markets [cite: 154-155, 308-309].

[cite_start]The goal was to move past theoretical assumptions and confront the "messy" reality of market data: asynchronous calendars, execution slippage, and the danger of overfitting [cite: 310, 339, 447-448].

## Why this spread?
[cite_start]The WTI (NYMEX) and Brent (ICE) spread is a primary benchmark for global crude oil[cite: 158, 314]. [cite_start]Because these two grades are global substitutes, their prices are fundamentally co-integrated[cite: 179, 335]. [cite_start]I built this bot to identify and exploit transient "dislocations" where the spread deviates from its historical mean[cite: 180, 336].

## Technical Highlights

### 1. The Data Synchronization Challenge
One of the main hurdles was aligning the data. [cite_start]NYMEX (US) and ICE (UK) have different exchange holidays (e.g., Labor Day vs. UK Bank Holidays)[cite: 204, 360, 449]. [cite_start]I implemented an inner-join logic in Python to ensure the backtest only runs on days where both markets are active, preventing the algorithm from trading on "stale" prices[cite: 53, 204, 360].

### 2. Signal Logic & Execution
[cite_start]The bot is built as a vectorized state machine to ensure speed and avoid look-ahead bias[cite: 211, 367].
* [cite_start]**Entry**: A dynamic Z-Score is calculated on a rolling window[cite: 192, 348]. I take a position when $|Z| > [cite_start]1.9$[cite: 198, 354].
* [cite_start]**Position Management**: I use `.ffill()` logic to maintain the "Hold" state until a clear exit signal is triggered, solving the issue of "flickering" signals [cite: 82-83, 392].
* [cite_start]**Exit**: The position is liquidated when the spread returns to equilibrium ($|Z| < 0.5$)[cite: 220, 378].
* **Risk Control**: A hard stop-loss is triggered at $|Z| > [cite_start]3.5$ to protect the portfolio against structural market shifts[cite: 224, 382].

### 3. Stability over "Perfect" Results
During the optimization phase (2000-2023), I deliberately avoided the parameters with the absolute highest profit. [cite_start]Instead, I selected the **3rd best parameter set** ($Z=1.9, n=10$) [cite: 395-396]. [cite_start]This choice was made to prioritize stability across nearby values and reduce the risk of overfitting[cite: 138, 450].

## Performance (Out-of-Sample: 2024 - 2026)
[cite_start]Tested on strictly unseen data, the model remained robust[cite: 340, 397]:
* [cite_start]**Sharpe Ratio**: 2.17 [cite: 340, 416]
* [cite_start]**Net PnL**: $14.60 / barrel (inclusive of estimated transaction costs/slippage) [cite: 416, 435]

---
**Contact**: Augustin Debove  
[cite_start]**References**: *The World for Sale* (Javier Blas & Jack Farchy), *Python for Algorithmic Trading* (Yves Hilpisch)[cite: 151, 155, 305, 309].
