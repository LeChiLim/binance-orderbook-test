#wss://fstream.binance.com/ws/<symbol>@depth@100ms

#create a websocket client that listens to depth updates for a given symbol on Binance Futures

import asyncio
import websockets
import json
from binance_sdk_spot.spot import Spot

#== CONFIGURATION ==#
TRADE_SYMBOL = "NEARUSDT"
URL = f"wss://fstream.binance.com/ws/{TRADE_SYMBOL}@depth@100ms"


client = Spot()

response = client.rest_api.depth(
   symbol=TRADE_SYMBOL,
   limit=5
)
print(response.data())


