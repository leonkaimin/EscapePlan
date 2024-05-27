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
np.set_printoptions(suppress=True, precision=3) 
Yr = np.empty((0))
for klass in KLASS:
    if klass == "ETF":
        continue
    Y = np.load(f"{settings['data_root']}/{klass}Y-iso.npy")  # 加载
    print(f"{klass}: {len(Y)}")
    Yr = np.r_[Yr, Y]

# 計算分位數
quantiles = np.linspace(0, 1, 11)  # 生成 11 個等分點 (0, 0.1, 0.2, ..., 1)
bin_edges = np.quantile(Yr, quantiles)  # 計算分位數作為 bin 邊界

# 計算每個 bin 的數量
hist, _ = np.histogram(Yr, bins=bin_edges)

print("Bin edges:", bin_edges)
print("Counts in each bin:", hist)
# [-466666.607     -21.747      -0.859       9.635      11.987      14.179
# 16.775      20.563      27.012      43.186  269164.567]