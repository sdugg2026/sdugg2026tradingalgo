import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce


# Calculate Bollinger Bands
def calculate_bollinger_bands(data, num_lookback = 20, num_std = 2) -> list[float]:
    hlc_avg = (data['High'] + data['Low'] + data['Close'])/3
    mean = hlc_avg.rolling(num_lookback).mean()
    std = hlc_avg.rolling(num_lookback).std()
    upper = mean + std * num_std
    lower = mean - std * num_std
    return upper, lower
    
# Calculate RSI

def calculate_RSI(data, window=14, adjust=False):
    delta = data['Close'].diff(1).dropna()
    loss = delta.copy()
    gains = delta.copy()

    gains[gains < 0] = 0
    loss[loss > 0] = 0

    gain_ewm = gains.ewm(com=window - 1, adjust=adjust).mean()
    loss_ewm = abs(loss.ewm(com=window - 1, adjust=adjust).mean())

    RS = gain_ewm / loss_ewm
    RSI = 100 - 100 / (1 + RS)

    return RSI

