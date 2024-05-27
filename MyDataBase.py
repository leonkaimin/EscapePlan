
import sqlite3
import os
import wget
import MyMath as mymath
from datetime import datetime
from datetime import datetime as Date
import datetime as Datetime
import sys
import json
from multiprocessing import Pool, current_process
import time as Time
import csv
from MyQuery import *
from MyFieldNum import *
from MyDownload import *
import nums_from_string
from MyTime import quarter_to_months, date_to_quarter, quarter_list
import re
from settings import *
import statistics

import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

now = datetime.now()

KLASS = [
    "ETF",
    "水泥工業",
    "食品工業",
    "塑膠工業",
    "建材營造",
    "汽車工業",
    "其他",
    "紡織纖維",
    "運動休閒",
    "電子零組件業",
    "電機機械",
    "電器電纜",
    "生技醫療業",
    "化學工業",
    "玻璃陶瓷",
    "造紙工業",
    "鋼鐵工業",
    "居家生活",
    "橡膠工業",
    "航運業",
    "電腦及週邊設備業",
    "半導體業",
    "其他電子業",
    "通信網路業",
    "光電業",
    "電子通路業",
    "資訊服務業",
    "貿易百貨",
    "油電燃氣業",
    "觀光餐旅",
    "金融保險業",
    "數位雲端",
    "綠能環保",
]


def validate(date_text):
    try:
        if date_text != datetime.strptime(date_text, "%Y/%m/%d").strftime('%Y/%m/%d'):
            raise ValueError
        return True
    except ValueError:
        return False


def read_pocket_list(path):
    with open(path, "r") as reserve_file:
        pocket_list = csv.reader(reserve_file)
        return [r for r in pocket_list]


def get_date_range(start_date, end_date):
    date_format = '%Y-%m-%d'  # 設定日期格式
    start_datetime = datetime.strptime(
        start_date, date_format)  # 將起始日期轉換為datetime物件
    end_datetime = datetime.strptime(
        end_date, date_format)  # 將結束日期轉換為datetime物件
    date_list = []  # 儲存日期的list

    # 從起始日期開始，每次加1天，直到到達結束日期
    while start_datetime <= end_datetime:
        # 將當前日期轉換為字串，並加入date_list
        date_list.append(datetime.strftime(start_datetime, date_format))
        start_datetime += Datetime.timedelta(days=1)  # 加1天

    return date_list


def str2d(d):
    if (d < 10):
        return str("0")+str(d)
    else:
        return str(d)


def tryfloat(numstr, numerr=0):
    try:
        f = float(numstr)
        return f
    except ValueError:
        return numerr


def get_field_num(tab, name):

    if (tab == "STOCK"):
        f = stock_fields_num
    elif (tab == "AMOUNT"):
        f = amount_fields_num
    elif (tab == "FUNDAMENTAL"):
        f = fund_fields_num

    return f[name]


