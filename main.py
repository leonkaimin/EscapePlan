#!/usr/bin/python3
from statistics import median
import time as TIME
from MyDataBase import MyDataBase, KLASS
# from MyCodeDrawer import MyCodeDrawer
import os
import multiprocessing as mp
import getopt
from datetime import datetime
import datetime as Datetime
import MyMath as mymath
import sys
import json
import xlsxwriter
import numpy as np
from dateutil.relativedelta import relativedelta
import MyDownload as mydownload
import csv
from functools import reduce
import scipy.optimize as optmize
# from MyCodeTab import *
from MyTime import quarter_to_months, date_to_quarter
from settings import *
now = datetime.now()

cpi = 0.0308


def read_pocket_list(path):
    with open(path, "r") as reserve_file:
        pocket_list = csv.reader(reserve_file)
        return [r for r in pocket_list]


def read_pocket_list(path):
    """Reads a CSV file and returns a list of its rows."""
    with open(path, "r", encoding="Big5") as reserve_file:
        return list(csv.reader(reserve_file))


def parse_reserve_row(row, filename):
    """Parses a row from the CSV file and calculates the reserve amount."""
    if len(row) == 0:
        return None, None

    if filename == rsv_file1:
        code = row[0].split("(")[1].split(")")[0]
        reserve = 0
        if row[7]:  # Check if column 7 has content
            reserve += 1000 * int(row[7])
        if row[13]:  # Check if column 13 has content
            reserve += int(row[13])
    else:  # reserve2.csv format
        code = row[0].split("(")[1].split(")")[0]
        reserve = int(row[3])

    return code, reserve


rsv_file1 = f"{settings['data_root']}/reserve1.csv"
rsv_file2 = f"{settings['data_root']}/reserve2.csv"


def read_all_pocket_list():
    """Reads multiple CSV files and combines reserve data."""
    pocket_list = {}

    for filename in [rsv_file1, rsv_file2]:
        data = read_pocket_list(filename)
        header_rows = 3 if filename == rsv_file1 else 1
        for row in data[header_rows:]:  # Skip header rows
            if row:  # Check for empty rows
                code, reserve = parse_reserve_row(row, filename)
                pocket_list[code] = pocket_list.get(code, 0) + reserve

    return pocket_list


pocket_list = read_all_pocket_list()

code_share = {}
code_dic = {}


