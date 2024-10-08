import yfinance
import talib as ta
import numpy as np
from scipy import stats
import pandas as pd
import requests
from datetime import datetime, timedelta
import finnhub
from base_strategies import *
from helpers import getListStocks
from macd_strategies import *
from rsi_strategies import *
from atr_stoploss import *
import time


def genSignals(stocks):

    buySignals = []
    sellSignals = []
    finnClient = finnhub.Client("cpf57opr01qh4lv5j39gcpf57opr01qh4lv5j3a0")

    for oneStock in stocks:
        try:
            rsiResultBuy, rsiResultSell = RSIStrategy(oneStock, oversold=50, overbought=60).analyze()
            if (rsiResultBuy):
                print("RSI")
                macComboResultBuy, macComboResultSell = (MacDStrategy(oneStock).macdCombo())
                if (macComboResultBuy.any()):
                    print("MACD")
                    strategy = MultipleHighLowStrategy(oneStock)
                    currentPrice = finnClient.quote(oneStock)["c"]
                    if (currentPrice >= 5): # Don't want penny stocks
  
                        if ((currentPrice-strategy.lowerBound) <= 0.01*currentPrice):

                            sentiScore = getSentimentScore(oneStock)

                            if (sentiScore >= 0.1):

                                atr = ATRStopLoss(oneStock, 1.5)

                                buySignals.append("Buy: " + str(oneStock) + ", Stop Loss: " + str(currentPrice-atr.variability) + ", Sell: " + str(currentPrice+atr.variability))
            elif (rsiResultSell):
                print("SHORT")
                print("RSI")
                macComboResultBuy, macComboResultSell = (MacDStrategy(oneStock).macdCombo())
                if (macComboResultSell.any()):
                    print("MACD Short")
                    strategy = MultipleHighLowStrategy(oneStock)
                    currentPrice = finnClient.quote(oneStock)["c"]
                    if (currentPrice >= 5): # Don't want penny stocks
  
                        if ((currentPrice-strategy.upperBound) <= 0.01*currentPrice):

                            # sentiScore = getSentimentScore(oneStock)

                            # if (sentiScore >= 0.1):

                            atr = ATRStopLoss(oneStock, 1.5)

                            sellSignals.append("Short: " + str(oneStock) + ", Stop Loss: " + str(currentPrice+atr.variability) + ", Sell: " + str(currentPrice-atr.variability))
        except:
            print("HI")
            continue
    return buySignals, sellSignals

def genSwingTrades():
    stocks = getListStocks()
    i = 0

    allStocks = []
    allShorts = []

    while i < (len(stocks)):

        buy, short = genSignals(stocks[i:i+50])
        allStocks += buy
        allShorts += short
        i+=50
        print(allStocks)
        print(allShorts)
    
    return allStocks, allShorts
