from option import Call, CallOption, Put, PutOption
from stock import Stock
import json

stock = Stock("AAPL")

stock_info = {
    "ticker" : stock.ticker,
    "price" : stock.price,
    "exchange" : stock.exchange
}

call = Call("AAPL")

call_150 = call.get_option_for_strike(150)

call_info = {
    "closest expiry" : call.get_expiry(),
    "next_expiry" : call.get_nearest_day(7).get_expiry(),
    "strike" : call_150.strike,
    "premium" : call_150.price,
    "open_interest" : call_150.interest,
    "volume" : call_150.volume,
    "bid" : call_150.bid,
    "ask" : call_150.ask,
    "delta" : call_150.delta()

}


put = Put("AAPL")
put_150 = put.get_option_for_strike(150)

put_info = {
    "closest expiry" : put.get_expiry(),
    "next_expiry" : put.get_nearest_day(7).get_expiry(),
    "strike" : put_150.strike,
    "premium" : put_150.price,
    "open_interest" : put_150.interest,
    "volume" : put_150.volume,
    "bid" : put_150.bid,
    "ask" : put_150.ask,
    "delta" : put_150.delta()

}

data = {
    "stock data" : stock_info,
    "call data" : call_info,
    "put data" : put_info

}

with open('instrument_data.json', 'w') as file:
    json.dump(data, file, indent=4)