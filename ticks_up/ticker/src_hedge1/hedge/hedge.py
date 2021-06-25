from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ticks_up.users.src.hedge.instruments import Stock
from ticks_up.users.src.hedge.instruments import Option


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

def get_options(ticker, type):
    option_dict = {}
    option_list = []

    #init driver and go to yahoofinance
    PATH = "/Users/chaiwanlin/Downloads/chromedriver"

    driver = webdriver.Chrome(PATH)
    driver.get(f"https://sg.finance.yahoo.com/quote/{ticker}/options")

    # get call/put table
    css_selector = "table.%s > tbody > tr" % type
    # why doesnt f string work

    table = driver.find_elements_by_css_selector(css_selector)

    for row in table:
        fields = row.find_elements_by_tag_name('td')
        option_dict[fields[2].text] = fields[3].text
        option_list.append(Option(ticker, fields[3].text, ticker, type, fields[2].text))
        # print(fields[2].text)
        # print(fields[3].text)

    driver.close()
    return (option_dict, option_list)

get_options("GME", "puts")


