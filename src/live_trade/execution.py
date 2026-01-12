import ccxt
import os
import logging

class BinanceAdapter:
    def __init__(self, api_key=None, secret=None, sand_box=False):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
        })
        if sand_box:
            self.exchange.set_sandbox_mode(True)
            
    def fetch_ticker(self, symbol):
        return self.exchange.fetch_ticker(symbol)
        
    def create_order(self, symbol, type, side, amount):
        try:
            return self.exchange.create_order(symbol, type, side, amount)
        except Exception as e:
            logging.error(f"Order Failed: {e}")
            return None

class PaperTradingAdapter:
    """
    Simulates an exchange. Stores orders in memory.
    Uses real market data for price, but executes locally.
    """
    def __init__(self, real_exchange_adapter):
        self.real_exchange = real_exchange_adapter # Use for price
        self.orders = []
        
    def fetch_ticker(self, symbol):
        # Pass through to real data
        return self.real_exchange.fetch_ticker(symbol)
        
    def create_order(self, symbol, type, side, amount):
        # Fake execution
        ticker = self.fetch_ticker(symbol)
        price = ticker['last']
        
        order = {
            'symbol': symbol,
            'type': type,
            'side': side,
            'amount': amount,
            'price': price,
            'status': 'closed', # Market orders fill instantly
            'id': f"paper_{len(self.orders)+1}"
        }
        self.orders.append(order)
        print(f"[PAPER TRADE] {side.upper()} {amount} {symbol} @ {price}")
        return order
