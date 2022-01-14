# v0.1 - Very minimal, single stock, no analysis.

"""Currently, usage is simple: under `ticker`, `startDate` and `endDate` below, you enter the 1 ticker in your portfolio. 
Separately, ensure that `holdings.csv` file contains how much you added to your ticker holdings and on what date. Then a graph is produced."""

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from matplotlib import pyplot as plt

#Enter Ticker and Dates
ticker = "QQQM"
startDate = "2021-09-15"
endDate = "2022-01-13"

def convert_date_to_correct_format(date):
    dateofint = datetime.strptime(date, '%Y-%m-%d')
    print(f"Date = {dateofint}")
    print(f"Weekday Number: {dateofint.weekday()}")
    if(dateofint.weekday() > 4):
        print(f"Is a Weekdend")
#         dateofint = dateofint - timedelta(days=2)
    return dateofint

startDate = convert_date_to_correct_format(startDate)
endDate = convert_date_to_correct_format(endDate)

tickerObject = yf.Ticker(ticker)
data = tickerObject.history(start=startDate, end=endDate)

closePricesDf = data['Close']
closePricesDf.name = ticker

ticker_column_name = ticker + " Holdings"

holdings = pd.read_csv('holdings.csv', index_col='Date', parse_dates=True, dayfirst=True)
holdings['cumulative'] = holdings[ticker_column_name].cumsum()
holdings.drop(columns=[ticker_column_name], inplace = True)

holdingUpdateDf = pd.DataFrame(index = pd.date_range(start=startDate, end=endDate))
holdingUpdateDf = pd.merge(holdingUpdateDf, closePricesDf, how = 'left', left_index=True, right_index=True)
holdingUpdateDf.head(10)

holdingUpdateDf = holdingUpdateDf.fillna(method="ffill")

holdingUpdateDf = pd.merge(holdingUpdateDf, holdings, how = 'left', left_index=True, right_index=True)
holdingUpdateDf['invested'] = holdingUpdateDf['cumulative'] * holdingUpdateDf[ticker]
holdingUpdateDf = holdingUpdateDf.fillna(method="ffill")
holdingUpdateDf = holdingUpdateDf.fillna(0)

valueDf = holdingUpdateDf.copy()
valueDf['value'] = valueDf[ticker]*valueDf['cumulative']

title = f'{ticker}: Value of Holdings & Amount Invested'
valueDf['value'].plot(label = "value", figsize=(16,8), title = title)
valueDf['invested'].plot(label = "invested")

plt.legend()
plt.show()