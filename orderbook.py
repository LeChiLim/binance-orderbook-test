import requests

# === Configuration === #
url = "https://fapi.binance.com/fapi/v1/depth?symbol=NEARUSDT&limit=10"
response = requests.get(url)
data = response.json()
print(data)