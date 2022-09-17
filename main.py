# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import datetime
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

def IsContinuitySmallRise(tradeData, startDate, endDate, riseRatio):
    df = pro.daily(ts_code=tradeData.ts_code, start_date=startDate, end_date=endDate)
    # print(" all trade days: ", df.shape[0])
    # print(df)
    lowRiseDays = 0   # 小幅上涨的天数
    highRiseDays = 0  # 大幅上涨的天数
    highFallDays = 0  # 下跌幅度过大的天数
    for index, row in df.iterrows():  # 按行遍历
        # print("index:", index, " ", row.ts_code, " ", row.trade_date,
        #       " open: ", row.open, " close: ", row.close, " pct_chg: ", row.pct_chg)
        if row.pct_chg >= -1.0 and row.pct_chg <= 6.0:
            lowRiseDays = lowRiseDays + 1
        elif row.pct_chg <= -7.0:
            highFallDays = highFallDays + 1
        elif row.pct_chg >= 7.0:
            highRiseDays = highRiseDays + 1

    if highFallDays >= 3:
        print("tsCodes: ", tradeData.ts_code, " highFallDays: ", highFallDays, " >= 3, return false")
        return False
    # if highRiseDays > 3:
    #     print("tsCodes: ", tradeData.ts_code, " highRiseDays: ", highRiseDays, " > 3, return false")
    #     return False

    ratio = lowRiseDays/df.shape[0]
    if ratio >= riseRatio:
        print("tsCodes: ", tradeData.ts_code, " riseDate: ", ratio, " >= ", riseRatio,
              " all trade days: ", df.shape[0], " ,return true")
        return True
    else:
        print("tsCodes: ", tradeData.ts_code, " riseDate: ", ratio, " < ", riseRatio,
              " all trade days: ", df.shape[0], " ,return false")
        return False

def TestAllTrades():
    spanDays = 19
    riseRatio = 0.8
    startDate = (datetime.datetime.now() + datetime.timedelta(days=-spanDays)).strftime("%Y%m%d")
    endDate = datetime.datetime.now().strftime("%Y%m%d")

    shTradeDatas = pro.stock_basic(exchange='SSE', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    shSmallRiseDatas = []
    for index, row in shTradeDatas.iterrows():  # 按行遍历
        interval = datetime.datetime.strptime(endDate, '%Y%m%d') - datetime.datetime.strptime(row.list_date, "%Y%m%d")

        if interval.days < 50:
            print("interval: ", interval.days, " < 50 days")
            break
        if index == 5:
            break
        if IsContinuitySmallRise(row, startDate, endDate, riseRatio):
            shSmallRiseDatas.append(row.ts_code)

    print("======= shSmallRiseDatas len: ", len(shSmallRiseDatas))
    for i, val in enumerate(shSmallRiseDatas):
        print("index:", i, " ", val)

# Press the green button in the gutter to run the script
if __name__ == '__main__':
    Init()
    # GetAllBlocks()
    # GetTrade()
    # TestInfo()
    # IsContinuitySmallRise()
    TestAllTrades()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
