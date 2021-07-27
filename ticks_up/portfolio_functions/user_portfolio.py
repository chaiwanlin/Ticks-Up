class User_Portfolio:

    def __init__(self, tickers, cash, type, sectors):
        self.tickers = tickers
        self.type = type
        self.sectors = sectors

        self.cash = cash

        self.capital_invested = 0
        self.capital_collateral = 0
        self.value = 0
        self.cost_to_cover = 0
        self.short_PL = 0     

        for e in sectors:
            self.capital_invested += e.capital_invested
            self.capital_collateral += e.capital_collateral
            self.value += e.value
            self.cost_to_cover += e.cost_to_cover
            self.short_PL += e.short_PL
        
        self.total_value = self.value + self.capital_collateral

    # def add_position(self, instrument, sector, industry, ticker):
    #     found = False

    #     for e in self.sectors:
    #         if e.id == sector:
    #             e.add_position(instrument, industry, ticker)
    #             found = True

    #     if not found:
    #         tickers = [instrument]
    #         industry = Industry_Portfolio(industry, tickers, type)
    #         sector = Sector_Portfolio(sector, type, industry, tickers)
    #         self.sectors.append(sector)    
    
    def breakdown_by_ticker(self):
        dic = {}
        for e in self.tickers:
            dic[e.ticker] = e.value / self.total_value

        return dic
    
    def average_ticker_weight(self):
        return 1 / len(self.tickers) 

    def breakdown_by_sectors(self):
        dic = {}
        for e in self.sectors:
            dic[e.id] = e.total_value / self.total_value

        return dic

    def average_sector_weight(self):
        return 1 / len(self.sectors) 
 
class Sector_Portfolio:
    def __init__(self, id, industries, tickers, type):
        self.id = id
        self.tickers = tickers
        self.type = type
        self.industries = industries

        self.capital_invested = 0
        self.capital_collateral = 0
        self.value = 0
        self.cost_to_cover = 0
        self.short_PL = 0     

        for e in industries:
            self.capital_invested += e.capital_invested
            self.capital_collateral += e.capital_collateral
            self.value += e.value
            self.cost_to_cover += e.cost_to_cover
            self.short_PL += e.short_PL
        
        self.total_value = self.value + self.capital_collateral

    def breakdown_by_ticker(self):
        dic = {}
        for e in self.tickers:
            dic[e.ticker] = e.value / self.total_value

        return dic
    
    def average_ticker_weight(self):
        return 1 / len(self.tickers) 
    
    def breakdown_by_industry(self):
        dic = {}
        for e in self.industries:
            dic[e.id] = e.total_value / self.total_value

        return dic

    def average_industry_weight(self):
        return 1 / len(self.industries) 

class Industry_Portfolio:
    def __init__(self, id, tickers, type):
        self.id = id
        self.tickers = tickers
        self.type = type

        self.capital_invested = 0
        self.capital_collateral = 0
        self.value = 0
        self.cost_to_cover = 0
        self.short_PL = 0     

        for e in tickers:
            self.capital_invested += e.capital_invested
            self.capital_collateral += e.capital_collateral
            self.value += e.value
            self.cost_to_cover += e.cost_to_cover
            self.short_PL += e.short_PL
        
        self.total_value = self.value + self.capital_collateral

    def breakdown_by_ticker(self):
        dic = {}
        for e in self.tickers:
            dic[e.id] = e.total_value / self.total_value

        return dic

    def average_ticker_weight(self):
        return 1 / len(self.tickers)