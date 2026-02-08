# theoquant-orderbook
TheoQuant orderbook assessment 2026

Programmed on WS- Ubuntu 24.02

Create venv, install from requirements.txt

# HOW TO USE
python3 orderbook.py

SEPERATED INTO
- orderbook class
- REST API functions
- WSS update functions

FUTURE IMPROVMENET 
- update into seperate files and run async

PLEASE IGNORE LISTENER.py

# NOTES FROM BEFORE

Things to do:
1. Create local orderbook
2. Use REST once to initialize
3. Use diff stream to update

listener.py:
How to get and what to expect from WS updates
https://www.binance.com/en/academy/articles/local-order-book-tutorial-part-1-depth-stream-and-event-buffering


orderbook.py:
How to get orderbook by REST API
https://stackoverflow.com/questions/69800961/how-to-get-the-order-book-list-with-binance-api


#How to maintain an orderbook according to Binance
https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/How-to-manage-a-local-order-book-correctly


# NOTES POST-ASSESSMENT
I've added the following based on the recommended guide above
- Drop any event where u is < lastUpdateId in the snapshot.
- The first processed event should have U <= ``lastUpdateId AND u >= ``lastUpdateId
- While listening to the stream, each new event's pu should be equal to the previous event's u, otherwise initialize the process from step 3.ß
- If the quantity is 0, remove the price level.


# Other improvements
- Do not sort bids / ask lists every print. Cache the top 10 every WSS update. 
- Use a sorted dict so that its faster and gives best bid/ask in O(1) time
- "SortedDict: 5-10x slower than raw dict but perfect for order book (need sorted access). Cache layer makes top-of-book O(1).** Alternative: Cython/raw arrays for 10x more speed if Python bottleneck confirmed."

