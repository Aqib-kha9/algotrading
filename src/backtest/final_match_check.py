import pandas as pd

# Client Data extracted from text
client_data = {
    '2026-01-01': {'PnL': -260, 'Entry': 87631, 'Type': 'SELL'},
    '2026-01-02': {'PnL': 620,  'Entry': 89074, 'Type': 'BUY'},
    '2026-01-03': {'PnL': -270, 'Entry': 90417, 'Type': 'BUY'},
    '2026-01-04': {'PnL': -180, 'Entry': 91366, 'Type': 'BUY'},
    '2026-01-05': {'PnL': 650,  'Entry': 92781, 'Type': 'SELL'},
    '2026-01-06': {'PnL': -280, 'Entry': 93981, 'Type': 'SELL'},
    '2026-01-07': {'PnL': 650,  'Entry': 92635, 'Type': 'SELL'},
    '2026-01-08': {'PnL': 630,  'Entry': 90636, 'Type': 'SELL'}, # Wait, text says 90636 for Buy/Sell?
    '2026-01-09': {'PnL': 640,  'Entry': 90384, 'Type': 'SELL'},
    '2026-01-10': {'PnL': -280, 'Entry': 90670, 'Type': 'BUY'},
    '2026-01-11': {'PnL': 50,   'Entry': 90655, 'Type': 'BUY'},
    '2026-01-12': {'PnL': 640,  'Entry': 91732, 'Type': 'BUY'},
    '2026-01-13': {'PnL': 640,  'Entry': 91411, 'Type': 'SELL'},
    '2026-01-14': {'PnL': -280, 'Entry': 91777, 'Type': 'BUY'},
}

# My Data
df = pd.read_csv('data/results/exness_results.csv')
df_2026 = df[df['date'].str.startswith('2026')].copy()

print(f"{'Date':<12} | {'S':<4} | {'Client PnL':<10} | {'My PnL':<10} | {'Diff':<8} | {'Entry (C)':<10} | {'Entry (M)':<10}")
print("-" * 80)

for d, c in client_data.items():
    my_row = df_2026[df_2026['date'] == d]
    if not my_row.empty:
        my_pnl = my_row.iloc[0]['pnl']
        my_entry = my_row.iloc[0]['entry_price']
        my_type = my_row.iloc[0]['type'].upper()
        diff = my_pnl - c['PnL']
        print(f"{d:<12} | {my_type:<4} | {c['PnL']:10.2f} | {my_pnl:10.2f} | {diff:8.2f} | {c['Entry']:10.2f} | {my_entry:10.2f}")
    else:
        print(f"{d:<12} | {'-':<4} | {c['PnL']:10.2f} | {'MISSING':<10} | {'-':<8} | {c['Entry']:10.2f} | {'-':<10}")
