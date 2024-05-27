#!/usr/bin/python3.6
import statistics
import numpy as np
from statistics import mean
import scipy.signal
import pandas as pd
from scipy.integrate import trapz
from sklearn.linear_model import LinearRegression


def cal_unsign_value(value):
    min_val = min(value)
    if min_val < 0:
        return [v-min_val for v in value]
    return value


def cal_normalized_value(value):
    max_val = max(value)
    min_val = min(value)
    base = max_val-min_val
    norm = [1] * len(value)
    for i in range(len(value)):
        if base != 0:
            norm[i] = (value[i]-min_val)/base

    return norm


def cal_mean_normalized_value(value):
    max_val = max(value)
    min_val = min(value)
    mean = np.mean(value)
    base = max_val-min_val
    norm = [0] * len(value)
    for i in range(len(value)):
        if base != 0:
            norm[i] = (value[i]-mean)/base

    return norm


def cal_sign_normalized_value(value):
    max_val = max(value)
    min_val = min(value)

    if min_val < 0 and -min_val > max_val:
        max_val = -min_val

    norm = [1] * len(value)
    for i in range(len(value)):
        if max_val != 0:
            norm[i] = value[i]/max_val

    return norm


def cal_OSC(price, exp=1):
    avg12 = cal_ema(price, 12*exp)
    avg26 = cal_ema(price, 26*exp)
    dif = cal_dif(avg12, avg26)
    macd = cal_macd(dif, exp)
    return cal_osc(dif, macd), macd, dif


def cal_axis(values):
    xs = np.array(range(len(values)), dtype=np.float64)
    ys = np.array(values, dtype=np.float64)
    return xs, ys


def cal_range_max(cprice, n):

    range_max = [0]*len(cprice)
    for i in range(len(cprice)):
        if i < n:
            j = 0
        else:
            j = i-n
        range_max[i] = max(cprice[j:i+1])

    return range_max


def cal_range_min(cprice, n):

    range_min = [0] * len(cprice)
    for i in range(len(cprice)):
        if i < n:
            j = 0
        else:
            j = i-n
        range_min[i] = min(cprice[j:i+1])

    return range_min


def cal_loss(price, top, bottom, exp=2):
    ceiling = [p*1.1 for p in price]
    floor = [p*0.9 for p in price]
    normal_top = [(t-f)/(c-f)*100 for t, c, f in zip(top, ceiling, floor)]
    normal_bottom = [(b-f)/(c-f)*100 for b, c,
                     f in zip(bottom, ceiling, floor)]
    normal_price = [(p-f)/(c-f)*100 for p, c,
                    f in zip(price, ceiling, floor)]
    return [pow(p-(t+b)/2, exp) for p, t, b in zip(normal_price, normal_top, normal_bottom)]


def cal_signal(price, top, bottom, exp=2):
    return [pow(1-(t+b)/2/p, exp)*10000 for p, t, b in zip(price, top, bottom)]


def cal_sakata_loss(price, day, exp=2):

    MAX = cal_range_max(price, day)
    MIN = cal_range_min(price, day)

    return [pow(p-(max+min)/2, exp) for p, max, min in zip(price, MAX, MIN)]


def cal_sakata_max_loss(price, day, exp=2):

    MAX = cal_range_max(price, day)

    return [pow(p-max, exp) for p, max in zip(price, MAX)]


def cal_sakata_min_loss(price, day, exp=2):

    MIN = cal_range_min(price, day)

    return [pow(p-min, exp) for p, min in zip(price, MIN)]


def cal_sakata_signal(price, day, exp=2):

    MAX = cal_range_max(price, day)
    MIN = cal_range_min(price, day)

    return [pow(1-(max+min)/2/p, exp)*10000 for p, max, min in zip(price, MAX, MIN)]


def cal_savgol(values, win_size=5):
    if len(values) < win_size:
        print("len(values) < win_size")
        return None
    return scipy.signal.savgol_filter(values, win_size, 1).tolist()


def cal_savgol_ins(values, win_size=5):
    if len(values) < win_size:
        print("len(values) < win_size")
        return None

    new_values = [0]*win_size
    new_values.extend(values)
    return scipy.signal.savgol_filter(new_values, win_size, 1).tolist()[0:-win_size]


