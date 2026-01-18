from src.backtest.engine import Backtester
import pandas as pd

def run_single_backtest():
    file_path = r'e:\cyptoalgotrading\data\processed\exness_2026_5m.csv'
    
    print(f"Running backtest on: {file_path}")
    
    # Initialize Backtester with ZERO fees and spread for exact calculations
    bt = Backtester(file_path, exchange_name='Exness_2026_NoFees', fee_pct=0, spread_pct=0)
    bt.run()
    
    # Summary is usually saved to internal list, let's print stats
    trades = bt.trades
    if not trades:
        print("No trades generated.")
        return
        
    df = pd.DataFrame(trades)
    
    total_trades = len(df)
    net_pnl = df['pnl_pct'].sum()
    wins = len(df[df['pnl_pct'] > 0])
    losses = len(df[df['pnl_pct'] <= 0])
    win_rate = (wins / total_trades) * 100
    
    print("-" * 30)
    print("BACKTEST RESULTS (Exness 2026 Data)")
    print("-" * 30)
    print(f"Total Trades: {total_trades}")
    print(f"Net PnL: {net_pnl:.2f}%")
    print(f"Win Rate: {win_rate:.2f}%")
    print("-" * 30)

if __name__ == "__main__":
    run_single_backtest()
