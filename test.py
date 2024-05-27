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

# klass = ''
klass = "半導體業"
X1 = np.load(f"{settings['data_root']}/{klass}X1-iso.npy")  # 加载
X2 = np.load(f"{settings['data_root']}/{klass}X2-iso.npy")  # 加载
X3 = np.load(f"{settings['data_root']}/{klass}X3-iso.npy")  # 加载
Y = np.load(f"{settings['data_root']}/{klass}Y-iso.npy")  # 加载

Xs = [[x1, x2, x3] for x1, x2, x3 in zip(X1, X2, X3)]

Ys_bin = np.empty((0))
for y in Y:
    score = 0
    for g in settings["gate"]:
        if y > g:
            score += 1
    Ys_bin = np.r_[Ys_bin, score]

Ys_bin = Ys_bin.reshape(-1, 1)

# print(Ys_bin)

# NOT CLEAN
# [-336.16161774 -271.41540736 -206.66919698 -141.9229866   -77.17677622
#  -12.43056584   52.31564453  117.06185491  181.80806529]
# CLEAN
# [-213.4468292  -164.03996739 -114.63310557  -65.22624376  -15.81938195
# 33.58747986   82.99434167  132.40120348  181.80806529]

parser = ArgumentParser()
parser.add_argument("n", help="The train times", type=int)
args = parser.parse_args()
n = args.n


# 2. 創建模型
modname = "my_model"
# db_path = "./my_database.db"  # 假設你有一個資料庫用於儲存模型
model = MyNeuralNet(modname, n)

batch_Xs = Xs
batch_Xs0 = [x[0] for x in batch_Xs]
batch_Xs1 = [x[1] for x in batch_Xs]
batch_Xs2 = [x[2] for x in batch_Xs]
batch_Ys = np.array(Ys_bin)
loss, acc = model.test(np.array([batch_Xs0, batch_Xs1, batch_Xs2]), batch_Ys)
print(f"Test Loss={loss}, Test Acc={acc}")
# 6. 儲存模型
# model.save()

# 4. 評估模型 (使用測試集或驗證集)
# test_Xs = [np.random.rand(20, 2) for _ in range(19)]  # 20 個測試樣本
# test_Ys = np.random.rand(20, 1)


# 5. 預測
# predict_Xs = [np.random.rand(5, 2) for _ in range(19)]  # 5 個預測樣本




exit()

line = []
line.append(avg)
line.append(rev)
line.append(eps)
line.append(dev)
line.append(buf)

drawer = MyCodeDrawer(
    "1 2 3 4 5",
    time,
    line,
    "V")
drawer.draw()
del drawer

exit()
