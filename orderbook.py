import requests
import logging
from queue import Queue
import asyncio
import websockets
import json

# === Configuration === #
TRADE_SYMBOL = "nearusdt"
LEVELS = 500
REST_URL = f"https://fapi.binance.com/fapi/v1/depth?symbol={TRADE_SYMBOL}&limit=10"
WS_URL = f"wss://fstream.binance.com/ws/{TRADE_SYMBOL}@depth@100ms"


logging.basicConfig(level=logging.INFO)

logging.info(f"Order Book for {TRADE_SYMBOL}:")




# ===== WebSocket Updates ====== #

#FIFO Queue
updates_buffer = Queue()

async def listen_to_depth():
    async with websockets.connect(WS_URL) as ws:
        logging.info(f"Connected to {WS_URL}")
        
        while True:
            try:
                message = await ws.recv()
                data = json.loads(message)
                
                if 'e' in data and data['e'] == 'depthUpdate':
                    logging.info(f"Depth Update:\n{json.dumps(data, indent=2)}")
                    # put into updates buffer
                    updates_buffer.put(data)
                else:
                    logging.info(f"Other message: {data}")
                    
            except Exception as e:
                logging.error(f"Error in loop: {e}")
                break



# ====== REST API ====== #
def get_orderbook_rest(symbol, limit):
    url = f"https://fapi.binance.com/fapi/v1/depth?symbol={symbol}&limit={limit}"
    response = requests.get(url)
    return response.json()

class OrderBook:
    def __init__(self, symbol):
        self.symbol = symbol
        self.levels = LEVELS
        self.bids = {}  # price: quantity
        self.asks = {}  # price: quantity

    def initialize_order_book(self, data):
        data = get_orderbook_rest(self.symbol, self.levels)
        print(data)
        for bid in data['bids']:
            price, qty = bid
            self.bids[price] = qty
        for ask in data['asks']:
            price, qty = ask
            self.asks[price] = qty

    def print_order_book(self):
        logging.info(f"Order Book for {self.symbol}:")
        for i in range(self.levels):
            bid_price = list(self.bids.keys())[i]
            bid_qty = self.bids[bid_price]
            ask_price = list(self.asks.keys())[i]
            ask_qty = self.asks[ask_price]
            logging.info(f"Level {i+1}: Bid: {bid_price} ({bid_qty}) | Ask: {ask_price} ({ask_qty})")

    async def get_updates(self):
        while True:
            if not updates_buffer.empty():
                update = updates_buffer.get()
                # Process the update (e.g., apply to local order book)
                logging.info(f"Processing update: {json.dumps(update, indent=2)}")
                self.set_update(update)
            await asyncio.sleep(0.01)  # Small delay to prevent busy waiting

    def set_update(self, update_data):
        for bid in update_data['bids']:
            price, qty = bid
            self.bids[price] = qty
        for ask in update_data['asks']:
            price, qty = ask
            self.asks[price] = qty

if __name__ == "__main__":
    ob = OrderBook(TRADE_SYMBOL)
    ob.initialize_order_book(data)
    ob.print_order_book()