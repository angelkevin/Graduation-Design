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

pro = ts.pro_api('55e32ea804a9a5eb666d9a47c2203377e0b2bc3751b16132a916ef4e')


def gpdata(code):
    df = pro.daily(**{
        "ts_code": f"{code}",
        "trade_date": "",
        "start_date": "20220101",
        "end_date": "20230101",
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


window_size = 10


def create_features(df, N):
    df = df.copy()
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
    df = np.asarray(df.dropna())

    train_data = df[:, 2:]
    train_data_normalized = scaler.fit_transform(train_data)
    train_data_normalized = torch.FloatTensor(train_data_normalized)

    result = []
    for i in range(len(train_data_normalized)):
        seq = train_data_normalized[i][:-1].reshape(1, -1)
        label = train_data_normalized[i][-1].reshape(1, -1)
        result.append((seq, label))

    return result


class LSTM(nn.Module):
    def __init__(self, input_size=80, hidden_layer_size=100, output_size=1):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size

        self.lstm = nn.LSTM(input_size, hidden_layer_size)

        self.linear = nn.Linear(hidden_layer_size, output_size)

        self.hidden_cell = (torch.zeros(1, 1, self.hidden_layer_size),
                            torch.zeros(1, 1, self.hidden_layer_size))

    def forward(self, input_seq):
        lstm_out, self.hidden_cell = self.lstm(input_seq.view(len(input_seq), 1, -1), self.hidden_cell)
        predictions = self.linear(lstm_out.view(len(input_seq), -1))
        return predictions[-1]


scaler = MinMaxScaler(feature_range=(-1, 1)) #归一化
model = LSTM()
loss_function = nn.MSELoss().cuda()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

epochs = 150
model.cuda()

def train(epochs, model,train_data):
    global single_loss
    for i in range(1, epochs + 1):
        for seq, labels in train_data:
            seq = seq.cuda()
            labels = labels.reshape(1).cuda()
            optimizer.zero_grad()
            model.hidden_cell = (torch.zeros(1, 1, model.hidden_layer_size).cuda(),
                                 torch.zeros(1, 1, model.hidden_layer_size).cuda())
            y_pred = model(seq)
            y_pred.cuda()

            single_loss = loss_function(y_pred, labels)
            single_loss.backward()
            optimizer.step()
    # print(f'loss: {single_loss.item():10.8f}')


# # 在这里运行
# code = pd.read_csv("./code.csv")
# for code_ in code.values:
#     print(code_[0])
#     data = gpdata(code_[0]) # 只需要在这里传入股票代码, example : 300857.SZ 然后下面就直接运行
#     data = data.sort_values(axis=0, by=['trade_date'], ascending=True).reset_index(drop=True)
#     train_data = create_features(data, window_size) # 创建训练集
#     train(150, model)
#     torch.save(model, f'../static/model/{data["ts_code"][0][:6]}.pt') # 保存模型文件

#
# param_value = '000045.SZ'
# data = gpdata(param_value)  # 只需要在这里传入股票代码, example : 300857.SZ 然后下面就直接运行
# data = data.sort_values(axis=0, by=['trade_date'], ascending=True).reset_index(drop=True)
# train_data = create_features(data, window_size)  # 创建训练集
# train(150, model,train_data)
# torch.save(model, f'../static/model/{param_value[:6]}.pt')  # 保存模型文件
