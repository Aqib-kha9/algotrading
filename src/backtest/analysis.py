import pandas as pd
import plotly.graph_objects as go
import os

def generate_report(results_file, report_file):
    if not os.path.exists(results_file):
        print("No results file found.")
        return

    df = pd.read_csv(results_file)
    
    # Cumulative PnL
    df['cumulative_pnl'] = df['pnl'].cumsum()
    
    # Metrics
    total_trades = len(df)
    wins = len(df[df['pnl'] > 0])
    losses = len(df[df['pnl'] <= 0])
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
    net_pnl = df['pnl'].sum()
    avg_pnl = df['pnl'].mean()
    
    # Drawdown (based on Cumulative PnL peak)
    equity = df['cumulative_pnl'].tolist()
    # Normalize equity to start at 0 or simply track localized drawdowns
    # Better: Peak = max(cum_pnl so far). DD = Peak - current_cum_pnl
    
    peak = -9999999
    drawdowns = []
    
    for val in equity:
        peak = max(peak, val)
        dd = peak - val
        drawdowns.append(dd)
    
    max_dd = max(drawdowns) if drawdowns else 0
    
    # Generate Markdown Report
    report_content = f"""# Backtest Performance Report
    
## SOW Metrics
- **Net Profit (Points)**: {net_pnl:.2f}
- **Total Trades**: {total_trades}
- **Win Ratio**: {win_rate:.2f}%
- **Max Drawdown**: {max_dd:.2f}%
- **Risk-Reward Ratio**: 1:{abs(0.70/0.30):.2f} (Base)

## Detailed Stats
- Average PnL per trade: {avg_pnl:.2f}%
- Final Equity (from 100): {final_equity:.2f}

## Equity Curve
(See attached image if generated, or run locally to view interactive Plotly chart)
"""
    
    with open(report_file, 'w') as f:
        f.write(report_content)
        
    print(report_content)
    
    # Generate Chart (HTML)
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=equity, mode='lines', name='Equity'))
    fig.update_layout(title='Strategy Equity Curve (Compound)', xaxis_title='Trade #', yaxis_title='Equity')
    fig.write_html("data/equity_curve.html")
    print("Chart saved to data/equity_curve.html")

if __name__ == "__main__":
    generate_report('data/backtest_results.csv', 'data/performance_report.md')
