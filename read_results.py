

try:
    with open('backtest_results_v2.txt', 'r', encoding='utf-16') as f:
        lines = f.readlines()
except:
    with open('backtest_results_v2.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

print("--- Parsed Results (Jan 4) ---")
for line in lines:
    if "2026-01-04" in line:
        print(line.strip())