class MyDataBase():

    sleep_time = 1

    def __init__(self, db_path=f"{settings['data_root']}/database/default.db"):

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()

    def insert_stock_table(self, date, code, name, shares, entries, amount, oprice,
                           highest, lowest, cprice, fluctuation):

        param = [date, code, name, shares, entries, amount, oprice,
                 highest, lowest, cprice, fluctuation]

        for p in param:
            if p is None:
                return

        query = INSERT_STOCK.format(
            date,
            code,
            name,
            shares,
            entries,
            amount,
            oprice,
            highest,
            lowest,
            cprice,
            fluctuation
        )
        # print(query)
        c = self.conn.cursor()
        c.execute(query)

    def insert_eps_table(self, quater, code, name, val):

        param = [quater, code, name, val]

        for p in param:
            if p is None:
                return

        try:
            float(val)
        except ValueError:
            return

        query = INSERT_EPS.format(
            quater,
            code,
            name,
            val
        )
        # print(query)
        c = self.conn.cursor()
        c.execute(query)

    def insert_margin_table(self, date, code, name, margin, short):
        param = [date, code, name, margin, short]

        for p in param:
            if p is None:
                return False

        query = INSERT_MARGIN.format(
            date,
            code,
            name,
            margin,
            short
        )
        # print(query)
        c = self.conn.cursor()
        c.execute(query)
        return True

    def insert_legal_table(self, date, code, name, legal):
        param = [date, code, name, legal]

        for p in param:
            if p is None:
                return False

        query = INSERT_LEGAL.format(
            date,
            code,
            name,
            legal
        )
        # print(query)
        c = self.conn.cursor()
        c.execute(query)
        return True

    def insert_etfdiv_table(self, date, code, name, val):

        param = [date, code, name, val]

        for p in param:
            if p is None:
                return

        try:
            float(val)
        except ValueError:
            return

        query = INSERT_ETFDIV.format(
            date,
            code,
            name,
            val
        )
        # print(query)
        c = self.conn.cursor()
        c.execute(query)

    def insert_basic_table(self, code, name, capital, deno, klass):

        param = [code, name, capital, deno]

        for p in param:
            if p is None:
                return

        try:
            float(capital)
            float(deno)
        except ValueError:
            return

        query = INSERT_BASIC.format(
            code,
            name,
            capital,
            deno,
            klass
        )
        #print(query)
        c = self.conn.cursor()
        c.execute(query)

    def insert_NPM_table(self, quater, code, name, val):

        param = [quater, code, name, val]

        for p in param:
            if p is None:
                return

        try:
            float(val)
        except ValueError:
            return

        query = INSERT_NPM.format(
            quater,
            code,
            name,
            val
        )
        # print(query)
        c = self.conn.cursor()
        c.execute(query)

    def insert_revenue_table(self, month, code, name, val):

        param = [month, code, name, val]

        for p in param:
            if p is None:
                return

        try:
            float(val)
        except ValueError:
            return

        query = INSERT_REVENUE.format(
            month,
            code,
            name,
            val
        )
        # print(query)
        c = self.conn.cursor()
        c.execute(query)

    def insert_book_table(self, quater, code, name, val):

        param = [quater, code, name, val]

        for p in param:
            if p is None:
                return

        try:
            float(val)
        except ValueError:
            return

        query = INSERT_BOOK.format(
            quater,
            code,
            name,
            val
        )
        c = self.conn.cursor()
        # print(query)
        c.execute(query)

    def insert_fund_table(self, date, code, name, per, pbr, dyr):

        param = [date, code, name, name, per, pbr, dyr]

        for p in param:
            if p is None:
                return

        query = INSERT_FUNDAMENTAL.format(
            date,
            code,
            name,
            per,
            pbr,
            dyr
        )

        c = self.conn.cursor()
        # print(query)
        c.execute(query)

    def load_stock_tab(self, field=None,  code=None, end=None, begin=None, date=None, limit=None):
        cursor = self.conn.cursor()

        lim = ""
        if limit is not None:
            lim = f"DESC LIMIT {limit}"

        conditions = []
        if field is None:
            field = "*"
        else:
            field = f"DATE, {field}"

        if begin is not None:
            conditions.append(f"DATE > '{begin}'")
        if end is not None:
            conditions.append(f"DATE <= '{end}'")
        if date is not None:
            conditions.append(f"DATE = '{date}'")
        if code is not None:
            conditions.append(f"CODE = '{code}'")
        whereclause = f"WHERE "
        if len(conditions) > 0:
            whereclause += " AND ".join(conditions)

        query = SELECT_STOCK.format(field, whereclause, lim)
        # print(query)
        cursor.execute(query)
        return cursor.fetchall()

    def load_stock_dict(self, code, field, end=None, begin=None):
        tab = self.load_stock_tab(field, code=code, begin=begin, end=end)
        return self.toDict(tab)

    def load_stock_dict_tuple(self, code, field, end=None, begin=None):
        tab = self.load_stock_tab(field, code=code, begin=begin, end=end)
        return self.toDict_tuple(tab)

    def load_tab(self, code, tab, end=None, begin=None, limit=None):
        cursor = self.conn.cursor()

        fromtab = f"SELECT * FROM {tab}"
        wherecode = f" WHERE CODE = '{code}'"

        begindate = ""
        if begin is not None:
            begindate = f" AND DATE > '{begin}'\n"

        enddate = ""
        if end is not None:
            enddate = f" AND DATE <= '{end}'\n"

        orderdate = " ORDER BY DATE"
        if limit is not None:
            orderdate = f" ORDER BY DATE DESC LIMIT {limit}"

        query = f"{fromtab}{wherecode}{begindate}{enddate}{orderdate}"
        # print(query)
        cursor.execute(query)
        return cursor.fetchall()

    def load_EPS_quater_tab(self, quater):
        cursor = self.conn.cursor()

        wherecode = f" WHERE QUATER = '{quater}'"
        query = SELECT_EPS.format(wherecode)

        cursor.execute(query)
        return cursor.fetchall()

    def load_EPS_tab(self, code):
        cursor = self.conn.cursor()

        wherecode = f" WHERE CODE = '{code}'"
        query = SELECT_EPS.format(wherecode)

        cursor.execute(query)
        return cursor.fetchall()

    def load_EPS_quater(self, quater):
        tab = self.load_EPS_quater_tab(quater)
        return [t[3]for t in tab]

    def load_EPS(self, code):
        tab = self.load_EPS_tab(code)
        return {t[0]: t[3] for t in tab}

    def load_EPS_tab_season(self, code, year, season):
        cursor = self.conn.cursor()

        wherecode = f" WHERE CODE = '{code}' and QUATER = '{year}Q{season}'"
        query = SELECT_EPS.format(wherecode)
        # print(query)
        cursor.execute(query)
        return cursor.fetchall()

    def load_EPS_season(self, code, year, season):
        tab = self.load_EPS_tab_season(code, year, season)
        if len(tab) > 0:
            return [t[3]for t in tab][0]
        return 0

    def load_ETFDIV_tab(self, code):
        cursor = self.conn.cursor()

        wherecode = f" WHERE CODE = '{code}'"
        query = SELECT_ETFDIV.format(wherecode)

        cursor.execute(query)
        return cursor.fetchall()

    def load_ETFDIV(self, code):
        tab = self.load_ETFDIV_tab(code)
        etfdiv = {}
        if len(tab) <= 0:
            return etfdiv
        qlist = quarter_list(tab[0][0], tab[-1][0])
        for q in qlist:
            etfdiv[q] = 0
        for t in tab:
            date = t[0]
            # print(date)
            quater = date_to_quarter(date)
            if not quater in etfdiv:
                etfdiv[quater] = 0
            etfdiv[quater] += t[3]

        etfdiv = list(etfdiv.values())
        new_etfdiv = []
        count = 0
        e = 0
        for i in range(len(etfdiv)-1, 0, -1):

            e += float(etfdiv[i])
            count += 1
            if count == 4:
                new_etfdiv.insert(0, e)
                count = 0
                e = 0

        return new_etfdiv

    def load_margin_tab(self, code):
        cursor = self.conn.cursor()

        wherecode = f" WHERE CODE = '{code}'"
        # print(wherecode)
        query = SELECT_MARGIN.format(wherecode)
        # print(query)
        cursor.execute(query)
        return cursor.fetchall()

    def load_margin(self, code):
        tab = self.load_margin_tab(code)
        return {t[0]: [t[3], t[4]] for t in tab}

    def load_NPM_tab(self, code):
        cursor = self.conn.cursor()

        wherecode = f" WHERE CODE = '{code}'"
        query = SELECT_NPM.format(wherecode)
        # print(query)
        cursor.execute(query)
        return cursor.fetchall()

    def load_NPM(self, code):
        tab = self.load_NPM_tab(code)
        return {t[0]: t[3] for t in tab}

    def load_NPM_items(self, code):
        return [i[1] for i in self.load_NPM(code).items()]

    def load_revenue_tab(self, code):
        cursor = self.conn.cursor()

        wherecode = f" WHERE CODE = '{code}'"
        query = SELECT_REVENUE.format(wherecode)
        # print(query)
        cursor.execute(query)
        return cursor.fetchall()

    def load_revenue(self, code):
        revenue_tab = self.load_revenue_tab(code)
        return {t[0]: t[3] for t in revenue_tab}

    def load_revenue_items(self, code):
        return [i[1] for i in self.load_revenue(code).items()]

    def load_revenue_tab_month(self, code, year, month):
        cursor = self.conn.cursor()

        wherecode = f" WHERE CODE = '{code}' and MONTH = '{year}/{month}'"
        query = SELECT_REVENUE.format(wherecode)
        # print(query)
        cursor.execute(query)
        return cursor.fetchall()

    def load_revenue_month(self, code, year, month):
        revenue_tab = self.load_revenue_tab_month(code, year, month)
        if len(revenue_tab) > 0:
            return [t[3]for t in revenue_tab][0]
        return 0

    def load_book_tab(self, code):
        cursor = self.conn.cursor()

        wherecode = f" WHERE CODE = '{code}'"
        query = SELECT_BOOK.format(wherecode)

        cursor.execute(query)
        return cursor.fetchall()

    def load_book(self, code):
        tab = self.load_book_tab(code)
        return [t[3]for t in tab]

    def load_bond_etf_codename(self, day):

        arr = []
        c = self.conn.cursor()
        query = SELECT_DISTINCT_CODE_BOND.format(
            day.strftime("%Y-%m-%d"))
        # print(query)
        c.execute(query)
        tab = c.fetchall()
        for i in range(len(tab)):
            arr.append(tab[i])
        if (not len(arr) > 0):
            prev_day = day - Datetime.timedelta(days=1)
            return self.load_bond_etf_codename(prev_day)
        # print(arr)
        return arr

    def load_codename(self, klass=None, like=None):
        whereklass = ''
        wherecode = ''
        if like is not None:
            wherecode = f" AND CODE like '{like}'"

        if klass is not None:
            whereklass = f" AND CLASS like '{klass}%'"
        arr = []
        c = self.conn.cursor()
        query = SELECT_DISTINCT_CODE.format(whereklass, wherecode)
        # print(query)
        c.execute(query)
        tab = c.fetchall()
        for i in range(len(tab)):
            arr.append(tab[i])
        # print(arr)
        return arr

    def load_code(self, klass=None, like=None):

        codes = [c[0] for c in self.load_codename(klass=klass, like=like)]

        # print(codes)
        return codes

    def load_issue_shares(self, code):
        cap, deno, klass = self.load_basic(code)
        if cap is not None or deno is not None:
            issue_shares = cap/deno
            return issue_shares
        return None

    def load_klass(self, code):
        cap, deno, klass = self.load_basic(code)
        if klass is not None:
            return klass
        return None

    def load_fluctuation_count_tab(self):
        c = self.conn.cursor()
        query = "SELECT DATE, COUNT(case when FLUCATION < 0 then 1 end), COUNT(case when FLUCATION > 0 then 1 end) FROM STOCK GROUP BY DATE;"
        # print(query)
        c.execute(query)
        tab = c.fetchall()
        return tab

    def count_on_date(self, date):
        c = self.conn.cursor()
        query = "select count(1) from STOCK where DATE = \"{}\"".format(date)
        # print(query)
        c.execute(query)
        row = c.fetchone()
        return row[0]

    def create_table(self):
        c = self.conn.cursor()
        c.execute(CREATE_STOCK_TABLE)
        c.execute(CREATE_AMOUNT_TABLE)
        c.execute(CREATE_FUNDAMENTAL_TABLE)
        c.execute(CREATE_EPS_TABLE)
        c.execute(CREATE_BOOK_TABLE)
        c.execute(CREATE_REVENUE_TABLE)
        c.execute(CREATE_NPM_TABLE)
        c.execute(CREATE_BASIC_TABLE)
        c.execute(CREATE_ETFDIV_TABLE)
        c.execute(CREATE_MARGIN_TABLE)
        c.execute(CREATE_LEGAL_TABLE)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def load_listed_stock_table(self, jdata):
        data = None
        state = None
        for key, value in jdata.items():
            if "data" in key:
                if (len(value) > 0):
                    if len(value[0]) == 16:
                        data = value
                    else:
                        continue
                else:
                    # print(value)
                    # print("UNEXPECTED ERROR!FIX IT MANUALLY!")
                    # sys.exit()
                    continue
            elif key == 'stat':
                state = value

        if state != "OK":
            if state == "很抱歉，沒有符合條件的資料!":
                return None
            else:
                print("stat: {}".format(state))
                print("jdata: {}".format(jdata))
                print("UNEXPECTED ERROR!FIX IT MANUALLY!")
                sys.exit()
        else:
            if data is not None:
                return data
            else:
                print("stat: {}".format(state))
                print("jdata: {}".format(jdata))
                print("UNEXPECTED ERROR!FIX IT MANUALLY!")
                sys.exit()

    def load_OTC_stock_table(self, jdata):
        data = None

        for key, value in jdata.items():
            if "aaData" in key:
                data = value
            elif "totalCount" in key:
                if value == 0:
                    return None
            else:
                # print(value)
                # print("UNEXPECTED ERROR!FIX IT MANUALLY!")
                # sys.exit()
                continue

        return data

    def download_fund_to_sqlite(self, y, m, d):

        date = Date(y, m, d).strftime('%Y-%m-%d')
        fund_fname = f'./fund/' + \
            Date(y, m, d).strftime('%Y_%m_%d') + '.csv'

        if not os.path.isfile(fund_fname):
            fund_fname = download_fund_csv_file(y, m, d)
            Time.sleep(3)
        if fund_fname is None:
            print("File is not on-line %s" % (date))
            return False

        with open(fund_fname, "r", encoding="cp950") as csvfile:
            fund_data = csv.reader(csvfile)
            rows = [r for r in fund_data]

            count = 0
            for r in rows:

                if len(r) == 7 and r[0].isnumeric and len(r[0]) == 4:
                    code = r[0]
                    name = r[1]
                    per = tryfloat(r[4])
                    pbr = tryfloat(r[5])
                    dyr = tryfloat(r[2])
                    self.insert_fund_table(date, code, name, per, pbr, dyr)
                    count = count + 1
                elif len(r) == 8 and r[0].isnumeric and len(r[0]) == 4:
                    code = r[0]
                    name = r[1]
                    per = tryfloat(r[4])
                    pbr = tryfloat(r[5])
                    dyr = tryfloat(r[2])
                    self.insert_fund_table(date, code, name, per, pbr, dyr)
                    count = count + 1
                elif len(r) == 6 and r[0].isnumeric and len(r[0]) == 4:
                    code = r[0]
                    name = r[1]
                    per = tryfloat(r[2])
                    pbr = tryfloat(r[4])
                    dyr = tryfloat(r[3])
                    self.insert_fund_table(date, code, name, per, pbr, dyr)
                    count = count + 1

            if (count == 0):
                day = Date(y, m, d).weekday()
                print("{} Empty fund csv table ".format(date), end="")
                if (day == 5 or day == 6):
                    print("Weekend OK", end="")
                    print()
                    return False

                print("fund count 0 failed".format(date))
                return False

            print("{} fund {} OK".format(date, count))
            return True

    def download_OTC_fundamental_to_sqlite(self, y, m, d):

        date = Date(y, m, d).strftime('%Y-%m-%d') + ".csv"
        fund_fname = f"{settings['data_root']}/OTC_fundamental/" + \
            Date(y, m, d).strftime('%Y_%m_%d') + ".csv"

        if not os.path.isfile(fund_fname):
            fund_fname = download_OTC_fund_csv_file(
                str(y), str2d(m), str2d(d))
            Time.sleep(1)
        if fund_fname is None:
            print("File is not on-line %s" % (date))
            return False

        with open(fund_fname, "r") as csvfile:
            fund_data = csv.reader(csvfile)
            rows = [r for r in fund_data]

            count = 0
            for r in rows:

                if len(r) >= 7 and r[0].isdigit() and len(r[0]) == 4:
                    # print(r)
                    code = r[0]
                    name = r[1]
                    per = tryfloat(r[2])
                    pbr = tryfloat(r[6])
                    dyr = tryfloat(r[5])

                    self.insert_fund_table(
                        date, code, name, per, pbr, dyr)
                    count = count + 1

            if (count == 0):
                day = Date(y, m, d).weekday()
                print(f"{date} Empty OTC fund csv table ", end="")
                if (day == 5 or day == 6):
                    print("Weekend OK", end="")
                    print()
                    return False

                print(f"{date} OTC fund count 0 failed")
                return False

            print(f"{date} OTC fund {count} OK")
            return True

    def download_listed_data_to_sqlite(self, date):

        filename = f"{settings['data_root']}/listed_data/" + \
            date.strftime('%Y_%m_%d') + ".csv"

        if not os.path.isfile(filename):
            filename = download_listed_data_csv(
                date)
            Time.sleep(3)

        if filename is None:
            print("File is not on-line %s" % (date.strftime('%Y-%m-%d')))
            return False

        with open(filename, "r", encoding="cp950") as csvfile:
            data = csv.reader(csvfile)
            rows = [r for r in data]
            i_code = None
            i_name = None
            i_shares = None
            i_entries = None
            i_amount = None
            i_oprice = None
            i_highest = None
            i_lowest = None
            i_cprice = None
            i_fluc_note = None
            i_fluc = None
            got_index = False
            for r in rows:
                if got_index is False:
                    if len(r) == 0:
                        continue
                        
                    if "證券代號" in r[0]:
                        vindex = 0
                        for v in r:
                            if "證券代號" in v:
                                i_code = vindex
                                vindex +=1
                                continue
                            if "證券名稱" in v:
                                i_name = vindex
                                vindex +=1
                                continue
                            if "成交股數" in v:
                                i_shares = vindex
                                vindex +=1
                                continue
                            if "成交筆數" in v:
                                i_entries = vindex
                                vindex +=1
                                continue
                            if "成交金額" in v:
                                i_amount = vindex
                                vindex +=1
                            if "開盤價" in v:
                                i_oprice = vindex
                                vindex +=1
                                continue
                            if "最高價" in v:
                                i_highest = vindex
                                vindex +=1
                                continue
                            if "最低價" in v:
                                i_lowest = vindex
                                vindex +=1
                                continue
                            if "收盤價" in v:
                                i_cprice = vindex
                                vindex +=1
                                continue
                            if "漲跌(+/-)" in v:
                                i_fluc_note = vindex
                                vindex +=1
                                continue
                            if "漲跌價差" in v:
                                i_fluc = vindex
                                vindex +=1
                                continue

                        got_index = True
                    continue

                if len(r) < vindex:
                    continue

                try:
                    code = r[i_code]
                    name = r[i_name]
                    shares = r[i_shares]
                    entries = r[i_entries]
                    amount = r[i_amount]
                    oprice = r[i_oprice]
                    highest = r[i_highest]
                    lowest = r[i_lowest]
                    cprice = r[i_cprice]
                    if '-' in r[i_fluc_note]:
                        fluctuation = f"-{r[i_fluc]}"
                    else:
                        fluctuation = r[i_fluc]
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    print(r)
                    self.commit()

                self.insert_stock_table(
                    date.strftime('%Y-%m-%d'),
                    str(code).replace("\"", "").replace("=", ""),
                    str(name).replace("\"", "").replace("=", ""),
                    locale.atoi(shares),
                    locale.atoi(entries),
                    locale.atoi(amount),
                    0 if oprice == '--' else locale.atof(oprice),
                    0 if highest == '--' else locale.atof(highest),
                    0 if lowest == '--' else locale.atof(lowest),
                    0 if cprice == '--' else locale.atof(cprice),
                    0 if fluctuation == '--' else locale.atof(fluctuation)
                )

        print(f"{date.strftime('%Y-%m-%d')} listed OK")
        return True

    def toDict(self, tab, length=None, reverse=False):
        dct = {}
        length = len(tab)

        for i in range(length):
            date = tab[i][0]
            dct[date] = tab[i][1]
        return dct

    def toDict_tuple(self, tab, length=None, reverse=False):
        dct = {}
        length = len(tab)

        for i in range(length):
            date = tab[i][0]
            tablen = len(tab[i])
            dct[date] = tab[i][1:tablen]
        return dct

    def load_field(self, tab, tablename, field, length=None, reverse=False):
        arr = []
        # tab = self.load_stock_tab(tablename, code)
        field_num = get_field_num(tablename, field)
        if not length:
            length = len(tab)
        if not reverse:
            for i in range(length):
                arr.append(tab[i][field_num])
        else:
            for i in range(length-1, -1, -1):
                arr.append(tab[i][field_num])
            # print(arr)

        if field == "CPRICE":
            for i in range(1, len(arr)):
                if arr[i] is None:
                    arr[i] = arr[-1]

        return arr

    def load_market_price(self, start, end):
        market_price = []
        date = []
        for d in get_date_range(start, end):
            tab = self.load_stock_tab(date=d)
            price = self.load_field(tab, "STOCK", "CPRICE")
            if len(price) <= 0:
                continue
            date.append(d)
            market_price.append(sum(price))
        return {
            "DATE": date,
            "PRICE": market_price
        }

    def download_revenue_to_sqlite(self, date):
        filename = f"{settings['data_root']}/revenue/t21sc03_{date.year-1911}_{date.month}.csv"
        with open(filename, "r", encoding="cp950") as csvfile:
            fund_data = csv.reader(csvfile)
            rows = [r for r in fund_data]
            rows.pop(0)
            count = 0
            for r in rows:
                if len(r) < 5:
                    continue
                d = r[1].split("/", 1)

                # fix mis-order in sqlite
                if len(d[1]) == 1:
                    m = f"{int(d[0])+1911}/0{d[1]}"
                else:
                    m = f"{int(d[0])+1911}/{d[1]}"

                code = r[2]
                name = r[3]
                value = r[5]
                self.insert_revenue_table(m, code, name, value)
                count = count+1

            if (count == 0):
                print("{} Empty revenue csv table ".format(date), end="")

                print("revenue count 0 failed".format(date))
                return False

            print("{} revenue {} OK".format(date, count))
            return True

    def download_NPM_to_sqlite(self, year, season):
        filename = f"{settings['data_root']}/NPM/npm{year}Q{season}.csv"
        if not os.path.isfile(filename):
            return False

        with open(filename, "r", encoding="cp950") as csvfile:
            data = csv.reader(csvfile)
            rows = [r for r in data]
            rows.pop(0)
            count = 0
            for r in rows:

                date = f"{year+1911}Q{season}"
                code = r[0]
                name = r[1]
                value = r[6]
                self.insert_NPM_table(date, code, name, value)
                count = count+1

            if (count == 0):
                print("{} Empty NPM csv table ".format(date), end="")

                print("NPM count 0 failed".format(date))
                return False

            print("{} NPM {} OK".format(date, count))
            return True

    def download_eps_to_sqlite(self, year, season):
        date = f"{year+1911}Q{season}"
        filename = f"{settings['data_root']}/EPS/eps{year}Q{season}.csv"
        with open(filename, "r", encoding="cp950") as csvfile:
            data = csv.reader(csvfile)
            rows = [r for r in data]
            count = 0

            for r in rows:
                if "出表日期" in r[0]:
                    vindex = 0
                    for v in r:
                        if "基本每股盈餘" in v:
                            break
                        vindex += 1
                    continue

                if len(r) < 3:
                    continue

                code = r[3]
                name = r[4]
                try:
                    value = float(r[vindex])
                except Exception as e:
                    print(e)
                    value = 0
                    self.commit()

                last_eps_sum = 0
                if season > 1:
                    for s in range(1, season):
                        last_eps_sum += self.load_EPS_season(
                            code, year+1911, s)

                self.insert_eps_table(date, code, name, value-last_eps_sum)
                count = count+1

            if (count == 0):
                print("{} Empty EPS csv table ".format(date), end="")

                print("EPS count 0 failed".format(date))
                return False

            print("{} EPS {} OK".format(date, count))
            return True

    def download_etfdiv_to_sqlite(self, year):
        date = f"{year}"
        filename = f"{settings['data_root']}/ETFdiv/ETFdiv{year}.csv"
        with open(filename, "r", encoding='utf-8') as csvfile:
            data = csv.reader(csvfile)
            rows = [r for r in data]
            count = 0

            for r in rows:
                if len(r) == 0:
                    continue

                if "證券代號" in r[0]:
                    continue

                try:
                    code = r[0]
                    name = r[1]
                    d = r[2].split("年")
                    date_year = d[0]
                    d = d[1].split("月")
                    date_month = d[0]
                    d = d[1].split("日")
                    date_day = d[0]
                    value = 0

                    date = f""
                    if len(r[4]) != 0:
                        value = float(r[4])
                except Exception as e:
                    print(e)
                    print(r)
                    self.commit()

                d = f"{year}/{date_month}/{date_day}"
                if validate(d):
                    self.insert_etfdiv_table(
                        f"{year}/{date_month}/{date_day}", code, name, value)
                    count = count+1

            if (count == 0):
                print("{} Empty EPS csv table ".format(date), end="")

                print("EPS count 0 failed".format(date))
                return False

            print("{} EPS {} OK".format(date, count))
            return True

    def histock_download_etfdiv(self, codeset):

        url = f"https://histock.tw/stock/{codeset[0]}/%E9%99%A4%E6%AC%8A%E9%99%A4%E6%81%AF"
        req = requests.get(url)
        html_content = req.content
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table', class_='tb-stock text-center tbBasic')
        if table is None:
            print(url)
            return
        # print(table)
        trs = table.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) > 6:
                y = tds[1].get_text()
                md = tds[3].get_text()
                if len(y) == 0 or len(md) == 0:
                    continue
                ymd = f"{y}/{md}"
                value = tds[6].get_text()
                self.insert_etfdiv_table(ymd, codeset[0], codeset[1], value)
                # print(f" {ymd} {codeset[0]} {codeset[1]} {value}")
        Time.sleep(3)

    def check_basic(self, code):
        print(f"check {code}")
        cursor = self.conn.cursor()

        wherecode = f" WHERE CODE = '{code}'"
        query = SELECT_BASIC.format("*", wherecode)
        # print(query)
        cursor.execute(query)
        if len(cursor.fetchall()) > 0:
            return True
        return False

    def load_basic(self, code):

        cursor = self.conn.cursor()
        field = "*"
        wherecode = f" WHERE CODE = '{code}'"
        query = SELECT_BASIC.format(field, wherecode)

        cursor.execute(query)
        basic = cursor.fetchall()
        if len(basic) > 0:
            cap = basic[0][2]
            deno = basic[0][3]
            klass = basic[0][4].split('\xa0')[0]
            return cap, deno, klass
        return None, None, None

    def insert_basic(self, code, name):
        # print(name)
        if self.check_basic(code):
            print(f"Pass basic {code} {name}")
            return True

        url = 'https://mops.twse.com.tw/mops/web/ajax_t05st03'

        if "00" in code[:2] or "02" in code[:2] or len(code) > 4:
            print(f"Pass basic {code} {name}")
            return True

        print(f"Insert basic {code} {name}")

        form_data = {
            'co_id': f'{code}',
            'TYPEK': 'all',
            'step': '1',
            'firstin': '1',
            'queryName': 'co_id',
            'inpuType': 'co_id'
        }

        try:
            response1 = requests.post(url, data=form_data)
        except Exception as e:
            print(e)
            self.sleep_time += self.sleep_time
            TIME.sleep(self.sleep_time)
            self.commit()
            return False

        html_content = response1.content
        # print the response text (the content of the requested file):
        soup = BeautifulSoup(html_content, 'html.parser')

        tab = [t.text for t in soup.find_all(['td', 'th'])]
        cap = None
        deno = None
        klass = None
        try:

            for i in range(len(tab)):
                if "產業類別" in tab[i]:
                    klass = tab[i+1].replace(" ", "")
                if "普通股每股面額" in tab[i]:
                    if "新台幣" in tab[i+1]:
                        deno = nums_from_string.get_nums(tab[i+1])[0]
                if "實收資本額" in tab[i]:
                    cap = nums_from_string.get_nums(tab[i+1])[0]

            if cap is None and deno is None and klass is None:
                print(f"{code} {name} Got {deno} {cap} {klass}")
                # self.insert_basic_table(code, name, 0, 0, klass)
                self.sleep_time += self.sleep_time
                TIME.sleep(self.sleep_time)
                return False

        except Exception as e:
            print(e)
            self.sleep_time += self.sleep_time
            TIME.sleep(self.sleep_time)
            self.commit()
            return False

        # print(f"issue share {cap}/{deno} {cap/deno}")
        self.insert_basic_table(code, name, cap, deno, klass)
        self.sleep_time = 1
        TIME.sleep(self.sleep_time)
        return True

    def download_book_to_sqlite(self, year, season):
        date = f"{year+1911}Q{season}"
        filename = f"{settings['data_root']}/BOOK/book{year}Q{season}.csv"
        with open(filename, "r", encoding="cp950") as csvfile:
            data = csv.reader(csvfile)
            rows = [r for r in data]
            count = 0

            for r in rows:
                if "出表日期" in r[0]:
                    vindex = 0
                    for v in r:
                        if "每股參考淨值" in v:
                            break
                        vindex += 1
                    continue
                if len(r) < 3:
                    continue

                code = r[3]
                name = r[4]
                try:
                    value = float(r[vindex])
                except Exception as e:
                    print(e)
                    value = 0
                    self.commit()
                self.insert_book_table(date, code, name, value)
                count = count+1

            if (count == 0):
                print("{} Empty BOOK csv table ".format(date), end="")

                print("BOOK count 0 failed".format(date))
                return False

            print("{} BOOK {} OK".format(date, count))
            return True

    def download_ETF_basic(self):
        # print(f"download ETF divident {year}")

        local_filename = f"{settings['data_root']}/etfbasic.csv"

        url = "https://mops.twse.com.tw/server-java/t105sb02"

        form_data = {
            'step': '10',
            'firstin': 'true',
            'filename': "t51sb11.csv",
        }

        response = requests.post(url, data=form_data, headers=headers)
        # print(response.content)
        # print the response text (the content of the requested file):

        with open(local_filename, "wb") as file:
            file.write(response.content)

        with open(local_filename, "r") as csvfile:
            data = csv.reader(csvfile)
            for r in data:
                if "基金代號" in r[0]:
                    continue
                code = r[0]
                name = r[1]

                value = nums_from_string.get_nums(r[17])[0]
                code = code.replace("=", "")
                code = code.replace("\"", "")
                self.insert_basic_table(code, name, value*10, 10, "ETF")

        local_filename = f"{settings['data_root']}/oetfbasic.csv"

        form_data = {
            'step': '10',
            'firstin': 'true',
            'filename': "o_t51sb11.csv",
        }

        response = requests.post(url, data=form_data, headers=headers)
        # print(response.content)
        # print the response text (the content of the requested file):

        with open(local_filename, "wb") as file:
            file.write(response.content)

        with open(local_filename, "r") as csvfile:
            data = csv.reader(csvfile)
            for r in data:
                if "基金代號" in r[0]:
                    continue
                code = r[0]
                name = r[1]

                value = nums_from_string.get_nums(r[17])[0]
                code = code.replace("=", "")
                code = code.replace("\"", "")
                self.insert_basic_table(code, name, value*10, 10, "ETF")

        return True

    def insert_amount_table(self, date, row_data, OTC=False):
        # print(row_data)
        if len(row_data) == 0:
            return False

        code = row_data[0]
        code = code.replace('"', '')
        code = code.replace('=', '')

        if len(code) != 4 or not code.isdigit():
            return False

        while '' in row_data:
            row_data.remove('')

        for i in range(len(row_data)):
            row_data[i] = row_data[i].replace(',', '')

        if not OTC:
            name = row_data[1]
            if len(row_data) == 12:
                forein_in = int(row_data[2])
                forein_out = int(row_data[3])
                forein_sum = int(row_data[4])
                local_in = int(row_data[5])
                local_out = int(row_data[6])
                local_sum = int(row_data[7])
                small_local_in = int(row_data[8])
                small_local_out = int(row_data[9])
                small_local_sum = int(row_data[10])
                total = int(row_data[11])
            elif len(row_data) == 16:
                forein_in = int(row_data[2])
                forein_out = int(row_data[3])
                forein_sum = int(row_data[4])
                local_in = int(row_data[5])
                local_out = int(row_data[6])
                local_sum = int(row_data[7])
                small_local_in = int(row_data[9])+int(row_data[12])
                small_local_out = int(row_data[10])+int(row_data[13])
                small_local_sum = int(row_data[8])
                total = int(row_data[15])
            elif len(row_data) == 17:
                forein_in = int(row_data[2])
                forein_out = int(row_data[3])
                forein_sum = int(row_data[4])
                local_in = int(row_data[6])
                local_out = int(row_data[7])
                local_sum = int(row_data[8])
                small_local_in = int(row_data[10])+int(row_data[13])
                small_local_out = int(row_data[11])+int(row_data[14])
                small_local_sum = int(row_data[9])
                total = int(row_data[16])
            elif len(row_data) == 19:
                forein_in = int(row_data[2])+int(row_data[5])
                forein_out = int(row_data[3])+int(row_data[6])
                forein_sum = int(row_data[4])+int(row_data[7])
                local_in = int(row_data[8])
                local_out = int(row_data[9])
                local_sum = int(row_data[10])
                small_local_in = int(row_data[12])+int(row_data[15])
                small_local_out = int(row_data[13])+int(row_data[16])
                small_local_sum = int(row_data[11])
                total = int(row_data[18])
            else:
                print(row_data)
                print("ERROR len: {}".format(len(row_data)))
                return False
        else:
            if len(row_data) == 16:
                name = row_data[1]
                forein_in = int(row_data[2])
                forein_out = int(row_data[3])
                forein_sum = int(row_data[4])
                local_in = int(row_data[5])
                local_out = int(row_data[6])
                local_sum = int(row_data[7])
                small_local_in = int(row_data[9])+int(row_data[12])
                small_local_out = int(row_data[10])+int(row_data[13])
                small_local_sum = int(row_data[8])
                total = int(row_data[15])
            elif len(row_data) == 24:
                name = row_data[1]
                forein_in = int(row_data[8])
                forein_out = int(row_data[9])
                forein_sum = int(row_data[10])
                local_in = int(row_data[11])
                local_out = int(row_data[12])
                local_sum = int(row_data[13])
                small_local_in = int(row_data[20])
                small_local_out = int(row_data[21])
                small_local_sum = int(row_data[22])
                total = int(row_data[23])
            else:
                print(row_data)
                print("ERROR OTC len: {}".format(len(row_data)))
                return False

        if forein_sum != forein_in - forein_out:
            print("ERRRRRRROR!!!!! Wrong forein {} {} len {}".format(
                name, date, len(row_data)))
            return False
        if local_sum != local_in - local_out:
            print("ERRRRRRROR!!!!! Wrong local {} {} len {}".format(
                name, date, len(row_data)))
            return False
        if small_local_sum != small_local_in - small_local_out:
            print("ERRRRRRROR!!!!! Wrong small_local {} {} len {}".format(
                name, date, len(row_data)))
            return False
        if total != small_local_sum + local_sum + forein_sum:
            print("ERRRRRRROR!!!!! Wrong total {} {} len {}".format(
                name, date, len(row_data)))
            return False

        query = "INSERT OR IGNORE INTO AMOUNT VALUES" \
                " (\"{}\", \"{}\", \"{}\", {}," \
                " {}, {}, {}, {}, {}, {}, {}, {}, {});".format(
                    date,
                    code,
                    name,
                    forein_in,
                    forein_out,
                    forein_sum,
                    local_in,
                    local_out,
                    local_sum,
                    small_local_in,
                    small_local_out,
                    small_local_sum,
                    total)

        c = self.conn.cursor()
        # print(query)
        c.execute(query)
        return True

    def download_amount_to_sqlite(self, y, m, d):

        date = "{}-{}-{}".format(y, str2d(m), str2d(d))
        amount_fname = f"{settings['data_root']}/amount/" + \
            str(y) + '_' + str2d(m) + '_' + str2d(d) + ".csv"

        if not os.path.isfile(amount_fname):
            amount_fname = download_amount_csv_file(
                str(y), str2d(m), str2d(d))
            Time.sleep(3)
        if amount_fname is None:
            print("File is not on-line %s" % (date))
            return False

        with open(amount_fname, "r") as csvfile:
            amount_data = csv.reader(csvfile)
            rows = [r for r in amount_data]

            count = 0
            for r in rows:
                if self.insert_amount_table(date, r):
                    count = count + 1

            if (count == 0):
                day = Date(y, m, d).weekday()
                print("{} Empty amount csv table ".format(date), end="")
                if (day == 5 or day == 6):
                    print("Weekend OK", end="")
                    print()
                    return False

                print("{} amount count 0 failed".format(date))
                return False

            print("{} amount {} OK".format(date, count))
            return True

    def download_OTC_amount_to_sqlite(self, y, m, d):

        date = "{}-{}-{}".format(y, str2d(m), str2d(d))
        amount_fname = f"{settings['data_root']}/OTC_amount/" + \
            str(y) + '_' + str2d(m) + '_' + str2d(d) + ".csv"

        if not os.path.isfile(amount_fname):
            amount_fname = download_OTC_amount_csv_file(
                str(y), str2d(m), str2d(d))
            Time.sleep(1)
        if amount_fname is None:
            print("File is not on-line %s" % (date))
            return False

        with open(amount_fname, "r") as csvfile:
            amount_data = csv.reader(csvfile)
            rows = [r for r in amount_data]

            count = 0
            for r in rows:
                if self.insert_amount_table(date, r, OTC=True):
                    count = count + 1

            if (count == 0):
                day = Date(y, m, d).weekday()
                print("{} Empty OTC amount csv table ".format(date), end="")
                if (day == 5 or day == 6):
                    print("Weekend OK", end="")
                    print()
                    return False

                print("{} OTC amount count 0 failed".format(date))
                return False

            print("{} OTC amount {} OK".format(date, count))
            return True

    def download_legal_to_sqlite(self, y, m, d):

        date = "{}-{}-{}".format(y, str2d(m), str2d(d))

        fname = f"{settings['data_root']}/legal/{y}_{m}_{d}.csv"

        if not os.path.isfile(fname):
            fname = download_legal_csv_file(
                y, m, d)
            Time.sleep(3)
        if fname is None:
            print("File is not on-line %s" % (date))
            return False

        with open(fname, "r", encoding="cp950") as csvfile:
            data = csv.reader(csvfile)

            rows = [r for r in data]

            count = 0

            legal_idx = None
            code_idx = None
            name_idx = None
            row_idx = 0
            for r in rows.copy():

                if len(r) == 0:
                    continue

                if not "證券代號" in r:
                    rows.remove(r)
                else:
                    i = 0
                    for v in r:
                        if v == "證券代號":
                            code_idx = i
                        if v == "證券名稱":
                            name_idx = i
                        if v == "全體外資及陸資持股比率":
                            legal_idx = i
                        elif v == "全體外資持股比率":
                            legal_idx = i
                        i += 1
                    break
                row_idx += 1

            if legal_idx is None:
                print(f'No legal idx')
                return False

            for r in rows:
                if len(r) < legal_idx:
                    continue
                code = r[code_idx]
                code = code.replace('"', '')
                code = code.replace('=', '')
                name = r[name_idx]
                if not code[0].isdigit():
                    continue
                legal = float(r[legal_idx])
                # print(f'{code} {name} {legal}')
                if self.insert_legal_table(date, code, name, legal):
                    count = count + 1

            if (count == 0):
                day = Date(y, m, d).weekday()
                print("{} Empty legal csv table ".format(date), end="")
                if (day == 5 or day == 6):
                    print("Weekend OK", end="")
                    print()
                    return False

                print("{} legal count 0 failed".format(date))
                return False

            print("{} legal {} OK".format(date, count))
            return True

    def download_margin_to_sqlite(self, y, m, d):

        date = "{}-{}-{}".format(y, str2d(m), str2d(d))
        margin_fname = f"{settings['data_root']}/margin/" + \
            str(y) + '_' + str2d(m) + '_' + str2d(d) + ".csv"

        if not os.path.isfile(margin_fname):
            margin_fname = download_margin_csv_file(
                y, m, d)
            Time.sleep(3)
        if margin_fname is None:
            print("File is not on-line %s" % (date))
            return False

        with open(margin_fname, "r", encoding="cp950") as csvfile:
            margin_data = csv.reader(csvfile)

            rows = [r for r in margin_data]

            count = 0

            margin_idx = None
            short_idx = None
            code_idx = None
            name_idx = None
            row_idx = 0
            for r in rows.copy():

                if len(r) == 0:
                    continue

                if not "代號" in r:
                    rows.remove(r)
                else:
                    i = 0
                    for v in r:
                        if v == "代號":
                            code_idx = i
                        if v == "名稱":
                            name_idx = i
                        if v == "今日餘額":
                            if margin_idx is None:
                                margin_idx = i
                            elif margin_idx is not None:
                                short_idx = i
                        i += 1
                    break
                row_idx += 1

            if margin_idx is None or short_idx is None:
                return False

            for r in rows:
                if len(r) < short_idx:
                    continue
                code = r[code_idx]
                code = code.replace('"', '')
                code = code.replace('=', '')
                name = r[name_idx]
                if not code[0].isdigit():
                    continue

                try:
                    margin = int(r[margin_idx].replace(',', ''))
                    short = int(r[short_idx].replace(',', ''))
                except Exception as e:
                    print(f"margin failed {e}")
                    self.commit()

                if self.insert_margin_table(date, code, name, margin, short):
                    count = count + 1

            if (count == 0):
                day = Date(y, m, d).weekday()
                print("{} Empty margin csv table ".format(date), end="")
                if (day == 5 or day == 6):
                    print("Weekend OK", end="")
                    print()
                    return False

                print("{} margin count 0 failed".format(date))
                return False

            print("{} margin {} OK".format(date, count))
            return True

    def get_code_list(self, klass_mask=None):

        codes = self.load_code()
        if codes is None:
            print("No code found")
            sys.exit()

        filted_code = []

        for c in codes:
            if len(c) == 6 and c[0] == '7':
                print(f"{c} filt out")
                continue
            if klass_mask:
                klass = self.load_klass(c)
                # print(f"{c}, {klass}")
                if klass is None:
                    continue
                if not klass_mask[klass]:
                    continue
            filted_code.append(c)

        return filted_code

    def load_stock_month_average(self, code):
        result = self.load_stock_dict_tuple(code, "CPRICE, SHARES")
        sum_month = {}
        share_month = {}
        for r in result:
            # print(f"{r}: {result[r][0]*result[r][1]}")
            m = re.match(r'(\S+)-(\S+)-(\S+)', r)
            date = m.groups()
            m = f"{date[0]}/{date[1]}"
            if not m in sum_month:
                sum_month[m] = 0
            if not m in share_month:
                share_month[m] = 0
            sum_month[m] += result[r][0] * result[r][1]
            share_month[m] += result[r][1]

        avg_month = {}
        for m in sum_month:
            avg_month[m] = sum_month[m]/share_month[m]

        return avg_month

    def load_stock_month_stdev(self, code):
        price = self.load_stock_dict(code, "CPRICE")

        price_month = {}
        for d in price:
            # print(f"{r}: {result[r][0]*result[r][1]}")
            dt = datetime.strptime(d, '%Y-%m-%d')
            month = dt.month
            year = dt.year

            if month < 10:
                m = f"{year}/0{month}"
            else:
                m = f"{year}/{month}"

            if m not in price_month:
                price_month[m] = []
            price_month[m].append(price[d])

        price_stdev = {}
        for m in price_month:
            price_stdev[m] = statistics.stdev(price_month[m])
        return price_stdev

