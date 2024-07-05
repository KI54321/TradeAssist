import yfinance
import talib as ta
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.preprocessing import *
from sklearn.multioutput import MultiOutputRegressor
from sklearn.svm import SVR
from sklearn.metrics import *
from sklearn.model_selection import train_test_split
import finnhub 
from twilio.rest import Client



twilioClient = Client("AC326232047b7e0241c7b3d7428e077e25", "915eed3c98adbfbddfa47bcc951c5284")

def sendMessage(message):
    twilioClient.messages.create(
        from_="+18335791828",
        body=message,
        to="+14084440130"
    )
    twilioClient.messages.create(
        from_="+18335791828",
        body=message,
        to="+4082187763"
    )
    print("Sent Successfully")


# Goal determine upper and lower bounds
class StockModel:

    def __init__(self, symbol):

        self.predicted = False
        self.notifiedHigh = False
        self.notifiedLow = False

        self.symbol = symbol
        self.finnClient = finnhub.Client("cp9bfahr01qo7b1a09d0cp9bfahr01qo7b1a09dg")

    def genModel(self):
        
        self.predicted = False  
        self.notifiedHigh = False
        self.notifiedLow = False

        pd.set_option('display.max_columns', None)  
        pd.set_option('display.max_rows', None)     
        pd.set_option('display.width', 1000)        

        self.data = yfinance.download(self.symbol, interval="1d")
        self.qqqData = yfinance.download("QQQ", interval="1d")
        self.spyData = yfinance.download("SPY", interval="1d")

        self.data = self.data.drop(columns=["Adj Close"])

        self.qqqData = self.qqqData.drop(columns=["Adj Close"])
        self.spyData = self.spyData.drop(columns=["Adj Close"])

        self.qqqData = self.qqqData.reindex(self.data.index)
        self.spyData = self.spyData.reindex(self.data.index)

        self.qqqData.columns = ["OpenQQQ", "HighQQQ", "LowQQQ", "CloseQQQ", "VolumeQQQ"]
        self.spyData.columns = ["OpenSPY", "HighSPY", "LowSPY", "CloseSPY", "VolumeSPY"]

        self.data["Prev Open"] = self.data["Open"].shift(1)
        self.data["Prev Close"] = self.data["Close"].shift(1)
        self.data["Prev High"] = self.data["High"].shift(1)
        self.data["Prev Low"] = self.data["Low"].shift(1)
        self.data["Prev Volume"] = self.data["Volume"].shift(1)
        self.data["Prev ATR"] = ta.ATR(self.data["Prev High"], self.data["Prev Low"], self.data["Prev Close"], timeperiod=14)
        self.data["Prev TRANGE"] = ta.ATR(self.data["Prev High"], self.data["Prev Low"], self.data["Prev Close"])
        self.data["Prev Percentage"] = ((self.data["Prev Close"] - self.data["Prev Open"]) / self.data["Prev Open"])*100

        self.qqqData["Prev OpenQQQ"] = self.qqqData["OpenQQQ"].shift(1)
        self.qqqData["Prev HighQQQ"] = self.qqqData["HighQQQ"].shift(1)
        self.qqqData["Prev LowQQQ"] = self.qqqData["LowQQQ"].shift(1)
        self.qqqData["Prev CloseQQQ"] = self.qqqData["CloseQQQ"].shift(1)
        self.qqqData["Prev VolumeQQQ"] = self.qqqData["VolumeQQQ"].shift(1)
        self.qqqData["Prev ATRQQQ"] = ta.ATR(self.qqqData["Prev HighQQQ"], self.qqqData["Prev LowQQQ"], self.qqqData["Prev CloseQQQ"], timeperiod=14)
        self.qqqData["Prev TRANGEQQQ"] = ta.TRANGE(self.qqqData["Prev HighQQQ"], self.qqqData["Prev LowQQQ"], self.qqqData["Prev CloseQQQ"])
        self.qqqData["Prev PercentageQQQ"] = ((self.qqqData["Prev CloseQQQ"] - self.qqqData["Prev OpenQQQ"]) / self.qqqData["Prev OpenQQQ"])*100

        self.spyData["Prev OpenSPY"] = self.spyData["OpenSPY"].shift(1)
        self.spyData["Prev HighSPY"] = self.spyData["HighSPY"].shift(1)
        self.spyData["Prev LowSPY"] = self.spyData["LowSPY"].shift(1)
        self.spyData["Prev CloseSPY"] = self.spyData["CloseSPY"].shift(1)
        self.spyData["Prev VolumeSPY"] = self.spyData["VolumeSPY"].shift(1)
        self.spyData["Prev ATRSPY"] = ta.ATR(self.spyData["Prev HighSPY"], self.spyData["Prev LowSPY"], self.spyData["Prev CloseSPY"], timeperiod=14)
        self.spyData["Prev TRANGESPY"] = ta.TRANGE(self.spyData["Prev HighSPY"], self.spyData["Prev LowSPY"], self.spyData["Prev CloseSPY"])
        self.spyData["Prev PercentageSPY"] = ((self.spyData["Prev CloseSPY"] - self.spyData["Prev OpenSPY"]) / self.spyData["Prev OpenSPY"])*100

        self.combinedDataset = pd.concat([self.data, self.qqqData, self.spyData], axis=1)

        self.combinedDataset = self.combinedDataset[[
            "Open", "High", "Low", "Prev Open", "Prev Close", "Prev High", "Prev Low", "Prev Volume",
            "OpenQQQ", "Prev OpenQQQ", "Prev HighQQQ", "Prev LowQQQ", "Prev CloseQQQ", "Prev VolumeQQQ", "OpenSPY", "Prev OpenSPY", "Prev HighSPY", "Prev LowSPY", "Prev CloseSPY", "Prev VolumeSPY", "Prev ATR", "Prev ATRQQQ", "Prev ATRSPY", "Prev TRANGE", "Prev TRANGEQQQ", "Prev TRANGESPY", "Prev Percentage", "Prev PercentageQQQ", "Prev PercentageSPY"
        ]]
        self.combinedDataset = self.combinedDataset.dropna()

        self.x = self.combinedDataset[[  "Open", "Prev Open", "Prev Close", "Prev High", "Prev Low", "Prev Volume",
            "OpenQQQ", "Prev OpenQQQ", "Prev HighQQQ", "Prev LowQQQ", "Prev CloseQQQ", "Prev VolumeQQQ", "OpenSPY", "Prev OpenSPY", "Prev HighSPY", "Prev LowSPY", "Prev CloseSPY", "Prev VolumeSPY", "Prev ATR", "Prev ATRQQQ", "Prev ATRSPY", "Prev TRANGE", "Prev TRANGEQQQ", "Prev TRANGESPY", "Prev Percentage", "Prev PercentageQQQ", "Prev PercentageSPY"]]
        self.y = self.combinedDataset[["High", "Low"]]

        self.minMaxScalerX = MinMaxScaler()
        self.minMaxScalerY = MinMaxScaler()
       
        self.xTrain, self.xTest, self.yTrain, self.yTest = train_test_split(self.x, self.y, test_size=0.2)

        self.xTrain = self.minMaxScalerX.fit_transform(self.xTrain)
        self.xTest = self.minMaxScalerX.transform(self.xTest)
        self.yTrain = self.minMaxScalerY.fit_transform(self.yTrain)
        self.yTest = self.minMaxScalerY.transform(self.yTest)
        
        self.stockModel = MultiOutputRegressor(estimator=SVR(C=100, epsilon=0.005, gamma=0.001))
        self.stockModel.fit(self.xTrain, self.yTrain)
       
        print("Generated Model")

        # self.yPredictions = self.stockModel.predict(self.xTest)

        # self.yPredictions = self.minMaxScalerY.inverse_transform(self.yPredictions)
        # self.yTest = self.minMaxScalerY.inverse_transform(self.yTest)

        # self.meanSquaredError = mean_squared_error(self.yTest, self.yPredictions)
        # self.r2Score = r2_score(self.yTest, self.yPredictions)

        # print(self.meanSquaredError)
        # print(self.r2Score)

    def predictor(self, open, openQQQ, openSPY):
                
        tempData = yfinance.download(self.symbol, interval="1d")
        tempDataQQQ = yfinance.download("QQQ", interval="1d")
        tempDataSPY = yfinance.download("SPY", interval="1d")
       
        tempDataATR = ta.ATR(tempData["High"], tempData["Low"], tempData["Close"], timeperiod=14).iloc[-1]
        tempDataATRQQQ = ta.ATR(tempDataQQQ["High"], tempDataQQQ["Low"], tempDataQQQ["Close"], timeperiod=14).iloc[-1]
        tempDataATRSPY = ta.ATR(tempDataSPY["High"], tempDataSPY["Low"], tempDataSPY["Close"], timeperiod=14).iloc[-1]
        
        tempDataTRANGE = ta.TRANGE(tempData["High"], tempData["Low"], tempData["Close"]).iloc[-1]
        tempDataQQQTRANGE = ta.TRANGE(tempDataQQQ["High"], tempDataQQQ["Low"], tempDataQQQ["Close"]).iloc[-1]
        tempDataSPYTRANGE = ta.TRANGE(tempDataSPY["High"], tempDataSPY["Low"], tempDataSPY["Close"]).iloc[-1]
        
        tempData = tempData.iloc[-1]
        tempDataQQQ = tempDataQQQ.iloc[-1]
        tempDataSPY = tempDataSPY.iloc[-1]

        tempDataArray = [[open, tempData["Open"],  tempData["Close"], tempData["High"]  ,tempData["Low"] ,  tempData["Volume"] , openQQQ, tempDataQQQ["Open"] ,   tempDataQQQ["High"] ,   tempDataQQQ["Low"], tempDataQQQ["Close"], tempDataQQQ["Volume"], openSPY, tempDataSPY["Open"] ,   tempDataSPY["High"] ,   tempDataSPY["Low"], tempDataSPY["Close"], tempDataSPY["Volume"], tempDataATR, tempDataATRQQQ, tempDataATRSPY, tempDataTRANGE, tempDataQQQTRANGE, tempDataSPYTRANGE, ((tempData["Close"] - tempData["Open"]) / tempData["Open"])*100, ((tempDataQQQ["Close"] - tempDataQQQ["Open"]) / tempDataQQQ["Open"])*100, ((tempDataSPY["Close"] - tempDataSPY["Open"]) / tempDataSPY["Open"])*100]]

        tempDataNormalize = self.minMaxScalerX.transform(tempDataArray)

        tempPreds = self.stockModel.predict(tempDataNormalize)
        tempPredsInverse = self.minMaxScalerY.inverse_transform(tempPreds)

        self.highPrice = tempPredsInverse[0][0]
        self.lowPrice = tempPredsInverse[0][1]

        print(tempPredsInverse)
        self.predicted = True

    
    def monitorPrice(self):
        if (not self.predicted):
            print("Model Not Ready")
            if (self.stockModel != None):
                self.predictor(self.finnClient.quote(self.symbol)["o"], self.finnClient.quote("QQQ")["o"], self.finnClient.quote("SPY")["o"])
        else:
            currPrice = self.finnClient.quote(self.symbol)["c"]
            range = currPrice * 0.01 # 1% error range
            if ((abs(self.highPrice-currPrice)) <= range):
                if (not self.notifiedHigh):
                    self.notifiedHigh = True
                    sendMessage("Sell Signal for "+ str(self.symbol) + " @ $" + str(self.highPrice))
            elif ((abs(self.lowPrice-currPrice)) <= range):
                if (not self.notifiedLow):
                    self.notifiedLow = True
                    sendMessage("Buy Signal for "+ str(self.symbol) + " @ $" + str(self.lowPrice))

