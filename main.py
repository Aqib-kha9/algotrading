import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Crypto Algo Trading System")
    parser.add_argument('mode', choices=['dashboard', 'bot'], help="Mode to run")
    parser.add_argument('--exchange', default='binance', help="Exchange to use for bot (binance, paper)")
    
    args = parser.parse_args()
    
    if args.mode == 'dashboard':
        print("Launching Dashboard...")
        os.system("streamlit run src/dashboard/app.py")
        
    elif args.mode == 'bot':
        print(f"Starting Trading Bot on {args.exchange}...")
        from src.live_trade.bot import TradingBot
        from src.live_trade.execution import BinanceAdapter, PaperTradingAdapter
        from dotenv import load_dotenv
        
        load_dotenv()
        
        config = {
            'symbol': 'BTC/USDT',
            'quantity': 0.001,
            'interval_seconds': 60
        }
        
        if args.exchange == 'paper':
            # Paper trade using Binance public data
            real_adapter = BinanceAdapter() # Public logic
            adapter = PaperTradingAdapter(real_adapter)
        else:
            api_key = os.getenv('BINANCE_API_KEY')
            secret = os.getenv('BINANCE_SECRET')
            if not api_key:
                print("Error: BINANCE_API_KEY not found in .env")
                return
            adapter = BinanceAdapter(api_key, secret)
            
        bot = TradingBot(adapter, config)
        bot.run()

if __name__ == "__main__":
    main()
