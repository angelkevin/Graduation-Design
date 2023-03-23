import pandas as pd
import pymysql
import time
import pymysql
import json
import requests
import random
from random import randint

pd.options.display.float_format = '{:.2f}'.format

index_num = randint(1, 100)
cookies = {
    'qgqp_b_id': 'f0eeace5b28b16b04feeefce1693cb8b',
    'HAList': 'ty-0-831906-N%u821C%u5B87%2Cty-0-000519-%u4E2D%u5175%u7EA2%u7BAD%2Cty-0-000032-%u6DF1%u6851%u8FBE%uFF21%2Cty-1-688522-%u7EB3%u777F%u96F7%u8FBE%2Cty-0-832149-N%u5229%u5C14%u8FBE%2Cty-1-688466-%u91D1%u79D1%u73AF%u5883%2Cty-1-688362-%u752C%u77FD%u7535%u5B50%2Cty-1-688292-%u6D69%u701A%u6DF1%u5EA6%2Cty-1-000001-%u4E0A%u8BC1%u6307%u6570%2Cty-1-688047-%u9F99%u82AF%u4E2D%u79D1',
    'st_si': '87025462235082',
    'st_asi': 'delete',
    'st_pvi': '58485145729842',
    'st_sp': '2023-01-17%2017%3A51%3A28',
    'st_inirUrl': 'https%3A%2F%2Fwww.baidu.com%2Flink',
    'st_sn': '2',
    'st_psi': '20230223010627267-113200301321-6756937031',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    # 'Cookie': 'qgqp_b_id=f0eeace5b28b16b04feeefce1693cb8b; HAList=ty-0-831906-N%u821C%u5B87%2Cty-0-000519-%u4E2D%u5175%u7EA2%u7BAD%2Cty-0-000032-%u6DF1%u6851%u8FBE%uFF21%2Cty-1-688522-%u7EB3%u777F%u96F7%u8FBE%2Cty-0-832149-N%u5229%u5C14%u8FBE%2Cty-1-688466-%u91D1%u79D1%u73AF%u5883%2Cty-1-688362-%u752C%u77FD%u7535%u5B50%2Cty-1-688292-%u6D69%u701A%u6DF1%u5EA6%2Cty-1-000001-%u4E0A%u8BC1%u6307%u6570%2Cty-1-688047-%u9F99%u82AF%u4E2D%u79D1; st_si=87025462235082; st_asi=delete; st_pvi=58485145729842; st_sp=2023-01-17%2017%3A51%3A28; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=2; st_psi=20230223010627267-113200301321-6756937031',
    'Referer': 'http://quote.eastmoney.com/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
}

def create_clickable_id(code):
    url_template= '''<a href="../../search/?q={code}" >{code}</a>'''.format(code=code)
    return url_template

def spider(n):
    # time_stamp = time.time()
    # time_stamp = int(time_stamp*1000)
    response = requests.get(
        f'http://{index_num}.push2.eastmoney.com/api/qt/clist/get?cb=jQuery1124046567885410502186_{time.time() * 1000}&pn={n}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_={time.time() * 1000}',
        cookies=cookies,
        headers=headers,
        verify=False, )
    jsondata = response.text
    start_data = jsondata.index('{"rc":0,')
    end_data = jsondata.index('}]}}') + len('}]}}')
    data_list = json.loads(jsondata[start_data:end_data])['data']['diff']
    df = pd.DataFrame(data_list)
    df = df.drop(
        ['f1', 'f13', 'f11', 'f20', 'f21', 'f22', 'f24', 'f25', 'f62', 'f115', 'f140', 'f141', 'f136', 'f152', 'f128'],
        axis=1)
    df.columns = ['latest_price',
                  'rise_and_fall',
                  'rise_and_fall_amount',
                  'volume',
                  'turnover',
                  'amplitude',
                  'turnover_rate',
                  'ratio_pb',
                  'volume_ratio',
                  'code',
                  'name',
                  'highest',
                  'lowest',
                  'open_today',
                  'yesterday',
                  'ratio']
    order = ['code',
             'name',
             'latest_price',
             'rise_and_fall',
             'rise_and_fall_amount',
             'volume',
             'turnover',
             'amplitude',
             'highest',
             'lowest',
             'open_today',
             'yesterday',
             'volume_ratio',
             'turnover_rate',
             'ratio_pb',
             'ratio']
    df = df[order]
    df.columns = ['代码',
                  '名称',
                  '最新价',
                  '涨跌幅(%)',
                  '涨跌额',
                  '成交量(手)',
                  '成交额',
                  '振幅',
                  '最高',
                  '最低',
                  '今开',
                  '昨收',
                  '量比',
                  '换手率',
                  '市盈率(动态)',
                  '市净率']
    df['代码'] = df['代码'].apply(create_clickable_id)
    return df

