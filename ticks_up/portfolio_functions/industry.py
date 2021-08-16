from bs4 import BeautifulSoup
from urllib.error import HTTPError
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from .industry_constants import *
from .portfolio_constants import PATH
from .data import Data
from utils.modify import *
import urllib.request as rq
import os
import json
import time


def get_driver():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(PATH, options=chrome_options)
    return driver
    
class Industry:

    def __init__(self, ticker):
        self.ticker = ticker.upper()
        # try:
        #     f = open('data.json', "r")
        #     data = json.load(f)

        #     self.sector = data[0].text
        #     self.industry = data[1].text
        # except KeyError:
        #     pass
        try: 
            request = rq.urlopen(f"https://www.tradingview.com/symbols/{ticker}/")
            soup = BeautifulSoup(request.read(), 'html.parser')

            lst = soup.findAll("span", class_ = "tv-widget-description__value") 

            self.sector = lst[0].text
            self.industry = lst[1].text
        except HTTPError:
            raise LookupError("hehexd invalid ticker!")

    # category: string choices
    # indicator: string choices
    @staticmethod
    def get_stocks_same_sector(sector, category, indicator):
        sector = sector.lower().replace(" ", "-")
        driver = get_driver()
        driver.get(f"https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/{sector}/")

        if category != "Overview":

            driver.find_element_by_xpath(f'//div[text()="{category}"]').click()

            # WebDriverWait(driver, 20).until(
            #     EC.presence_of_element_located((By.XPATH, f'//div[text()="{category}"]'))
            # ).click()

            sleep(1)
                
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'th[data-field="{indicator[0]}"]'))
        ).click()

        sleep(1)

        while(True):
            try: 
                driver.find_element_by_class_name("tv-load-more__btn").click()
                sleep(1)
            except ElementNotInteractableException:
                break

        body = driver.find_element_by_css_selector('div[class="tv-screener__content-pane"]') \
            .find_element_by_css_selector('tbody[class="tv-data-table__tbody"]').find_elements_by_xpath("./tr")
                
        result = []
        index = indicator[1]

        for tr in body:
            tds = tr.find_elements_by_xpath("./td")
            
            ticker = tds[0].find_element_by_css_selector('a[class="tv-screener__symbol apply-common-tooltip"]').text
            value = tds[index].text

            data = {
                "Ticker" : ticker,
                indicator : value
            }

            result.append(Data(value, data))
       
        return result

    def get_k_closest_same_sector(self, k, category, indicator):
        sector = self.sector.lower().replace(" ", "-")
        driver = get_driver()
        driver.get(f"https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/{sector}/")

        if category != "Overview":

            driver.find_element_by_xpath(f'//div[text()="{category}"]').click()

            # WebDriverWait(driver, 20).until(
            #     EC.presence_of_element_located((By.XPATH, f'//div[text()="{category}"]'))
            # ).click()

            sleep(1)
                
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'th[data-field="{indicator[0]}"]'))
        ).click()

        sleep(1)

        while(True):
            try: 
                driver.find_element_by_class_name("tv-load-more__btn").click()
                sleep(1)
            except ElementNotInteractableException:
                break

        sleep(1)

        body = driver.find_element_by_css_selector('div[class="tv-screener__content-pane"]') \
            .find_element_by_css_selector('tbody[class="tv-data-table__tbody"]').find_elements_by_xpath("./tr")

        result = []
        ticker_index = 0
        ticker_val = 0
        count = 0
        index = indicator[1]

    
        for tr in body:
            tds = tr.find_elements_by_xpath("./td")

            ticker = tds[0].find_element_by_css_selector('a[class="tv-screener__symbol apply-common-tooltip"]').text
            value = tds[index].text

            data = {
                "Ticker" : ticker,
                indicator : value
            }

            if ticker == self.ticker:
                ticker_index = count
                ticker_val = value

            result.append(Data(value, data))
            count += 1
        
        length = count - 1
        lo, hi = ticker_index - 1, ticker_index + 1
        lst = []
        true_val = string_to_float(ticker_val)


        while k > 0 and lo >=0 and hi <= length:
            true_lo_val = string_to_float(result[lo].value)
            true_hi_val = string_to_float(result[hi].value)

            if (true_val - true_lo_val) <= (true_hi_val - true_val):
                lst.append(result[lo])
                lo -= 1
                k -= 1
            else:
                lst.append(result[hi])
                hi += 1
                k -= 1

        # no ele on right
        while k > 0 and lo >= 0 :
            lst.append(result[lo])
            lo -= 1
            k -= 1
 
        #no ele on left
        while k > 0 and hi <= length :
            lst.append(result[hi])
            hi += 1
            k -= 1

        return lst

    @staticmethod
    def get_stocks_same_industry(industry, category, indicator):
        industry = parse_industry(industry.lower())
        driver = get_driver()
        driver.get(f"https://www.tradingview.com/markets/stocks-usa/sectorandindustry-industry/{industry}/")

        if category != "Overview":

            driver.find_element_by_xpath(f'//div[text()="{category}"]').click()

            # WebDriverWait(driver, 20).until(
            #     EC.presence_of_element_located((By.XPATH, f'//div[text()="{category}"]'))
            # ).click()

            sleep(1)
                
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'th[data-field="{indicator[0]}"]'))
        ).click()

        sleep(1)

        while(True):
            try: 
                driver.find_element_by_class_name("tv-load-more__btn").click()
                sleep(1)
            except ElementNotInteractableException:
                break

        body = driver.find_element_by_css_selector('div[class="tv-screener__content-pane"]') \
            .find_element_by_css_selector('tbody[class="tv-data-table__tbody"]').find_elements_by_xpath("./tr")

        result = []
        index = indicator[1]

        for tr in body:
            tds = tr.find_elements_by_xpath("./td")
            
            ticker = tds[0].find_element_by_css_selector('a[class="tv-screener__symbol apply-common-tooltip"]').text
            value = tds[index].text

            data = {
                "Ticker" : ticker,
                indicator : value
            }

            result.append(Data(value, data))
       
        return result

    def get_k_closest_same_industry(self, k, category, indicator):
        industry = parse_industry(self.industry.lower())
        driver = get_driver()
        driver.get(f"https://www.tradingview.com/markets/stocks-usa/sectorandindustry-industry/{industry}/")

        if category != "Overview":

            driver.find_element_by_xpath(f'//div[text()="{category}"]').click()

            # WebDriverWait(driver, 20).until(
            #     EC.presence_of_element_located((By.XPATH, f'//div[text()="{category}"]'))
            # ).click()

            sleep(1)
                
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'th[data-field="{indicator[0]}"]'))
        ).click()

        sleep(1)

        while(True):
            try: 
                driver.find_element_by_class_name("tv-load-more__btn").click()
                sleep(1)
            except ElementNotInteractableException:
                break

        sleep(1)

        body = driver.find_element_by_css_selector('div[class="tv-screener__content-pane"]') \
            .find_element_by_css_selector('tbody[class="tv-data-table__tbody"]').find_elements_by_xpath("./tr")

        result = []
        ticker_index = 0
        ticker_val = 0
        count = 0
        index = indicator[1]

        for tr in body:
            tds = tr.find_elements_by_xpath("./td")

            ticker = tds[0].find_element_by_css_selector('a[class="tv-screener__symbol apply-common-tooltip"]').text
            # print(ticker)
            value = tds[index].text

            data = {
                "Ticker" : ticker,
                indicator : value
            }

            if ticker == self.ticker:
                ticker_index = count
                ticker_val = value

            result.append(Data(value, data))
            count += 1
        
        length = count - 1
        lo, hi = ticker_index - 1, ticker_index + 1
        lst = []
        true_val = string_to_float(ticker_val)


        while k > 0 and lo >=0 and hi <= length:
            true_lo_val = string_to_float(result[lo].value)
            true_hi_val = string_to_float(result[hi].value)

            if (true_val - true_lo_val) <= (true_hi_val - true_val):
                lst.append(result[lo])
                lo -= 1
                k -= 1
            else:
                lst.append(result[hi])
                hi += 1
                k -= 1

        # no ele on right
        while k > 0 and lo >= 0 :
            lst.append(result[lo])
            lo -= 1
            k -= 1
 
        #no ele on left
        while k > 0 and hi <= length :
            lst.append(result[hi])
            hi += 1
            k -= 1

        return lst

    def sector_list():
        request = rq.urlopen("https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/")
        soup = BeautifulSoup(request.read(), 'html.parser')

        body = soup.find("tbody", class_ = "tv-data-table__tbody") 
        body = body.findAll("tr") 
        result = []
        

        for tr in body:
            sector = tr.find('a', class_ = "tv-screener__symbol").text
            
            result.append(sector)


        return result

    def industry_list():
        request = rq.urlopen("https://www.tradingview.com/markets/stocks-usa/sectorandindustry-industry/")
        soup = BeautifulSoup(request.read(), 'html.parser')

        body = soup.find("tbody", class_ = "tv-data-table__tbody") 
        body = body.findAll("tr") 
        result = []
        
        for tr in body:
            tds = tr.findAll('td')
            industry = tds[0].find('a', class_ = "tv-screener__symbol").text
            sector = tds[5].find('span', class_ = "tv-screener__symbol--secondary").text
            result.append((sector, industry))

        return result

    def industry_list_sector(sector):
        sector = sector.lower().replace(" ", "-")
        request = rq.urlopen(f"https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/{sector}/industries/")
        soup = BeautifulSoup(request.read(), 'html.parser')

        body = soup.find("tbody", class_ = "tv-data-table__tbody") 
        body = body.findAll("tr") 
        result = []
        
        for tr in body:
            sector = tr.find('a', class_ = "tv-screener__symbol").text
            result.append(sector)

        return result

    def ticker_dict_by_industry():
        driver = get_driver()
        lst = Industry.industry_list()
        result = {}

        for industry in lst:
            industry_link = parse_industry(industry[1].lower())
            driver.get(f"https://www.tradingview.com/markets/stocks-usa/sectorandindustry-industry/{industry_link}/")

            while(True):
                try: 
                    driver.find_element_by_class_name("tv-load-more__btn").click()
                    sleep(1)
                except ElementNotInteractableException:
                    break

            sleep(1)

            body = driver.find_element_by_css_selector('div[class="tv-screener__content-pane"]') \
                .find_element_by_css_selector('tbody[class="tv-data-table__tbody"]').find_elements_by_xpath("./tr")

            for tr in body:
                tds = tr.find_elements_by_xpath("./td")
                ticker = tds[0].find_element_by_css_selector('a[class="tv-screener__symbol apply-common-tooltip"]').text

                result[ticker] = {
                    "Sector" : industry[0],
                    "Industry" : industry[1]    
                }

        with open('./industry.json', 'w') as file:
            json.dump(result, file, indent=4)

    def dict_to_django():
        f = open('./industry.json')
        data = json.load(f)

        new_data = []
        count = 1

        for key in data:
            new_data.append(
                {
                    "model": "ticks_up.ticker",
                    "pk": count,
                    "fields": {
                        "name"
                        "sector": data[key]["Sector"],
                        "industry": data[key]["Industry"]
                    }
                }
            )

            

        with open('./industry_django.json', 'w') as file:
            json.dump(new_data, file, indent=4)

# result = Industry("AAPL")
# result = Industry("AAPL").get_k_closest_same_sector(5, PERFORMANCE, FOUR_H_CHG)
# for i in result:
#     print(i.data)
# Industry.get_stocks_same_sector("energy Minerals", "Overview", MKT_CAP)
# Industry.get_stocks_same_industry("aerospace defense","","")
# print(Industry("pltr").sector)

# print(Industry.industry_list())

# Industry.ticker_dict_by_industry()

Industry.dict_to_django()







