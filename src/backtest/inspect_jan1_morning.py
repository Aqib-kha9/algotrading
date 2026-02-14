import pandas as pd

file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)

jan1 = df[df.index.date == pd.to_datetime('2026-01-01').date()]
print("--- Jan 1st Candles (00:00 - 06:00 UTC) ---")
print(jan1.between_time('00:00', '06:00')[['<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>']])
