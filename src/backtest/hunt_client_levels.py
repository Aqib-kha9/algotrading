import pandas as pd

# Load raw Exness data
file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
try:
    df = pd.read_csv(file_path, sep='\t')
except:
    df = pd.read_csv(file_path)

df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
df.set_index('dt', inplace=True)
df['mid_h'] = df['<HIGH>'] + (df['<SPREAD>'] * 0.01 / 2)
df['mid_l'] = df['<LOW>'] + (df['<SPREAD>'] * 0.01 / 2)

# Client data extracted from their text/screenshots
# Format: {Date: (Expected_Range_High, Expected_Range_Low)}
# Based on the user's latest text:
client_expt = {
    '2026-01-01': (None, 87674.93),
    '2026-01-02': (89029.84, None),
    '2026-01-07': (None, 92681.54),
    '2026-01-09': (None, 90869.77),
    '2026-01-12': (None, 91365.44)
}

print(f"{'Date':<12} | {'Sess Bid L':<12} | {'Sess Mid L':<12} | {'Target (C)':<12} | {'Match Type'}")
print("-" * 80)

for d_str, targets in client_expt.items():
    day_data = df[df.index.date == pd.to_datetime(d_str).date()]
    sess = day_data.between_time('02:45', '03:55')
    
    bid_h = sess['<HIGH>'].max()
    bid_l = sess['<LOW>'].min()
    mid_h = sess['mid_h'].max()
    mid_l = sess['mid_l'].min()
    
    tgt_h, tgt_l = targets
    
    if tgt_l:
        match_type = "NONE"
        if round(bid_l, 2) == round(tgt_l, 2): match_type = "BID L ✅"
        elif round(mid_l, 2) == round(tgt_l, 2): match_type = "MID L ✅"
        print(f"{d_str:<12} | {bid_l:12.2f} | {mid_l:12.2f} | {tgt_l:12.2f} | {match_type}")
    
    if tgt_h:
        match_type = "NONE"
        if round(bid_h, 2) == round(tgt_h, 2): match_type = "BID H ✅"
        elif round(mid_h, 2) == round(tgt_h, 2): match_type = "MID H ✅"
        print(f"{d_str:<12} | {bid_h:12.2f} | {mid_h:12.2f} | {tgt_h:12.2f} | {match_type}")