def cal_avg(arr, num=5):
    avg = []
    avg.append(sum(arr[0:num])/num)
    for i in range(1, len(arr)):
        avg.append(avg[i-1]*(num-1)/num+arr[i]/num)
    return avg


def cal_ema(arr, days=5):
    data = pd.Series(arr)
    return data.ewm(span=days, min_periods=0, adjust=False, ignore_na=False).mean()


def cal_weight(arr):
    weight = []

    total = sum(arr)

    if len(arr) == 0:
        return []

    if total == 0:
        return [1/len(arr)]*len(arr)
    for i in range(len(arr)):

        weight.append(arr[i]/total)

    # print(sum(weight))
    return weight


def calc_weight_avg(price, amount, num=300):

    w_avg = []
    for i in range(1, len(price)+1):
        first = i - num
        last = i
        if first < 0:
            first = 0

        weighted_price = [x*y for x,
                          y in zip(price[first:last], cal_weight(amount[first:last]))]

        w_avg.append(sum(weighted_price))

    return w_avg


def cal_weight_top(price, fluc, amount, num):

    top_amount = []
    for f, a in zip(fluc, amount):
        if f > 0:
            top_amount.append(a)
        else:
            top_amount.append(0)

    w_avg = []
    for i in range(1, len(price)+1):
        first = i - num
        last = i
        if first < 0:
            first = 0

        weighted_price = [x*y for x,
                          y in zip(price[first:last], cal_weight(top_amount[first:last]))]

        w_avg.append(sum(weighted_price))

    return w_avg


def cal_weight_bottom(price, fluc, amount, num):

    bt_amount = []
    for f, a in zip(fluc, amount):
        if f < 0:
            bt_amount.append(a)
        else:
            bt_amount.append(0)

    w_avg = []
    for i in range(1, len(price)+1):
        first = i - num
        last = i
        if first < 0:
            first = 0

        weighted_price = [x*y for x,
                          y in zip(price[first:last], cal_weight(bt_amount[first:last]))]

        w_avg.append(sum(weighted_price))

    return w_avg


def percentify(value):
    percentage = []
    last_v = value[0]
    for v in value:
        percentage.append(v/last_v)
        last_v = v
    return percentage


def ema_weight(num):
    ema = [i/sum(range(num)) for i in range(num)]
    # print(sum(ema))
    return ema


def cal_ratio(arr1, arr2):
    ratio = []
    if len(arr1) != len(arr2):
        print("arr1 len {} != arr2 len {}".format(
            len(arr1), len(arr2)
        ))
        return None

    for i in range(len(arr1)):
        if arr2[i] == 0:
            ratio.append(0)
        else:
            ratio.append(arr1[i]/arr2[i])

    return ratio


def cal_dif(X1, X2):

    dif = [0] * len(X1)
    for i in range(len(X1)):
        dif[i] = X1[i] - X2[i]
    return dif


def cal_macd(dif, n=9):
    return cal_ema(dif, n)


def cal_osc(dif, macd):

    osc = [0] * len(dif)

    for i in range(len(dif)):
        osc[i] = round(dif[i] - macd[i], 2)
    return osc


def cal_fluctuation_pts(fluctuation, price):
    pts = [0]*len(fluctuation)
    for i in range(len(fluctuation)):
        pts[i] = fluctuation[i]/price[i]*100
    return pts


def cal_acmlt(fluctuation):

    acmlt = [0] * len(fluctuation)
    acmlt[0] = fluctuation[0]
    for i in range(1, len(fluctuation)):
        acmlt[i] = fluctuation[i] + acmlt[i-1]

    return acmlt


def cal_rsv(cprice, max, min):

    rsv = [0] * len(cprice)
    for i in range(len(cprice)):
        if (max[i] != min[i]):
            rsv[i] = (cprice[i] - min[i])/(max[i]-min[i])
    return rsv


# 當日K值(%K)= 2/3 前一日 K值 + 1/3 RSV
def cal_K(rsv, exp=1):

    K = [0] * (len(rsv))
    for i in range(exp, len(rsv)):
        K[i] = K[i-exp]*2/3 + rsv[i]/3
    return K


