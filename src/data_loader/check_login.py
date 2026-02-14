import MetaTrader5 as mt5
import argparse

def check_login(path=None):
    print(f"Testing connection to: {path if path else 'Default'}")
    
    init_args = {}
    if path:
        init_args['path'] = path
        
    if not mt5.initialize(**init_args):
        print(f"FAILED to initialize: {mt5.last_error()}")
        return

    print("Initialize SUCCESS.")
    
    # Check Terminal Info
    term = mt5.terminal_info()
    print(f"Terminal: {term.name} | Build: {term.build}")
    print(f"Connected: {term.connected}")
    print(f"Algo Trading Allowed: {term.trade_allowed}")  # This is crucial!
    
    # Check Account Info
    account = mt5.account_info()
    if account:
        print(f"\nAccount: {account.login}")
        print(f"Server: {account.server}")
        print(f"Balance: {account.balance} {account.currency}")
        print(f"Trade Allowed (Account): {account.trade_allowed}")
        print("LOGIN STATUS: OK")
    else:
        print("\nNO ACCOUNT DETECTED.")
        print("Please log in to the terminal manually.")
        
    mt5.shutdown()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="Path to terminal64.exe")
    args = parser.parse_args()
    check_login(args.path)
