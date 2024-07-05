from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template
from model_stock import *
from strategies import *
from datetime import *
import pytz


class StockCron:
    def __init__(self):

        self.allSwingTrades = []
        self.allShortSwingTrades = []
        self.lastUpdated = datetime.now()
        self.monitorStocks = [StockModel("BA"), StockModel("AVGO"), StockModel("CRWD"), StockModel("AMD"),
                                StockModel("META"), StockModel("SNOW"), StockModel("AAPL"), StockModel("TSLA"),
                                StockModel("PANW"), StockModel("DIS"), StockModel("RDDT"), StockModel("CMG"),
                                StockModel("ENPH"), StockModel("TMDX"), StockModel("NVDA"), StockModel("OKTA"),
                                StockModel("ZS"), StockModel("UBER"), StockModel("JPM"), StockModel("GS"),
                                StockModel("FSLR"), StockModel("FDX"), StockModel("UPS"), StockModel("NFLX"),
                                StockModel("GOOG"), StockModel("AMZN"), StockModel("COST"), StockModel("CRM"),
                                StockModel("MDB"), StockModel("MU"), StockModel("MRVL"), StockModel("ENVX"), 
                                StockModel("AFRM"), StockModel("BBY"), StockModel("GME"), StockModel("AMC")]

        self.stockScheduler = BackgroundScheduler(daemon=True, timezone=pytz.timezone("US/Pacific"))

        # Swing-Trade
        self.stockScheduler.add_job(self.handleStockSwingTrade, "cron", day_of_week="mon-fri", hour="6-12", minute="*/10", max_instances=1) # 6:00-12:59

        # Day-Trade
        self.stockScheduler.add_job(self.handleGenerationStock, "cron", day_of_week="mon-fri", hour="4", minute="0") # 4:00 Model Generation
        self.stockScheduler.add_job(self.handleStockMonitoring, "cron", day_of_week="mon-fri", hour="6", minute="30-59", max_instances=1) # 6:30-6:59
        self.stockScheduler.add_job(self.handleStockMonitoring, "cron", day_of_week="mon-fri", hour="7-12", minute="*", max_instances=1) # 7:00-12:59
        self.stockScheduler.start()

    def handleGenerationStock(self):
        print("Generating")
        for oneStock in self.monitorStocks:
            oneStock.genModel()

    def handleStockMonitoring(self):
        print("Monitoring")
        for oneStock in self.monitorStocks:
            oneStock.monitorPrice()
            
    def handleStockSwingTrade(self):

        self.allSwingTrades, self.allShortSwingTrades = genSwingTrades()
        self.lastUpdated = datetime.now()


stockJob = StockCron()
application = Flask(__name__)

@application.route("/")
def provideSwingTrades():
    return "Long Positions: " + str(stockJob.allSwingTrades) + ", Short Positions: " + str(stockJob.allShortSwingTrades) + ", Last Updated: " + str(stockJob.lastUpdated)

@application.route("/daytrade")
def provideDayTrades():
    dayHighLows = []
    for oneStock in stockJob.monitorStocks:
        highPrice = oneStock.highPrice
        lowPrice = oneStock.highPrice
        if highPrice == None:
            highPrice = 0
        if lowPrice == None:
            lowPrice = 0

        dayHighLows.append(oneStock.symbol + " - High: " + str(highPrice) + ", Low: " + str(lowPrice))
    
    return dayHighLows

if __name__ == "__main__":
    application.run()
