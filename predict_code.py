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
from argparse import ArgumentParser
import re

mydb = MyDataBase(db_path=f"{home}/.default.db")

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

def get_data(code):

    # stdev = mydb.load_stock_month_stdev(code)

    revenue = mydb.load_revenue(code)
    npm = mydb.load_NPM(code)
    EPS = mydb.load_EPS(code)
    cap, deno, klass = mydb.load_basic(code)
    avg_month = mydb.load_stock_month_average(code)
    bufidx = get_bufidx()
    time = []
    avg_price = []
    rev = []
    buf = []
    issue_shares = cap/deno
    for r in revenue:

        if not month_to_quart(r) in npm or not r in avg_month:
            continue

        mat = re.match(r"(\S+)/(\S+)", r).groups()
        y = mat[0]
        m = mat[1]
        time.append(int(y)*12+int(m))
        avg_price.append(avg_month[r])

        buf.append(bufidx[r])
        tmp = revenue[r]*1000*npm[month_to_quart(r)]/100/issue_shares
        rev.append(tmp)
        # buf.append(bufidx[r])
        # dev.append(stdev[r])

    rev_sum = []
    rev_stdev = []
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

    x1 = np.array(rev_stdev[12:])
    x2 = np.array(rev_sum[12:])
    x3 = np.array(rev_growth[12:])
    x4 = np.array(buf[12:])
    x5 = np.array(time[12:])
    x6 = np.array([1 << KLASS.index(k)]*len(time[12:]))
    batchx = [x1, x2, x3, x4]
    return rev_sum[12:], avg_price[12:], time[12:], batchx, per[12:]


parser = ArgumentParser()
parser.add_argument("n", help="The train times", type=int)
args = parser.parse_args()
n = args.n

code = "2330"
rev_sum, avg_price, time, batchx, per = get_data(code)

batch_Xs0 = batchx[0]
batch_Xs1 = batchx[1]
batch_Xs2 = batchx[2]
batch_Xs3 = batchx[3]
batch_Xs4 = batchx[4]
batch_Xs5 = batchx[5]

modname = "my_model"
model = MyNeuralNet(modname, n)
predictions = model.compute_answer(np.array([batch_Xs0, batch_Xs1, batch_Xs2, batch_Xs3]))

result = [ r*settings["gate"][int(p)] for r, p in zip(rev_sum, predictions)]

revenue = mydb.load_revenue(code)


line = []

line.append(result)
line.append(avg_price)
line.append(rev_sum)
line.append([settings["gate"][int(p)] for p in predictions])
line.append(per)
print(len(avg_price))
draw_fmt = "1,2 3 4,5"


drawer = MyCodeDrawer(
    draw_fmt,
    time,
    line,
    "V")
drawer.draw()
del drawer
