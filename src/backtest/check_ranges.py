import pandas as pd

def check_ranges():
    path = r"e:\cyptoalgotrading\data\processed\exness_btcusd_5m_ist.csv"
    df = pd.read_csv(path)
    df['datetime_ist_val'] = pd.to_datetime(df['datetime'], utc=True).dt.tz_convert('Asia/Kolkata')
    
    dates_to_check = ['2026-01-02', '2026-01-03', '2026-01-04', '2026-01-06']
    client_ranges = {
        '2026-01-02': 89029.84, # Range High
        '2026-01-03': 90372.00, # Range High
        '2026-01-04': 91320.54, # Range High
        '2026-01-06': 93933.64  # Range High
    }
    
    print("--- Session Range Comparison (8:15-9:15 IST) ---")
    for d_str in dates_to_check:
        d = pd.to_datetime(d_str).date()
        day_data = df[df['datetime_ist_val'].dt.date == d]
        session = day_data[(day_data['datetime_ist_val'].dt.hour * 100 + day_data['datetime_ist_val'].dt.minute >= 815) & 
                          (day_data['datetime_ist_val'].dt.hour * 100 + day_data['datetime_ist_val'].dt.minute <= 915)]
        
        our_high = session['high'].max()
        client_high = client_ranges[d_str]
        diff = our_high - client_high
        
        print(f"Date: {d_str} | Our High: {our_high:.2f} | Client High: {client_high:.2f} | Diff: {diff:.2f}")

if __name__ == "__main__":
    check_ranges()
