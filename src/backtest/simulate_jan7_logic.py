import pandas as pd
import os

path = r"e:\cyptoalgotrading\data\processed\exness_btcusd_5m_ist.csv"
df = pd.read_csv(path)
df['datetime_ist_val'] = pd.to_datetime(df['datetime'], utc=True).dt.tz_convert('Asia/Kolkata')

# Strategy State Jan 7
session_high = -1.0
session_low = 999999999.0
daily_trade_taken = False

print(f"--- Simulating Jan 7 Logic ---")
jan7_data = df[df['datetime_ist_val'].dt.date == pd.to_datetime("2026-01-07").date()]

for i, row in jan7_data.iterrows():
    dt_ist = row['datetime_ist_val']
    time_val = dt_ist.hour * 100 + dt_ist.minute
    
    # Session Update (8:15 – 9:15 IST)
    if 815 <= time_val <= 915:
        old_low = session_low
        session_high = max(session_high, row['high'])
        session_low = min(session_low, row['low'])
        # if session_low != old_low:
        #    print(f"Update Session Low at {dt_ist.time()}: {session_low}")

    # Entry Check (After 9:15)
    if not daily_trade_taken and session_low != 999999999.0 and time_val > 915:
        sell_trigger = session_low * 0.9995
        if row['low'] <= sell_trigger:
            print(f"!!! ENTRY HIT at {dt_ist.time()} !!!")
            print(f"    Session Low: {session_low}")
            print(f"    Sell Trigger: {sell_trigger}")
            print(f"    Current Low: {row['low']}")
            daily_trade_taken = True
            
            # Now simulate trade management
            entry_price = sell_trigger
            sl = entry_price * 1.0030
            tp = entry_price * 0.9930
            print(f"    SL: {sl} | TP: {tp}")
            
            # Search for exit in subsequent rows
            future_data = jan7_data.loc[i+1:]
            for j, frow in future_data.iterrows():
                ftime = frow['datetime_ist_val'].time()
                if frow['high'] >= sl:
                    print(f"    >>> EXIT at {ftime}: STOP LOSS HIT (High {frow['high']} >= {sl})")
                    break
                if frow['low'] <= tp:
                    print(f"    >>> EXIT at {ftime}: TARGET HIT (Low {frow['low']} <= {tp})")
                    break
                if frow['datetime_ist_val'].hour * 100 + frow['datetime_ist_val'].minute >= 1915:
                    print(f"    >>> EXIT at {ftime}: TIME EXIT (Close {frow['close']})")
                    break
            break

if not daily_trade_taken:
    print(f"No trade taken. Final Session Low: {session_low} | Sell Trigger: {session_low * 0.9995 if session_low != 999999999.0 else 'N/A'}")
