
import pandas as pd
import pytz

# Load data
file_path = 'e:/cyptoalgotrading/data/processed/exness_btcusd_5m_ist.csv'
df = pd.read_csv(file_path)

# Fix Timezone (Method from engine.py)
df['datetime_ist'] = pd.to_datetime(df['datetime'], utc=True).dt.tz_convert('Asia/Kolkata')

# Filter for Jan 7 and 8 2026
df_jan = df[(df['datetime_ist'].dt.year == 2026) & (df['datetime_ist'].dt.month == 1) & (df['datetime_ist'].dt.day.isin([7, 8]))]

# Function to analyze a specific day
def analyze_day(day_df, day_int):
    print(f"\n--- Analysis for Jan {day_int} ---")
    
    # 1. Identify Session High/Low (08:15 - 09:15)
    # 8:15 is 815, 9:15 is 915
    day_df = day_df.copy()
    day_df['time_val'] = day_df['datetime_ist'].dt.hour * 100 + day_df['datetime_ist'].dt.minute
    
    session_df = day_df[(day_df['time_val'] >= 815) & (day_df['time_val'] <= 915)]
    
    if session_df.empty:
        print("No session data found.")
        return

    s_high = session_df['high'].max()
    s_low = session_df['low'].min()
    
    print(f"Session (08:15-09:15) High: {s_high}")
    print(f"Session (08:15-09:15) Low:  {s_low}")
    
    # Calculated Triggers
    buy_trig = s_high * 1.0005
    sell_trig = s_low * 0.9995
    print(f"Calc Buy Trigger: {buy_trig:.2f}")
    print(f"Calc Sell Trigger: {sell_trig:.2f}")

    # 2. Find Entry
    # Look for first candle after 09:15 crossing trigger
    
    entry_df = day_df[day_df['time_val'] > 915]
    trade_type = None
    entry_price = 0
    entry_time = None
    
    for idx, row in entry_df.iterrows():
        if row['high'] > buy_trig:
            trade_type = 'BUY'
            entry_price = buy_trig # Assumption: Entry at trigger
            entry_time = row['datetime_ist']
            print(f"Trade Triggered: BUY at {entry_time} (Candle High: {row['high']})")
            break
        elif row['low'] < sell_trig:
            trade_type = 'SELL'
            entry_price = sell_trig
            entry_time = row['datetime_ist']
            print(f"Trade Triggered: SELL at {entry_time} (Candle Low: {row['low']})")
            break
            
    if trade_type == 'SELL':
        sl = entry_price * 1.003
        tp = entry_price * 0.993
        print(f"Setup: SELL @ {entry_price:.2f} | SL: {sl:.2f} | TP: {tp:.2f}")
        
        # Check subsequent candles
        trade_candles = entry_df[entry_df['datetime_ist'] > entry_time]
        for idx, row in trade_candles.iterrows():
            if row['high'] >= sl:
                print(f"STOP LOSS HIT at {row['datetime_ist']} | High: {row['high']} >= {sl:.2f}")
                break
            if row['low'] <= tp:
                print(f"TARGET HIT at {row['datetime_ist']} | Low: {row['low']} <= {tp:.2f}")
                break
                
    elif trade_type == 'BUY':
        sl = entry_price * 0.997
        tp = entry_price * 1.007
        print(f"Setup: BUY @ {entry_price:.2f} | SL: {sl:.2f} | TP: {tp:.2f}")
        
        trade_candles = entry_df[entry_df['datetime_ist'] > entry_time]
        for idx, row in trade_candles.iterrows():
            if row['low'] <= sl:
                print(f"STOP LOSS HIT at {row['datetime_ist']} | Low: {row['low']} <= {sl:.2f}")
                break
            if row['high'] >= tp:
                print(f"TARGET HIT at {row['datetime_ist']} | High: {row['high']} >= {tp:.2f}")
                break

# Run
analyze_day(df_jan[df_jan['datetime_ist'].dt.day == 7], 7)
# analyze_day(df_jan[df_jan['datetime_ist'].dt.day == 8], 8)
