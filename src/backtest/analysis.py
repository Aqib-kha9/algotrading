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
    max_drawdown = 0 # Simple calc TODO
    # Calculate Drawdown
    # Assuming 'cumulative_pnl' is equity curve percentage based (Log Scaleish)
    # Proper drawdown needs equity balance. Let's assume starting capital 100.
    
    equity = [100]
    peak = 100
    drawdowns = []
    
    for pnl in df['pnl']:
        # PnL is percentage. New Equity = Old * (1 + pnl/100)
        new_equity = equity[-1] * (1 + pnl/100)
        equity.append(new_equity)
        
        peak = max(peak, new_equity)
        dd = (peak - new_equity) / peak * 100
        drawdowns.append(dd)
    
    max_dd = max(drawdowns) if drawdowns else 0
    final_equity = equity[-1]
    roi = (final_equity - 100)
    
    # Generate Markdown Report
    report_content = f"""# Backtest Performance Report
    
## SOW Metrics
- **Net Profit**: {roi:.2f}% (Compound)
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
