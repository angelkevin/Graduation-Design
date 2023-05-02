import base64
import csv
import io

# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

import pandas as pd
import pymysql
import time
import pymysql
import json
import requests
import random
from random import randint

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib_inline.backend_inline import FigureCanvas

from myweb.py.predict import predict_code
from myweb.py.spider import spider
from myweb.py.kline import gpdata
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Page


# Create your views here.


def spider_data(request):
    data = [i for i in range(0, 266)]
    paginator = Paginator(data, 1)
    try:
        page_number = request.GET.get('page', 1)
    except PageNotAnInteger:
        page_number = 1
    page_obj = paginator.get_page(page_number)
    result = spider(page_number)
    result = result.to_html(classes=None, render_links=True, escape=False, index=False)
    return render(request, "spider.html", {'result': result, 'page_obj': page_obj})


def draw(request):
    code = request.GET.get('id')
    df = gpdata(code)
    df.sort_values(by="trade_date", inplace=True, ascending=True)
    ochl = df[['open', 'close', 'low', 'high']]
    ochl_tolist = [ochl.iloc[i].tolist() for i in range(len(ochl))]

    kline = (
        Kline(init_opts=opts.InitOpts(width="1700px"))
        .add_xaxis(df['trade_date'].tolist())
        .add_yaxis("K-Line", ochl_tolist)
        .set_global_opts(

            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            datazoom_opts=[opts.DataZoomOpts(

                type_="slider",
                range_start=90,  # 默认滑块在最右边
                range_end=100,
            )],
            title_opts=opts.TitleOpts(title=code)
        )
    )
    close_line = Line()
    close_line.add_xaxis(df['trade_date'].tolist())
    close_line.add_yaxis("close", df['close'].tolist())
    close_line.set_global_opts(
        title_opts=opts.TitleOpts(title="close_line"),
        xaxis_opts=opts.AxisOpts(name="Date"),
        yaxis_opts=opts.AxisOpts(name="Value"),
    )
    open_line = Line()
    open_line.add_xaxis(df['trade_date'].tolist())
    open_line.add_yaxis("open", df['open'].tolist())
    open_line.set_global_opts(
        title_opts=opts.TitleOpts(title="open_line"),
        xaxis_opts=opts.AxisOpts(name="Date"),
        yaxis_opts=opts.AxisOpts(name="Value"),
    )
    low_line = Line()
    low_line.add_xaxis(df['trade_date'].tolist())
    low_line.add_yaxis("low", df['low'].tolist())
    low_line.set_global_opts(
        title_opts=opts.TitleOpts(title="low_line"),
        xaxis_opts=opts.AxisOpts(name="Date"),
        yaxis_opts=opts.AxisOpts(name="Value"),
    )
    high_line = Line()
    high_line.add_xaxis(df['trade_date'].tolist())
    high_line.add_yaxis("high", df['high'].tolist())
    high_line.set_global_opts(
        title_opts=opts.TitleOpts(title="high_line"),
        xaxis_opts=opts.AxisOpts(name="Date"),
        yaxis_opts=opts.AxisOpts(name="Value"),
    )

    kline_html = kline.render_embed()
    close_line_html = close_line.render_embed()
    open_line_html = open_line.render_embed()
    low_line_html = low_line.render_embed()
    high_line_html = high_line.render_embed()

    context = {
        'kline_html': kline_html,
        'close_line_html': close_line_html,
        'open_line_html': open_line_html,
        'low_line_html': low_line_html,
        'high_line_html': high_line_html,
    }

    return render(request, 'draw.html', context)


def company_list(request):
    with open(r'myweb/static/stock_company.csv', 'r', encoding=' utf-8') as f:
        reader = csv.DictReader(f)
        companies_ = [row for row in reader]
    data = [i for i in range(int(len(companies_) / 40) + 1)]
    paginator = Paginator(data, 1)
    try:
        page_number = request.GET.get('page', 1)
    except PageNotAnInteger:
        page_number = 1
    page_obj = paginator.get_page(page_number)
    companies = companies_[(int(page_number) - 1) * 40: int(page_number) * 40]
    return render(request, 'company_list.html', {'companies': companies, 'page_obj': page_obj})


def search(request):
    result = []
    q = request.GET.get('q')
    with open(r'myweb/static/stock_company.csv', 'r', encoding=' utf-8') as f:
        reader = csv.DictReader(f)
        companies_ = [row for row in reader]
    for i in companies_:
        if str(q) in str(i.get('ts_code')):
            result.append(i)

    if len(result) == 0 or len(q) != 6:
        return render(request, 'error_msg.html')
    code = result[0].get('ts_code')
    df = gpdata(code)
    df.sort_values(by="trade_date", inplace=True, ascending=True)
    ochl = df[['open', 'close', 'low', 'high']]
    ochl_tolist = [ochl.iloc[i].tolist() for i in range(len(ochl))]

    kline = (
        Kline(init_opts=opts.InitOpts(width="1000px"))
        .add_xaxis(df['trade_date'].tolist())
        .add_yaxis("K-Line", ochl_tolist)
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            datazoom_opts=[opts.DataZoomOpts(

                type_="slider",
                range_start=90,
                range_end=100,
            )],
            title_opts=opts.TitleOpts(title=code)
        )
    )
    kline_html = kline.render_embed()
    return render(request, 'detail.html', {'companies': result, 'kline_html': kline_html})


def detail(request):
    result = []
    code = request.GET.get('id')
    with open(r'myweb/static/stock_company.csv', 'r', encoding=' utf-8') as f:
        reader = csv.DictReader(f)
        companies_ = [row for row in reader]
    for i in companies_:
        if str(code) in str(i.get('ts_code')):
            result.append(i)
    df = gpdata(code)
    df.sort_values(by="trade_date", inplace=True, ascending=True)
    ochl = df[['open', 'close', 'low', 'high']]
    ochl_tolist = [ochl.iloc[i].tolist() for i in range(len(ochl))]

    kline = (
        Kline(init_opts=opts.InitOpts(width="1000px"))
        .add_xaxis(df['trade_date'].tolist())
        .add_yaxis("K-Line", ochl_tolist)
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            datazoom_opts=[opts.DataZoomOpts(

                type_="slider",
                range_start=90,
                range_end=100,
            )],
            title_opts=opts.TitleOpts(title=code)
        )
    )
    kline_html = kline.render_embed()
    return render(request, 'detail.html', {'companies': result, 'kline_html': kline_html})


def predict(request):
    param_value = request.GET.get('socket_code')

    try:

        pred, actual = predict_code(param_value)
        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0] = 15
        fig_size[1] = 5
        plt.rcParams["figure.figsize"] = fig_size
        plt.grid(True)
        plt.title("predict && actual")
        plt.xticks([i for i in range(1, len(pred) + 1)])
        plt.autoscale(axis='x', tight=True)
        predict_, = plt.plot(pred)
        actual_, = plt.plot(actual)
        plt.legend(handles=[predict_, actual_], labels=["predict", "actual"], loc="lower left", fontsize=15)
        plt.savefig(f'myweb/static/img/predict.png')
        plt.close()

        return render(request, 'predict.html')
    except:
        return render(request, 'error_msg.html')
