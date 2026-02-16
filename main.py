import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# PART 1 : OPTIMIZATION 
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# downloading recent data
tickers = ['CL=F', 'BZ=F']
end_date = "2024-01-01" #end date of the training model

# Fetching data since 2000 for moving average history
raw_data = yf.download(tickers, start="2000-01-01", end=end_date, progress=False)['Close']

# Data Cleaning and Alignment
data = pd.DataFrame()
data['WTI'] = raw_data['CL=F']
data['Brent'] = raw_data['BZ=F']
data.dropna(inplace=True) # Aligning time series: we only keep observations where both NYMEX (WTI) and ICE (Brent) markets are open to avoid non-synchronous data bias.

# Grid search for the best Z-score and the optimal rolling window
profit = {} 
sharpe = {}
drawdown = {}

# Computation of the spread
data['spread'] = data['WTI'] - data['Brent']
data['spread_diff'] = data['spread'].diff()

# Definition of the transaction cost per unit, covering spread and transaction fees
transaction_cost = 0.05 


# Loop over windows
for i in range(5, 51, 5): # windows from 5 to 50 days
    
    # Pre-calculate rolling stats for this window to speed up the loop
    mean = data['spread'].rolling(i).mean()
    std = data['spread'].rolling(i).std()
    
    # Loop over Z-score thresholds
    for k in range(10, 401, 5): # Z-score from 0.1 to 4.0
        z = k / 100
        
        # Z-score calculation
        temp_Z = (data['spread'] - mean) / std

        
        # 1. Initialize signal with NaN
        signal = pd.Series(np.nan, index=data.index)
        
        # 2. Entries
        signal.loc[temp_Z < -z] = 1  # Long Spread
        signal.loc[temp_Z > z] = -1  # Short Spread
        
        # 3. Exits (Mean Reversion)
        # We exit when Z-score comes back to normal (between -0.5 and 0.5)
        signal.loc[temp_Z.abs() < 0.5] = 0
        
        # 4. Stop Loss (Optional but recommended for optimization realism)
        # If Z-score explodes > 4, we cut (Black Swan protection)
        signal.loc[temp_Z.abs() > 4] = 0
        
        # 5. Position Filling
        # We propagate the signal until a new condition (Exit or Reverse) is met
        pos = signal.ffill().fillna(0)
        
        
        # Computation of the costs
        trades = pos.diff().fillna(0).abs() 
        total_costs = trades * transaction_cost
        
        # Net performance computation
        strat_return = (pos.shift(1) * data['spread_diff']) - total_costs
        
        profit_final = strat_return.sum()
        
        # Storing of the final profit
        profit[(i, z)] = profit_final
        
        # Sharpe Ratio Computation
        if strat_return.std() != 0:
            # Annulized Sharpe
            s = (strat_return.mean() / strat_return.std()) * np.sqrt(252)
        else:
            s = 0
        sharpe[(i, z)] = s

        # Max Drawdown Computation
        equity_curve = strat_return.cumsum()
        max_dd = (equity_curve - equity_curve.cummax()).min()
        drawdown[(i, z)] = max_dd
        
# Converting the profit dictionary to a DataFrame
df_opti = pd.Series(profit).reset_index()
df_opti.columns = ['Fenetre', 'Z_score', 'Profit']

# Converting the Drawdown dictionary to a DataFramee
df_dd = pd.Series(drawdown).reset_index()
df_dd.columns = ['Fenetre', 'Z_score', 'Drawdown']
df_opti = df_opti.join(df_dd['Drawdown'])

# Converting the Sharpe dictionary to a DataFrame
df_risk = pd.Series(sharpe).reset_index()
df_risk.columns = ['Fenêtre', 'Z_score', 'Sharpe']
df_opti = df_opti.join(df_risk['Sharpe'])

# Displaying the best results
print("\nTOP 5 BY PROFIT")
top_5_profit = df_opti.sort_values(by='Profit', ascending=False).head(5)
print(top_5_profit)

print("\nTOP 5 BY SHARPE RATIO")
top_5_sharpe = df_opti.sort_values(by='Sharpe', ascending=False).head(5)
print(top_5_sharpe)


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# PART 2 : OUT-OF-SAMPLE TEST
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#  DOWNLOADING DATA
tickers = ['CL=F', 'BZ=F']
end_date = datetime.now().strftime('%Y-%m-%d') 

# Fetching data that is unknown for the model (Out-of-Sample)
raw_data_oos = yf.download(tickers, start="2024-01-02", end=end_date, progress=False)['Close']

#  DATA CLEANING AND ALIGNMENT
data_oos = pd.DataFrame()
data_oos['WTI'] = raw_data_oos['CL=F']
data_oos['Brent'] = raw_data_oos['BZ=F']

# Aligning time series: we only keep observations where both NYMEX (WTI) and ICE (Brent) markets are open.
data_oos.dropna(inplace=True) 

#  PARAMETERIZATION 
# These are automatically assigned from the optimization above
stop_loss_z = 3.5 
transaction_cost = 0.05 

# INDICATORS
data_oos['spread'] = data_oos['WTI'] - data_oos['Brent']
data_oos['spread_diff'] = data_oos['spread'].diff()

# Moving calculations
mean_oos = data_oos['spread'].rolling(window=best_window).mean()
std_oos = data_oos['spread'].rolling(window=best_window).std()
data_oos['z_score'] = (data_oos['spread'] - mean_oos) / std_oos


# Initialize signal container with NaN (Empty)
data_oos['position'] = np.nan 

# Entry Signals
# Long if Z < -best_z_entry
data_oos.loc[data_oos['z_score'] < -best_z_entry, 'position'] = 1  
# Short if Z > best_z_entry
data_oos.loc[data_oos['z_score'] > best_z_entry, 'position'] = -1 

# Exit Conditions (Mean Reversion)
# Exit when Z returns inside [-0.5, 0.5]. 
data_oos.loc[data_oos['z_score'].abs() < 0.5, 'position'] = 0

# Stop Loss (Risk Management)
# Force exit if Z explodes (> 3.5)
data_oos.loc[data_oos['z_score'].abs() > stop_loss_z, 'position'] = 0

# Propagation (The fix)
data_oos['position'] = data_oos['position'].ffill()

# Handle the very beginning (before first signal)
data_oos['position'] = data_oos['position'].fillna(0)

# PERFORMANCE CALCULATION
trades_oos = data_oos['position'].diff().fillna(0).abs()
costs_oos = trades_oos * transaction_cost

# PnL strategy (using shift(1) to avoid look-ahead bias)
data_oos['strategy_return'] = (data_oos['position'].shift(1) * data_oos['spread_diff']) - costs_oos

# Cumulative Returns
data_oos['cum_profit'] = data_oos['strategy_return'].cumsum()

#  VISUALIZATION & METRICS
final_pnl = data_oos['cum_profit'].iloc[-1]
sharpe_ratio = (data_oos['strategy_return'].mean() / data_oos['strategy_return'].std()) * np.sqrt(252)

print(f"\n RESULTS (2024 - Today) ")
print(f"Net PnL per Barrel : {final_pnl:.2f} $")
print(f"Sharpe Ratio : {sharpe_ratio:.2f}")

# Chart
plt.figure(figsize=(10, 6))
plt.plot(data_oos.index, data_oos['cum_profit'], label='PnL Stratégie (Net)')
plt.title(f"Performance Out-of-Sample (WTI/Brent) - Sharpe: {sharpe_ratio:.2f}")
plt.xlabel("Date")
plt.ylabel("Profit ($)")
plt.legend()
plt.grid(True)
plt.show()
