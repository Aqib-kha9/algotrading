import pandas as pd
import os

file_path = "data/raw/BTCUSDm_M5_202001010000_202601121835.csv"
if os.path.exists(file_path):
    try:
        df = pd.read_csv(file_path, sep='\t')
    except:
        df = pd.read_csv(file_path)
    
    df['dt'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'])
    jan1 = df[df['dt'].dt.date == pd.to_datetime('2026-01-01').date()]
    if not jan1.empty:
        print(f"Jan 1st Open: {jan1.iloc[0]['<OPEN>']}")
    else:
        print("No data for Jan 1st.")
else:
    print("File not found.")
