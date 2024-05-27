#! /usr/bin/env python3

from MyMath import *
from MyTime import date_to_month
from MyTime import month_to_quart
from datetime import datetime
import csv
from MyDataBase import MyDataBase, KLASS
from MyDataBase import MyDataBase
from settings import settings
from MyCodeDrawer import MyCodeDrawer
import csv
import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt

from neuralnet import MyNeuralNet
from MyDataBase import KLASS 
from argparse import ArgumentParser

# klass = ''

def tarin(klass, model):

    X1 = np.load(f"{settings['data_root']}/{klass}X1-iso.npy")  # 加载
    X2 = np.load(f"{settings['data_root']}/{klass}X2-iso.npy")  # 加载
    X3 = np.load(f"{settings['data_root']}/{klass}X3-iso.npy")  # 加载
    X4 = np.load(f"{settings['data_root']}/{klass}X4-iso.npy")  # 加载
    X5 = np.load(f"{settings['data_root']}/{klass}X5-iso.npy")  # 加载
    X6 = np.load(f"{settings['data_root']}/{klass}X6-iso.npy")  # 加载
    Y = np.load(f"{settings['data_root']}/{klass}Y-iso.npy")  # 加载

    Xs = [[x1, x2, x3, x4, x5, x6] for x1, x2, x3, x4, x5, x6 in zip(X1, X2, X3, X4, X5, X6)]

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

    # 2. 創建模型

    # 3. 訓練模型
    epochs = 10  # 訓練輪數
    batch_size = 100   # 批次大小
    for epoch in range(epochs):
        for i in range(0, len(Xs), batch_size):
            batch_Xs = Xs[i:i+batch_size]
            batch_Xs0 = [x[0] for x in batch_Xs]
            batch_Xs1 = [x[1] for x in batch_Xs]
            batch_Xs2 = [x[2] for x in batch_Xs]
            batch_Xs3 = [x[3] for x in batch_Xs]
            batch_Xs4 = [x[4] for x in batch_Xs]
            batch_Xs5 = [x[5] for x in batch_Xs]
            batch_Ys = np.array(Ys_bin[i:i+batch_size])
            loss, acc = model.train(
                np.array([batch_Xs0, batch_Xs1, batch_Xs2, batch_Xs3, batch_Xs4, batch_Xs5]), batch_Ys, batch_size=batch_size)
            print(
                f"Epoch {epoch+1}, Batch {i//batch_size+1}: Loss={loss}, Acc={acc}")
    # 6. 儲存模型


parser = ArgumentParser()
parser.add_argument("n", help="The train times", type=int)
args = parser.parse_args()
n = args.n

modname = f"my_model"
model = MyNeuralNet(modname, n-1)
for k in KLASS:
    if k == "ETF":
        continue
    if k == "半導體業":
        continue
    n = args.n

    tarin(k, model)

model.save(modname, n)
print("save")

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
