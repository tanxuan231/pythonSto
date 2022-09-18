# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import datetime
import tushare as ts
import numpy as np
import pandas as pd

def Init():
    global pro
    # 186
    #pro = ts.pro_api('fe53d1b0cd472d831db6eba72cb2500c90dc9dc22de4b15badf78a2b')
    # 177
    pro = ts.pro_api('f8653060b31a45bfa403d40fd01ad59f01615b4af974e3e2772552b4')

def GetAllBlocks():
    # 查询当前所有正常上市交易的股票列表
    # shData = pro.stock_basic(exchange='SSE', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    # szData = pro.stock_basic(exchange='SZSE', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    shData = pro.stock_basic(exchange='SSE', list_status='L', fields='ts_code')
    szData = pro.stock_basic(exchange='SZSE', list_status='L', fields='ts_code')
    allData = pd.merge(shData, szData, how='left', on='ts_code')

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

def IsSmallRise(tradeData, startDate, endDate, riseRatio):
    df = pro.daily(ts_code=tradeData.ts_code, start_date=startDate, end_date=endDate)
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

# 连续小阳
# 1. 价额位于8个月以来的相对低点
# 2. 不能是新股
def IsContinuitySmallRise(tsCode, movingAverageRiseRatio):
    riseRatio = 0.65
    spanDays = 20   # 统计的交易日
    # 获取近12个月时间的数据
    startDate = (datetime.datetime.now() + datetime.timedelta(days=-550)).strftime("%Y%m%d")
    endDate = datetime.datetime.now().strftime("%Y%m%d")
    # print("date: ", startDate, " => ", endDate)
    df = pro.daily(ts_code=tsCode, start_date=startDate, end_date=endDate)

    # 排除2个月内的新股 40
    newStock = 40
    if df.shape[0] < newStock:
        print("df length time ", df.shape[0], " < ", newStock, " days, is a new trade code: ", tsCode)
        return False

    maxClosePrice = 0   # 统计最大的收盘价

    movingAverageDays = 3  # 移动平均计算天数
    lastAverageClose = -100   # 上轮移动平均收盘价
    lastAveragePctChg = -100
    movingCloseRiseDays = 0      # 收盘价的移动平均上涨天数
    movingPctChgRiseDays = 0    # 涨跌幅的移动平均上涨天数

    lowRiseDays = 0   # 小幅上涨的天数
    highRiseDays = 0  # 大幅上涨的天数
    highFallDays = 0  # 下跌幅度过大的天数
    for index, row in df.iterrows():  # 按行遍历
        # print("index:", index, " ", row.ts_code, " ", row.trade_date,
        #       " open: ", row.open, " close: ", row.close, " pct_chg: ", row.pct_chg)
        if maxClosePrice < row.close:
            maxClosePrice = row.close
            maxCloseData = row
        if index + 1 < movingAverageDays:
            continue
        if index >= spanDays:
            continue
        # 取(index - movingAverageDays, index]行数据
        movingDatas = df.iloc[index - movingAverageDays : index, : ]
        wholeClose = 0
        wholePctChg = 0
        for j, row2 in movingDatas.iterrows():
            # print("j:", j, " ", row2.ts_code, " ", row2.trade_date,
            #       " open: ", row2.open, " close: ", row2.close, " pct_chg: ", row2.pct_chg)
            wholeClose = wholeClose + row2.close
            wholePctChg = wholePctChg + row2.pct_chg
        curAverageClose = wholeClose/movingAverageDays
        curAveragePctChg = wholePctChg/movingAverageDays
        # print("curAverageClose: ", curAverageClose, " lastAverageClose: ", lastAverageClose, " wholeClose: ", wholeClose)
        # print("curAveragePctChg: ", curAveragePctChg, " lastAveragePctChg: ", lastAveragePctChg, " wholePctChg: ", wholePctChg)
        if lastAverageClose != -100 and curAverageClose <= lastAverageClose:
            # print("movingCloseRiseDays from ", movingCloseRiseDays, " to ", movingCloseRiseDays+1)
            movingCloseRiseDays = movingCloseRiseDays + 1
        if lastAveragePctChg != -100 and curAveragePctChg <= lastAveragePctChg:
            movingPctChgRiseDays = movingPctChgRiseDays + 1
        lastAverageClose = curAverageClose
        lastAveragePctChg = curAveragePctChg

        if row.pct_chg >= -1.0 and row.pct_chg <= 6.0:
            lowRiseDays = lowRiseDays + 1
        elif row.pct_chg <= -7.0:
            highFallDays = highFallDays + 1
        elif row.pct_chg >= 7.0:
            highRiseDays = highRiseDays + 1

    print("============================ compute over fro code: ", tsCode, " ===============================")
    if maxClosePrice < 1.6*lastAverageClose:
        print("maxClosePrice: ", maxClosePrice, " lastAverageClose: ", lastAverageClose, ", return false")
        print("maxCloseData: ", maxCloseData.trade_date, " close: ", maxCloseData.close, " code: ", maxCloseData.ts_code)
        return False

    if highFallDays >= 3:
        print("tsCodes: ", tsCode, " highFallDays: ", highFallDays, " >= 3, return false")
        return False
    # if highRiseDays > 3:
    #     print("tsCodes: ", tsCode, " highRiseDays: ", highRiseDays, " > 3, return false")
    #     return False

    # 移动平均上涨概率
    movingAverageRiseRatio = movingCloseRiseDays/spanDays
    if movingAverageRiseRatio >= riseRatio:
        print("tsCodes: ", tsCode, " movingCloseRiseDays: ", movingCloseRiseDays,
              " movingAverageRiseRatio: ", movingAverageRiseRatio, ",return true")
        return True
    else:
        print("tsCodes: ", tsCode, " movingCloseRiseDays: ", movingCloseRiseDays,
              " movingAverageRiseRatio: ", movingAverageRiseRatio, ",return false")
        return False

def Test():
    shMovingCloseRiseDatas = []
    movingAverageRiseRatio = 0.0
    # 上海
    shTradeDatas = pro.stock_basic(exchange='SSE', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    for index, row in shTradeDatas.iterrows():  # 按行遍历
        if IsContinuitySmallRise(row.ts_code, movingAverageRiseRatio):
            shMovingCloseRiseDatas.append(row.ts_code)

    # 深圳
    szTradeDatas = pro.stock_basic(exchange='SZSE', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    for index, row in szTradeDatas.iterrows():  # 按行遍历
        if IsContinuitySmallRise(row.ts_code, movingAverageRiseRatio):
            shMovingCloseRiseDatas.append(row.ts_code)

    print("*****============ shMovingCloseRiseDatas len: ", len(shMovingCloseRiseDatas), " ==========*****")
    for i, val in enumerate(shMovingCloseRiseDatas):
        print("i: ", i, " code: ", val)

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
    Test()
