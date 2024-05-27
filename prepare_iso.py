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


def prepare(klass):
    X1 = np.load(f"{settings['data_root']}/{klass}X1.npy", allow_pickle=True)  # 加载
    X2 = np.load(f"{settings['data_root']}/{klass}X2.npy", allow_pickle=True)  # 加载
    X3 = np.load(f"{settings['data_root']}/{klass}X3.npy", allow_pickle=True)  # 加载
    X4 = np.load(f"{settings['data_root']}/{klass}X4.npy", allow_pickle=True)  # 加载
    X5 = np.load(f"{settings['data_root']}/{klass}X5.npy", allow_pickle=True)  # 加载
    X6 = np.load(f"{settings['data_root']}/{klass}X6.npy", allow_pickle=True)  # 加载
    Y = np.load(f"{settings['data_root']}/{klass}Y.npy", allow_pickle=True)  # 加载

    # X2 = [np.sqrt(x) for x in X2]

    X = np.c_[X1, X2, X3, X4, X5, X6]


    # 建立 Isolation Forest 模型
    # n_estimators: 孤立樹的數量 (越多越準確，但計算量更大)
    # contamination: 預估的異常比例 (用於設定異常分界閾值)
    # max_samples: 每棵樹所使用的樣本數 (可以是整數或'auto')
    # random_state: 隨機種子 (確保結果可重複)
    iso_model = IsolationForest(n_estimators=100, contamination=0.1)

    # 訓練模型 (學習資料分佈，建構孤立樹)
    iso_model.fit(X)

    # 預測異常分數 (越低越可能是異常點)
    scores_pred = iso_model.decision_function(X)

    # 預測異常標籤 (-1 表示異常，1 表示正常)
    y_pred = iso_model.predict(X)

    # Ys = np.array(Y)
    X1s = np.empty((0))
    X2s = np.empty((0))
    X3s = np.empty((0))
    X4s = np.empty((0))
    X5s = np.empty((0))
    X6s = np.empty((0))
    Ys = np.empty((0))
    for i in range(len(y_pred)):
        if y_pred[i] == 1:
            X1s = np.r_[Ys, Y[i]]
            X2s = np.r_[Ys, Y[i]]
            X3s = np.r_[Ys, Y[i]]
            X4s = np.r_[Ys, Y[i]]
            Ys = np.r_[Ys, Y[i]]

    np.save(f"{settings['data_root']}/{klass}X1-iso.npy", X1s)  # 保存
    np.save(f"{settings['data_root']}/{klass}X2-iso.npy", X2s)  # 保存
    np.save(f"{settings['data_root']}/{klass}X3-iso.npy", X3s)  # 保存
    np.save(f"{settings['data_root']}/{klass}X4-iso.npy", X4s)  # 保存
    np.save(f"{settings['data_root']}/{klass}X5-iso.npy", X5s)  # 保存
    np.save(f"{settings['data_root']}/{klass}X6-iso.npy", X6s)  # 保存
    np.save(f"{settings['data_root']}/{klass}Y-iso.npy", Ys)  # 保存


for k in KLASS:
    if k == "ETF":
        continue
    prepare(k)