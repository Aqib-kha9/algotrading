import pandas as pd

# Load data
file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)
df['h'] = df['<HIGH>'] + (df['<SPREAD>'] * 0.01 / 2)
df['l'] = df['<LOW>'] + (df['<SPREAD>'] * 0.01 / 2)

def analyze_day(date_str):
    print(f"\n--- Analysis for {date_str} ---")
    data = df[df.index.date == pd.to_datetime(date_str).date()]
    
    RANGE_START_UTC = "02:45"
    RANGE_END_UTC   = "03:55" 
    BUFF_PERC = 0.0005
    
    # Session Analysis
    sess = data.between_time(RANGE_START_UTC, RANGE_END_UTC)
    if sess.empty:
        print("No session data found!")
        return
        
    sess_h = sess['h'].max()
    sess_l = sess['l'].min()
    buy_trig = sess_h * (1 + BUFF_PERC)
    sell_trig = sess_l * (1 - BUFF_PERC)
    
    print(f"Session Range: {RANGE_START_UTC} - {RANGE_END_UTC} UTC")
    print(f"Session H: {sess_h:.2f} | Sess L: {sess_l:.2f}")
    print(f"Buy Trigger: {buy_trig:.2f} | Sell Trigger: {sell_trig:.2f}")
    
    # Trade Scan Analysis
    scan_start = RANGE_END_UTC
    scan_end = "13:40"
    scan_data = data[(data.index.time > pd.Timestamp(scan_start).time()) & 
                    (data.index.time <= pd.Timestamp(scan_end).time())]
                    
    print(f"\nScanning trades from {scan_start} UTC onwards...")
    
    first_hit = None
    for t, row in scan_data.iterrows():
        if row['h'] >= buy_trig and row['l'] <= sell_trig:
             print(f"{t.time()} - BOTH TRIGGERS HIT IN SAME CANDLE! H: {row['h']:.2f}, L: {row['l']:.2f}")
             first_hit = "Both"
             break
        elif row['h'] >= buy_trig:
            print(f"{t.time()} - BUY TRIGGER HIT at {row['h']:.2f}")
            first_hit = "Buy"
            break
        elif row['l'] <= sell_trig:
            print(f"{t.time()} - SELL TRIGGER HIT at {row['l']:.2f}")
            first_hit = "Sell"
            break
            
    if not first_hit:
        print("No triggers hit today.")

# Analyze the problematic days
analyze_day('2026-01-02')
analyze_day('2026-01-05')
analyze_day('2026-01-07')
