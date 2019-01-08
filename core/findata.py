import datetime
import requests
import numpy as np
import pandas as pd
# from bs4 import BeautifulSoup


def todayint():
    today = datetime.date.today()
    return int('{}{:02d}{:02d}'.format(today.year, today.month, today.day))


def rateinfo(ratenum, lang="en", start=20000101, end=None):
    # [ratenum]
    # 100 : Kor T-Bill(1Y)                101 : Kor T-Bill(3Y)
    # 102 : Kor T-Bill(10Y)               103 : Kor T-Bill(30Y)
    # 104 : Monetary Stabilization(91)    105 : Monetary Stabilization(1Y)
    # 110 : Call Total                    111 : Call Intermediary
    # 112 : CD(91)                        113 : MMF(7)
    # 120 : Corporate(Credit Rating, AA-) 121 : Corporate(3Y, AA-)
    # [lang] : en / kr
    # start, end : YYYYMMDD
    source = "http://ecos.bok.or.kr/api/StatisticSearch/ZJY909ABF1UMF1LTPQBF"
    codedic = {100: '010190000', 101: '010200000', 102: '010210000', 103: '010230000', 104: '010400001',
               105: '010400000', 110: '010101000', 111: '010102000', 112: '010502000', 113: '010501000',
               120: '010310000', 121: '010300000', }
    if not end:
        end = todayint()
    startdate = datetime.date(int(str(start)[:4]), int(str(start)[4:6]), int(str(start)[-2:]))
    enddate = datetime.date(int(str(end)[:4]), int(str(end)[4:6]), int(str(end)[-2:]))
    codes = codedic[ratenum], (enddate-startdate).days
    url = "{}/{}/{}/0/{}/060Y001/DD/{}/{}/{}".format(source, "json", lang, codes[1], start, end, codes[0])
    raw = requests.get(url=url).json()['StatisticSearch']['row']
    unit, index, value = raw[0]['UNIT_NAME'], [], []
    for i in raw:
        index.append(int(i['TIME']))
        value.append(float(i['DATA_VALUE']))
    print(unit)
    return pd.DataFrame({'data': value}, index=index)


def moneyinfo(moneynum, lang="en", start=19960531, end=None):
    # [moneynum] ~ 205, 206, 207 last balance
    # 200 : Base Money        201 : M2                202 : Reserve Requirement
    # 203 : Demand Deposit    204 : Saving Deposit
    # 205 : Household Deposit 206 : Firm Deposit      207 : Others Deposit
    # [lang] : en / kr
    # start, end : YYYYMMDD
    source = "http://ecos.bok.or.kr/api/StatisticSearch/ZJY909ABF1UMF1LTPQBF"
    codedic = {200: ('054Y008', 'ABA1'), 201: ('001Y007', 'BBHA00'), 202: ('050Y001', '1020000'),
               203: ('001Y0048', '1010000'), 204: ('001Y0048', '1020000'),
               205: ('001Y051', '1010000'), 206: ('001Y051', '1020000'), 207: ('001Y051', '1030000'),
               208: (),}
    if not end:
        end = todayint()
    startdate = datetime.date(int(str(start)[:4]), int(str(start)[4:6]), int(str(start)[-2:]))
    enddate = datetime.date(int(str(end)[:4]), int(str(end)[4:6]), int(str(end)[-2:]))
    codes = codedic[ratenum], (enddate-startdate).days
    url = "{}/{}/{}/0/{}/060Y001/MM??/{}/{}/{}".format(source, "json", lang, codes[1], start, end, codes[0])
    raw = requests.get(url=url).json()['StatisticSearch']['row']
    unit, index, value = raw[0]['UNIT_NAME'], [], []
    for i in raw:
        index.append(int(i['TIME']))
        value.append(float(i['DATA_VALUE']))
    print(unit)
    return pd.DataFrame({'data': value}, index=index)


