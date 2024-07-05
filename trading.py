from base_strategies import *
from portfolio import Portfolio
from strategies import *
import backtrader as bt 


# portfolio = Portfolio()

buySignals, sellSignals = genSignals()
trader = bt.Cerebro()
trader.adddata(bt.feeds.PandasData(dataname=yf.download("AAPL", "2024-01-01", "2024-06-05")))
trader.broker.setcash(10000)
trader.run()
print(trader.broker.getvalue())

# trader.plot()
# print(buySignals)
# for oneSignal in buySignals:
#     portfolio.addSymbol(oneSignal["symbol"], 100, oneSignal["upperBound"], oneSignal["lowerBound"], oneSignal["sentiment"], oneSignal["price"])

# print(portfolio.getPortfolio())