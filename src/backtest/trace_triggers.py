import pandas as pd

file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)
df['high_mid'] = df['<HIGH>'] + (df['<SPREAD>'] * 0.01 / 2)
df['low_mid']  = df['<LOW>']  + (df['<SPREAD>'] * 0.01 / 2)

def trace_day(date_str):
    print(f"\n--- TRACING {date_str} ---")
    day_data = df[df.index.date == pd.to_datetime(date_str).date()]
    
    RANGE_START_UTC = "00:45"
    RANGE_END_UTC   = "01:55"
    BUFF_PERC = 0.0005
    
    session_data = day_data.between_time(RANGE_START_UTC, RANGE_END_UTC)
    if session_data.empty:
        print("No session data!")
        return
        
    sess_h = session_data['high_mid'].max()
    sess_l = session_data['low_mid'].min()
    buy_trig = sess_h * (1 + BUFF_PERC)
    sell_trig = sess_l * (1 - BUFF_PERC)
    
    print(f"Session H: {sess_h:.2f} | L: {sess_l:.2f}")
    print(f"Buy Trig:  {buy_trig:.2f} | Sell Trig: {sell_trig:.2f}")
    
    trade_data = day_data[day_data.index.time > pd.Timestamp(RANGE_END_UTC).time()]
    for t, row in trade_data.iterrows():
        if row['high_mid'] >= buy_trig and row['low_mid'] <= sell_trig:
            print(f"{t.time()} | BOTH CRITICAL CROSS! H: {row['high_mid']:.2f}, L: {row['low_mid']:.2f}")
        elif row['high_mid'] >= buy_trig:
            print(f"{t.time()} | BUY TRIGGER HIT at {row['high_mid']:.2f}")
            break
        elif row['low_mid'] <= sell_trig:
            print(f"{t.time()} | SELL TRIGGER HIT at {row['low_mid']:.2f}")
            break

trace_day('2026-01-02')
trace_day('2026-01-05')
trace_day('2026-01-07')
