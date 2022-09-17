# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import tushare as ts
import numpy as np
import pandas as pd

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def Init():
    print("tushare version: ", ts.__version__)
    global pro
    pro = ts.pro_api('fe53d1b0cd472d831db6eba72cb2500c90dc9dc22de4b15badf78a2b')
    # df = pro.trade_cal(exchange='', start_date='20180901', end_date='20181001',
    #                    fields='exchange,cal_date,is_open,pretrade_date', is_open='0')
    # print("df: ", df)

def GetAllBlocks():
    # 查询当前所有正常上市交易的股票列表
    # shData = pro.stock_basic(exchange='SSE', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    # szData = pro.stock_basic(exchange='SZSE', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    shData = pro.stock_basic(exchange='SSE', list_status='L', fields='ts_code')
    szData = pro.stock_basic(exchange='SZSE', list_status='L', fields='ts_code')
    allData = pd.merge(shData, szData, how='left', on='ts_code')
    print(shData)
    print("================")
    print(szData)
    print("all blocks: ")
    print(allData)

def GetTrade():
    tradeDates = pro.trade_cal(exchange='', start_date='20220901', end_date='20220917')
    print(tradeDates)

def TestInfo():
    df = pro.daily(ts_code='000001.SZ', start_date='20220901', end_date='20220917')
    for index, row in df.iterrows():  # 按行遍历
        print("index:", index, " ", row.ts_code, " ", row.trade_date,
              " open: ", row.open, " close: ", row.close)

def IsTradeDate(date):
    tradeDates = pro.trade_cal(exchange='', start_date=date, end_date=date)
    return tradeDates.is_open

# 连续小阳
def IsContinuitySmallRise2():
    startDate = '20220429'
    endDate = '20220523'

    df = pro.daily(ts_code='000159.SZ', start_date=startDate, end_date=endDate)
    print(df)
    riseDate = 0
    for index, row in df.iterrows():  # 按行遍历
        print("index:", index, " ", row.ts_code, " ", row.trade_date,
              " open: ", row.open, " close: ", row.close, " pct_chg: ", row.pct_chg)
        if (row.pct_chg >= 0):
            riseDate = riseDate + 1

    print("riseDate: ", riseDate)

# Press the green button in the gutter to run the script
if __name__ == '__main__':
    Init()
    # GetAllBlocks()
    # GetTrade()
    # TestInfo()
    IsContinuitySmallRise()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
