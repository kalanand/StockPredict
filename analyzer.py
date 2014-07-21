#! /usr/bin/python

## Copyright 2012 Kalanand Mishra

## StockPredict is a free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License or any later version: <http://www.gnu.org/licenses/>.
## This software is distributed WITHOUT ANY WARRANTY.

## Instructions: The main executable is 'analyzer.py'. You can
## modify input stock ticker symbols according to your needs.

import matplotlib.pyplot as plt
import matplotlib.dates as mdates 
import numpy as np
import os, re, math, datetime

'''
geometric brownian motion with drift!

Specification:

    mu    : drift factor in % 
    sigma : volatility in % (assumed constant here)
    T     : time span
    dt    : lenght of steps
    S0    : Stock Price in t=0
    W     : normal distribution with a mean zero and standard deviation of one
            = N[0,1]
    Wt    : Brownian Motion with Drift = W*sqrt(dt) = N[0,1] * sqrt(dt)

    Stock price at time t: 
    S(t) = S0 * exp( (mu - sigma**2/2)*t + sigma * Wt)


Yahoo Finance CSV Formatting Options:

s - Symbol 
n - Name 
l - Last Trade (with time)
l1 - Last Trade (without time)
d1 - Last Trade Date
t1 - Last Trade Time
k3 - Last Trade Size
c - Change and Percent Change
c1 - Change
p2 - Change in Percent
t7 - Ticker Trend
v - Volume
a2 - Average Daily Volume
i - More Info
t6 - Trade Links
b - Bid
b6 - Bid Size
a - Ask
a5 - Ask Size
p - Previous Close
o - Open 
m - Day's Range
w - 52 Week Range
j5 - Change from 52 Week Low
j6 - Percent Change from 52 Week Low
k4 - Change from 52 Week High
k5 - Percent Change from 52 Week High
e - Earnings/Share
r - P/E Ratio
s7 - Short Ratio
r1 - Dividend Pay Date
q - Ex-Dividend Date
d - Dividend/Share
y - Dividend Yield
f6 - Float Shares
j1 - Market Capitalization
t8 - 1 Year Target Price
e7 - EPS Est. Current Year
e8 - EPS Est. Next Year
e9 - EPS Est. Next Quarter
r6 - Price/EPS Est. Current Year
r7 - Price/EPS Est. Next Year
r5 - PEG Ratio
b4 - Book Value
p6 - Price/Book
p5 - Price/Sales
j4 - EBITDA
m3 - 50 Day Moving Average
m7 - Change from 50 Day Moving Average
m8 - Percent Change from 50 Day Moving Average
m4 - 200 Day Moving Average
m5 - Change from 200 Day Moving Average
m6 - Percent Change from 200 Day Moving Average
s1 - Shares Owned
p1 - Price Paid
c3 - Commission
v1 - Holdings Value
w1 - Day's Value Change
g1 - Holdings Gain Percent
g4 - Holdings Gain
d2 - Trade Date
g3 - Annualized Gain
l2 - High Limit
l3 - Low Limit
n4 - Notes
k1 - Last Trade (Real-time) with Time
b3 - Bid (Real-time)
b2 - Ask (Real-time)
k2 - Change Percent (Real-time)
c6 - Change (Real-time)
v7 - Holdings Value (Real-time)
w4 - Day's Value Change (Real-time)
g5 - Holdings Gain Percent (Real-time)
g6 - Holdings Gain (Real-time)
m2 - Day's Range (Real-time)
j3 - Market Cap (Real-time)
r2 - P/E (Real-time)
c8 - After Hours Change (Real-time)
i5 - Order Book (Real-time)
x - Stock Exchange

The format string "snl1d1t1c1w" will return, in this order, the 
following values per stock queried:

Symbol
Name
Last Trade (Price Only)
Last Trade Date
Last Trade Time
Change
52-Week Range
'''

#### Yahoo finance web query interface 
api = "curl -s \'http://download.finance.yahoo.com/d/quotes.csv?s=" 

### Dow Jones 30 components
symbols = ['AXP', 'BA', 'CAT', 'CSCO', 'CVX', 'DD', 'DIS', 'GE', 'GS', 'HD', 
           'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 'MCD', 'MMM', 'MRK', 'MSFT', 
           'NKE', 'PFE', 'PG', 'T', 'TRV', 'UNH', 'UTX', 'V', 'VZ', 'WMT', 
           'XOM']

T = 10           ### time span = 10 days 
dt = 0.01        ### computing in steps of 0.01 day
N = round(T/dt)  ### number of steps 
t = np.linspace(0, T, N) ### time intervals 




### Get current stock price at t=0
def CurrentPrice(ticker):
    p = os.popen(api + ticker + "\&f=l1\'","r")
    return float(p.readline()) 


### Drift computed using difference from 50 days moving average  
def Drift(ticker):
    p = os.popen(api + ticker + "\&f=m8\'","r") 
    line = p.readline()
    line = line.replace("%","")
    return float(line) * 0.01 * T/50


### Use VIX as proxy for volatility
def Volatility():
    p = os.popen(api + "%5EVIX\&f=l1\'","r")
    return float(p.readline()) * 0.01 / math.sqrt(12 * 30 / T)



### Prediction of stock price at time t using geometric brownian motion 
def Prediction(S0, mu, sigma):
    numIter = 1000
    S = 0
    for i in range(numIter):
        W = np.random.standard_normal(size = N) 
        W = np.cumsum(W)*np.sqrt(dt) ### standard brownian motion ###
        X = (mu-0.5*sigma**2)*t + sigma*W 
        S += S0*np.exp(X)/numIter ### geometric brownian motion ###
    return S


### Plot maker: specify how many stock predictions you want to plot  
def Plot( start, end, outputFileName):
    tSigma = Volatility()
   
    fig = plt.figure()
    ax = plt.subplot(111)
    plt.rcParams.update({'font.size': 14})
    timestr = datetime.datetime.now().strftime("%Y-%m-%d")
    plt.title('Prediction for the next 10 days from ' + timestr)
    plt.xlabel('Days', fontsize=20)
    plt.ylabel('Stock price', fontsize=20)
    for i in range(start, end):
        plt.plot(t, Prediction(CurrentPrice(symbols[i]), 
                               Drift(symbols[i]), tSigma), label = symbols[i])
    ax.legend()
    #plt.show()
    plt.savefig(outputFileName)


### The main function 
Plot(0, 3, 'plot_Dow_4.png')
