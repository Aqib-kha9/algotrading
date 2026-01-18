import pandas as pd
import numpy as np
import os
from datetime import time
import pytz

class Backtester:
    def __init__(self, data_path, exchange_name='Delta', fee_pct=0.06, spread_pct=0.02):
        self.data_path = data_path
        self.exchange_name = exchange_name
        self.fee_pct = fee_pct / 100 
        self.spread_pct = spread_pct / 100
        self.trades = []
        
    def run(self):
        if not os.path.exists(self.data_path):
            print(f"Error: Data file {self.data_path} not found.")
            return
            
        with open('debug_engine.log', 'w') as f:
            f.write(f"Loading data from: {self.data_path}\n")
            
        df = pd.read_csv(self.data_path)
        
        # Use 'datetime' (UTC) column as source for accuracy
        # The 'datetime_ist' column in CSV is already shifted but labeled UTC, causing double-shift if converted.
        df['datetime_ist'] = pd.to_datetime(df['datetime'], utc=True)
        
        # Filter for 2026

        
        # Strategy State
        session_high = -1.0
        session_low = 999999999.0
        current_date = None
        daily_trade_taken = False
        active_position = None 
        
        print(f"Running backtest for {self.exchange_name}...")
        
        
        # Main Loop
        for i, row in df.iterrows():
            dt_ist = row['datetime_ist']
            
            # Ensure IST
            if dt_ist.tzinfo is None:
                 dt_ist = dt_ist.tz_localize('UTC') # Assume UTC if naive
            
            dt_ist = dt_ist.tz_convert('Asia/Kolkata')
            
            row_date = dt_ist.date()
            row_time = dt_ist.time()
            time_val = row_time.hour * 100 + row_time.minute

            # Reset daily state at new date
            if row_date != current_date:
                current_date = row_date
                session_high = -1.0
                session_low = 999999999.0
                daily_trade_taken = False
            
            # 1. Update Session High/Low (8:15 – 9:15 IST)
            if 815 <= time_val <= 915:
                session_high = max(session_high, row['high']) if session_high != -1.0 else row['high']
                session_low = min(session_low, row['low'])
            
            # 2. Check for Time-Based Exit (19:15 IST)
            if active_position and time_val >= 1915:
                # Close trade immediately at 19:15 or later
                self._close_trade(active_position, dt_ist, row['close'], 'TimeExit')
                self.trades.append(active_position)
                active_position = None
                continue

            # 3. Manage Active Trade
            if active_position:
                self._manage_trade(active_position, row)
                if active_position['status'] == 'closed':
                    self.trades.append(active_position)
                    active_position = None
                continue # Skip entry check if in position

            # 4. Check for New Entry (After 9:15, only one trade per day)
            if not daily_trade_taken and session_high != -1.0 and time_val > 915:
                buy_trigger = session_high * 1.0005
                sell_trigger = session_low * 0.9995 # -0.05%
                
                # Buy Entry
                if row['high'] >= buy_trigger:
                    entry_price = buy_trigger * (1 + self.spread_pct)
                    sl = entry_price * 0.9970 # -0.30%
                    tp = entry_price * 1.0070 # +0.70%
                    
                    active_position = {
                        'date': row_date,
                        'type': 'buy',
                        'entry_time': dt_ist,
                        'entry_price': entry_price,
                        'sl': sl,
                        'tp': tp,
                        'status': 'open',
                        'trailing_active': False
                    }
                    daily_trade_taken = True
                    
                # Sell Entry
                elif row['low'] <= sell_trigger:
                    entry_price = sell_trigger * (1 - self.spread_pct)
                    sl = entry_price * 1.0030 # +0.30%
                    tp = entry_price * 0.9930 # -0.70%
                    
                    active_position = {
                        'date': row_date,
                        'type': 'sell',
                        'entry_time': dt_ist,
                        'entry_price': entry_price,
                        'sl': sl,
                        'tp': tp,
                        'status': 'open',
                        'trailing_active': False
                    }
                    daily_trade_taken = True

        self._summarize()

    def _manage_trade(self, trade, row):
        if trade['type'] == 'buy':
            # Check for Target (High)
            if row['high'] >= trade['tp']:
                self._close_trade(trade, row['datetime_ist'], trade['tp'], 'Target')
                return
            
            # Check for Stop Loss (Low)
            if row['low'] <= trade['sl']:
                self._close_trade(trade, row['datetime_ist'], trade['sl'], 'StopLoss')
                return
            
            # Trailing Logic: If price moves +0.40%, modify SL to -0.20%
            if not trade['trailing_active'] and row['high'] >= trade['entry_price'] * 1.0040:
                trade['sl'] = trade['entry_price'] * 0.9980 # -0.20%
                trade['trailing_active'] = True
                
        else: # Sell
            # Check for Target (Low)
            if row['low'] <= trade['tp']:
                self._close_trade(trade, row['datetime_ist'], trade['tp'], 'Target')
                return
            
            # Check for Stop Loss (High)
            if row['high'] >= trade['sl']:
                self._close_trade(trade, row['datetime_ist'], trade['sl'], 'StopLoss')
                return
                
            # Trailing Logic: If price moves -0.40%, modify SL to +0.20%
            if not trade['trailing_active'] and row['low'] <= trade['entry_price'] * 0.9960:
                trade['sl'] = trade['entry_price'] * 1.0020 # +0.20%
                trade['trailing_active'] = True

    def _close_trade(self, trade, exit_time, exit_price, reason):
        trade['exit_time'] = exit_time
        trade['exit_price'] = exit_price
        trade['reason'] = reason
        trade['status'] = 'closed'
        
        # Calculate PnL (including fees)
        if trade['type'] == 'buy':
            raw_pnl = (exit_price - trade['entry_price']) / trade['entry_price']
        else:
            raw_pnl = (trade['entry_price'] - exit_price) / trade['entry_price']
            
        trade['pnl_pct'] = (raw_pnl - (self.fee_pct * 2)) * 100

    def _summarize(self):
        df_trades = pd.DataFrame(self.trades)
        if df_trades.empty:
            print("No trades executed.")
            return
            
        total_pnl = df_trades['pnl_pct'].sum()
        win_rate = (len(df_trades[df_trades['pnl_pct'] > 0]) / len(df_trades)) * 100
        
        print(f"\nBacktest Results for {self.exchange_name}:")
        print(f"Total Trades: {len(df_trades)}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Net PnL (%): {total_pnl:.2f}%")
        
        # Save to csv
        output_dir = 'data/results'
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{self.exchange_name.lower()}_results.csv"
        df_trades.to_csv(os.path.join(output_dir, filename), index=False)
        print(f"Results saved to {os.path.join(output_dir, filename)}")

if __name__ == "__main__":
    # Example runs (assuming prepare_datasets.py finished for Delta)
    delta_path = r"e:\cyptoalgotrading\data\processed\delta_btcusdt_5m_ist.csv"
    if os.path.exists(delta_path):
        bt = Backtester(delta_path, 'Delta')
        bt.run()
    
    exness_path = r"e:\cyptoalgotrading\data\processed\exness_btcusd_5m_ist.csv"
    if os.path.exists(exness_path):
        bt = Backtester(exness_path, 'Exness')
        bt.run()

