import time
import datetime
import win32com.client
import pandas as pd
from findata import todayint


def basedata():
    instCpCodeMgr = win32com.client.Dispatch("CpUtil.CpCodeMgr")
    industrydic = {'000': 'UNKNOWN'}
    industrycodelist = (list(instCpCodeMgr.GetIndustryList())
                        + list(instCpCodeMgr.GetKosdaqIndustry1List())
                        + list(instCpCodeMgr.GetKosdaqIndustry2List()))
    for industryCode in industrycodelist:
        industrydic[industryCode] = instCpCodeMgr.GetIndustryName(industryCode)
    kospilist = [(code, "KOSPI") for code in instCpCodeMgr.GetStockListByMarket(1)]
    kosdaqlist = [(code, "KOSDAQ") for code in instCpCodeMgr.GetStockListByMarket(2)]
    codesetlist = [codeset for codeset in kospilist + kosdaqlist
                   if instCpCodeMgr.GetStockControlKind(codeset[0]) == 0
                   and instCpCodeMgr.GetStockSupervisionKind(codeset[0]) == 0
                   and instCpCodeMgr.GetStockStatusKind(codeset[0]) == 0]
    codelist = []
    basedic = {'MARK': [], 'SECT': []}
    for codeset in codesetlist:
        if instCpCodeMgr.GetStockSectionKind(codeset[0]) == 1:
            codelist.append(codeset[0])
            basedic['MARK'].append(codeset[1])
            basedic['SECT'].append("STOCK")
        elif instCpCodeMgr.GetStockSectionKind(codeset[0]) == 10:
            codelist.append(codeset[0])
            basedic['MARK'].append(codeset[1])
            basedic['SECT'].append("ETF")
    basedic['NAME'] = [instCpCodeMgr.CodeToName(code) for code in codelist]
    basedic['INDU'] = [industrydic[instCpCodeMgr.GetStockIndustryCode(code)] for code in codelist]
    basedic['DATE'] = [instCpCodeMgr.GetStockListedDate(code) for code in codelist]
    return pd.DataFrame(basedic, index=codelist, columns=['NAME', 'MARK', 'SECT', 'INDU', 'DATE'])


def stockdata(code, startdate, enddate=0):
    if not enddate:
        enddate = todayint()
    datelist = []
    datadic = {"open": [], "high": [], "low": [],
               "close": [], "volume": [], "dividend": [], "split": []}
    instStockChart = win32com.client.Dispatch("CpSysDib.StockChart")
    instStockChart.SetInputValue(0, code)
    instStockChart.SetInputValue(1, ord('1'))
    instStockChart.SetInputValue(2, enddate)
    instStockChart.SetInputValue(3, startdate)
    instStockChart.SetInputValue(5, (0, 2, 3, 4, 5, 8))
    instStockChart.SetInputValue(6, ord('D'))
    instStockChart.SetInputValue(9, ord('1'))
    instStockChart.BlockRequest()
    numData = instStockChart.GetHeaderValue(3)
    for i in range(numData):
        date = str(instStockChart.GetDataValue(0, i))
        datelist.append(datetime.date(int(date[:4]), int(date[4:6]), int(date[6:])))
        datadic["open"].append(instStockChart.GetDataValue(1, i))
        datadic["high"].append(instStockChart.GetDataValue(2, i))
        datadic["low"].append(instStockChart.GetDataValue(3, i))
        datadic["close"].append(instStockChart.GetDataValue(4, i))
        datadic["volume"].append(instStockChart.GetDataValue(5, i))
        datadic["dividend"].append(0.0)
        datadic["split"].append(1.0)
    result = pd.DataFrame(datadic, index=datelist, columns=("open", "high", "low",
                                                            "close", "volume", "dividend", "split"))
    result.index.name = 'date'
    if datelist:
        last = datelist[-1]
        compdate = last - datetime.timedelta(days=1)
        comp = int(str(compdate.year) + str('{:02d}'.format(compdate.month)) + str('{:02d}'.format(compdate.day)))
        if comp > startdate:
            time.sleep(0.3)
            return pd.concat([result, stockdata(code, startdate, comp)])
        else:
            return result
    return result


def eyedata(code):
    instMarketEye = win32com.client.Dispatch("CpSysDib.MarketEye")
    instMarketEye.SetInputValue(0, (4, 67, 70, 74, 75, 78, 80, 86, 88, 90, 91, 92, 94, 125))
    instMarketEye.SetInputValue(1, code)
    instMarketEye.BlockRequest()
    return (instMarketEye.GetDataValue(0, 0), instMarketEye.GetDataValue(1, 0),
            instMarketEye.GetDataValue(2, 0), instMarketEye.GetDataValue(3, 0),
            instMarketEye.GetDataValue(4, 0), instMarketEye.GetDataValue(5, 0),
            instMarketEye.GetDataValue(6, 0), instMarketEye.GetDataValue(7, 0),
            instMarketEye.GetDataValue(8, 0), instMarketEye.GetDataValue(9, 0),
            instMarketEye.GetDataValue(10, 0), instMarketEye.GetDataValue(11, 0),
            instMarketEye.GetDataValue(12, 0), instMarketEye.GetDataValue(13, 0))