def cal_workbook_row(data, fund, klass_sum):
    name = data["name"]
    price = data["price"]
    code = data["code"]
    amount = data["shares"]
    date = data["date"]
    last_date = date[-1]
    trading_shares = data["shares"][-1]
    # weighted_avg = mymath.calc_weight_avg(price, amount, 300)
    # weighted_avg_dev = (price[-1] - weighted_avg[-1])/weighted_avg[-1]
    mydb = MyDataBase()
    npm = mydb.load_NPM_items(code)
    eps = mydb.load_EPS(code)
    eps_values = list(eps.values())
    eps_quarter = list(eps)
    book = mydb.load_book(code)

    predicted_EPS = None
    median_npm = 0
    last_eps_quarter = None
    last_eps = None
    last_price = price[-1]
    year_range = 3
    hot = 0

    etfdiv = mydb.load_ETFDIV(code)
    # print(etfdiv)

    issue_shares = None
    if len(eps_values) > 0:
        last_eps = eps_values[-1]
        last_eps_quarter = eps_quarter[-1]

    last_book = None
    if len(book) > 0:
        last_book = book[-1]

    revenue = mydb.load_revenue_items(code)
    cap, deno, klass = mydb.load_basic(code)
    if cap is not None or deno is not None:
        issue_shares = cap/deno
    mcap = None
    # product = None
    if issue_shares is not None:
        mcap = issue_shares*last_price
        hot = float(trading_shares)/issue_shares

        # if last_eps is not None:
        # product = issue_shares*last_eps

        if len(npm) > 0:
            median_npm = median(npm)

        else:
            if last_eps_quarter is not None:
                year, months = quarter_to_months(last_eps_quarter)
                rev_sum = 0
                for m in months:
                    rev_sum += mydb.load_revenue_month(code, year, m)
                median_npm = (last_eps*issue_shares)/(rev_sum*1000)*100
                # print(f"{median_npm:.2f}%")

        if median_npm < 0:
            median_npm = 0

    margin = mydb.load_margin(code)
    last_margin = 0
    last_short = 0
    if len(margin) > 0:
        margin_sum = []
        last_key = list(margin.keys())[-1]
        last_margin = margin[last_key][0]
        last_short = margin[last_key][1]

    mydb.close()

    last_per = None
    per = 0
    if fund is not None:
        per = [z[1] for z in zip(
            fund["date"], fund["per"]) if z[0] in data["date"]]
        last_per = per[-1]

    # if len(eps_values) == 0:
    #     return None
    eps_pstdev = None
    eps_variance = None
    eps_mean = None
    eps_growth = None
    book_dif = None
    book_mean = None
    book_variance = None
    book_pstdev = None
    roe = None
    try:

        predicted_EPS = None
        if median_npm is not None and issue_shares is not None and len(revenue) > 3:
            predicted_EPS = sum(revenue[-3:]) * \
                1000*(median_npm/100)/issue_shares
            eps_values.append(predicted_EPS)
            print(f"{code} predict EPS {predicted_EPS}")

        if len(eps_values) > 4*year_range:
            eps_mean = mymath.calc_mean(
                eps_values[-4*year_range:])*4/last_price
            eps_variance = mymath.calc_variance(
                eps_values[-4*year_range:])*4/last_price
            eps_pstdev = mymath.calc_pstdev(
                eps_values[-4*year_range:])/last_price*np.sqrt(year_range)
            eps_growth = mymath.calc_growth_rate(eps_values)
        if len(etfdiv) >= year_range:
            # `print(f"cal etfdiv {code}")
            eps_mean = mymath.calc_mean(
                etfdiv)/last_price
            eps_variance = mymath.calc_variance(
                etfdiv)/last_price
            eps_pstdev = mymath.calc_pstdev(
                etfdiv)/last_price*np.sqrt(len(etfdiv))
            eps_growth = mymath.calc_growth_rate(etfdiv)
        if len(book) > 4*year_range:
            book_dif = np.diff(np.array(book))
            book_mean = mymath.calc_mean(
                book_dif[-4*year_range:])*4/last_price
            book_variance = mymath.calc_variance(
                book_dif[-4*year_range:])*4/last_price
            book_pstdev = mymath.calc_pstdev(
                book[-4*year_range:])/last_price*np.sqrt(year_range)

        # print(f"eps_mean_y2 {eps_mean_y2}")
        # print(f"eps_pstdev {eps_pstdev}")
        # print(f"eps_mean_y2 {eps_sum_y2}")
        # print(f"eps_mean_y1 {eps_sum_y1}")
        # print(f"eps_index {(eps_sum_y2 - eps_sum_y1)}")
    except Exception as e:

        print(f"{code} {e}")
        exit()
        # return None

    # adx, di_plus, di_neg = mymath.calc_adx(
    #     data["price"], data["top"], data["bottom"])

    disc_rate = None
    if len(eps_values) > 4*year_range:
        if sum(eps_values[-4:]) > 0:
            disc_rate = sum(eps_values[-4:])/last_price
        #     disc_rate = 1-sum(eps_values[-4:])/last_price
        # else:
    elif len(etfdiv) >= year_range:
        if etfdiv[-1] > 0:
            disc_rate = etfdiv[-1]/last_price
        #     disc_rate = 1-etfdiv[-1]/last_price
        # else:
    reserve = 0
    if code in pocket_list.keys():
        reserve = pocket_list[code]*last_price

    fluctuation = data["fluctuation"]
    # print(f"{code}: {sum(fluctuation[-252:])}")

    mean = mymath.calc_mean(
        fluctuation[-252*year_range:])*252/last_price
    variance = mymath.calc_variance(
        fluctuation[-252*year_range:])*252/last_price
    pstdev = mymath.calc_pstdev(
        fluctuation[-252*year_range:])/last_price*np.sqrt(252)

    predicted_EPS_year = sum(eps_values[-4:])
    predicted_per = None
    if predicted_EPS_year is not None:
        if predicted_EPS_year > 0:
            predicted_per = price[-1]/predicted_EPS_year

        roe = None
        if last_book != None:
            roe = predicted_EPS_year/last_book

    if len(etfdiv) >= year_range:
        predicted_EPS_year = etfdiv[-1]
        last_eps = etfdiv[-1]

    mean = mymath.calc_mean(price[-70:])

    bias = 0
    # if len(margin_sum) > 0:
    #     weight = [a + m for a, m in zip(amount, margin_sum)]
    # else:
    weight = amount

    weighted_avg = mymath.calc_weight_avg(price, weight, 300)
    bias = (price[-1] - weighted_avg[-1])/weighted_avg[-1]

    beta = {}
    """
    klass_sum_copy = []
    for d in date:
        klass_sum_copy.append(klass_sum["system"][d])

    beta["system"] = mymath.calculate_beta(
        klass_sum_copy, price)
    """
    # print(f"{code} system beta {beta['system']}")

    for k in KLASS:

        klass_sum_copy = []
        for d in date:
            klass_sum_copy.append(klass_sum[k][d])

        beta[k] = mymath.calculate_beta(
            klass_sum_copy, price)
        # print(f"{code} {k} beta {beta[k]}")
        if beta[k] is None:
            print()

    return [
        code, name,
        last_per, predicted_per,
        last_eps, predicted_EPS_year, eps_mean, eps_pstdev, eps_variance, eps_growth,
        last_book, book_mean, book_pstdev, book_variance,
        last_price, 0, 0, reserve, mcap, mean, pstdev, variance, disc_rate, roe, 0, hot, bias, klass, last_margin, last_short, amount[-1], beta, None, None, None]


def cal_workbook_row_fake():
    code = "0000"
    name = " 台新活存"
    eps = 0.032
    price = 1
    last_per = price/eps
    predicted_per = last_per
    last_eps = eps
    predicted_EPS_year = last_eps
    eps_mean = last_eps
    eps_pstdev = 0
    eps_variance = 0
    eps_growth = 0
    last_book = 1
    book_mean = 1
    book_pstdev = 0
    book_variance = 0
    last_price = 1
    reserve = 1000000
    mcap = 1
    mean = 1
    pstdev = 0
    variance = 0
    disc_rate = 0
    roe = eps/last_book
    hot = 0
    bias = 0
    klass = None
    last_margin = 0
    last_short = 0
    amount = 1
    beta = {}
    # beta["system"] = 0
    # print(f"{code} system beta {beta['system']}")

    for k in KLASS:

        beta[k] = 0

    return [
        code, name,
        last_per, predicted_per,
        last_eps, predicted_EPS_year, eps_mean, eps_pstdev, eps_variance, eps_growth,
        last_book, book_mean, book_pstdev, book_variance,
        last_price, 0, 0, reserve, mcap, mean, pstdev, variance, disc_rate, roe, 0, hot, bias, klass, last_margin, last_short, amount, beta, None, None, None]


