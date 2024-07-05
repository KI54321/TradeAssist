import yfinance as yf
import talib
import numpy as np
import logging
import os

class RSIStrategy:
    def __init__(self, symbol: str, period: int = 14, overbought: int = 70, oversold: int = 30):
        self.symbol = symbol
  
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        self.data = self.fetch_data()
        self.data['RSI'] = self.calculate_rsi()

    def fetch_data(self):
        return yf.download(self.symbol, period="3mo")

    def calculate_rsi(self):
        close_prices = self.data['Close']
        return talib.RSI(close_prices, timeperiod=self.period)

    def analyze(self):
        data = self.data
        return ((data.tail(3)["RSI"] <= self.oversold).any()), ((data.tail(3)["RSI"] >= self.overbought).any())
        # buy_signals = data[data['RSI'] < self.oversold]
        # sell_signals = data[data['RSI'] > self.overbought]
        
        #TODO replace with logger
        # print(f"RSI Strategy Analysis for {self.symbol}")
        # print(f"Buy signals (RSI < {self.oversold}):")
        # for index, row in buy_signals.iterrows():
        #     print(f"Date: {index}, RSI: {row['RSI']}, Close: {row['Close']}")

        # print(f"Sell signals (RSI > {self.overbought}):")
        # for index, row in sell_signals.iterrows():
        #     print(f"Date: {index}, RSI: {row['RSI']}, Close: {row['Close']}")

