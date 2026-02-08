import requests
import logging
from queue import Queue
import asyncio
import websockets
import json
import time

# === Configuration === #
TRADE_SYMBOL = "nearusdt"
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
        logging.debug(f"Connected to {WS_URL}")
        
        while True:
            try:
                message = await ws.recv()
                data = json.loads(message)
                
                if 'e' in data and data['e'] == 'depthUpdate':
                    #logging.info(f"Depth Update:\n{json.dumps(data, indent=2)}")
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
        self.last_update_id = 0

    def initialize_order_book(self):
        data = get_orderbook_rest(self.symbol, self.levels)
        self.last_update_id = data['lastUpdateId']
        #print(data)
        for bid in data['bids']:
            price, qty = float(bid[0]), float(bid[1]) 
            if qty > 0:  
                self.bids[price] = qty
        for ask in data['asks']:
            price, qty = float(ask[0]), float(ask[1])
            if qty > 0:
                self.asks[price] = qty

    async def get_updates(self):
        while True:
            if not updates_buffer.empty():
                update = updates_buffer.get()
                # Process the update (e.g., apply to local order book)
                #logging.info(f"Processing update: {json.dumps(update, indent=2)}")
                self.set_update(update)
            await asyncio.sleep(0.01)  # Small delay to prevent busy waiting

    def set_update(self, update_data):
        #incorporate the update into the order book
        #future: add ID checks
        for price_str, qty_str in update_data['b']:
            price, qty = float(price_str), float(qty_str)
            if qty == 0:
                self.bids.pop(price, None) 
            else:
                self.bids[price] = qty
                
        for price_str, qty_str in update_data['a']:
            price, qty = float(price_str), float(qty_str)
            if qty == 0:
                self.asks.pop(price, None) 
            else:
                self.asks[price] = qty
        #after every update, print the order book levels
        self.print_order_book_levels()

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
        
        utc8_time = time.strftime("%Y-%m-%d %H:%M:%S.%f", time.gmtime(time.time() + 8*3600))[:-3]
        print("{:<23} | {:<12.8f} | {:<12.8f} | {:<12.8f} | {:<12.8f} | {:<12.8f} | {:<12.8f}".format(
            utc8_time,
            spreads[0], spreads[4], spreads[9],
            bid_prices[0], ask_prices[0], mid_prices[0]
        ))


async def main():
    ob = OrderBook(TRADE_SYMBOL)
    ob.initialize_order_book()

    # start WS listener and updater
    listener_task = asyncio.create_task(listen_to_depth())
    updates_task = asyncio.create_task(ob.get_updates())

    ob.print_order_book_header()

    # keep running; printing happens inside set_update()
    try:
        await asyncio.gather(listener_task, updates_task)
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    asyncio.run(main())
