import pandas as pd
from backtesting.backtester import BacktestDataSource

class Backtest_Portfolio:

    def __init__(self, symbols, bt_start=None, bt_end=None, strategies=[]):

        self.symbols = symbols
        self.bt_start = bt_start
        self.bt_end = bt_end
        self.data_sources = {}
        self.strategies = []

        for oneSymbol in self.symbols:
            self.data_sources[oneSymbol] = BacktestDataSource(oneSymbol, bt_start, bt_end)
   

    def addSymbol(self, symbol):
        self.symbols.append(symbol)
        self.data_sources[symbol] = BacktestDataSource(symbol, self.bt_start, self.bt_end)

    def removeSymbol(self, symbol):
        self.symbols.remove(symbol)
        self.data_sources.pop(symbol)

    def getPortfolio(self):
        return self.symbols