
#best
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import pytz
from datetime import datetime, timedelta
from datetime import date
import numpy as np
import ta
import asyncio
import aiohttp
import nest_asyncio
#from allstocks import symbols
from variable import s



buystock = []
sellstock = []

interval = 5 # enter 15,60,240,1440,10080,43800
dayback = 15
ed = datetime.now()
stdate = ed - timedelta(dayback)

st.set_page_config(layout="wide")
st.title('Stock Trading Open High Low  200ma crossing')

c1,c2=st.columns(2,vertical_alignment="top")

def conv(x):

    timestamp = int(x.timestamp() * 1000)
    timestamp_str = str(timestamp)[:-4] + '0000'
    final_timestamp = int(timestamp_str)
    return  final_timestamp

ist_timezone = pytz.timezone('Asia/Kolkata')

fromdate = conv(stdate)
todate = conv(ed)




async def getdata(session, stock):


    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        #'Accept-Encoding': 'gzip, deflate, br'
    }
    url = f'https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/{stock}?endTimeInMillis={todate}&intervalInMinutes={interval}&startTimeInMillis={fromdate}'
    async with session.get(url, headers=headers) as response:
        try:
            
            resp = await response.json()
            candle = resp['candles']
            dt = pd.DataFrame(candle)
            fd = dt.rename(columns={0: 'datetime', 1: 'Open', 2: 'High', 3: 'Low', 4: 'Close', 5: 'Volume'})
            
            
            fd['symbol'] = stock
            pd.options.mode.chained_assignment = None
            final_df = fd
            

            final_df['Open'] = final_df['Open'].astype(float)
            final_df['Close'] = final_df['Close'].astype(float)
            final_df['High'] = final_df['High'].astype(float)
            final_df['Low'] = final_df['Low'].astype(float)
            final_df['Volume'] = final_df['Volume'].astype(float)
            final_df['datetime1'] = pd.to_datetime(final_df['datetime'], unit='s', utc=True)
            final_df['datetime1'] = final_df['datetime1'].dt.tz_convert(ist_timezone)
            
            

# Format the datetime to 'dd:mm:yyyy hh:mm:ss'
            #final_df['datetime1'] = final_df['datetime1'].dt.strftime('%d:%m:%Y %H:%M:%S')

            final_df.set_index(final_df.datetime1, inplace=True)
            final_df.drop(columns=['datetime'], inplace=True)

            final_df['prevopen'] = final_df['Open'].shift(1)
            final_df['prevhigh'] = final_df['High'].shift(1)
            final_df['prevlow1'] = final_df['Low'].shift(2)
            final_df['prevhigh1'] = final_df['High'].shift(2)
            final_df['prevlow2'] = final_df['Low'].shift(3)
            final_df['prevhigh2'] = final_df['High'].shift(3)
            final_df['prevclose'] = final_df['Close'].shift(1)
            
            
        
            final_df['time_column'] = final_df.datetime1.dt.time
            
            time_string = "09:15:00"            