"""
    def download_OTC_data_to_sqlite(self, y, m, d):
        date = Date(y, m, d).strftime("%Y-%m-%d")
        json_fname = f"{settings['data_root']}/OTC_data/" + \
            Date(y, m, d).strftime("%Y_%m_%d") + '.json'

        if not os.path.isfile(json_fname):
            json_fname = download_OTC_json_file(
                y, m, d)
            Time.sleep(1)

        if json_fname is None:
            print("File is not on-line %s" % (date))
            return False

        jdata = self.load_json_file(json_fname)
        # print(jdata)
        if jdata is None:
            print("{} Empty JSON File, Remove!".format(date))
            os.remove(json_fname)
            return False

        jTab = self.load_OTC_stock_table(jdata)
        if jTab is None:
            # This ignore holiday
            day = Date(y, m, d).weekday()
            print("{} Empty OTC json table ".format(date), end="")
            if (day == 5 or day == 6):
                print("Weekend OK")
                return False
            print("failed")
            return False
        for i in range(len(jTab)):

            # It filts the needless code out

            if jTab[i][0][-1] != 'B':
                continue

            # Weird data
            if (self.jTab2SqlTab.get("TypeCPrice")(jTab[i][2]) == 0):
                continue

            self.insert_stock_table(
                date,
                self.jTab2SqlTab.get("TypeCode")(jTab[i][0]),
                self.jTab2SqlTab.get("TypeName")(jTab[i][1]),
                self.jTab2SqlTab.get("TypeShares")(jTab[i][8]),
                self.jTab2SqlTab.get("TypeEntries")(jTab[i][10]),
                self.jTab2SqlTab.get("TypeAmount")(jTab[i][9]),
                self.jTab2SqlTab.get("TypeOPrice")(jTab[i][4]),
                self.jTab2SqlTab.get("TypeHighest")(jTab[i][5]),
                self.jTab2SqlTab.get("TypeLowest")(jTab[i][6]),
                self.jTab2SqlTab.get("TypeCPrice")(jTab[i][2]),
                self.jTab2SqlTab.get("TypeFlucation")(jTab[i][3])
            )

        print(date + " OTC OK")
        return True
"""

