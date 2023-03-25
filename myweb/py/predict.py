import torch
import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
import pandas as pd
import matplotlib.pyplot as plt
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torchvision.datasets import MNIST
from torch.utils.data import TensorDataset
import torchvision.transforms as transforms
from sklearn.model_selection import train_test_split
import os
import talib
from sklearn.preprocessing import MinMaxScaler
import tushare as ts

window_size = 10

scaler = MinMaxScaler(feature_range=(-1, 1))


def create_features(data, N):
    df = data.copy()
    df = df.drop('pre_close', axis=1)
    for i in range(1, N):
        df[f'open_{i}'] = df['open'].shift(i)
        df[f'high_{i}'] = df['high'].shift(i)
        df[f'low_{i}'] = df['low'].shift(i)
        df[f'close_{i}'] = df['close'].shift(i)
        df[f'change_{i}'] = df['change'].shift(i)
        df[f'pct_chg_{i}'] = df['pct_chg'].shift(i)
        df[f'vol_{i}'] = df['vol'].shift(i)
        df[f'amount_{i}'] = df['amount'].shift(i)
    df['lable'] = df['close'].shift(-1)
    df = np.asarray(df)

    train_data = df[:, 2:]

    train_data_normalized = scaler.fit_transform(train_data)
    train_data_normalized = torch.FloatTensor(train_data_normalized)

    result = []
    for i in range(len(train_data_normalized)):
        seq = train_data_normalized[i][:-1].reshape(1, -1)
        label = train_data_normalized[i][-1].reshape(1, -1)
        result.append((seq, label))

    return result


pro = ts.pro_api('55e32ea804a9a5eb666d9a47c2203377e0b2bc3751b16132a916ef4e')


def gpdata(code):
    df = pro.daily(**{
        "ts_code": f"{code}",
        "trade_date": "",
        "start_date": "20230101",
        "end_date": "",
        "offset": "",
        "limit": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "pre_close",
        "change",
        "pct_chg",
        "vol",
        "amount"
    ])
    return df


def test(test_data, model_test):
    test_result = test_data.copy()
    pred = []
    actual = []
    for seq, labels in test_result:
        seq = seq.cuda()
        labels = labels.cuda()
        with torch.no_grad():
            model_test.hidden_cell = (torch.zeros(1, 1, model_test.hidden_layer_size).cuda(),
                                      torch.zeros(1, 1, model_test.hidden_layer_size).cuda())

            y_pred = model_test(seq)
            pred.append(
                scaler.inverse_transform(np.asarray(torch.cat((seq.cpu(), y_pred.cpu().reshape(-1, 1)), dim=1)))[0][-1])
            actual.append(scaler.inverse_transform(np.asarray(torch.cat((seq.cpu(), labels.cpu()), dim=1)))[0][-1])

    return pred, actual


def predict_code(socket_code):
    df = gpdata(socket_code)
    df = df.sort_values(axis=0, by=['trade_date'], ascending=True).reset_index(drop=True)
    pre = create_features(df, window_size)
    pre = pre[10:]
    code = socket_code[0:6]
    model_test = torch.load(fr'myweb/static/model/{code}.pt')
    model_test.cuda()
    pred, actual = test(pre, model_test)


    return pred, actual