#----------------------

            final_df['ma200'] = round(ta.momentum._ema(series=final_df['Close'],periods=200))
            final_df['ma50'] = round(ta.momentum._ema(series=final_df['Close'],periods=50))
            newdf = final_df
            newdf['o-h'] = np.where((newdf['Open'] == newdf['High']),1,0)
           
            newdf['o-l'] = np.where((newdf['Open'] == newdf['Low']),2,0)
            newdf['o-hs'] = np.where((newdf['Open'] == newdf['High']),1,0)
           
            newdf['o-ls'] = np.where((newdf['Open'] == newdf['Low']),1,0)
            newdf = newdf.iloc[-100:]
           
            newdf1 = final_df[final_df.index.time == pd.to_datetime(time_string).time()].reset_index(drop=True)
            
            last_candle = newdf1.iloc[-1]
            
            
            if last_candle['o-h'] == 1:#2
                sellstock.append(last_candle['symbol'])
                # st.write(last_candle['symbol'])

                

                fig = go.Figure(data=[go.Candlestick(x=newdf.index, open=newdf.Open, close=newdf.Close, high=newdf.High,low=newdf.Low,name=stock),
                                      go.Scatter(x=newdf.index, y=newdf.ma200, line=dict(color='red', width=2),name='ma200'),
                                      go.Scatter(x=newdf.index, y=newdf.ma50, line=dict(color='blue', width=2),name='ma500')
                                      ])
                fig.add_trace(
                    go.Scatter(x=newdf[newdf['o-hs']==1].index, y=newdf[newdf['o-hs']==1]['High'], mode='markers', marker_symbol='triangle-down',
                               marker_size=25,marker_color='red'))
               

                fig.update_layout(autosize=False, width=1800, height=800, xaxis_rangeslider_visible=False)
                fig.layout.xaxis.type = 'category'
                c1.write(' oh sell stratergy')
                c1.plotly_chart(fig,use_container_width=True)
                
                #st.write(' oh sell stratergy')
                #st.plotly_chart(fig)

            if last_candle['o-l'] == 2:#3

                buystock.append(last_candle['symbol'])
                fig = go.Figure(data=[go.Candlestick(x=newdf.index, open=newdf.Open, close=newdf.Close, high=newdf.High,low=newdf.Low,name=stock),                                     
                                      go.Scatter(x=newdf.index, y=newdf.ma50, line=dict(color='blue', width=2),name='ma500'),
                                      go.Scatter(x=newdf.index, y=newdf.ma200, line=dict(color='red', width=2),name='ma200')])
                fig.add_trace(
                    go.Scatter(x=newdf[newdf['o-ls']==1].index, y=newdf[newdf['o-ls']==1]['Low'], mode='markers', marker_symbol='triangle-up',
                               marker_size=25,marker_color='green'))
                

                fig.update_layout(autosize=False, width=1800, height=800, xaxis_rangeslider_visible=False)
                fig.layout.xaxis.type = 'category'
                c2.write(' oh buy stratergy')
                c2.plotly_chart(fig,use_container_width=True)
                
                # st.write(' ol buy stratergy')
                # st.plotly_chart(fig)



            return
        except:
            print('no data')
            pass


async def main():
    async with aiohttp.ClientSession() as session:

        tasks = []
        for stocks in s:
            try:
                stock = stocks

                task = asyncio.ensure_future(getdata(session, stock))

                tasks.append(task)
            except:
                pass
        df = await asyncio.gather(*tasks)
        # print(df)


nest_asyncio.apply()
asyncio.run(main())





st.write('buy')
st.write(buystock)
st.write('sell')
st.write(sellstock)


# #best
# import pandas as pd
# import plotly.graph_objects as go
# import streamlit as st
# import pytz
# from datetime import datetime, timedelta
# from datetime import date
# import numpy as np
# import ta
# import asyncio
# import aiohttp
# import nest_asyncio
# #from allstocks import symbols
# from variable import s



# buystock = []
# sellstock = []

# interval = 5 # enter 15,60,240,1440,10080,43800
# dayback = 15
# ed = datetime.now()
# stdate = ed - timedelta(dayback)

# st.set_page_config(layout="wide")
# st.title('Stock Trading Open High Low  200ma crossing')



# def conv(x):

#     timestamp = int(x.timestamp() * 1000)
#     timestamp_str = str(timestamp)[:-4] + '0000'
#     final_timestamp = int(timestamp_str)
#     return  final_timestamp

# ist_timezone = pytz.timezone('Asia/Kolkata')

# fromdate = conv(stdate)
# todate = conv(ed)




# async def getdata(session, stock):


#     headers = {
#         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0',
#         'Accept': 'application/json',
#         'Accept-Language': 'en-US,en;q=0.5',
#         #'Accept-Encoding': 'gzip, deflate, br'
#     }
#     url = f'https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/{stock}?endTimeInMillis={todate}&intervalInMinutes={interval}&startTimeInMillis={fromdate}'
#     async with session.get(url, headers=headers) as response:
#         try:
            
#             resp = await response.json()
#             candle = resp['candles']
#             dt = pd.DataFrame(candle)
#             fd = dt.rename(columns={0: 'datetime', 1: 'Open', 2: 'High', 3: 'Low', 4: 'Close', 5: 'Volume'})
            
            
#             fd['symbol'] = stock
#             pd.options.mode.chained_assignment = None
#             final_df = fd
            

#             final_df['Open'] = final_df['Open'].astype(float)
#             final_df['Close'] = final_df['Close'].astype(float)
#             final_df['High'] = final_df['High'].astype(float)
#             final_df['Low'] = final_df['Low'].astype(float)
#             final_df['Volume'] = final_df['Volume'].astype(float)
#             final_df['datetime1'] = pd.to_datetime(final_df['datetime'], unit='s', utc=True)
#             final_df['datetime1'] = final_df['datetime1'].dt.tz_convert(ist_timezone)
            
            