# 當日D值(%D)= 2/3 前一日 D值＋ 1/3 當日K值
def cal_D(K, exp=1):

    D = [0] * (len(K))
    for i in range(exp, len(K)):
        D[i] = D[i-exp]*2/3 + K[i]/3

    return D


# 當日D值(%D)= 2/3 前一日 D值＋ 1/3 當日K值
# RSI= UpAvg ÷ ( UpAvg ＋ DownAvg ) × 100
def cal_rsi(fluctuation, n):

    U = [0] * len(fluctuation)
    D = [0] * len(fluctuation)

    for i in range(len(fluctuation)):
        if fluctuation[i] > 0:
            U[i] = fluctuation[i]
        elif fluctuation[i] < 0:
            D[i] = -fluctuation[i]

    ema_U = cal_ema(U, n)
    ema_D = cal_ema(D, n)

    RSI = [0] * len(fluctuation)
    for i in range(len(RSI)):
        if (ema_U[i]+ema_D[i] != 0):
            RSI[i] = ema_U[i]/(ema_U[i]+ema_D[i])

    return RSI


def cal_tr(cprice, top, bottom, n):

    tr = [0] * len(cprice)
    for i in range(1, len(cprice)):

        tr[i] = max(top[i], bottom[i], cprice[i-1]) - \
            min(top[i], bottom[i], cprice[i-1])

    return cal_avg(tr, n)


def cal_dm(top, bottom, n):

    dm_pos = [0] * len(top)
    dm_neg = [0] * len(bottom)

    for i in range(1, len(dm_pos)):
        pos = 0
        neg = 0
        if top[i] > top[i-1]:
            pos = top[i] - top[i-1]

        if bottom[i-1] > bottom[i]:
            neg = bottom[i-1] - bottom[i]

        if pos > neg:
            dm_pos[i] = pos
        elif pos < neg:
            dm_neg[i] = neg

    return cal_avg(dm_pos, n), cal_avg(dm_neg, n)


def cal_di_n(dm, tr):

    di = [0] * len(dm)
    for i in range(len(dm)):
        if tr[i] != 0:
            di[i] = dm[i]/tr[i]*100
    return di


def cal_di(top, bottom, cprice, n):
    tr = cal_tr(top, bottom, cprice, n)
    dm_pos, dm_neg = cal_dm(top, bottom, n)
    return cal_di_n(dm_pos, tr), cal_di_n(dm_neg, tr)


def cal_adx(di_pos, di_neg, n):

    dx = [0] * len(di_pos)
    for i in range(len(di_pos)):
        if (di_pos[i] + di_neg[i]) != 0:
            dx[i] = abs(di_pos[i] - di_neg[i]) / (di_pos[i] + di_neg[i])*100

    return cal_avg(dx, n)


def get_kd(price, n=9):

    if len(price) < n:
        n = len(price)
    range_max = cal_range_max(price, n)
    range_min = cal_range_min(price, n)
    rsv = cal_rsv(price, range_max, range_min)
    K = cal_K(rsv, exp=int(n/9))
    D = cal_D(K, exp=int(n/9))
    KD = cal_dif(K, D)

    return KD, K, D


def get_kd_w(price):

    n = 45
    if len(price) < n:
        n = len(price)

    range_max = cal_range_max(price, n)
    range_min = cal_range_min(price, n)
    rsv = cal_rsv(price, range_max, range_min)
    K = cal_K(rsv, exp=5)
    D = cal_D(K, exp=5)
    KD = cal_dif(K, D)

    return KD, K, D


def get_rsi(fluctuation, n=5):

    if len(fluctuation) < n:
        n = len(fluctuation)

    rsi1 = cal_rsi(fluctuation, n)
    rsi2 = cal_rsi(fluctuation, n*2)

    return rsi1, rsi2


def get_rsi_w(fluctuation):
    n = 25
    if len(fluctuation) < n:
        n = len(fluctuation)
    rsi = cal_rsi(fluctuation, n)

    return rsi


def calc_adx(price, top, bottom, n=70):
    if len(price) < n:
        n = len(price)

    di_pos, di_neg = cal_di(top, bottom, price, n)
    adx = cal_adx(di_pos, di_neg, n)

    return list(adx), list(di_pos), list(di_neg)


