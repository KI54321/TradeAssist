import pandas as pd
import finnhub
import time

class Portfolio:

    def __init__(self):
        self.data = {}
        self.client = finnhub.Client("cp9bfahr01qo7b1a09d0cp9bfahr01qo7b1a09dg")

    def addSymbol(self, symbol, shares, upperBound, lowerBound, sentiment, price):
        self.data[symbol] = {"symbol": symbol, "shares": shares, "price": price, "timestamp": time.time(), "purchasePrice": price, "upperBound": upperBound, "lowerBound": lowerBound, "sentimentPol": sentiment}

    def removeSymbol(self, symbol):
        self.data.pop(symbol)

    def getPortfolio(self):
        return self.data
    
    def currentPrice(self, symbol):
        return self.client.quote(symbol)["c"]
