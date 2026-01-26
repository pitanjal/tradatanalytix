import pandas as pd
import numpy as np
import requests
import datetime
import numpy as np
import numpy as np
import urllib.parse


def getHistData(instrument):
    try:
        instrument = urllib.parse.quote(instrument)
        today = datetime.date.today()
        to_date =datetime.date.strftime(today,'%Y-%m-%d')
        from_date = datetime.date.strftime(today- datetime.timedelta(days=365),'%Y-%m-%d')
        url = f'https://api.upstox.com/v2/historical-candle/{instrument}/day/{to_date}/{from_date}'
        candleRes = requests.get(url, headers={'accept': 'application/json'}).json()
        candleData = pd.DataFrame(candleRes['data']['candles'])
        candleData.columns = ['date','open','high','low', 'close','vol','oi']
        candleData =  candleData[['date','open','high','low', 'close']]
        candleData['date'] = pd.to_datetime(candleData['date']).dt.tz_convert('Asia/Kolkata')
        candleData['date'] = candleData.apply(lambda x: x.date.date(), axis=1)
        candleData.sort_values(by = 'date', inplace=True)
        return candleData
    except Exception as e:
        print(f"Exception when calling HistoryApi->get_intra_day_candle_data {e}")

