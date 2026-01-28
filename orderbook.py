import requests
import logging

# === Configuration === #
SYMBOL = "nearusdt"
LEVELS = 10
URL = f"https://fapi.binance.com/fapi/v1/depth?symbol={SYMBOL}&limit=10"
response = requests.get(URL)
data = response.json()
print(data)

logging.basicConfig(level=logging.INFO)

logging.info(f"Order Book for {SYMBOL}:")

def get_orderbook_rest(symbol, limit=10):
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


if __name__ == "__main__":
    ob = OrderBook(SYMBOL)
    ob.initialize_order_book(data)
    ob.print_order_book()