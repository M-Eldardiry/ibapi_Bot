from datetime import time
from hmac import new
from idlelib.pyshell import usage_msg

from ibapi.client import *
# EClient sends requests to TWS
from ibapi.wrapper import *
# EWrapper handles incoming messages
from ibapi.contract import *

from time import sleep
from datetime import datetime
from threading import Thread

import config
from config import host, port, client_id, ib_account

contract_request_dictionary = {1: 'AAPL', 2: 'GOOG'}
# contract_request_dictionary["symbol"] = "NASDAQ"

class TradeApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

# custom attributes or Variables
        self.account_balance = None
        self.account_equity = None
        self.portfolio = {}

        # for key in contract_request_dictionary.items():
        self.marketdata = {}
        for key, val in contract_request_dictionary.items():
            self.marketdata[val] = {}

        self.marketdata['AAPL'] = {}
        self.marketdata['GOOG'] = {}

# EWrapper Function

    def updateAccountValue(self, key:str, val:str, currency:str, account:str):
        # print("updateAccountValue. Key:", key, "Value:", val, "Currency:", currency, "AccountName:", account)
            # current_time = datetime.now()
        if key == "TotalCashBalance" and currency == "BASE":
            # print(current_time, "My Cash Balance = ", val)
            self.account_balance = val
        elif key == "NetLiquidationByCurrency" and currency == "BASE":
            # print(current_time, "My Equity = ", val)
            self.account_equity = val

    def updatePortfolio(self, ib_contract: Contract, position: float, market_price: float, market_value: float,
                        average_cost: float, unrealized_pnl: float, realized_pnl: float, account_name: str):

        # print("Local Symbol:", contract.localSymbol)
        """
        print("Update Portfolio.", "Symbol:", contract.symbol, "SecType:", contract.secType, "Exchange:", contract.exchange,
              "Position:", position, "MarketPrice:", market_price, "MarketValue:", market_value, "AverageCost:", average_cost,
              "UnrealizedPnl:", unrealized_pnl, "RealizedPnl:", realized_pnl, "Account Name:", account_name)
        print("="* 70)
        """

        self.portfolio[contract.symbol] = {"position": position,
                                           "market_price": market_price,
                                           "market_value": market_value,
                                           "average_cost": average_cost,
                                           "unrealized_pnl": unrealized_pnl,
                                           "realized_pnl": realized_pnl,
                                           "account_name": account_name}
    # EWrapper function will return the TickPrice

    def tickPrice(self, reqId:TickerId , tickType:TickType, price:float,attrib:TickAttrib):
        # print(reqId, tickType, price, attrib)
        # Bid Price		    IBApi.EWrapper.tickPrice	1
        # Ask Price		    IBApi.EWrapper.tickPrice	2
        # Last Price		IBApi.EWrapper.tickPrice	4
        # High			    IBApi.EWrapper.tickPrice	6
        # Low			    IBApi.EWrapper.tickPrice	7
        # Volume			IBApi.EWrapper.tickSize		8
        # Close Price		IBApi.EWrapper.tickPrice	9
        if TickType==1:
            self.marketdata[contract_request_dictionary[reqId]]["Bid Price"] = price
        elif TickType==2:
            self.marketdata[contract_request_dictionary[reqId]]["Ask Price"] = price
        elif TickType==4:
            self.marketdata[contract_request_dictionary[reqId]]["Last Price"] = price

if __name__ == '__main__':
    app = TradeApp()

    app.connect(host, port, client_id)
    sleep(1)

    app_thread = Thread(target=app.run, daemon=True)
    app_thread.start()

    # reqAccountUpdates will return the values both from updateAccountValue and updatePortfolio
    app.reqAccountUpdates( True, ib_account)

    # this to define apple contract test
    contract = Contract()
    contract.conId = 265598
    contract.exchange = "SMART"
    contract.primaryExchange = "NASDAQ"

    # subscribing and requesting Market Data
    reqId = 1 # it is unique number that use to ident Incoming messages
    app.reqMktData(reqId, contract, genericTickList="", snapshot=False, regulatorySnapshot=False, mktDataOptions=[])

    sleep(3)
    while True:
        current_time = datetime.now()
        print(current_time,  "My Cash Balance = ", app.account_balance, "My Equity = ", app.account_equity)
        print("Current Time:", current_time)
        print("Account Balance:", app.account_balance)
        print("Account Equity:", app.account_equity)
        print("Portfolio:", app.portfolio)
        print('Market Data', app.marketdata)
        print("="* 70)
        sleep(5)

    # app request account data
    # app request market data
