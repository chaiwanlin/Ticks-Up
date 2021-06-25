from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .instruments.stock import Stock
from wallstreet import Stock, Call, Put


# need to handle error at search and exit
def get_stock(ticker):
    #init driver and go to yahoofinance
    PATH = "/Users/chaiwanlin/Downloads/chromedriver"
    driver = webdriver.Chrome(PATH)
    driver.get("https://sg.finance.yahoo.com/")

    # search for ticker
    search = driver.find_element_by_id("yfin-usr-qry")
    search.send_keys(ticker + Keys.RETURN)

    price = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.quote-header-section span[class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"]'))
    )

    print(price.text)

    # driver.close()

    return Stock(ticker, price.text)

def binarySearch(data, val):
    highIndex = len(data) - 1
    lowIndex = 0
    while highIndex > lowIndex:
        index = (highIndex + lowIndex) // 2
        sub = data[index]
        if data[lowIndex] == val:
            return [lowIndex, lowIndex]
        elif sub == val:
            return [index, index]
        elif data[highIndex] == val:
            return [highIndex, highIndex]
        elif sub > val:
            if highIndex == index:
                return sorted([highIndex, lowIndex])
            highIndex = index
        else:
            if lowIndex == index:
                return sorted([highIndex, lowIndex])
            lowIndex = index
    return sorted([highIndex, lowIndex])

def get_options(ticker, target):
    s = Stock(ticker)
    price = s.price
    print(price)
    calls = Call(ticker)
    puts = Put(ticker)
    strikes = calls.strikes

    diff = price - target

    if diff < 0:
        p = strikes[binarySearch(strikes, price)[0]]
        tp = strikes[binarySearch(strikes, target)[0]]
        calls.set_strike(p)
        p1 = calls.price
        calls.set_strike(tp)
        tp1 = calls.price
        d = tp1 - p1
        max_profit = (-diff + d) * 100
        max_loss = d * 100
        breakeven = price - d
        debit_spread = \
            {'max_profit': max_profit, 'max_loss': max_loss, 'breakeven': breakeven}

        p = strikes[binarySearch(strikes, price)[0]]
        tp = strikes[binarySearch(strikes, target)[0]]
        puts.set_strike(p)
        p1 = puts.price
        puts.set_strike(tp)
        tp1 = puts.price
        d = tp1 - p1
        max_profit = d * 100
        max_loss = (p - tp + d) * 100
        breakeven = target - d
        credit_spread = \
            {'max_profit': max_profit, 'max_loss': max_loss, 'breakeven': breakeven}
    else:
        p = strikes[binarySearch(strikes, price)[0]]
        tp = strikes[binarySearch(strikes, target)[0]]
        puts.set_strike(p)
        p1 = puts.price
        puts.set_strike(tp)
        tp1 = puts.price
        d = tp1 - p1
        max_profit = (diff + d) * 100
        max_loss = d * 100
        breakeven = price + d
        debit_spread = \
            {'max_profit': max_profit, 'max_loss': max_loss, 'breakeven': breakeven}

        p = strikes[binarySearch(strikes, price)[0]]
        tp = strikes[binarySearch(strikes, target)[0]]
        calls.set_strike(p)
        p1 = calls.price
        calls.set_strike(tp)
        tp1 = calls.price
        d = tp1 - p1
        max_profit = d * 100
        max_loss = (-p + tp + d) * 100
        breakeven = target + d
        credit_spread = \
            {'max_profit': max_profit, 'max_loss': max_loss, 'breakeven': breakeven}

    return {'debit_spread': debit_spread, 'credit_spread': credit_spread}


