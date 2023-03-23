import tushare as ts

pro = ts.pro_api('55e32ea804a9a5eb666d9a47c2203377e0b2bc3751b16132a916ef4e')


def gpdata(code):
    df = pro.daily(**{
        "ts_code": f"{code}",
        "trade_date": "",
        "start_date": "20210101",
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
#
# print(gpdata('688633.SH')['trade_date'].tolist())