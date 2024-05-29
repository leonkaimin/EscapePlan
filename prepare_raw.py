#! /usr/bin/env python3

from MyMath import *
from MyTime import date_to_month
from MyTime import month_to_quart
from datetime import datetime
import csv
from MyDataBase import MyDataBase, KLASS
from MyDataBase import MyDataBase
from settings import *
from MyCodeDrawer import MyCodeDrawer
import csv
import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
from neuralnet import MyNeuralNet
from MyDataBase import KLASS
import re

def get_bufidx():
    fname = f"{settings['data_root']}/bufidx.csv"
    with open(fname, "r", encoding="cp950") as csvfile:
        data = csv.reader(csvfile)

        rows = [r for r in data]
        rows.pop(0)
        date = [d[0] for d in rows]
        buf = [float(d[1])*100/(int(d[2])+int(d[3])) for d in rows]

    bufidx = {}
    for d, b in zip(date, buf):
        m = date_to_month(d)
        if m not in bufidx:
            bufidx[m] = 0
        bufidx[m] += b
    return bufidx

def prepare(klass):
    mydb = MyDataBase(db_path=f"{home}/.default.db")

    X1 = np.empty((0))
    X2 = np.empty((0))
    X3 = np.empty((0))
    X4 = np.empty((0))
    X5 = np.empty((0))
    X6 = np.empty((0))
    Y = np.empty((0))

    for code in mydb.load_code(klass=klass):
        # for code in mydb.load_code():
        if "00" in code:
            continue
        try:

            # stdev = mydb.load_stock_month_stdev(code)
            avg_month = mydb.load_stock_month_average(code)
            revenue = mydb.load_revenue(code)
            npm = mydb.load_NPM(code)
            EPS = mydb.load_EPS(code)
            cap, deno, klass = mydb.load_basic(code)
            if len(revenue) == 0:
                print(f'{code} empty')
                continue

            if cap == 0:
                print(f"{code} cap == 0")
                continue
            if deno == 0:
                print(f"{code} deno == 0")
                continue

            print(f"{code} go")
            issue_shares = cap/deno

            bufidx = get_bufidx()

            time = []
            avg_price = []
            rev = []
            buf = []
            # dev = []

            for r in revenue:
                if not month_to_quart(r) in npm or not r in avg_month:
                    continue

                mat = re.match(r"(\S+)/(\S+)", r).groups()
                y = mat[0]
                m = mat[1]
                time.append(int(y)*12+int(m))
                avg_price.append(avg_month[r])
                tmp = revenue[r]*1000*npm[month_to_quart(r)]/100/issue_shares
                rev.append(tmp)
                buf.append(bufidx[r])
                # dev.append(stdev[r])

            rev_stdev = []
            rev_sum = []
            rev_growth = []
            rev12 = [0] * 11
            for r in rev:

                rev12.append(r)
                rev_stdev.append(statistics.stdev(rev12))
                rev_sum.append(sum(rev12))
                rev_growth.append(calc_growth_rate(rev12))
                rev12.pop(0)

            per = []
            for p, e in zip(avg_price, rev_sum):
                if e == 0:
                    per.append(999999999)
                else:
                    per.append(p/e)

            # X1 = np.array(dev)
            x1 = np.array(rev_stdev[12:])
            x2 = np.array(rev_sum[12:])
            x3 = np.array(rev_growth[12:])
            x4 = np.array(buf[12:])
            x5 = np.array(time[12:])
            x6 = np.array([1 << KLASS.index(k)]*len(time[12:]))
            y1 = np.array(per[12:])

            X1 = np.r_[X1, x1]
            X2 = np.r_[X2, x2]
            X3 = np.r_[X3, x3]
            X4 = np.r_[X4, x4]
            X5 = np.r_[X5, x5]
            X6 = np.r_[X6, x6]
            Y = np.r_[Y, y1]
        except ZeroDivisionError as excp:
            print(f"Error on line {excp.__traceback__.tb_lineno}: {excp}") 
        except Exception as excp:
            print(f"exception {excp}")
            continue

    print(X4)
    # print([[z1, z2, z3, z4] for z1,z2,z3,z4 in zip(X1, X2, X3, Y)])
    np.save(f"{settings['data_root']}/{klass}X1.npy", X1)  # 保存
    np.save(f"{settings['data_root']}/{klass}X2.npy", X2)  # 保存
    np.save(f"{settings['data_root']}/{klass}X3.npy", X3)  # 保存
    np.save(f"{settings['data_root']}/{klass}X4.npy", X4)  # 保存
    np.save(f"{settings['data_root']}/{klass}X5.npy", X5)  # 保存
    np.save(f"{settings['data_root']}/{klass}Y.npy", Y)  # 保存


for k in KLASS:
    if k == "ETF":
        continue
    prepare(k)

exit()
