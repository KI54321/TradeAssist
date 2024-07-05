
def getListStocks():

    with open("src/live_trading/stock_list.txt", "r") as stock_list:

        stockLists = stock_list.read().splitlines()
        stockListsFilter = [symbol for symbol in stockLists if ('^' not in symbol) and ('.' not in symbol) and ('/' not in symbol)]
        stock_list.close()

        return stockListsFilter