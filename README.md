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