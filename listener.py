#wss://fstream.binance.com/ws/<symbol>@depth@100ms

#create a websocket client that listens to depth updates for a given symbol on Binance Futures

import asyncio
import websockets
import json
from binance_sdk_spot.spot import Spot

#== CONFIGURATION ==#
URL = "wss://fstream.binance.com/ws/<symbol>@depth@100ms"

def get_all_symbols():
    
    client = Spot()

    response = client.rest_api.exchange_info()
    data = response.data()

    usdt_symbols = [symbol for symbol in data.symbols if symbol.quote_asset == "USDT"]
    usdt_trading_symbols = [symbol for symbol in usdt_symbols if symbol.status == "TRADING"]
    return usdt_trading_symbols

def get_url(symbol):
    return URL.replace("<symbol>", symbol)