class Tab():
    workbook = xlsxwriter.Workbook(
        f"{settings['data_root']}/output/{now.strftime('%m-%d-%Y_%H-%M-%S')}anlz.xlsx", {'nan_inf_to_errors': True})
    summary_sheet = workbook.add_worksheet('Summary')

    def_format = workbook.add_format()
    def_format.set_font_color('black')
    def_format.set_bg_color('white')

    r_format = workbook.add_format()
    r_format.set_bg_color('pink')
    r_format.set_font_color('white')

    g_format = workbook.add_format()
    g_format.set_bg_color('cyan')
    g_format.set_font_color('white')

    b_format = workbook.add_format()
    b_format.set_bg_color('blue')
    b_format.set_font_color('white')

    grey_format = workbook.add_format()
    grey_format.set_bg_color('grey')
    grey_format.set_font_color('white')

    CODE = 0
    NAME = 1
    PER = 2
    P_PER = 3
    EPS = 4
    P_EPS = 5
    EPS_MEAN = 6
    EPS_PSTDEV = 7
    EPS_VAR = 8
    EPS_GROWTH = 9
    BOOK = 10
    BOOK_ROR = 11
    BOOK_PSTDEV = 12
    BOOK_VOL = 13
    PRICE = 14
    P_PRICE = 15
    P_DIFF_RATE = 16
    RESERVE = 17
    MCAP = 18
    # PRODUCT = 18
    ROR = 19
    PSTDEV = 20
    VOL = 21
    DISC_RATE = 22
    ROE = 23
    RISK_COMP = 24
    HOT = 25
    BIAS = 26
    KLASS = 27
    MARGIN = 28
    SHORT = 29
    AMOUNT = 30
    BETA = 31
    PRICE_WEIGHT = 32
    EPS_WEIGHT = 33
    BOOK_WEIGHT = 34
    WEIGHT_AVG = 35

    Valist = [
        CODE, NAME, P_PER, P_EPS, BOOK, PRICE, P_PRICE, P_DIFF_RATE, RESERVE, EPS_WEIGHT, MCAP, HOT, BIAS, EPS_PSTDEV, EPS_GROWTH, RISK_COMP, MARGIN, SHORT, AMOUNT]

    content = {
        CODE: ["代碼", b_format],
        NAME: ["名稱", def_format],
        PER: ["本益比", def_format],
        P_PER: ["預測本益比", def_format],
        EPS: ["淨利", def_format],
        P_EPS: ["預測淨利", def_format],
        EPS_MEAN: ["平均淨利", def_format],
        EPS_PSTDEV: ["淨利標準差", def_format],
        EPS_VAR: ["淨利變異數", def_format],
        EPS_GROWTH: ["淨利成長率", def_format],
        BOOK: ["淨值", def_format],
        BOOK_ROR: ["淨值報酬", def_format],
        BOOK_PSTDEV: ["淨值標準差", def_format],
        BOOK_VOL: ["淨值波動率", def_format],
        PRICE: ["現價", def_format],
        P_PRICE: ["估價", def_format],
        P_DIFF_RATE: ["價差", def_format],
        RESERVE: ["庫存", def_format],
        MCAP: ["市值", def_format],
        PRICE_WEIGHT: ["股價權重", def_format],
        EPS_WEIGHT: ["淨利權重", def_format],
        BOOK_WEIGHT: ["淨值權重", def_format],
        WEIGHT_AVG: ["均權", def_format],
        ROR: ["股價報酬率", def_format],
        PSTDEV: ["股價標準差", def_format],
        VOL: ["股價波動率", def_format],
        DISC_RATE: ["折現率", def_format],
        ROE: ["股東權益", def_format],
        RISK_COMP: ["風險補償", def_format],
        HOT: ["熱度", def_format],
        BIAS: ["乖移率", def_format],
        KLASS: ["類別", def_format],
        MARGIN: ["融資", def_format],
        SHORT: ["融券", def_format],
        AMOUNT: ["成交量", def_format],
    }


analyze_data = []
eps_data = []
book_data = []
price_data = []

# ====================== EPS


def sum_eps_mean(weights):
    for d in eps_data:
        if d[Tab.EPS_MEAN] is None:
            return -99999
    epsp_means = np.array([d[Tab.EPS_MEAN]
                          for d in eps_data])
    return np.sum(epsp_means*weights)


def sqrt_eps_vars(weights):
    for d in eps_data:
        if d[Tab.EPS_VAR] is None:
            return 1
    eps_vars = np.sum(
        np.array([d[Tab.EPS_VAR] for d in eps_data]))
    return np.sqrt(np.dot(weights.T, np.dot(eps_vars, weights)))
    # return np.array([d[Tab.EPS_VAR] for d in analyze_data])


def std_deviation_eps(weights):
    return -sum_eps_mean(weights)/sqrt_eps_vars(weights)

# ====================== ROR


def sum_ror_mean(weights):
    ror_means = np.array([d[Tab.ROR] for d in price_data])
    return np.sum(ror_means*weights)


def sqrt_vol_vars(weights):
    vol_vars = np.sum(
        np.array([d[Tab.VOL] for d in price_data]))
    return np.sqrt(np.dot(weights.T, np.dot(vol_vars, weights)))
    # return np.array([d[Tab.EPS_VAR] for d in price_data])


def std_deviation_price(weights):
    return -sum_ror_mean(weights)/sqrt_vol_vars(weights)


# ====================== BOOK
def sum_book_mean(weights):
    ror_means = np.array([d[Tab.BOOK_ROR] for d in book_data])
    return np.sum(ror_means*weights)


def sqrt_book_vars(weights):
    vol_vars = np.sum(
        np.array([d[Tab.BOOK_VOL] for d in book_data]))
    return np.sqrt(np.dot(weights.T, np.dot(vol_vars, weights)))
    # return np.array([d[Tab.EPS_VAR] for d in analyze_data])


def std_deviation_book(weights):
    return -sum_book_mean(weights)/sqrt_book_vars(weights)
# ======================


