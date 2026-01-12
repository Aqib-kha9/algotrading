from engine import Backtester
import pandas as pd
import os

def run_comparison():
    print("Running Exchange Comparison Simulation (Phase 4)...")
    data_path = 'data/processed/btcusdt_5m_1825d.csv'
    
    # Scenarios
    # 1. Delta Exchange (Crypto Futures): Low Fees (e.g., 0.05%), Tight Spread
    # 2. XM (CFD): No Comm, but Higher Spread (e.g. 0.05% Spread built-in?) -> Let's assume 0.03% Fee equivalent + 0.02% Spread
    # 3. Exness (CFD): High leverage, Variable Spread.
    
    scenarios = [
        {'name': 'Delta_Exchange', 'fee': 0.05, 'spread': 0.01}, 
        {'name': 'XM_Global', 'fee': 0.0, 'spread': 0.08}, # Zero fee, high spread
        {'name': 'Exness', 'fee': 0.0, 'spread': 0.05},    # Zero fee, med spread
    ]
    
    summary = []
    
    for scen in scenarios:
        print(f"Simulating {scen['name']}...")
        bt = Backtester(data_path, {}, fee_pct=scen['fee'], spread_pct=scen['spread'])
        bt.run()
        
        # Calculate Stats from last run results (saved in memory or file)
        # We need to grab results from the instance before they are overwritten or extract from CSV
        # Modifying engine to return stats or reading the csv
        
        # Quick Hack: Read the just-saved csv
        res_df = pd.read_csv('data/backtest_results.csv')
        net_pnl = res_df['pnl'].sum()
        win_rate = len(res_df[res_df['pnl'] > 0]) / len(res_df) * 100
        
        summary.append({
            'Exchange': scen['name'],
            'Net PnL (%)': round(net_pnl, 2),
            'Win Rate (%)': round(win_rate, 2),
            'Fee Config': f"{scen['fee']}%",
            'Spread Config': f"{scen['spread']}%"
        })
        
        # Save specific file
        res_df.to_csv(f"data/backtest_{scen['name']}.csv", index=False)

    # Save Comparison
    df_sum = pd.DataFrame(summary)
    df_sum.to_csv('data/exchange_comparison.csv', index=False)
    
    print("\n=== Exchange Comparison Report ===")
    print(df_sum.to_markdown())
    
    # Save Report
    with open('data/comparison_report.md', 'w') as f:
        f.write("# Exchange Comparison Report\n\n")
        f.write(df_sum.to_markdown())

if __name__ == "__main__":
    run_comparison()
