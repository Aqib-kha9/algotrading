import time
import pandas as pd
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Setup Logging
logging.basicConfig(
    filename='logs/trading_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TradingBot:
    def __init__(self, exchange_adapter, config):
        self.exchange = exchange_adapter
        self.config = config
        
        # Strategy State
        self.session_high = None
        self.session_low = None
        self.daily_trade_taken = False
        self.current_date = None
        
        # Position State
        self.active_position = None # { 'symbol': 'BTC/USDT', 'side': 'buy', 'entry': 100, 'sl': 99, 'tp': 102 }

    def run(self):
        logging.info("Starting Trading Bot...")
        print("Bot Started. Waiting for data...")
        
        while True:
            try:
                self.tick()
                time.sleep(self.config.get('interval_seconds', 60)) # Check every minute
            except KeyboardInterrupt:
                print("Stopping Bot...")
                break
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(10)

    def tick(self):
        # 1. Get Time (IST)
        import pytz
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist) 
        
        symbol = self.config['symbol']
        ticker = self.exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Reset Logic (New Day)
        today_str = now.strftime('%Y-%m-%d')
        if self.current_date != today_str:
            self.current_date = today_str
            self.session_high = None
            self.session_low = None
            self.daily_trade_taken = False
            logging.info(f"New Day: {today_str}. Resetting state.")

        # 2. Session Logic (08:15 - 09:15)
        # Assuming simple time check (Hours 8, Minute 15 etc)
        # Note: server time vs IST. using datetime.now() implies local server time. 
        # SHOULD use pytz for robust IST. Simplified here.
        
        curr_hour = now.hour
        curr_min = now.minute
        time_val = curr_hour * 100 + curr_min
        
        if 815 <= time_val <= 915:
            # During Session: Update High/Low
            if self.session_high is None:
                self.session_high = current_price
                self.session_low = current_price
            else:
                self.session_high = max(self.session_high, current_price)
                self.session_low = min(self.session_low, current_price)
            return

        # 3. Post-Session: Look for Entries
        if self.session_high and not self.daily_trade_taken and not self.active_position:
            # Check Buy
            buy_trigger = self.session_high * (1 + 0.0005)
            if current_price > buy_trigger:
                self.execute_entry('buy', current_price)
                return

            # Check Sell
            sell_trigger = self.session_low * (1 - 0.0005)
            if current_price < sell_trigger:
                self.execute_entry('sell', current_price)
                return

        # 4. Manage Open Position
        if self.active_position:
            self.manage_position(current_price)

    def execute_entry(self, side, price):
        logging.info(f"Signal Detected: {side.upper()} @ {price}")
        
        # Calculate Risk Config
        sl_pct = 0.0030
        tp_pct = 0.0070
        
        if side == 'buy':
            sl = price * (1 - sl_pct)
            tp = price * (1 + tp_pct)
        else:
            sl = price * (1 + sl_pct)
            tp = price * (1 - tp_pct)
            
        # Place Order (Live)
        order = self.exchange.create_order(self.config['symbol'], 'market', side, self.config['quantity'])
        if order:
            self.active_position = {
                'side': side,
                'entry': price, # Use fill price ideally
                'sl': sl,
                'tp': tp,
                'trailing_active': False
            }
            self.daily_trade_taken = True
            logging.info(f"Trade Executed: {self.active_position}")
            print(f"Entered {side.upper()} Trade.")

    def manage_position(self, current_price):
        pos = self.active_position
        side = pos['side']
        
        # Check SL/TP
        hit_sl = (side == 'buy' and current_price <= pos['sl']) or (side == 'sell' and current_price >= pos['sl'])
        hit_tp = (side == 'buy' and current_price >= pos['tp']) or (side == 'sell' and current_price <= pos['tp'])
        
        if hit_sl or hit_tp:
            reason = 'TP' if hit_tp else 'SL'
            logging.info(f"Exiting Trade: {reason} Hit. Price: {current_price}")
            
            # Close Order
            close_side = 'sell' if side == 'buy' else 'buy'
            self.exchange.create_order(self.config['symbol'], 'market', close_side, self.config['quantity'])
            
            self.active_position = None
            print(f"Trade Closed ({reason})")
            return
            
        # Trailing Logic
        # Update SL if moved 0.40% in favor
        if side == 'buy':
             if current_price >= pos['entry'] * 1.0040 and not pos.get('trailing_updated'):
                 new_sl = pos['entry'] * 0.9980 # Entry - 0.20%
                 pos['sl'] = new_sl
                 pos['trailing_updated'] = True
                 logging.info(f"Trailing SL Updated to {new_sl}")
        elif side == 'sell':
             if current_price <= pos['entry'] * 0.9960 and not pos.get('trailing_updated'):
                 new_sl = pos['entry'] * 1.0020 # Entry + 0.20%
                 pos['sl'] = new_sl
                 pos['trailing_updated'] = True
                 logging.info(f"Trailing SL Updated to {new_sl}")

# Abstract Exchange Adapter for mocking/switching
class ExchangeInterface:
    def fetch_ticker(self, symbol):
        pass
    def create_order(self, symbol, type, side, amount):
        pass
