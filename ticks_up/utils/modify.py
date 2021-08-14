# value error for convertability
def string_to_float(string):
    if type(string) is float or type(string) is int:
        return string
    elif string == "Strong Sell":
        return -2.0
    elif string == "Sell":
        return -1.0
    elif string == "Neutral":
        return 0.0
    elif string == "Buy":
        return 1.0
    elif string == "Strong Buy":
        return 2.0
    elif "%" in string:
        string = string.replace("−", "-")
        return float(string.strip("%"))
    elif "K" in string:
        string = string.replace("K", "")
        return float(string) * 1000
    elif "M" in string:
        string = string.replace("M", "")
        return float(string) * 1000000
    elif "B" in string:
        string = string.replace("B", "")
        return float(string) * 1000000000
    elif "T" in string:
        string = string.replace("T", "")
        return float(string) * 1000000000000

def parse_ticker_trading_view(string):
    if "^" in string:
        string = string.strip("^")
    if "." in string: 
        return string.split(".", 1)[0]
    else:
        return string

def parse_industry(string):
    return string.replace(" & ", "-").replace(": ", "-").replace(" ", "-").replace("/", "-")