def system_summarize(codes_list, begin, end):
    system_sum = {}
    code_share_sum = 0
    mydb = MyDataBase()
    for code in codes_list:
        if code not in code_share:
            code_share[code] = mydb.load_issue_shares(code)
        if not code_share[code]:
            print(f"{code} share is None")
            continue
        code_share_sum += code_share[code]

    code_share_ratio = {}
    for code in codes_list:
        if not code_share[code]:
            code_share_ratio[code] = 0
            continue
        code_share_ratio[code] = code_share[code]/code_share_sum

    for code in codes_list:
        if not code in code_dic.keys():
            print(f"system_summarize load {code}")
            dic = mydb.load_stock_dict(code, "CPRICE", begin=begin, end=end)
            code_dic[code] = dic
        else:
            dic = code_dic[code]

        for key in dic:
            if not key in system_sum:
                system_sum[key] = 0
            system_sum[key] += dic[key]*code_share_ratio[code]
    mydb.close()
    return system_sum


def analyze(begin=None, end=None, target=None):

    mydb = MyDataBase()
    system_sum = {}
    # print(system_sum)
    klass_sum = {k: 0 for k in KLASS}
    klass_sum["ETFB"] = 0
    for kls in KLASS:
        klass_mask = {k: False for k in KLASS}

        klass_mask[kls] = True
        code_list = mydb.get_code_list(klass_mask)
        if kls == "ETF":
            etf = []
            etfb = []
            for c in code_list:
                if "B" in c:
                    etfb.append(c)
                else:
                    etf.append(c)
            klass_sum[kls] = system_summarize(etf, begin, end)
            klass_sum["ETFB"] = system_summarize(etfb, begin, end)
        else:
            klass_sum[kls] = system_summarize(code_list, begin, end)
        # print(list(klass_sum[kls].values()))

    """
    klass_mask = {k: True for k in KLASS}
    klass_mask["ETF"] = False
    code_list = mydb.get_code_list(klass_mask)
    system_sum = system_summarize(code_list, begin, end)
    klass_sum["system"] = system_sum
    """
    codes_list = mydb.get_code_list()

    mydb.close()

    workbook_data = []
    if (codes_list is None):
        print("Empty Database")
        sys.exit()

    cn_idx = 0
    end_idx = len(codes_list)

    print("Start to analyze stocks from {} to {} ".format(
        cn_idx,
        end_idx
    ))
    pool = mp.Pool(15)

    summary_fileds = [Tab.content[i][0] for i in Tab.Valist]
    Tab.summary_sheet.write_row(0, 0, summary_fileds)

    # while(cn_idx != end_idx):

    for code in codes_list:

        # if "00" in code:
        # 　  cn_idx += 1
        #     print(f"Pass {code}")
        #     continue

        data = load_data(code, begin=begin, end=end)
        if (data is None):
            print('Data is None. Possibly the duration '
                  'that you specify is too short [{}]'.format(
                      code))
            cn_idx += 1
            continue
        fund = load_fund(code, begin=begin, end=end)

        # if fund is None:
        #     print('fund is None. [{}]'.format(code))
        #     cn_idx += 1
        #     continue

        if (data["length"] < 252*3):
            print(f'Code:{code} {cn_idx}/{end_idx} Data length < 252')
            cn_idx += 1
            continue

        row_result = pool.apply_async(
            cal_workbook_row, (data, fund, klass_sum, ))
        workbook_data.append(row_result)

        cn_idx += 1
        print(f"Code:{code} {cn_idx}/{end_idx}")

    # total_product = 0
    # total_disk_rate = 0

    total_mcap = 0
    for w in workbook_data:
        row = w.get()
        if row is None:  # or row[Tab.RESERVE] is None or row[Tab.VOL] is None:
            continue

        if row[Tab.MCAP] is None:
            print(f"Cap of {row[Tab.CODE]} is none")
            continue

        total_mcap += row[Tab.MCAP]
        analyze_data.append(row)
        # if row[Tab.PRODUCT] is not None:
        #     total_product += row[Tab.PRODUCT]
    # print(f"TOTAL_MCAP={total_mcap/total_product}")
    analyze_data.append(cal_workbook_row_fake())

    sum_slarge_diskrate = 0
    sum_smedium_diskrate = 0
    sum_ssmall_diskrate = 0
    slarge_diskrate_num = 0
    smedium_diskrate_num = 0
    ssmall_diskrate_num = 0

    total_diskrate = 0
    total_diskrate_num = 0

    klass_diskrate_sum = {}
    klass_diskrate_num = {}

    for row in analyze_data:
        if row[Tab.KLASS] is None:
            continue
        if row[Tab.DISC_RATE] is not None:
            total_diskrate += row[Tab.DISC_RATE]*row[Tab.MCAP]
            total_diskrate_num += row[Tab.MCAP]

            scale = row[Tab.MCAP]/total_mcap
            if scale > 0.0025:
                sum_slarge_diskrate += row[Tab.DISC_RATE]*row[Tab.MCAP]
                slarge_diskrate_num += row[Tab.MCAP]
            elif scale > 0.0004:
                sum_smedium_diskrate += row[Tab.DISC_RATE]*row[Tab.MCAP]
                smedium_diskrate_num += row[Tab.MCAP]
            else:
                sum_ssmall_diskrate += row[Tab.DISC_RATE]*row[Tab.MCAP]
                ssmall_diskrate_num += row[Tab.MCAP]

            if not row[Tab.KLASS] in klass_diskrate_sum:
                klass_diskrate_sum[row[Tab.KLASS]] = 0
            if not row[Tab.KLASS] in klass_diskrate_num:
                klass_diskrate_num[row[Tab.KLASS]] = 0

            klass_diskrate_sum[row[Tab.KLASS]
                               ] += row[Tab.DISC_RATE]*row[Tab.MCAP]
            klass_diskrate_num[row[Tab.KLASS]] += row[Tab.MCAP]

    slarge_risk_discrate = sum_slarge_diskrate/slarge_diskrate_num
    smedium_risk_discrate = sum_smedium_diskrate/smedium_diskrate_num
    ssmall_risk_discrate = sum_ssmall_diskrate/ssmall_diskrate_num
    total_risk_discrate = total_diskrate/total_diskrate_num

    klass_risk_discrate = {}
    for kls in klass_diskrate_sum:
        klass_risk_discrate[kls] = klass_diskrate_sum[kls] / \
            klass_diskrate_num[kls]
        print(f"{kls}類別因子折現: {klass_risk_discrate[kls]}")

    # print(
    #     f"規模因子折現-L:{slarge_risk_discrate}/M:{smedium_risk_discrate}/S:{ssmall_risk_discrate}")
    print(
        f"系統折現:{total_risk_discrate}")
    for row in analyze_data:
        cap_ratio = 0
        code = row[Tab.CODE]
        name = row[Tab.NAME]
        hot = row[Tab.HOT]
        klass = row[Tab.KLASS]
        bias = row[Tab.BIAS]
        amount = row[Tab.AMOUNT]
        margin = row[Tab.MARGIN]
        epsdev = row[Tab.EPS_PSTDEV]
        price = row[Tab.PRICE]
        short = row[Tab.SHORT]
        mcap = row[Tab.MCAP]

        margin_cap = margin*price
        short_cap = short*price
        margin_risk = (margin_cap+short_cap)/(mcap*0.25)+1

        if mcap is not None:
            cap_ratio = mcap/total_mcap

        if row[Tab.DISC_RATE] is not None:
            klass_risk = 0
            scale_risk = 0

            if klass is not None:
                klass_risk = klass_risk_discrate[klass]
                scale = row[Tab.MCAP]/total_mcap

                if scale > 0.0025:
                    scale_risk = slarge_risk_discrate
                elif scale > 0.0004:
                    scale_risk = smedium_risk_discrate
                else:
                    scale_risk = ssmall_risk_discrate

            # total_risk_discrate*row[Tab.BETA]["system"] +
            bias = row[Tab.BIAS]
            risk_discrate = cpi + \
                row[Tab.EPS_PSTDEV] * \
                (klass_risk+scale_risk) * margin_risk * (1+hot) * (1+bias)

            row[Tab.RISK_COMP] = risk_discrate
            # if row[Tab.EPS_PSTDEV] is None:
            #     print(row[Tab.CODE])

            if risk_discrate - row[Tab.EPS_GROWTH] < 0.033:
                row[Tab.P_PRICE] = row[Tab.P_EPS] / 0.033
            else:
                row[Tab.P_PRICE] = row[Tab.P_EPS] / \
                    (risk_discrate - row[Tab.EPS_GROWTH])

            if row[Tab.CODE] == "0000":
                row[Tab.P_PRICE] = 1

            row[Tab.P_DIFF_RATE] = (
                row[Tab.P_PRICE] - price)/price
            diff_rate = row[Tab.P_DIFF_RATE]

        reserve = row[Tab.RESERVE]

        if klass is None or (row[Tab.EPS] is not None and diff_rate >= 0.05 and row[Tab.P_EPS]/price > cpi and ((bias <= 0 and margin/amount <= 0.01 and epsdev <= 0.04) or (reserve > 0))):
            eps_data.append(row)

        # if row[Tab.BOOK] is not None and (cap_ratio > 0.001 and (hot > 0.01 and diff_rate > 1)):
        #    if row[Tab.P_DIFF_RATE] > 0.1:
        #         book_data.append(row)

        # if row[Tab.PRICE] is not None and (cap_ratio > 0.001 or "00" == row[Tab.CODE][:2] or (hot > 0.01 and diff_rate > 1)):
        #     if row[Tab.P_DIFF_RATE] > 0.1:
        #         price_data.append(row)

    eps_opts = None
    # book_opts = None
    # price_opts = None

    noa = len(eps_data)
    unit = 1
    if noa > 0:
        bnds = tuple((0, unit) for x in range(noa))
        cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - unit})
        weights = np.array(noa*[unit / noa,])
        eps_opts = optmize.minimize(std_deviation_eps, weights, method='SLSQP', bounds=bnds,
                                    constraints=cons)

    """
    noa = len(price_data)
    unit = 1
    if noa > 0:
        bnds = tuple((0, unit) for x in range(noa))
        cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - unit})
        weights = np.array(noa*[unit / noa,])
        price_opts = optmize.minimize(std_deviation_price, weights, method='SLSQP', bounds=bnds,
                                      constraints=cons)

    noa = len(book_data)
    unit = 1
    if noa > 0:
        bnds = tuple((0, unit) for x in range(noa))
        cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - unit})
        weights = np.array(noa*[unit / noa,])
        book_opts = optmize.minimize(std_deviation_book, weights, method='SLSQP', bounds=bnds,
                                     constraints=cons)
    """

    # print(opts['x'].round(3))
    cnum = 0
    investment = 2200000

    for i in range(len(eps_data)):
        # if int(eps_data[i][Tab.CODE]) in invalid_list:
        #     continue
        eps_data[i][Tab.EPS_WEIGHT] = int(eps_opts['x'][i]*investment/unit)

    """
    for i in range(len(book_data)):
        # if int(book_data[i][Tab.CODE]) in invalid_list:
        #     continue
        book_data[i][Tab.BOOK_WEIGHT] = int(
            book_opts['x'][i]*investment/unit)

    for i in range(len(price_data)):
        # if int(price_data[i][Tab.CODE]) in invalid_list:
        #     continue
        price_data[i][Tab.PRICE_WEIGHT] = int(
            price_opts['x'][i]*investment/unit)
    """

    for row in analyze_data:
        w = 0
        divider = 0
        avg_weight = None
        # for row2 in analyze_data2:
        #     if row[Tab.CODE] != row2[Tab.CODE]:
        #         w = row2[Tab.WEIGHT]
        #         row.append(None)
        if row[Tab.EPS_WEIGHT] is not None:
            w = w+row[Tab.EPS_WEIGHT]
            divider += 1

        """

        if row[Tab.PRICE_WEIGHT] is not None:
            w = w+row[Tab.PRICE_WEIGHT]
            divider += 1
        if row[Tab.BOOK_WEIGHT] is not None:
            w = w+row[Tab.BOOK_WEIGHT]
            divider += 1

        if divider != 0:
            avg_weight = int(w/divider)
        """
        row.append(avg_weight)

        n = 0
        for rnum in Tab.Valist:
            tabformat = Tab.def_format
            # if row[rnum] is None:
            #     continue

            Tab.summary_sheet.write(
                cnum+1, n, row[rnum], tabformat)
            n += 1

        cnum = cnum + 1
    Tab.workbook.close()

    return 0


