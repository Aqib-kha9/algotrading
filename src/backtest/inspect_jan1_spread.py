import pandas as pd

file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)

jan1 = df[df.index.date == pd.to_datetime('2026-01-01').date()]
sess = jan1.between_time('02:40', '04:05')
print("--- Jan 1st Session Detail (with Spread) ---")
for t, row in sess.iterrows():
    print(f"{t.time()} | H: {row['<HIGH>']:.2f} | L: {row['<LOW>']:.2f} | C: {row['<CLOSE>']:.2f} | S: {row['<SPREAD>']}")