def get_osc(price, n=9):

    if len(price) < int(n/9*26):
        n = len(price)
    n0 = n
    n1 = int(n/9*12)
    n2 = int(n/9*26)

    avg12 = cal_ema(price, n1)
    avg26 = cal_ema(price, n2)
    dif = cal_dif(avg12, avg26)
    macd = cal_ema(dif, n0)
    osc = cal_osc(dif, macd)

    return list(osc), list(macd), list(dif)


def get_weighted_osc(price, amount, n=9):

    if len(price) < int(n/9*26):
        n = len(price)
    n0 = n
    n1 = int(n/9*12)
    n2 = int(n/9*26)

    avg12 = calc_weight_avg(price, amount, n1)
    avg26 = calc_weight_avg(price, amount,  n2)
    dif = cal_dif(avg12, avg26)
    macd = cal_macd(dif, n0)
    osc = cal_osc(dif, macd)

    return list(osc), list(macd), list(dif)


def calc_pstdev(price):
    return statistics.pstdev(price)


def calc_variance(price):
    return statistics.variance(price)


def calc_mean(price):
    return statistics.mean(price)


def calc_std(data):
    mean = statistics.mean(data)
    stdev = statistics.stdev(data)
    return [(x - mean) / stdev for x in data]


def calc_gagr(data):

    data = pd.Series(data)
    # 检查是否存在 NaN 值
    if data.isnull().any():
        raise ValueError('数据中存在 NaN 值')

    # 计算每个时间段的改变率（增长率）
    returns = data.pct_change().add(1)

    # 计算 GAGR
    gagr = returns.ewm(span=len(data), min_periods=0, adjust=False,
                       ignore_na=False).mean()
    return gagr[gagr.size-1]


def calc_linear_regression(y):
    """
    使用线性回归计算x,y序列的斜率。

    参数：
        x: 一个Numpy数组或列表，表示自变量序列。
        y: 一个Numpy数组或列表，表示因变量序列。

    返回：
        斜率：一个浮点数，表示x,y序列的斜率。
    """
    # 将输入转换为二维数组
    X = np.array(list(range(1, len(y)+1))).reshape(-1, 1)
    Y = np.array(y)

    # 定义线性回归模型并拟合数据
    model = LinearRegression().fit(X, Y)

    # 提取斜率
    # print(model.coef_)
    slope = model.coef_[0]

    return slope


def calc_slope(data):
    """
    计算给定数据序列的整体斜率。

    Args:
        data: list 或 numpy array，包含数值序列。

    Returns:
        slope: float，输入数据序列的整体斜率。
    """

    slope = np.gradient(data)
    overall_slope = trapz(slope)

    return overall_slope


def calc_growth_rate(sequence):
    n = len(sequence)

    if n == 1:
        return 0

    # Calculate the average of values from index 0 to n-1
    first_value = sum(sequence[:-1]) / (n - 1)

    # Calculate the average of values from index 1 to n
    last_value = sum(sequence[1:]) / (n - 1)
    if first_value < 0 or last_value < 0:
        return 0

    if first_value > last_value:
        return 0
    
    if first_value == 0:
        return 99999999

    growth_rate = (last_value / first_value) - 1

    return growth_rate


def calculate_beta(seq1, seq2):
    """
    计算贝塔值的函数

    参数：
    seq1: array-like，市场指数的时间序列
    seq2: array-like，个股的股价时间序列

    返回值：
    beta: float，个股的贝塔值
    """
    # 将序列转换为 numpy 数组
    if len(seq1) != len(seq2):
        print(f"len{len(seq1)} != len{len(seq2)}")
        return None
    seq1 = np.array(seq1)
    seq2 = np.array(seq2)

    # 计算序列的对数收益率
    log_returns_seq1 = np.diff(np.log(seq1))
    log_returns_seq2 = np.diff(np.log(seq2))

    # 使用最小二乘法拟合线性回归模型，求解斜率即为贝塔值
    beta = np.cov(log_returns_seq1, log_returns_seq2)[
        0, 1] / np.var(log_returns_seq1)

    return beta