def crawling_thread(cur_date, end_date=None):

    mydb = MyDataBase()

    if end_date is None:
        end_date = cur_date + Datetime.timedelta(days=1)
    else:
        end_date = end_date + Datetime.timedelta(days=1)

    print(
        f"The date to be Crawled is started from {cur_date} and it will be ended at {end_date}")

    while cur_date < end_date:
        listed_data_ok = True
        amount_ok = True
        fund_ok = True
        margin_data_ok = True
        legal_data_ok = True
        """
        OTC_amount_ok = True
        OTC_fund_ok = True
        """
        OTC_data_ok = True

        if cur_date.year >= 2006:
            print(f"crawl {cur_date}")

            if not mydb.download_listed_data_to_sqlite(
                    cur_date):
                listed_data_ok = False

            """
            if cur_date.year >= 2013:
                if not mydb.download_amount_to_sqlite(
                        cur_date.year, cur_date.month, cur_date.day):
                    amount_ok = False
            """
            if not mydb.download_fund_to_sqlite(
                    cur_date.year, cur_date.month, cur_date.day):
                fund_ok = False

        """
        if cur_date.year >= 2015:
            if not mydb.download_OTC_amount_to_sqlite(
                    cur_date.year, cur_date.month, cur_date.day):
                OTC_amount_ok = False

            if not mydb.download_OTC_fundamental_to_sqlite(
                    cur_date.year, cur_date.month, cur_date.day):
                OTC_fund_ok = False

        """
        if cur_date.year >= 2008:
            # needsleep |= mydb.download_OTC_data_to_sqlite(
            #   cur_date.year, cur_date.month, cur_date.day)
            # It seems won't be blocked by server,
            # even if you access extremely frequently.
            # if not mydb.download_OTC_data_to_sqlite(
            #         cur_date.year, cur_date.month, cur_date.day):
            #     OTC_data_ok = False

            if not mydb.download_margin_to_sqlite(
                    cur_date.year, cur_date.month, cur_date.day):
                margin_data_ok = False

            if not mydb.download_legal_to_sqlite(
                    cur_date.year, cur_date.month, cur_date.day):
                legal_data_ok = False

        cur_date += Datetime.timedelta(days=1)
        mydb.commit()
        # if listed_data_ok and OTC_fund_ok and OTC_data_ok and OTC_data_ok:
        # if listed_data_ok and fund_ok and amount_ok:
        if listed_data_ok and margin_data_ok and legal_data_ok:
            print("All pass")
        # elif not listed_data_ok  and not OTC_fund_ok and not OTC_data_ok and not OTC_data_ok:
        elif not listed_data_ok and not fund_ok and not amount_ok and not margin_data_ok and not legal_data_ok:
            print("All fail")
        else:
            # TIME.sleep(1)
            print("Error, retry!")
            print(listed_data_ok)
            print(amount_ok)
            print(fund_ok)
            # print(OTC_amount_ok)
            # print(OTC_fund_ok)
            # print(OTC_data_ok)
            continue

    mydb.close()


