import pandas as pd
import numpy as np

def backtest_manual_strategy(file_path):
    print(f"Loading {file_path}...")
    try:
        df = pd.read_csv(file_path, sep='\t')
    except:
        df = pd.read_csv(file_path)
        
    # Process Datetime (Exness is UTC)
    df['datetime'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
    df.set_index('datetime', inplace=True)
    
    # Calculate Mid-Prices (Logic discovered: Client uses Bid + Spread*0.01/2)
    # For BTCUSD on Exness, spread is in 0.01 units.
    df['high'] = df['<HIGH>'] + (df['<SPREAD>'] * 0.01 / 2)
    df['low']  = df['<LOW>']  + (df['<SPREAD>'] * 0.01 / 2)
    df['close'] = df['<CLOSE>'] + (df['<SPREAD>'] * 0.01 / 2)
    
    # Strategy Parameters
    # Adjusted to UTC (Client 02:45-03:55 Terminal Time is 00:45-01:55 UTC)
    RANGE_START_UTC = "00:45" 
    RANGE_END_UTC   = "01:55" 
    ENTRY_LIMIT_UTC = "12:30" # 18:00 IST (UTC based limit)
    EXIT_TIME_UTC   = "13:40" # 19:10 IST
    
    BUFF_PERC = 0.0005 # 0.05%
    TGT_PERC  = 0.0070 # 0.70%
    SL_PERC   = 0.0030 # 0.30%
    
    # TSL Parameters
    TSL_ACTIVATE_PERC = 0.0040 # 0.40%
    TSL_TRAIL_COORD   = 0.0020 # 0.20% locked profit level
    
    # Results
    daily_results = []
    
    # Filter for Jan 2026
    df = df[df.index >= '2026-01-01']
    
    # Iterate by Date
    unique_dates = sorted(list(set(df.index.date)))
    
    print(f"\nScanning {len(unique_dates)} days (Jan 2026)...")
    print(f"{'Date':<12} | {'Signal':<6} | {'Entry':<10} | {'Exit':<10} | {'Result':<10} | {'PnL':<8}")
    print("-" * 80)
    
    for current_date in unique_dates:
        # Filter Day Data
        day_str = str(current_date)
        day_data = df[df.index.date == current_date]
        
        if day_data.empty: continue
        
        # 1. Define Session Range 
        session_mask = (day_data.index.time >= pd.Timestamp(RANGE_START_UTC).time()) & \
                       (day_data.index.time <= pd.Timestamp(RANGE_END_UTC).time())
        session_data = day_data[session_mask]
        
        if session_data.empty:
            continue
            
        range_high = session_data['high'].max()
        range_low  = session_data['low'].min()
        
        # 2. Define Triggers
        buy_trigger = range_high * (1 + BUFF_PERC)
        sell_trigger = range_low * (1 - BUFF_PERC)
        
        # 3. Scan for Entry (After Session Range)
        trade_data = day_data[day_data.index.time > pd.Timestamp(RANGE_END_UTC).time()]
        trade_data = trade_data[trade_data.index.time <= pd.Timestamp(EXIT_TIME_UTC).time()]
        
        position = None # 'BUY' or 'SELL'
        entry_price = 0.0
        entry_time = None
        exit_price = 0.0
        
        trade_pnl = 0.0
        result_type = "NO TRD"
        
        for t_time, row in trade_data.iterrows():
            if position is None:
                # Check for Entry (Only before Entry Limit)
                if t_time.time() > pd.Timestamp(ENTRY_LIMIT_UTC).time():
                    continue

                if row['high'] >= buy_trigger:
                    position = 'BUY'
                    entry_price = buy_trigger
                    entry_time = t_time
                    tp_price = entry_price * (1 + TGT_PERC)
                    sl_price = entry_price * (1 - SL_PERC)
                    tsl_active = False
                    
                elif row['low'] <= sell_trigger:
                    position = 'SELL'
                    entry_price = sell_trigger
                    entry_time = t_time
                    tp_price = entry_price * (1 - TGT_PERC)
                    sl_price = entry_price * (1 + SL_PERC)
                    tsl_active = False
                    
            else:
                # Manage Trade
                curr_h = row['high']
                curr_l = row['low']
                
                if position == 'BUY':
                    # Trail Logic
                    if not tsl_active and curr_h >= entry_price * (1 + TSL_ACTIVATE_PERC):
                        tsl_active = True
                        sl_price = entry_price * (1 - TSL_TRAIL_COORD)
                    
                    # Check SL
                    if curr_l <= sl_price:
                        result_type = "TSL HIT" if tsl_active else "SL HIT"
                        exit_price = sl_price
                        trade_pnl = exit_price - entry_price
                        break
                    # Check TP
                    if curr_h >= tp_price:
                        result_type = "TP HIT"
                        exit_price = tp_price
                        trade_pnl = exit_price - entry_price
                        break
                        
                elif position == 'SELL':
                    # Trail Logic
                    if not tsl_active and curr_l <= entry_price * (1 - TSL_ACTIVATE_PERC):
                        tsl_active = True
                        sl_price = entry_price * (1 + TSL_TRAIL_COORD)
                            
                    # Check SL
                    if curr_h >= sl_price:
                        result_type = "TSL HIT" if tsl_active else "SL HIT"
                        exit_price = sl_price
                        trade_pnl = entry_price - exit_price
                        break
                    # Check TP
                    if curr_l <= tp_price:
                        result_type = "TP HIT"
                        exit_price = tp_price
                        trade_pnl = entry_price - exit_price
                        break
        
        # End of Day Check
        if position is not None and result_type == "NO TRD":
            exit_price = trade_data.iloc[-1]['close']
            result_type = "TIME EXIT"
            trade_pnl = (exit_price - entry_price) if position == 'BUY' else (entry_price - exit_price)
                
        daily_results.append({
            'Date': day_str,
            'Signal': position if position else '-',
            'Entry': round(entry_price, 2) if position else 0,
            'Exit': round(exit_price if position else 0, 2),
            'Result': result_type if position else '-',
            'PnL': round(trade_pnl, 2)
        })
        
        # Print Row
        if position:
            print(f"{day_str:<12} | {position:<6} | {entry_price:10.2f} | {exit_price:10.2f} | {result_type:<10} | {trade_pnl:8.2f}")
        else:
            print(f"{day_str:<12} | {'-':<6} | {'-':>10} | {'-':>10} | {'-':<10} | {0.0:8.2f}")

    # Summary
    print("\n--- Summary ---")
    total_pnl = sum([x['PnL'] for x in daily_results])
    print(f"Total P&L: {total_pnl:.2f}")

if __name__ == "__main__":
    backtest_manual_strategy("data/raw/BTCUSDm_M5_202001010000_202601121835.csv")
