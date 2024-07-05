import yfinance
import talib as ta
import numpy as np
from scipy import stats
import pandas as pd
import requests
from datetime import datetime, timedelta
from textblob import TextBlob
import finnhub
   
# Goal determine upper and lower bounds
class MultipleHighLowStrategy:
    
    def __init__(self, symbol):
        
        # Download Yahoo Finance
        self.symbol = symbol
        startDay = (datetime.today() - timedelta(weeks=2))
        
        data2W = yfinance.download(symbol, start=(str(startDay.year)+"-"+str(startDay.month)+"-"+str(startDay.day)), interval="1d")
        data1M = yfinance.download(symbol, period="1mo", interval="1d")
        data3M = yfinance.download(symbol, period="3mo", interval="1d")
        data6M = yfinance.download(symbol, period="6mo", interval="1d")
        
        upper2WBound = self.calculateData(data2W["Close"], "max")
        lower2WBound = self.calculateData(data2W["Close"], "min")

        upper1MBound, lower1MBound = self.calculate(data1M)
        upper3MBound, lower3MBound = self.calculate(data3M)
        upper6MBound, lower6MBound = self.calculate(data6M)

        strength2WUpper, strength2WLower = self.analyzeStrength(data2W, upper2WBound, lower2WBound)
        strength1MUpper, strength1MLower = self.analyzeStrength(data1M, upper1MBound, lower1MBound)
        strength3MUpper, strength3MLower = self.analyzeStrength(data3M, upper3MBound, lower3MBound)
        strength6MUpper, strength6MLower = self.analyzeStrength(data6M, upper6MBound, lower6MBound)

        calcUpperBound = upper3MBound
        calcLowerBound = lower3MBound
       
        if (strength2WUpper > 0 and strength2WUpper < 100):
            calcUpperBound = upper2WBound
            print("Upper 2W")
        elif (strength1MUpper > 0 and strength1MUpper < 100):
            calcUpperBound = upper1MBound
            print("Upper 1M")

        elif (strength3MUpper > 0 and strength3MUpper < 100):
            calcUpperBound = upper3MBound
            print("Upper 3M")

        elif (strength6MUpper > 0 and strength6MUpper < 100):
            calcUpperBound = upper6MBound
            print("Upper 6M")

        else:
            calcUpperBound = upper1MBound
            print("Unsorted Upper 1M")
        
        if (strength2WLower > 0 and strength2WLower < 100):
            calcLowerBound = lower2WBound
            print("Lower 2W")

        elif (strength1MLower > 0 and strength1MLower < 100):
            calcLowerBound = lower1MBound
            print("Lower 1M")

        elif (strength3MLower > 0 and strength3MLower < 100):
            calcLowerBound = lower3MBound
            print("Lower 3M")

        elif (strength6MLower > 0 and strength6MLower < 100):
            calcLowerBound = lower6MBound
            print("Lower 6M")

        else:
            calcLowerBound = lower1MBound
            print("Unsorted Lower 1M")

        print("Upper Bound: " + str(calcUpperBound))
        print("Lower Bound: " + str(calcLowerBound))
    
        self.upperBound = calcUpperBound
        self.lowerBound = calcLowerBound

    def analyzeStrength(self, data, upperBound, lowerBound):
        dataHigh = data["High"]
        dataLow = data["Low"]

        upperTouched = dataHigh[(dataHigh >= upperBound) & (dataHigh.shift(1) < upperBound)]
        lowerTouched = dataLow[(dataLow <= lowerBound) & (dataLow.shift(1) > lowerBound)]
        # print("--------")
        # print(upperBound)
        # print(lowerBound)

        return (round(len(upperTouched)/3.00*100)), (round(len(lowerTouched)/3.00*100))
    
    def calculate(self, data):
        
        # Gets the simple moving average for 10 days for the high and low data seperately
        smaHighData = ta.SMA(data["Close"], timeperiod=10).dropna()
        smaLowData = ta.SMA(data["Close"], timeperiod=10).dropna()

        # Gets the max and min of the most clustered peaks and valleys
        upperBound = self.calculateData(smaHighData, "max")
        lowerBound = self.calculateData(smaLowData, "min")

        return upperBound, lowerBound

    def calculateData(self, data, type):

        # Fits the data to a polynomial function of degree 20
        stockCoe = np.polyfit(np.arange(len(data)), data, deg=20)
        
        # Takes the derivative of the function above
        stockDerCoe = np.polyder(stockCoe)

        # Takes the roots of the derivative to find all relative extrema
        relExtrema = np.roots(stockDerCoe)
        
        # Data filtering and removes data with plus/minuses
        relExtrema = relExtrema[(relExtrema >= 0) & (relExtrema <= len(data))]
        relExtrema = np.unique([tempVal.real for tempVal in relExtrema])

        # Gets all the respective y values for the relative extrema
        relExtremaY = np.polyval(stockCoe, relExtrema)
        relExtremaY = relExtremaY[(relExtremaY >= 0)]
        
        # Calculates the threshold using a trimmed mean of 5% from all the distances between each relative extrema y value
        avgExtremaDiffs = []
        for exI in range(len(relExtremaY)-1):
            avgExtremaDiffs.append(abs((relExtremaY[exI+1] - relExtremaY[exI])))
        avgDiff = stats.trim_mean(avgExtremaDiffs, 0.05)

        # Takes all of the relative y extremas that are clustered withing the average difference value calculated
        allRelExtrema = []
        for exI in range(len(relExtremaY)-1):
            if abs((relExtremaY[exI+1] - relExtremaY[exI])) <= avgDiff:
                if (type == "max"):
                    allRelExtrema.append(max(relExtremaY[exI], relExtremaY[exI+1]))
                else:
                    allRelExtrema.append(min(relExtremaY[exI], relExtremaY[exI+1]))

        # Returns the final max min value
        if (type == "max"):
            return max(allRelExtrema)
        else:
            return min(allRelExtrema)


def getSentimentScore(symbol):

    end = datetime.now().date()
    start = datetime.now().date() - timedelta(3)

    response = requests.get("https://finnhub.io/api/v1/company-news?symbol=" + symbol + "&from=" + str(start) + "&to=" + str(end) + "&token=cp9bfahr01qo7b1a09d0cp9bfahr01qo7b1a09dg")

    if response.status_code == 200:
        news_data = response.json()

        sentimentScore = 0
        allNews = 0
        for article in news_data:
            sentimentHeadlines = TextBlob(article["headline"]).sentiment.polarity
            sentimentScore += sentimentHeadlines
            allNews += 1

        if (allNews == 0):
            return 0
        
        return sentimentScore/allNews

