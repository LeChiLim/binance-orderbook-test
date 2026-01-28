import requests
import logging
from queue import Queue
import asyncio
import websockets
import json
import time

# === Configuration === #
TRADE_SYMBOL = "btcusdt"
LEVELS = 500
REST_URL = f"https://fapi.binance.com/fapi/v1/depth?symbol={TRADE_SYMBOL}&limit={LEVELS}"
WS_URL = f"wss://fstream.binance.com/ws/{TRADE_SYMBOL}@depth@100ms"


logging.basicConfig(level=logging.INFO)

logging.info(f"Order Book for {TRADE_SYMBOL}:")




# ===== WebSocket Updates ====== #

#FIFO Queue
updates_buffer = Queue(maxsize=10000)

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

    def initialize_order_book(self):
        data = get_orderbook_rest(self.symbol, self.levels)
        print(data)
        for bid in data['bids']:
            price, qty = bid
            self.bids[price] = qty
        for ask in data['asks']:
            price, qty = ask
            self.asks[price] = qty

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

    def print_order_book(self):
        logging.info(f"Order Book for {self.symbol}:")
        for i in range(self.levels):
            bid_price = list(self.bids.keys())[i]
            bid_qty = self.bids[bid_price]
            ask_price = list(self.asks.keys())[i]
            ask_qty = self.asks[ask_price]
            logging.info(f"Level {i+1}: Bid: {bid_price} ({bid_qty}) | Ask: {ask_price} ({ask_qty})")

    #print price level of 1,5,10 + mid price + spreads
    def print_order_book_header(self):
        #PRINT_HEADER = ("{:<23} | {:<12} | {:<12} | {:<12} | {:<12} | {:<12} | {:<12}")
        print("{:<23} | {:<12} | {:<12} | {:<12} | {:<12} | {:<12} | {:<12}".format("EventTime", "Spread_L1", "Spread_L5", "Spread_L10", "Bid_L1", "Ask_L1", "Mid_L1"))
        
    def print_order_book_levels(self):
        # from the assesment
        #PRINT_ROW = ("{:<23} | {:<12.8f} | {:<12.8f} | {:<12.8f} | {:<12.8f} | {:<12.8f} | {:<12.8f}")
        #things to print: Spread_L1, Spread_L5, Spread_L10, Bid_L1, Ask_L1, Mid_L1
        #print("{:<23} | {:<12} | {:<12} | {:<12} | {:<12} | {:<12} | {:<12}".format("EventTime", "Spread_L1", "Spread_L5", "Spread_L10", "Bid_L1", "Ask_L1", "Mid_L1"))
        
        levels_to_print = [1, 5, 10]
        mid_prices = [0.0] * max(levels_to_print)  
        spreads = [0.0] * max(levels_to_print)

        bid_prices = sorted([float(price) for price in self.bids.keys()], reverse=True)
        ask_prices = sorted([float(price) for price in self.asks.keys()])

    
        for l in levels_to_print:
            # in reality, levels start from 0 index
            l -= 1
            mid_price = (bid_prices[l] + ask_prices[l]) / 2
            mid_prices[l] = mid_price
            spread = (ask_prices[l] - bid_prices[l]) / mid_price
            spreads[l] = spread
        
        time_str = time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] 
        print("{:<23} | {:<12.8f} | {:<12.8f} | {:<12.8f} | {:<12.8f} | {:<12.8f} | {:<12.8f}".format(
            time_str,
            spreads[0], spreads[4], spreads[9],
            bid_prices[0], ask_prices[0], mid_prices[0]
        ))


if __name__ == "__main__":
    ob = OrderBook(TRADE_SYMBOL)
    ob.initialize_order_book()
    #ob.print_order_book()
    
    #start WS Listener
    loop = asyncio.get_event_loop()
    loop.create_task(listen_to_depth())
    loop.create_task(ob.get_updates())
    
    #print order book levels every 1 ms
    ob.print_order_book_header()
    while True:
        ob.print_order_book_levels()
        time.sleep(0.001)

    #start processing updates

