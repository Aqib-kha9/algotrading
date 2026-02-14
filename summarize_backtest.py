
try:
    with open('backtest_results.txt', 'r', encoding='utf-16') as f:
        lines = f.readlines()
except:
    with open('backtest_results.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

output = "| Date | Signal | Result | P&L |\n|---|---|---|---|\n"
count = 0
for line in lines:
    if "2026-01-" in line:
        parts = line.split('|')
        # Structure: Date | Signal | Entry | Exit | Result | P&L
        if len(parts) >= 6:
            date = parts[0].strip()
            signal = parts[1].strip()
            result = parts[4].strip()
            pnl = parts[5].strip()
            output += f"| {date} | {signal} | {result} | {pnl} |\n"
            count += 1

with open('backtest_summary.md', 'w', encoding='utf-8') as f:
    f.write(output)
    
print(f"Summary written to backtest_summary.md with {count} rows.")
