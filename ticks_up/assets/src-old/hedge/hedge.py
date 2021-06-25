import time 
import json
import urllib.request

url = "https://query2.finance.yahoo.com/v7/finance/options/AAPL"

response = urllib.request.urlopen(url)

data = json.loads(response.read())

print(data["optionChain"]["result"][1])