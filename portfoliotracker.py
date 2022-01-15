# v0.2 - Largely Minimal, but can deal with multiple stocks directly from a csv where you only have to list down how many shares of stock you bought that day

"""Currently, usage is simple: under `ticker`, `startDate` and `endDate` below, you enter the 1 ticker in your portfolio. 
Separately, ensure that `holdings.csv` file contains how much you added to your ticker holdings and on what date. Then a graph is produced."""

import yfinance as yf
from datetime import datetime, timedelta, date
import pandas as pd
from matplotlib import pyplot as plt

# Get ticker data from holdings directly and sort 
holdings = pd.read_csv('holdings.csv', index_col='Date', parse_dates=True, dayfirst=True)
holdings = holdings.sort_index()

# Get dates from start of holdings to today
tickers = list(holdings.columns)
startDate = holdings.index[0]
endDate = date.today()

holdingUpdateDf = pd.DataFrame(index = pd.date_range(start=startDate, end=endDate))

for ticker in tickers:
    print(ticker)
    
    newDf = pd.DataFrame(holdings[ticker])
    newDf = newDf.rename(columns = {ticker:f'units bought of {ticker}'})
    newDf[f'cumulative {ticker}'] = newDf[f'units bought of {ticker}'].cumsum()
    newDf.dropna(inplace = True)
    newDf = newDf[newDf[f'cumulative {ticker}'] != 0]
    print('newdf\n',newDf)
    
    # Get yfinance data
    tickerObject = yf.Ticker(ticker)
    data = tickerObject.history(start=startDate, end=endDate)
    closePricesDf = data['Close']
    closePricesDf.name = ticker
#     print(closePricesDf)
    
    holdingUpdateDf = pd.merge(holdingUpdateDf, closePricesDf, how = 'left', left_index=True, right_index=True)
    holdingUpdateDf = holdingUpdateDf.fillna(method="ffill")
    
    holdingUpdateDf = pd.merge(holdingUpdateDf, newDf, how = 'left', left_index=True, right_index=True)
    holdingUpdateDf[f'cost of {ticker}'] = holdingUpdateDf[ticker] * holdingUpdateDf[f'units bought of {ticker}']
    holdingUpdateDf[f'total cost of {ticker}'] = holdingUpdateDf[f'cost of {ticker}'].cumsum()
    holdingUpdateDf[[f'units bought of {ticker}']] = holdingUpdateDf[[f'units bought of {ticker}']].fillna(value=0)
    holdingUpdateDf = holdingUpdateDf.fillna(method="ffill")
    holdingUpdateDf = holdingUpdateDf.fillna(value = 0)
    
    holdingUpdateDf[f'value of {ticker}'] = holdingUpdateDf[ticker] * holdingUpdateDf[f'cumulative {ticker}']
    
holdingUpdateDf  

# Show subplot of each investment
total = len(tickers)
cols = 2
# Compute Rows required
rows = total // cols 
rows += total % cols

# Create a Position index
position = range(1, total + 1)

fig = plt.figure(1, figsize=(20,10))
for k in range(total):
    ticker = tickers[k]
    valLabel = f'{ticker} value'
    invLabel = f'{ticker} invested'
    ax = fig.add_subplot(rows,cols,position[k])
    ax.plot(holdingUpdateDf[f'value of {ticker}'], label=valLabel)      # Or whatever you want in the subplot
    ax.plot(holdingUpdateDf[f'total cost of {ticker}'], label=invLabel)
    ax.legend()
    title = f"Value of {ticker} Holdings & Amount Invested"
    plt.title(title)
plt.show()

holdingUpdateDf['total invested'] = 0
holdingUpdateDf['total value'] = 0
for ticker in tickers:
    holdingUpdateDf['total invested'] += holdingUpdateDf[f'total cost of {ticker}']
    holdingUpdateDf['total value'] += holdingUpdateDf[f'value of {ticker}']
holdingUpdateDf

title = 'Value of Holdings & Amount Invested'
holdingUpdateDf['total value'].plot(label = "value", figsize=(16,8), title = title)
holdingUpdateDf['total invested'].plot(label = "invested")

plt.legend()
plt.show()

holdingUpdateDf.to_csv("holdings_updated.csv")