import yfinance
import talib as ta
import numpy as np
from scipy import stats

from helpers import *

class MacDStrategy:
    
    def __init__(self, symbol):

        # Download Yahoo Finance
        self.symbol = symbol
        # if (data == None):
        self.data = yfinance.download(symbol, period="3mo", interval="1d")
        # self.data = data
        self.calculate()

    def calculate(self):
        self.macd, self.macd_signal, self.macd_history = ta.MACD(self.data["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
        
        self.macd = self.macd.dropna()
        self.macd_signal = self.macd_signal.dropna()
        self.macd_history = self.macd_history.dropna()
    
    def signalCrossover(self):
        # Locating crossover events when the macd crosses signal higher its a buy
        # When the macd crosses signal lower its a sell
        macdBuyCrossover = (self.macd > self.macd_signal) & (self.macd.shift(1) <= self.macd_signal.shift(1))
        macdSellCrossover = (self.macd < self.macd_signal) & (self.macd.shift(1) >= self.macd_signal.shift(1))
        return (macdBuyCrossover), (macdSellCrossover)

    def zeroline(self):
        # When the macd crosses over to the 0 from below its a buy
        # When it crosses over to the 0 from above its a sell
        macdBuyZero = (self.macd > 0) & (self.macd.shift(1) <= 0)
        macdSellZero = (self.macd < 0) & (self.macd.shift(1) >= 0)

        return (macdBuyZero), (macdSellZero)

    def macdCombo(self):
        # Locating crossover events when the macd crosses signal higher its a buy
        # When the macd crosses signal lower its a sell
        macdBuyCombo = ((self.macd > self.macd_signal) & (self.macd.shift(1) <= self.macd_signal.shift(1))) | ((self.macd > 0) & (self.macd.shift(1) <= 0))
        macdSellCombo = (self.macd < self.macd_signal) & (self.macd.shift(1) >= self.macd_signal.shift(1)) | ((self.macd < 0) & (self.macd.shift(1) >= 0))

        return (macdBuyCombo.tail(2)), macdSellCombo.tail(2)

