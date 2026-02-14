import pandas as pd
import os

file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)
df['h'] = df['<HIGH>'] + (df['<SPREAD>'] * 0.01 / 2)
df['l'] = df['<LOW>'] + (df['<SPREAD>'] * 0.01 / 2)

def trace(d):
    print(f"\n--- {d} ---")
    data = df[df.index.date == pd.to_datetime(d).date()]
    sess = data.between_time('00:45', '01:55')
    if sess.empty:
        print("No session data!")
        return
        
    h, l = sess['h'].max(), sess['l'].min()
    bt, st = h * 1.0005, l * 0.9995
    print(f"Sess H: {h:.2f} L: {l:.2f} | BT: {bt:.2f} ST: {st:.2f}")
    
    scan = data[data.index.time > pd.Timestamp('01:55').time()]
    for t, r in scan.iterrows():
        if r['h'] >= bt:
            print(f"{t.time()} BUY HIT at {r['h']:.2f}")
            return
        if r['l'] <= st:
            print(f"{t.time()} SELL HIT at {r['l']:.2f}")
            return
    print("NO TRD HIT ALL DAY")

for day in ['2026-01-02', '2026-01-05', '2026-01-07']:
    trace(day)
