import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from indicators import calculate_bollinger_bands, calculate_RSI
import time


# Download historical data for QQQ and PSQ
end = dt.datetime.now()
start = end- dt.timedelta(days = 10)

qqq = yf.download("QQQ", start=start, end=end,period = "1d", progress=False, interval="2m")
qqq['Upper'], qqq['Lower'] = calculate_bollinger_bands(qqq)
qqq['RSI'] =  calculate_RSI(qqq)
qqq = qqq.dropna()

psq = yf.download("PSQ", start=start, end=end,period="1d", progress=False, interval="2m")
psq['Upper'], psq['Lower'] = calculate_bollinger_bands(psq)
psq['RSI'] = calculate_RSI(psq)
psq = psq.dropna()
#Preconditions are satisfied now


# Using Simulated Trading Data from Jun 21 2023 at a five-minute interval
QQQ = yf.download("QQQ", start="2023-06-21", end="2023-06-22", interval="5m")
PSQ = yf.download("PSQ", start="2023-06-21", end="2023-06-22", interval="5m")

for i in range (1, min(QQQ['Open'].size, PSQ['Open'].size)):

    QQQ['Upper'], QQQ['Lower'] = calculate_bollinger_bands(QQQ)
    QQQ['RSI'] =  calculate_RSI(QQQ)

    PSQ['Upper'], PSQ['Lower'] = calculate_bollinger_bands(PSQ)
    PSQ['RSI'] = calculate_RSI(PSQ)
    
    qqq_price = QQQ['Open'][i]
    psq_price = PSQ['Open'][i]


    #short QQQ and long PSQ
    if qqq_price >= QQQ['Upper'][i-1] and QQQ['RSI'][i-1] >= 70 and psq_price <= PSQ['Lower'][i-1] and PSQ['RSI'][i-1] <= 30:
        
        print("Short QQQ and Long PSQ:")
        print("\n")
        print("QQQ Price: " + str(qqq_price))
        print(QQQ.iloc[i-1])
        print("\n")
        print("PSQ Price: " + str(psq_price))
        print(PSQ.iloc[i-1])
        print("\n")

    #long QQQ and short PSQ
    elif qqq_price <= QQQ['Lower'][i-1] and QQQ['RSI'][i-1] <= 30 and psq_price >= PSQ['Upper'][i-1] and PSQ['RSI'][i-1] >= 70:

        print("Long QQQ and Short PSQ:")
        print("\n")
        print("QQQ Price: " + str(qqq_price))
        print(QQQ.iloc[i-1])
        print("\n")
        print("PSQ Price: " + str(psq_price))
        print(PSQ.iloc[i-1])
        print("\n")

    
