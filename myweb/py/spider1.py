import json
import time

import requests
import pandas as pd

def spider(ts_code):
    cookies = {
        'qgqp_b_id': 'f0eeace5b28b16b04feeefce1693cb8b',
        'emshistory': '%5B%22600631%22%2C%22600827%22%5D',
        'HAList': 'ty-1-688480-%u8D5B%u6069%u65AF%2Cty-1-688225-%u4E9A%u4FE1%u5B89%u5168%2Cty-1-688502-N%u8302%u83B1%2Cty-0-300059-%u4E1C%u65B9%u8D22%u5BCC%2Cty-116-03333-%u4E2D%u56FD%u6052%u5927%2Cty-0-873339-%u6052%u592A%u7167%u660E%2Cty-0-430478-N%u5CC6%u4E00%2Cty-0-300309-*ST%u5409%u827E%2Cty-1-600781-*ST%u8F85%u4EC1%2Cty-1-600247-*ST%u6210%u57CE',
        'st_si': '94756897303045',
        'st_asi': 'delete',
        'st_pvi': '58485145729842',
        'st_sp': '2023-01-17%2017%3A51%3A28',
        'st_inirUrl': 'https%3A%2F%2Fwww.baidu.com%2Flink',
        'st_sn': '3',
        'st_psi': '20230317164724494-113300300815-4716391340',
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        # 'Cookie': 'qgqp_b_id=f0eeace5b28b16b04feeefce1693cb8b; emshistory=%5B%22600631%22%2C%22600827%22%5D; HAList=ty-1-688480-%u8D5B%u6069%u65AF%2Cty-1-688225-%u4E9A%u4FE1%u5B89%u5168%2Cty-1-688502-N%u8302%u83B1%2Cty-0-300059-%u4E1C%u65B9%u8D22%u5BCC%2Cty-116-03333-%u4E2D%u56FD%u6052%u5927%2Cty-0-873339-%u6052%u592A%u7167%u660E%2Cty-0-430478-N%u5CC6%u4E00%2Cty-0-300309-*ST%u5409%u827E%2Cty-1-600781-*ST%u8F85%u4EC1%2Cty-1-600247-*ST%u6210%u57CE; st_si=94756897303045; st_asi=delete; st_pvi=58485145729842; st_sp=2023-01-17%2017%3A51%3A28; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=3; st_psi=20230317164724494-113300300815-4716391340',
        'Referer': 'https://data.eastmoney.com/',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    params = {
        'cb': f'jQuery112302624740855349563_{time.time() * 1000}',
        'fltt': '2',
        'secids': f'{ts_code}',
        'fields': 'f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f64,f65,f70,f71,f76,f77,f82,f83,f164,f166,f168,f170,f172,f252,f253,f254,f255,f256,f124,f6,f278,f279,f280,f281,f282',
        'ut': 'b2884a393a59ad64002292a3e90d46a5',
        '_': f'{time.time() * 1000}',
    }

    response = requests.get('https://push2.eastmoney.com/api/qt/ulist.np/get', params=params, cookies=cookies,
                            headers=headers)

    jsondata = response.text
    start_data = jsondata.index('{"rc":0,')
    end_data = jsondata.index('}]}}') + len('}]}}')
    data_list = json.loads(jsondata[start_data:end_data])['data']['diff']
    df = pd.DataFrame(data_list)
    df = df.drop(
        ["f164", "f166", "f168", "f170", "f172", "f252", "f253", "f254", "f255", "f256", "f124", "f6", "f278", "f279",
         "f280", "f281", "f282"], axis=1)
    df.columns = ["今日主力",
                  "主力净比",
                  "超大单流入",
                  "超大单流出",
                  "今日超大单净入",
                  "超大单净比",
                  "大单流入",
                  "大单流出",
                  "今日大单净入",
                  "大单净比",
                  "中单流入",
                  "中单流出",
                  "今日中单净入",
                  "今日中单净比",
                  "小单流入",
                  "小单流出",
                  "小单净流入",
                  "小单净比"]
    return df