def crawl_command(opts):
    dates = opt_get_dates(opts)

    dtime = []
    for d in dates:
        dtime.append(datetime.strptime(d, '%Y-%m-%d'))
    # print(dtime)

    if len(dates) == 1:
        crawling_thread(dtime[0])
    elif len(dates) == 2:
        crawling_thread(dtime[0], dtime[1])
    else:
        print("輸入格式錯誤!")
        help_command(opts)
        sys.exit()


def crawl_revenue_thread(d0, d1):

    d0bak = d0

    while d1 >= d0:
        print(f"download revenue {d0.year}/{d0.month}")
        if mydownload.download_revenue(d0.year-1911, d0.month):
            TIME.sleep(10)
        d0 = d0 + relativedelta(months=1, day=1)

    d0 = d0bak

    mydb = MyDataBase()
    while d1 >= d0:
        print(f"insert revenue {d0.year}/{d0.month}")
        mydb.download_revenue_to_sqlite(d0)
        d0 = d0 + relativedelta(months=1, day=1)
    mydb.close()


def crawl_revenue_command(opts):
    dates = opt_get_dates(opts)

    dtime = []
    for d in dates:
        dtime.append(datetime.strptime(d, '%Y-%m'))
    # print(dtime)

    if len(dates) == 1:
        crawl_revenue_thread(dtime[0], dtime[0])
    elif len(dates) == 2:
        crawl_revenue_thread(dtime[0], dtime[1])
        pass
    else:
        print("輸入格式錯誤!")
        help_command(opts)
        sys.exit()


def crawl_NPM_thread(s0, s1):

    y0 = int(s0[0])
    q0 = int(s0[1])
    y1 = int(s1[0])
    q1 = int(s1[1])
    while y1*10+q1 >= y0*10+q0:
        print(f"download NPM {y0}Q{q0}")
        if mydownload.download_NPM(y0-1911, q0):
            # TIME.sleep(10)
            pass
        if q0 == 4:
            y0 = y0+1
            q0 = 1
        else:
            q0 = q0+1

    y0 = int(s0[0])
    q0 = int(s0[1])

    mydb = MyDataBase()
    while y1*10+q1 >= y0*10+q0:
        print(f"insert NPM {y0}/{q0}")
        mydb.download_NPM_to_sqlite(y0-1911, q0)
        if q0 == 4:
            y0 = y0+1
            q0 = 1
        else:
            q0 = q0+1
    mydb.close()


