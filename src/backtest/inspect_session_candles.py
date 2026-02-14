import pandas as pd

file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)

def inspect_day(date_str):
    print(f"\n--- Inspecting {date_str} (02:45 - 03:55 UTC) ---")
    day_data = df[df.index.date == pd.to_datetime(date_str).date()]
    sess = day_data[(day_data.index.time >= pd.Timestamp('02:45').time()) & 
                    (day_data.index.time <= pd.Timestamp('03:55').time())]
    print(sess[['<HIGH>', '<LOW>', '<CLOSE>']])
    print(f"Max High: {sess['<HIGH>'].max()}")
    print(f"Min Low:  {sess['<LOW>'].min()}")

inspect_day('2026-01-01')
inspect_day('2026-01-07')
