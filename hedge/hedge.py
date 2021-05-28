from typing import Text
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
# from instruments.instrument import Instrument
# from instruments.stock import Stock
import time


# need to handle error at search and exit
def get_stock(ticker):
    #init driver and go to yahoofinance
    PATH = "C:\Program Files (x86)/chromedriver.exe"
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

    # return Stock(ticker, price, ticker)

def get_option(ticker):
    #init driver and go to yahoofinance
    PATH = "C:\Program Files (x86)/chromedriver.exe"
    driver = webdriver.Chrome(PATH)
    driver.get("https://sg.finance.yahoo.com/")

    # search for ticker
    search = driver.find_element_by_id("yfin-usr-qry")
    search.send_keys(ticker + Keys.RETURN)

    #wait and click on options
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Options"))
    ).click()

    # calls
    table = driver.find_elements_by_css_selector("table.puts > tbody > tr")

    for row in table:
        fields = row.find_elements_by_tag_name('td')
        print(fields[2].text)
        print(fields[3].text)

    #puts 
    table = driver.find_elements_by_css_selector("table.puts > tbody > tr")

    for row in table:
        fields = row.find_elements_by_tag_name('td')
        print(fields[2].text)
        print(fields[3].text)


    # return Stock(ticker, 5, ticker)

get_option("AAPL")
