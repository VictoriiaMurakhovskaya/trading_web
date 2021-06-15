from bs4 import BeautifulSoup as bs
import urllib.request as urllib2
import pandas as pd
import plotly.graph_objects as go
import numpy as np


def getData(stockName):
    """
    Загрузка статистики торгов с YahooFinance
    Результат работы - stock_data.csv, которые потом используются при прогнозировании
    """
    data = []
    url = "https://finance.yahoo.com/quote/" + stockName + "/history/"
    rows = bs(urllib2.urlopen(url).read(), "lxml").findAll('table')[0].tbody.findAll('tr')

    for each_row in rows:
        divs = each_row.findAll('td')
        if divs[1].span != 'Dividend':  # Ignore this row in the table
            data.append({'open': divs[1].span.text.replace(',', ''), 'Adj close': float(divs[5].span.text.replace(',', ''))})

    cArray = [c['Adj close'] for c in data]
    oArray = [o['open'] for o in data]

    dayChange, nextDayChange, profit = [], [], []

    for k in range(len(data) - 2):
        dayChange.append((float(cArray[k]) - float(oArray[k + 1])) / float(oArray[k + 1]))
        nextDayChange.append((float(cArray[k + 1]) - float(oArray[k + 2])) / float(oArray[k + 2]))
        profit.append(float(oArray[k]) - float(oArray[k + 1]))

    datasize = len(dayChange)

    fig = go.Figure(data=go.Scatter(x=list(range(len(oArray))), y=np.array(oArray).astype('float64'), name='Открытие'))
    fig.add_scatter(x=list(range(len(oArray))), y=np.array(cArray).astype('float64'), name='Закрытие')

    return fig, pd.DataFrame({'Counter': list(range(len(dayChange))), 'Difference': dayChange,
                              'ND_Difference': nextDayChange, 'Profit': profit})