def season_loop(y0, q0, y1, q1, season_func):
    while y1*10+q1 >= y0*10+q0:
        print(f"{season_func.__name__} {y0}Q{q0}")
        if season_func(y0-1911, q0):
            TIME.sleep(10)
        if q0 == 4:
            y0 = y0+1
            q0 = 1
        else:
            q0 = q0+1


def crawl_EPS_thread(s0, s1):

    y0 = int(s0[0])
    q0 = int(s0[1])
    y1 = int(s1[0])
    q1 = int(s1[1])

    mydb = MyDataBase()

    season_func = mydownload.download_EPS
    season_loop(y0, q0, y1, q1, season_func)

    while y1*10+q1 >= y0*10+q0:
        print(f"Insert EPS {y0}Q{q0}")
        mydb.download_eps_to_sqlite(y0-1911, q0)
        if q0 == 4:
            y0 = y0+1
            q0 = 1
        else:
            q0 = q0+1
    mydb.close()


def crawl_BOOK_thread(s0, s1):

    y0 = int(s0[0])
    q0 = int(s0[1])
    y1 = int(s1[0])
    q1 = int(s1[1])

    season_func = mydownload.download_BOOK
    season_loop(y0, q0, y1, q1, season_func)

    mydb = MyDataBase()
    while y1*10+q1 >= y0*10+q0:
        print(f"insert BOOK {y0}Q{q0}")
        mydb.download_book_to_sqlite(y0-1911, q0)
        if q0 == 4:
            y0 = y0+1
            q0 = 1
        else:
            q0 = q0+1
    mydb.close()


def crawl_Q_command(opts):

    print("Crawl Season")

    seasons = opt_get_seasons(opts)

    print(seasons)

    if len(seasons) == 1:
        crawl_EPS_thread(seasons[0].split('Q'), seasons[0].split('Q'))
        crawl_BOOK_thread(seasons[0].split('Q'), seasons[0].split('Q'))
        crawl_NPM_thread(seasons[0].split('Q'), seasons[0].split('Q'))
    elif len(seasons) == 2:
        crawl_EPS_thread(seasons[0].split('Q'), seasons[1].split('Q'))
        crawl_BOOK_thread(seasons[0].split('Q'), seasons[1].split('Q'))
        crawl_NPM_thread(seasons[0].split('Q'), seasons[1].split('Q'))
    else:
        print("輸入格式錯誤!")
        help_command(opts)
        sys.exit()


def load_amount(code, begin=None, end=None):
    mydb = MyDataBase()
    tab = mydb.load_tab(code, "AMOUNT", begin=begin, end=end)
    name = mydb.load_field(tab, "AMOUNT", "NAME")

    name = name[0]
    forein_in = mydb.load_field(tab, "AMOUNT", "FOREIN_IN")
    forein_out = mydb.load_field(tab, "AMOUNT", "FOREIN_OUT")
    forein_sum = mydb.load_field(tab, "AMOUNT", "FOREIN_SUM")
    local_in = mydb.load_field(tab, "AMOUNT", "LOCAL_IN")
    local_out = mydb.load_field(tab, "AMOUNT", "LOCAL_OUT")
    local_sum = mydb.load_field(tab, "AMOUNT", "LOCAL_SUM")
    s_local_in = mydb.load_field(tab, "AMOUNT", "SMALL_LOCAL_IN")
    s_local_out = mydb.load_field(tab, "AMOUNT", "SMALL_LOCAL_OUT")
    s_local_sum = mydb.load_field(tab, "AMOUNT", "SMALL_LOCAL_SUM")
    total = mydb.load_field(tab, "AMOUNT", "TOTAL")
    mydb.close()

    return {
        "length": len(tab),
        "code": code,
        "name": name,
        "forein_in": forein_in,
        "forein_out": forein_out,
        "forein_sum": forein_sum,
        "local_in": local_in,
        "local_out": local_out,
        "local_sum": local_sum,
        "s_local_in": s_local_in,
        "s_local_out": s_local_out,
        "s_local_sum": s_local_sum,
        "total_in": [i1+i2+i3 for i1, i2, i3 in zip(forein_in, local_in, s_local_in)],
        "total_out": [i1+i2+i3 for i1, i2, i3 in zip(forein_out, local_out, s_local_out)],
        "total": total
    }


def load_fund(code, begin=None, end=None):
    mydb = MyDataBase()
    tab = mydb.load_tab(code, "FUNDAMENTAL", begin=begin, end=end)
    name = mydb.load_field(tab, "FUNDAMENTAL", "NAME")
    date = mydb.load_field(tab, "FUNDAMENTAL", "DATE")
    if len(tab) == 0:
        return None
    name = name[0]
    per = mydb.load_field(tab, "FUNDAMENTAL", "PER")
    pbr = mydb.load_field(tab, "FUNDAMENTAL", "PBR")
    dyr = mydb.load_field(tab, "FUNDAMENTAL", "DYR")
    mydb.close()

    return {
        "length": len(tab),
        "code": code,
        "name": name,
        "date": date,
        "per": per,
        "pbr": pbr,
        "dyr": dyr
    }


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


def load_market_price():
    mydb = MyDataBase()
    for d in get_date_range("2008-01-01", "2023-04-28"):
        tab = mydb.load_stock_tab(d)
        # print(tab)


