#wss://fstream.binance.com/ws/<symbol>@depth@100ms

#create a websocket client that listens to depth updates for a given symbol on Binance Futures

import asyncio
import websockets
import json
#from binance_sdk_spot.spot import Spot, ConfigurationWebSocketStreams, Spot, SPOT_WS_STREAMS_PROD_URL
import logging

#== CONFIGURATION ==#
TRADE_SYMBOL = "nearusdt"
WS_URL = f"wss://fstream.binance.com/ws/{TRADE_SYMBOL}@depth10@100ms"

logging.basicConfig(level=logging.INFO)

async def listen_to_depth():
    async with websockets.connect(WS_URL) as ws:
        logging.info(f"Connected to {WS_URL}")
        
        while True:
            try:
                message = await ws.recv()
                data = json.loads(message)
                
                if 'e' in data and data['e'] == 'depthUpdate':
                    logging.info(f"Depth Update:\n{json.dumps(data, indent=2)}")
                    # Apply to your local book here
                else:
                    logging.info(f"Other message: {data}")
                    
            except Exception as e:
                logging.error(f"Error in loop: {e}")
                break

asyncio.run(listen_to_depth())