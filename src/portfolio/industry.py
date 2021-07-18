  
from os import PathLike
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from portfolio.portfolio_constants import PATH
from portfolio.data import Data

class Industry:

    def __init__(self, ticker):
        # PATH = "C:\Program Files (x86)/chromedriver.exe"
        driver = webdriver.Chrome(PATH)
        # driver.get("https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/") 
        driver.get("https://www.tradingview.com/markets/stocks-usa/market-movers-large-cap/") 
        
        # search for ticker
        # search = driver.find_element_by_class_name("tv-screener-table__search-input js-search-input")
        # search = driver.find_element_by_css_selector('div.tv-screener-table__search-query js-search-query tv-screener-table__search-query--without-description =input.tv-screener-table__search-input js-search-input')
        # search.send_keys(ticker + Keys.RETURN)

        search = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="tv-screener-table__search-query js-search-query tv-screener-table__search-query--without-description"] input[class="tv-screener-table__search-input js-search-input"]'))
        )
        search.send_keys(ticker + Keys.RETURN)

        search = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[class="tv-screener__symbol apply-common-tooltip"]'))
        ).click()

        lst = driver.find_elements_by_class_name("tv-widget-description__value")
        self.sector = lst[0].text
        self.industry = lst[1].text
    
    def get_industry(self):
        return self.industry

    def get_sector(self):
        return self.sector    

    def get_stocks_same_sector(sector, category, indicator):
        sector = sector.lower().replace(" ", "-")
        print(sector)
        driver = webdriver.Chrome(PATH)
        driver.get(f"https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/{sector}/")

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[text()="Performance"]'))
        ).click()
        
        sleep(1)
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'th[data-field="market_cap_basic"]'))
        ).click()

        sleep(1)

        body = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody[class="tv-data-table__tbody"]'))
        )

        body = body.find_elements_by_xpath("./tr")
        result = []

        for tr in body:
            tds = tr.find_elements_by_xpath("./td")

            value = tds[0].find_element_by_xpath(".//div/a").text
            data = {
                "Ticker" : tds[6].text,
                "Market Cap" : value
            }

            result.append(Data(value, data))

            print(tds[0].find_element_by_xpath(".//div/a").text)
            print(tds[6].text)
        
        return result

    def get_stocks_same_industry(industry, category, indicator):
        industry = industry.lower().replace(" ", "-")
        print(industry)
        driver = webdriver.Chrome(PATH)
        driver.get(f"https://www.tradingview.com/markets/stocks-usa/sectorandindustry-industry/{industry}/")

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[text()="Performance"]'))
        ).click()
        
        sleep(1)
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'th[data-field="market_cap_basic"]'))
        ).click()

        sleep(1)

        body = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody[class="tv-data-table__tbody"]'))
        )

        body = body.find_elements_by_xpath("./tr")
        result = []

        for tr in body:
            tds = tr.find_elements_by_xpath("./td")

            value = tds[0].find_element_by_xpath(".//div/a").text
            data = {
                "Ticker" : tds[6].text,
                "Market Cap" : value
            }

            result.append(Data(value, data))

            print(tds[0].find_element_by_xpath(".//div/a").text)
            print(tds[6].text)
        
        return result


# Industry("AAPL")
Industry.get_stocks_same_sector("energy Minerals")
# Industry.get_stocks_same_industry("aerospace defense")