def load_data(code, begin=None, end=None):
    mydb = MyDataBase()
    tab = mydb.load_stock_tab(code=code, begin=begin, end=end)
    name = mydb.load_field(tab, "STOCK", "NAME")
    date = mydb.load_field(tab, "STOCK", "DATE")

    if len(name) == 0:
        name = code
    else:
        name = name[-1]
    price = mydb.load_field(tab, "STOCK", "CPRICE")
    fluctuation = mydb.load_field(tab, "STOCK", "FLUCATION")
    shares = mydb.load_field(tab, "STOCK", "SHARES")
    top = mydb.load_field(tab, "STOCK", "TOP")
    bottom = mydb.load_field(tab, "STOCK", "BOTTOM")
    date = mydb.load_field(tab, "STOCK", "DATE")
    mydb.close()

    return {
        "length": len(tab),
        "code": code,
        "name": name,
        "date": date,
        "price": price,
        "fluctuation": fluctuation,
        "shares": shares,
        "top": top,
        "bottom": bottom,
    }


def check_and_make_dirs(dir_list):
    for d in dir_list:
        if not os.path.exists(d):
            os.makedirs(d)


def opt_get_dates(opts):
    dates = None
    for opt, arg in opts:
        if opt in ("-t", "--time"):
            time = arg
            dates = time.split(':')
    return dates


def opt_get_seasons(opts):
    dates = None
    for opt, arg in opts:
        if opt in ("-s", "--season"):
            time = arg
            dates = time.split(':')
    return dates


def opt_get_years(opts):
    years = None
    for opt, arg in opts:
        if opt in ("-y", "--year"):
            time = arg
            years = time.split(':')
    return [int(years[0]), int(years[1])]


def opt_get_target(opts):
    target = None
    for opt, arg in opts:
        if opt in ("-T", "--target"):
            target = arg
    return target


def opt_get_code(opts):
    code = None
    for opt, arg in opts:
        if opt in ("-c", "--code"):
            code = arg
    return code


def analyze_command(opts):
    target = opt_get_target(opts)
    dates = opt_get_dates(opts)
    if len(dates) == 1:
        analyze(begin=dates[0], target=target)
    elif len(dates) == 2:
        analyze(begin=dates[0], end=dates[1], target=target)
    else:
        print("No start point specifed")
    sys.exit()


def crawl_basic_command(opts):

    print("Update BASIC")
    mydb = MyDataBase()
    mydb.download_ETF_basic()
    codes = mydb.load_codename(now)
    for c in codes:
        code = c[0]
        name = c[1]
        while not mydb.insert_basic(code, name):
            print(f"Fail to request {code} {name}")
        mydb.commit()
    mydb.close()
    sys.exit()


def crawl_etf_command(opts):

    y0, y1 = opt_get_years(opts)
    print(f"Crawl ETF {y0}:{y1}")
    mydb = MyDataBase()

    bond_etf_list = mydb.load_bond_etf_codename(now)
    for betf in bond_etf_list:
        mydb.histock_download_etfdiv(betf)

    for y in range(y0, y1+1):
        mydownload.download_ETF_div(y)
        mydb.download_etfdiv_to_sqlite(y)
    mydb.close()


def help_command(opts):
    help_info = """Usage:
\t-h, --help
\t-C, --command = [crawl, analyze]
\t\trequired"""
    print(help_info)


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


def plot():
    """
    mydb = MyDataBase()

    code = "8478"
    data = load_data(code, begin="2019-01-01", end="2024-03-07")
    price = data["price"]

    date_raw = data["date"]
    date = [Datetime.datetime.strptime(
        str(d), '%Y-%m-%d').date() for d in date_raw]
    margin = mydb.load_margin(code)
    margin_sum = []
    amount = data["shares"]

    last_margin_sum = 0
    for key in margin:
        margin_sum.append(margin[key][0] + margin[key][1])

    weight1 = amount
    weight2 = [a * m for a, m in zip(amount, margin_sum)]
    print(len(weight1))
    print(len(weight2))
    print(len(margin_sum))
    avg = mymath.cal_avg(price, 300)
    weighted_avg1 = mymath.calc_weight_avg(price, weight1, 300)
    weighted_avg2 = mymath.calc_weight_avg(price, weight2, 300)

    mydb.close()
    line = []
    line.append(price)
    line.append(avg)
    line.append(weighted_avg1)
    line.append(weighted_avg2)

    drawer = MyCodeDrawer(
        "1,2,3,4",
        date,
        line,
        "V2V")
    drawer.draw()
    del drawer
    """
    pass


def plot_command(opts):

    plot()


commands = {
    "analyze": analyze_command,
    "crawl_Q": crawl_Q_command,
    "crawl": crawl_command,
    "crawl_revenue": crawl_revenue_command,
    "crawl_basic": crawl_basic_command,
    "crawl_etf": crawl_etf_command,
    "plot": plot_command,
    "help": help_command
}

if __name__ == "__main__":

    check_and_make_dirs(
        [
            f"{settings['data_root']}/listed_data",
            f"{settings['data_root']}/BOOK",
            f"{settings['data_root']}/amount",
            f"{settings['data_root']}/database"
            f"{settings['data_root']}/EPS",
            f"{settings['data_root']}/fund",
            f"{settings['data_root']}/NPM",
            f"{settings['data_root']}/revenue",
            f"{settings['data_root']}/ETFdiv",
            f"{settings['data_root']}/legal",
            f"{settings['data_root']}/margin",
        ]
    )

    code = None
    target = None
    help = None

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "C:hc:m:d:i:e:pfz:t:T:EBUFs:ry:",
            ["command=", "code=", "help",
             "input=", "end_idx=", "time=", "target=", "season=", "year=", "redownload"])

        for opt, arg in opts:
            if opt in ("-r", "--redownload"):
                mydownload.redownload = True
                print("redownload")
            elif opt in ("-C", "--command"):
                # command = arg
                if arg not in commands:
                    print("no such command: {}".format(arg))
                    sys.exit()
                commands[arg](opts)

    except getopt.GetoptError:
        print("getopt error!")
