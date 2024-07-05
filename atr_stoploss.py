import yfinance
import talib as ta
import numpy as np
from scipy import stats

from helpers import *


class ATRStopLoss:
    
    def __init__(self, symbol, riskMultiplier):

        # Download Yahoo Finance
        self.symbol = symbol
        # if (data == None):
        self.data = yfinance.download(symbol, period="3mo", interval="1d")
        # self.data = data
        self.riskMultiplier = riskMultiplier # 1.5 - 3

        self.calculate()

    def calculate(self):
        
        self.atr = ta.ATR(self.data["High"], self.data["Low"], self.data["Close"], timeperiod=14)
        
        self.atr = self.atr.dropna()

        self.variability = (self.atr.iloc[-1]) * self.riskMultiplier
