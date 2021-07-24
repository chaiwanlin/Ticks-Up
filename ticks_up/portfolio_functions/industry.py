from os import PathLike
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ticks_up.portfolio_functions.portfolio_constants import PATH, MKT_CAP
from ticks_up.portfolio_functions.data import Data

class Industry:

    def __init__(self, ticker):
        # PATH = "C:\Program Files (x86)/chromedriver.exe"
        self.ticker = ticker
        driver = webdriver.Chrome(PATH)
        driver.get("https://www.tradingview.com/markets/stocks-usa/market-movers-large-cap/") 

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
        driver = webdriver.Chrome(PATH)
        driver.get(f"https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/{sector}/")

        if category != "Overview":

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, f'//div[text()="{category}"]'))
            ).click()

            sleep(1)
                
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'th[data-field="{indicator}"]'))
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
                indicator : value
            }

            result.append(Data(value, data))
       
        return result

    def get_k_closest_same_sector(self, k, category, indicator):
        sector = self.sector.lower().replace(" ", "-")
        driver = webdriver.Chrome(PATH)
        driver.get(f"https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/{sector}/")

        if category != "Overview":

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, f'//div[text()="{category}"]'))
            ).click()

            sleep(1)
                
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'th[data-field="{indicator}"]'))
        ).click()

        sleep(1)

        body = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody[class="tv-data-table__tbody"]'))
        )

        body = body.find_elements_by_xpath("./tr")
        result = []
        index = 0
        count = 0
        val = 0

        for tr in body:
            tds = tr.find_elements_by_xpath("./td")

            ticker = tds[6].text
            value = tds[0].find_element_by_xpath(".//div/a").text

            data = {
                "Ticker" : ticker,
                indicator : value
            }

            if ticker == self.ticker:
                index = count
                val = value

            result.append(Data(value, data))
            count += 1

            print(tds[0].find_element_by_xpath(".//div/a").text)
            print(tds[6].text)
        
        len = count - 1
        lo, hi = index - 1, index + 1
        lst = []

        while k > 0 and lo >=0 and hi <= len:
            if val - result[lo].value <= result[hi] - val:
                lst.append(result[lo])
                lo -= 1
            else:
                lst.append(result[hi])
                hi += 1
        
        return lst

    def get_stocks_same_industry(industry, category, indicator):
        industry = industry.lower().replace(" ", "-")
        driver = webdriver.Chrome(PATH)
        driver.get(f"https://www.tradingview.com/markets/stocks-usa/sectorandindustry-industry/{industry}/")

        if category != "Overview":

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, f'//div[text()="{category}"]'))
            ).click()

            sleep(1)
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'th[data-field="{indicator}"]'))
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
                indicator : value
            }

            result.append(Data(value, data))

            print(tds[0].find_element_by_xpath(".//div/a").text)
            print(tds[6].text)
        
        return result

    def get_k_closest_same_industry(self, k, category, indicator):
        industry = self.industry.lower().replace(" ", "-")
        driver = webdriver.Chrome(PATH)
        driver.get(f"https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/{industry}/")

        if category != "Overview":

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, f'//div[text()="{category}"]'))
            ).click()

            sleep(1)
                
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'th[data-field="{indicator}"]'))
        ).click()

        sleep(1)

        body = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody[class="tv-data-table__tbody"]'))
        )

        body = body.find_elements_by_xpath("./tr")
        result = []
        index = 0
        count = 0
        val = 0

        for tr in body:
            tds = tr.find_elements_by_xpath("./td")

            ticker = tds[6].text
            value = tds[0].find_element_by_xpath(".//div/a").text

            data = {
                "Ticker" : ticker,
                indicator : value
            }

            if ticker == self.ticker:
                index = count
                val = value

            result.append(Data(value, data))
            count += 1

            print(tds[0].find_element_by_xpath(".//div/a").text)
            print(tds[6].text)
        
        len = count - 1
        lo, hi = index - 1, index + 1
        lst = []

        while k > 0 and lo >=0 and hi <= len:
            if val - result[lo].value <= result[hi] - val:
                lst.append(result[lo])
                lo -= 1
            else:
                lst.append(result[hi])
                hi += 1
        
        return lst

# Industry("AAPL")

# Industry.get_stocks_same_sector("energy Minerals", "Overview", MKT_CAP)
# Industry.get_stocks_same_industry("aerospace defense","","")