def loaninfo(loannum, lang="en", start=19960531, end=None):
    # [loannum]
    # 300 : Total
    # INDUSTRY
    # 301 : Industry Total    302 : Agriculture       303 : Mining
    # 304 : Manufacturing     305 : Electricity, Gas  306 : Water, Waste
    # 307 : Construction      308 : Wholesale, Retail 309 : Trans., Storage
    # 310 : Accommo., Food    311 : Info., Commun.    312 : Finance., Insure.
    # 313 : Real Estate       314 : Prof., Science    315 : Business Manage.
    # 316 : Education         317 : Health, Social    318 : Public
    # HOUSEHOLD
    # 319 : Household Total   320 : Household Loan    321 : Merchandise credit
    # 322 : Commercial Bank   323 : Non-Bank Deposit. 324 : Other Finance.
    # 325 : Mortgage Total    326 : Other Loan Total  327 : Comm. Mortgage
    # 328 : Comm. Other Loan  329 : Non-Bank Mortgage 330 : Non-Bank Other Loan
    # Delinquency Ratio
    # 331 : Enterprise        332 : Household         333 : Credit Card
    # [lang] : en / kr
    # start, end : YYYYMMDD
    source = "http://ecos.bok.or.kr/api/StatisticSearch/ZJY909ABF1UMF1LTPQBF"
    codedic = {}
    return None


def justbefore(datelist, term='M'):
    # date before a month(M) or a week(W)
    # datelist: iterable consisted of yyyymmdd style int.s
    # if 'term' is 'M', and the date is 29, 30, or 31, changes to 28
    # latest day comes first
    comp = datelist[0]
    if term == 'M' and int(str(comp)[-2:]) >= 29:
        comp = int(str(comp)[:-2] + '28')
    for d in datelist[1:]:
        if d > comp:
            continue
        elif d <= comp:
            year = int(str(comp)[:4])
            month = int(str(comp)[4:6])
            day = int(str(comp)[-2:])
            if term == 'W':
                date = datetime.date(year, month, day)
                delta = datetime.timedelta(weeks=1)
                date -= delta
                comp = int('{}{:02d}{:02d}'.format(date.year, date.month, date.day))
                yield d
            elif term == 'M':
                month -= 1
                if month == 0:
                    year, month = year-1, 12
                date = datetime.date(year, month, day)
                comp = int('{}{:02d}{:02d}'.format(date.year, date.month, date.day))
                yield d


def corredges(dic):
    first = list(dic.keys())
    na, nb, co = [], [], []
    for i, a in enumerate(first[:-1]):
        alen = len(dic[a])
        print("Calculating Correlation... ({}/{})".format(i+1, len(first)-1))
        for b in first[i+1:]:
            blen = len(dic[b])
            if alen >= blen:
                corr = np.corrcoef(dic[a][:blen], dic[b])[0][1]
            else:
                corr = np.corrcoef(dic[a], dic[b][:alen])[0][1]
            if np.isnan(corr):
                corr = 0
            na.append(a)
            nb.append(b)
            co.append(corr)
    return pd.DataFrame({'a': na, 'b': nb, 'corr': co})


# def crawldata(code, lastupdate=0):
#     # NOT AVAILABLE
#     page, nex = 0, 1
#     date = []
#     assetdict = {'close': [], 'volume': []}
#     while nex:
#         page += 1
#         url = "http://finance.daum.net/item/quote_yyyymmdd_sub.daum?page={}&code={}&modify=1".format(page, code)
#         r = requests.get(url)
#         soup = BeautifulSoup(r.content, 'html.parser')
#         infolist = soup.find_all("tr", {"onmouseout": "highlight(this,false)"})
#         for inf in infolist:
#             text = inf.text.replace(".", "").replace(",", "").split("\n")
#             if int(text[1]) > 500000:
#                 d = int("19" + text[1])
#             else:
#                 d = int("20" + text[1])
#             if d > lastupdate:
#                 date.append(d)
#                 assetdict['close'].append(int(text[5]))
#                 assetdict['volume'].append(int(text[-2]))
#             else:
#                 return pd.DataFrame(assetdict, index=date, columns=['close', 'volume'])
#         nex = soup.find("span", {"class", "jumpNext"})
#     return pd.DataFrame(assetdict, index=date, columns=['close', 'volume'])
