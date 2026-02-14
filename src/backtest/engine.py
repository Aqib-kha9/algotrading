import pandas as pd
import numpy as np
import os
from datetime import time
import pytz

class Backtester:
    def __init__(self, data_path, exchange_name='Exness', fee_pct=0.0, spread_pct=0.0):
        self.data_path = data_path
        self.exchange_name = exchange_name
        self.fee_pct = fee_pct / 100 
        self.spread_pct = spread_pct / 100
        self.trades = []
        
    def run(self):
        if not os.path.exists(self.data_path):
            print(f"Error: Data file {self.data_path} not found.")
            return
            
        print(f"Loading data from: {self.data_path}...")
        try:
            df = pd.read_csv(self.data_path, sep='\t')
        except:
            df = pd.read_csv(self.data_path)
        
        # Datetime processing
        # Exness data is UTC. We work in UTC but align with Terminal Time (UTC+2)
        df['datetime'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
        df.set_index('datetime', inplace=True)
        
        # Mid-Price discovery: Client uses Bid + Spread*0.01/2
        df['high_mid'] = df['<HIGH>'] + (df['<SPREAD>'] * 0.01 / 2)
        df['low_mid']  = df['<LOW>']  + (df['<SPREAD>'] * 0.01 / 2)
        df['close_mid'] = df['<CLOSE>'] + (df['<SPREAD>'] * 0.01 / 2)
        
        # Strategy Parameters
        # Verified: Client 02:45-03:55 session is UTC-based
        RANGE_START_UTC = "02:45" 
        RANGE_END_UTC   = "03:55" 
        ENTRY_LIMIT_UTC = "12:30" # 6 PM IST
        EXIT_TIME_UTC   = "13:40" # 7:15 PM IST
        
        BUFF_PERC = 0.0005 # 0.05%
        TGT_PERC  = 0.0070 # 0.70%
        SL_PERC   = 0.0030 # 0.30%
        
        # TSL Parameters
        TSL_ACTIVATE_PERC = 0.0040 # 0.40%
        TSL_TRAIL_COORD   = 0.0020 # 0.20% locked profit level
        
        # Strategy State
        current_date = None
        daily_trade_taken = False
        active_position = None 
        
        print(f"Running full backtest for {self.exchange_name} (Mid-Price Logic)...")
        
        unique_dates = sorted(list(set(df.index.date)))
        
        for row_date in unique_dates:
            day_data = df[df.index.date == row_date]
            if day_data.empty: continue
            
            # Reset daily state
            session_high = -1.0
            session_low = 999999999.0
            daily_trade_taken = False
            
            # 1. Define Session Range 
            session_mask = (day_data.index.time >= pd.Timestamp(RANGE_START_UTC).time()) & \
                           (day_data.index.time <= pd.Timestamp(RANGE_END_UTC).time())
            session_data = day_data[session_mask]
            
            if session_data.empty: continue
            
            session_high = session_data['high_mid'].max()
            session_low  = session_data['low_mid'].min()
            
            buy_trigger = session_high * (1 + BUFF_PERC)
            sell_trigger = session_low * (1 - BUFF_PERC)
            
            # 2. Trade Scanning
            trade_mask = (day_data.index.time > pd.Timestamp(RANGE_END_UTC).time()) & \
                         (day_data.index.time <= pd.Timestamp(EXIT_TIME_UTC).time())
            trade_data = day_data[trade_mask]
            
            if trade_data.empty: continue
            
            for t_time, row in trade_data.iterrows():
                # Case A: No active position, look for entry
                if not active_position:
                    if daily_trade_taken: continue
                    if t_time.time() > pd.Timestamp(ENTRY_LIMIT_UTC).time(): continue
                    
                    # Check Buy
                    if row['high_mid'] >= buy_trigger:
                        entry_price = buy_trigger
                        active_position = {
                            'date': row_date,
                            'type': 'buy',
                            'entry_time': t_time,
                            'entry_price': entry_price,
                            'sl': entry_price * (1 - SL_PERC),
                            'tp': entry_price * (1 + TGT_PERC),
                            'status': 'open',
                            'trailing_active': False
                        }
                        daily_trade_taken = True
                    # Check Sell
                    elif row['low_mid'] <= sell_trigger:
                        entry_price = sell_trigger
                        active_position = {
                            'date': row_date,
                            'type': 'sell',
                            'entry_time': t_time,
                            'entry_price': entry_price,
                            'sl': entry_price * (1 + SL_PERC),
                            'tp': entry_price * (1 - TGT_PERC),
                            'status': 'open',
                            'trailing_active': False
                        }
                        daily_trade_taken = True
                
                # Case B: Manage active position
                else:
                    curr_h = row['high_mid']
                    curr_l = row['low_mid']
                    
                    if active_position['type'] == 'buy':
                        # TSL Activation
                        if not active_position['trailing_active'] and curr_h >= active_position['entry_price'] * (1 + TSL_ACTIVATE_PERC):
                            active_position['trailing_active'] = True
                            active_position['sl'] = active_position['entry_price'] * (1 - TSL_TRAIL_COORD)
                        
                        # Stop Loss
                        if curr_l <= active_position['sl']:
                            reason = 'TSL HIT' if active_position['trailing_active'] else 'StopLoss'
                            self._close_trade(active_position, t_time, active_position['sl'], reason)
                            self.trades.append(active_position)
                            active_position = None
                            continue
                        # Target
                        if curr_h >= active_position['tp']:
                            self._close_trade(active_position, t_time, active_position['tp'], 'Target')
                            self.trades.append(active_position)
                            active_position = None
                            continue
                            
                    else: # SELL
                        if not active_position['trailing_active'] and curr_l <= active_position['entry_price'] * (1 - TSL_ACTIVATE_PERC):
                            active_position['trailing_active'] = True
                            active_position['sl'] = active_position['entry_price'] * (1 + TSL_TRAIL_COORD)
                        
                        if curr_h >= active_position['sl']:
                            reason = 'TSL HIT' if active_position['trailing_active'] else 'StopLoss'
                            self._close_trade(active_position, t_time, active_position['sl'], reason)
                            self.trades.append(active_position)
                            active_position = None
                            continue
                        if curr_l <= active_position['tp']:
                            self._close_trade(active_position, t_time, active_position['tp'], 'Target')
                            self.trades.append(active_position)
                            active_position = None
                            continue
            
            # Close EOD if still open
            if active_position:
                last_candle = trade_data.iloc[-1]
                self._close_trade(active_position, trade_data.index[-1], last_candle['close_mid'], 'TimeExit')
                self.trades.append(active_position)
                active_position = None

        self._summarize()

    def _close_trade(self, trade, exit_time, exit_price, reason):
        trade['exit_time'] = exit_time
        trade['exit_price'] = exit_price
        trade['reason'] = reason
        trade['status'] = 'closed'
        
        # PnL logic
        if trade['type'] == 'buy':
            trade['pnl'] = exit_price - trade['entry_price']
            trade['pnl_pct'] = (exit_price / trade['entry_price'] - 1) * 100
        else:
            trade['pnl'] = trade['entry_price'] - exit_price
            trade['pnl_pct'] = (trade['entry_price'] / exit_price - 1) * 100
            
    def _summarize(self):
        df_trades = pd.DataFrame(self.trades)
        if df_trades.empty:
            print("No trades executed.")
            return
            
        total_pnl = df_trades['pnl'].sum()
        total_pnl_pct = df_trades['pnl_pct'].sum()
        win_rate = (len(df_trades[df_trades['pnl'] > 0]) / len(df_trades)) * 100
        
        print(f"\nBacktest Results for {self.exchange_name}:")
        print(f"Total Trades: {len(df_trades)}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Net PnL (Points): {total_pnl:.2f}")
        print(f"Net PnL (%): {total_pnl_pct:.2f}%")

        print("\nLatest 2026 Trades:")
        df_2026 = df_trades[df_trades['date'].astype(str).str.startswith('2026')]
        if not df_2026.empty:
            print(df_2026[['date', 'type', 'entry_price', 'exit_price', 'reason', 'pnl']].tail(15).to_string(index=False))
        
        # UI expects specific format
        output_dir = 'data/results'
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{self.exchange_name.lower()}_results.csv"
        path = os.path.join(output_dir, filename)
        
        try:
            df_trades.to_csv(path, index=False)
            print(f"Results saved to {path}")
        except Exception as e:
            print(f"Warning: Could not save CSV to {path}. Error: {e}")
            alt_path = os.path.join(output_dir, f"{self.exchange_name.lower()}_results_alt.csv")
            df_trades.to_csv(alt_path, index=False)
            print(f"Saved to alternative path: {alt_path}")

if __name__ == "__main__":
    # Exness BTCUSD raw file
    exness_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
    if os.path.exists(exness_path):
        bt = Backtester(exness_path, 'Exness')
        bt.run()