# # Format the datetime to 'dd:mm:yyyy hh:mm:ss'
#             #final_df['datetime1'] = final_df['datetime1'].dt.strftime('%d:%m:%Y %H:%M:%S')

#             final_df.set_index(final_df.datetime1, inplace=True)
#             final_df.drop(columns=['datetime'], inplace=True)

#             final_df['prevopen'] = final_df['Open'].shift(1)
#             final_df['prevhigh'] = final_df['High'].shift(1)
#             final_df['prevlow1'] = final_df['Low'].shift(2)
#             final_df['prevhigh1'] = final_df['High'].shift(2)
#             final_df['prevlow2'] = final_df['Low'].shift(3)
#             final_df['prevhigh2'] = final_df['High'].shift(3)
#             final_df['prevclose'] = final_df['Close'].shift(1)
            
            
        
#             final_df['time_column'] = final_df.datetime1.dt.time
            
#             time_string = "09:15:00"            
# #----------------------

#             final_df['ma200'] = round(ta.momentum._ema(series=final_df['Close'],periods=200))
#             final_df['ma50'] = round(ta.momentum._ema(series=final_df['Close'],periods=50))
#             newdf = final_df
#             newdf['o-h'] = np.where((newdf['Open'] == newdf['High']),1,0)
           
#             newdf['o-l'] = np.where((newdf['Open'] == newdf['Low']),2,0)
#             newdf['o-hs'] = np.where((newdf['Open'] == newdf['High']),1,0)
           
#             newdf['o-ls'] = np.where((newdf['Open'] == newdf['Low']),1,0)
#             newdf = newdf.iloc[-100:]
           
#             newdf1 = final_df[final_df.index.time == pd.to_datetime(time_string).time()].reset_index(drop=True)
            
#             last_candle = newdf1.iloc[-1]
            
            
#             if last_candle['o-h'] == 1:#2
#                 sellstock.append(last_candle['symbol'])
#                 st.write(last_candle['symbol'])

                

#                 fig = go.Figure(data=[go.Candlestick(x=newdf.index, open=newdf.Open, close=newdf.Close, high=newdf.High,low=newdf.Low,name=stock),
#                                       go.Scatter(x=newdf.index, y=newdf.ma200, line=dict(color='red', width=2),name='ma200'),
#                                       go.Scatter(x=newdf.index, y=newdf.ma50, line=dict(color='blue', width=2),name='ma500')
#                                       ])
#                 fig.add_trace(
#                     go.Scatter(x=newdf[newdf['o-hs']==1].index, y=newdf[newdf['o-hs']==1]['High'], mode='markers', marker_symbol='triangle-down',
#                                marker_size=25,marker_color='red'))

#                 fig.update_layout(autosize=False, width=1800, height=800, xaxis_rangeslider_visible=False)
#                 fig.layout.xaxis.type = 'category'
                
#                 st.write(' oh sell stratergy')
#                 st.plotly_chart(fig)

#             if last_candle['o-l'] == 2:#3

#                 buystock.append(last_candle['symbol'])
#                 fig = go.Figure(data=[go.Candlestick(x=newdf.index, open=newdf.Open, close=newdf.Close, high=newdf.High,low=newdf.Low,name=stock),                                     
#                                       go.Scatter(x=newdf.index, y=newdf.ma50, line=dict(color='blue', width=2),name='ma500'),
#                                       go.Scatter(x=newdf.index, y=newdf.ma200, line=dict(color='red', width=2),name='ma200')])
#                 fig.add_trace(
#                     go.Scatter(x=newdf[newdf['o-ls']==1].index, y=newdf[newdf['o-ls']==1]['Low'], mode='markers', marker_symbol='triangle-up',
#                                marker_size=25,marker_color='green'))

#                 fig.update_layout(autosize=False, width=1800, height=800, xaxis_rangeslider_visible=False)
#                 fig.layout.xaxis.type = 'category'
                
#                 st.write(' ol buy stratergy')
#                 st.plotly_chart(fig)



#             return
#         except:
#             print('no data')
#             pass


# async def main():
#     async with aiohttp.ClientSession() as session:

#         tasks = []
#         for stocks in s:
#             try:
#                 stock = stocks

#                 task = asyncio.ensure_future(getdata(session, stock))

#                 tasks.append(task)
#             except:
#                 pass
#         df = await asyncio.gather(*tasks)
#         # print(df)


# nest_asyncio.apply()
# asyncio.run(main())





# st.write('buy')
# st.write(buystock)
# st.write('sell')
# st.write(sellstock)

