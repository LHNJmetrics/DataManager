import sqlite3
import time
import sys
import numpy as np
import pandas as pd
from findata import justbefore
from cybosbase import basedata, stockdata


class FormError(Exception):
    def __str__(self):
        return "'form' should be 'db'(default) or 'csv'"


class InputError(Exception):
    def __str__(self):
        return "'address' and 'form' are the only possible inputs"


class RangeError(Exception):
    def __str__(self):
        return "out of range"


def make_usable(data, term='M'):
    # DataFrame(index=date, column=['close', 'volume'])으로 받은 주가 정보를 사용가능한 형태로 변환
    # 주가, 거래량, 로그수익률, 거래량변동률
    dates = [d for d in justbefore(data.index, term)]
    df = data.reindex(dates)
    latter = np.array(df.ix[dates[:-1]])
    former = np.array(df.ix[dates[1:]])
    rates = pd.Series(np.log(latter[:, 0] / former[:, 0]), index=dates[:-1])
    vol_fluc = pd.Series(np.log(latter[:, 1] / former[:, 1]), index=dates[:-1])
    df = df.drop(dates[-1], 0)
    df['RATES'] = rates
    df['VOLFL'] = vol_fluc
    return df


def makedb(address="D:\\yodadb", form="db"):
    bd = basedata()
    allcodes = bd.index
    if form == "db":
        raws = sqlite3.connect(address + "\\raws.db")
    total = len(allcodes)
    last = []
    for i, code in enumerate(allcodes):
        sd = stockdata(code, int(bd.DATE[code])).iloc[::-1]
        last.append(sd.index[0])
        if form == "db":
            sd.to_sql('{}'.format(code), raws, if_exists='replace', index_label='date')
        elif form == "csv":
            sd.to_csv(address + "\\{}.csv".format(code), index_label='date')
        else:
            raise FormError
        print("{} raw({}/{})".format(code, i + 1, total))
        time.sleep(0.3)
    bd['LAST'] = last
    if form == "db":
        bd.to_sql('allcode', raws, if_exists='replace', index_label='code')
    elif form == "csv":
        bd.to_csv(address + "\\allcode.csv", index_label='code')
    print("all code complete")


def timetable():
    pass


if __name__ == "__main__":
    if len(sys.argv) == 1:
        address = "D:\\yodadb"
        form = "db"
    elif len(sys.argv) == 2:
        if sys.argv[1] in ['db', 'csv']:
            address = "D:\\yodadb"
            form = sys.argv[1]
        else:
            address = sys.argv[1]
            form = "db"
    elif len(sys.argv) == 2:
        address = sys.argv[1]
        form = sys.argv[2]
    else:
        raise InputError
    makedb(address=address, form=form)
