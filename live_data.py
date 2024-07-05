import finnhub

# Realtime data source
class RealtimeDataSource:

    def __init__(self, symbol):
        self.client = finnhub.Client("cp9bfahr01qo7b1a09d0cp9bfahr01qo7b1a09dg")
        self.symbol = symbol
    
    def currentPrice(self):
        return self.client.quote(self.symbol)["c"]
    