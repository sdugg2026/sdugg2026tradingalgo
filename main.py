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



if __name__ == "__main__":

    RUNNING = True
    # Get our account information.
    trading_client = TradingClient('api-key', 'secret-key')
    account = trading_client.get_account()

    # Initialize positions and capital using Alpaca API
    capital = account.cash
    qqq_shares = 0
    psq_shares = 0


    # Download historical data for QQQ and PSQ
    end = dt.datetime.now()
    start = end- dt.timedelta(days = 90)

    qqq = yf.download("QQQ", start=start, end=end, progress=False)
    qqq['Upper'], qqq['Lower'] = calculate_bollinger_bands(qqq)
    qqq['RSI'] =  calculate_RSI(qqq)
    qqq = qqq.dropna()

    psq = yf.download("PSQ", start=start, end=end, progress=False)
    psq['Upper'], psq['Lower'] = calculate_bollinger_bands(psq)
    psq['RSI'] = calculate_RSI(psq)
    psq = psq.dropna()
    #Preconditions are satisfied now

    start_time = time.time()
    duration = 10

    iteration = 0



    while RUNNING:
        #Update Historical Data with Live Data
        #Calculate Bollinger Bands and RSI on QQQ using Historical + Real Time Data
        #Execute Trade and Update positions based on indicators
        iteration +=1


        #Update table with live data

        qqq_ticker = yf.Ticker("QQQ")
        qqq_price = qqq_ticker.fast_info['lastPrice']
        latest_data_QQQ = yf.download("QQQ", start=pd.Timestamp.now(), end=pd.Timestamp.now(), progress=False)

        psq_ticker = yf.Ticker("PSQ")
        psq_price = psq_ticker.fast_info['lastPrice']
        latest_data_PSQ = yf.download("PSQ", start=pd.Timestamp.now(), end=pd.Timestamp.now(), progress=False)

        if qqq.empty or psq.empty:
            print("No Data")
            continue

        # Check if the live data's timestamp is different from the latest entry in qqq and psq and continue if new data is present
        if latest_data_QQQ.index[-1] != qqq.index[-1] and latest_data_PSQ.index[-1] != psq.index[-1]:
            # Concatenate live data with the existing table
            qqq = pd.concat([qqq, latest_data_QQQ])
            psq = pd.concat([psq, latest_data_PSQ])

            #Calculate new indicators

            qqq['Upper'], qqq['Lower'] = calculate_bollinger_bands(qqq)
            qqq['RSI'] =  calculate_RSI(qqq)
            qqq = qqq.dropna()

            psq['Upper'], psq['Lower'] = calculate_bollinger_bands(psq)
            psq['RSI'] = calculate_RSI(psq)
            psq = psq.dropna()

            #Fully Hedged Position (Quantity for PSQ)
            Hedge_Qty = (qqq_price/psq_price) * 10

            #Make Decisions


            #short QQQ and long PSQ
            if qqq_price >= qqq['Upper'][-2] and qqq['RSI'][-2] >= 70 and psq_price <= psq['Lower'][-2] and psq['RSI'][-2] <= 30:
                

                market_order_data_QQQ = MarketOrderRequest(
                symbol="QQQ",
                qty=10.0,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY
                )
                trading_client.submit_order(order_data=market_order_data_QQQ)

                market_order_data_PSQ = MarketOrderRequest(
                symbol="PSQ",
                qty=Hedge_Qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
                )

                trading_client.submit_order(order_data=market_order_data_PSQ)

                print("Short QQQ and Long PSQ:")
                print(latest_data_PSQ)
                print(latest_data_QQQ)
                print("\n")

            #long QQQ and short PSQ
            elif qqq_price <= qqq['Lower'][-2] and qqq['RSI'][-2] <= 30 and psq_price >= psq['Upper'][-1] and psq['RSI'][-2] >= 70:
                

                market_order_data_PSQ = MarketOrderRequest(
                symbol="PSQ",
                qty=Hedge_Qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY
                )
                
                trading_client.submit_order(order_data=market_order_data_PSQ)

                market_order_data_QQQ = MarketOrderRequest(
                symbol="QQQ",
                qty=10.0,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
                )
                trading_client.submit_order(order_data=market_order_data_QQQ)

                print("Long QQQ and Short PSQ:")
                print(latest_data_PSQ)
                print(latest_data_QQQ)
                print("\n")
        
        if iteration %10 ==0:
            print("Iteration Number: ")
            print(iteration)
        if time.time() - start_time >= duration:
            RUNNING = False
            print("Terminated")
    
    