"""
    def load_json_file(self, fname):
        # print("open {}".format(fname))
        jfile = open(fname, "r", encoding="utf-8")
        jstring = jfile.read()
        try:
            jdata = json.loads(jstring)
            if jdata is None:
                os.remove(fname)
                print('Empty JSON File, Remove!')
            return jdata
        except Exception as e:
            print("Load json file execption: " + e)
            os.remove(fname)
            return None


def jDataToFloat(jdata):
    jdata = jdata.replace('-', '')
    jdata = jdata.replace(',', '')
    if not jdata.strip():
        return None

    try:
        f = float(jdata)
        return f
    except ValueError:
        print('Value Error: {} (#float excepted)'.format(jdata))
        sys.exit()


def jDataToInt(jdata):
    jdata = jdata.replace('-', '')
    jdata = jdata.replace(',', '')
    if not jdata.strip():
        return None
    try:
        i = int(jdata)
        return i
    except ValueError:
        print('Value Error: {} (int excepted)'.format(jdata))
        sys.exit()
        return None


def jDataToSignFloat(jdata, sign=None):
    s = -1 if sign and '-' in sign else 1
    jdata = jdata.replace(',', '').strip()

    try:
        return float(jdata) * s

    except ValueError:
        options = {
            "--- ": 0.,
            "除權 ": 0.,
            "除息 ": 0.,
            "除息": 0.,
            "除權息 ": 0.,
            "---": 0.,
            "+######": 0.,
        }
        if jdata in options:
            return options[jdata]

        print(f'Value Error: {jdata} (float expected)')
        sys.exit()


"""
