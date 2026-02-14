import pandas as pd

file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)

# Filter for Jan 2026
df_jan = df[df.index >= '2026-01-01']

RANGE_START = '02:45'
RANGE_END   = '03:55'

print(f"{'Date':<12} | {'Sess_High':<10} | {'Sess_Low':<10}")
print("-" * 35)

unique_dates = sorted(list(set(df_jan.index.date)))
for d in unique_dates:
    if d > pd.to_datetime('2026-01-14').date(): break
    day_data = df_jan[df_jan.index.date == d]
    sess = day_data[(day_data.index.time >= pd.Timestamp(RANGE_START).time()) & 
                    (day_data.index.time <= pd.Timestamp(RANGE_END).time())]
    if not sess.empty:
        sh = sess['<HIGH>'].max()
        sl = sess['<LOW>'].min()
        print(f"{str(d):<12} | {sh:10.2f} | {sl:10.2f}")
    else:
        print(f"{str(d):<12} | {'No Data':<10} | {'No Data':<10}")
