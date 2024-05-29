import pandas as pd
import requests
from datetime import datetime as Date
import os
import time as TIME
from bs4 import BeautifulSoup
import importlib
import json
import csv
from settings import *

headers = {
    'user-agent': '"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

redownload = False


def download_file(url, path):
    try:
        print(f"download {url} {path}")
        response = requests.get(url, headers=headers)
        with open(path, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        print(f"Cannot get {url} {e}")
        return None

    return path


def toDate(y, m, d):
    return Date(int(y), m, d).strftime('%Y%m%d')


def toDate_slash(y, m, d):
    date = Date(y, m, d)
    minguo = int(date.year)-1911
    return f"{minguo}/{date.strftime('%m/%d')}"


def download_listed_data_csv(date):

    url = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date={}&type=ALL&response=csv".format(
              date.strftime('%Y%m%d'))
    fname = date.strftime('%Y_%m_%d')
    local_filename = f"{settings['data_root']}/listed_data/{fname}.csv"
    if os.path.exists(local_filename):

        if redownload == True:
            os.remove(local_filename)
        else:
            return local_filename
        
    return download_file(url, local_filename)



def download_legal_csv_file(year, month, day):
    """
    下載外資融資餘額資料

    Args:
        year: 年份
        month: 月份
        day: 日期

    Returns:
        下載的檔案路徑
    """

    url = "https://www.twse.com.tw/rwd/zh/fund/MI_QFIIS?date={}&selectType=ALLBUT0999&response=csv".format(
        toDate(year, month, day)
    )

    local_filename = f"{settings['data_root']}/legal/{year}_{month}_{day}.csv"

    if os.path.exists(local_filename):

        if redownload == True:
            os.remove(local_filename)
        else:
            return True
        
    try:
        return download_file(url, local_filename)
    except Exception as e:
        print(f'下載檔案失敗：{e}')
        sys.exit(1)


def download_margin_csv_file(y, m, d):
    url = "https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN?date={}&selectType=ALL&response=csv".format(
        toDate(y, m, d))
    local_filename = f"{settings['data_root']}/margin/{y}_{m}_{d}.csv"

    if os.path.exists(local_filename):

        if redownload == True:
            os.remove(local_filename)
        else:
            return local_filename
    
    try:
        return download_file(url, local_filename)
    except Exception as e:
        print(f'下載檔案失敗：{e}')





def download_amount_csv_file(y, m, d):
    date = toDate(y, m, d)
    url = f'https://www.twse.com.tw/fund/T86?response=csv&date={date}&selectType=ALL'

    csv_f = f"{settings['data_root']}/amount/{y}_{m}_{d}.csv"
    return download_file(url, csv_f)


def download_fund_csv_file(y, m, d):
    url = 'https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=csv&date={}&selectType=ALL'.format(
        toDate(y, m, d))
    
    local_filename = f"{settings['data_root']}/fund/{y}_{m}_{d}.csv"

    if os.path.exists(local_filename):

        if redownload == True:
            os.remove(local_filename)
        else:
            return local_filename
        
    return download_file(url, local_filename)


def download_OTC_amount_csv_file(y, m, d):
    url = 'https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php?l=zh-tw&o=csv&se=EW&t=D&d={}&s=0,asc'.format(
        toDate_slash(y, m, d))
    csv_f = f"{settings['data_root']}/OTC_amount/{y}_{m}_{d}.csv"
    return download_file(url, csv_f)


def download_OTC_fund_csv_file(y, m, d):
    url = 'https://www.tpex.org.tw/web/stock/aftertrading/peratio_analysis/pera_result.php?l=zh-tw&o=csv&d={}&s=0,asc'.format(
        toDate_slash(y, m, d))
    csv_f = f"{settings['data_root']}/OTC_fundamental/{y}_{m}_{d}.csv"
    return download_file(url, csv_f)


def download_revenue(y, m):
    url = 'https://mops.twse.com.tw/server-java/FileDownLoad'
    filename = f"t21sc03_{y}_{m}.csv"
    local_filename = f"{settings['data_root']}/revenue/{filename}"
    if os.path.exists(local_filename):
        if redownload == True:
            os.remove(local_filename)
        else:
            return False

    form_data = {
        'step': '9',
        'functionName': 'show_file2',
        'filePath': '/t21/sii/',
        'fileName': filename,
    }

    response = requests.post(url, data=form_data, headers=headers)

    # print the response text (the content of the requested file):
    response.raise_for_status()

    with open(local_filename, "wb") as file:
        file.write(response.content)
    return True


def download_NPM(y, season):

    local_filename = f"{settings['data_root']}/NPM/npm{y}Q{season}.csv"

    if os.path.exists(local_filename):
        if redownload == True:
            os.remove(local_filename)
            print(f"remove {local_filename}")
        else:
            return False

    url = 'https://mops.twse.com.tw/mops/web/t163sb06'
    form_data = {
        'year': f'{y}',
        'season': f'0{season}',
        'TYPEK': 'sii',
        'step': '1',
        'firstin': 'true',
        'off': '1',
        'isQuery': 'Y'
    }

    response1 = requests.post(url, data=form_data, headers=headers)
    html_content = response1.content
    # print the response text (the content of the requested file):

    soup = BeautifulSoup(html_content, 'html.parser')
    # print(soup)
    fname_soup = soup.find('input', {'name': 'filename'})

    if fname_soup is None:
        print("NPM soup not found")
        return False

    filename = fname_soup['value']

    url = "https://mops.twse.com.tw/server-java/t105sb02"

    TIME.sleep(10)
    response2 = requests.post(url, data={
        'step': "10",
        'firstin': "true",
        'filename': filename,
    }, headers=headers)
    html_content = response1.content

    # print the response text (the content of the requested file):
    response2.raise_for_status()

    with open(f"{settings['data_root']}/NPM/npm{y}Q{season}.csv", "wb") as file:
        file.write(response2.content)

    return True


def download_EPS(y, season):

    local_filename = f"{settings['data_root']}/EPS/eps{y}Q{season}.csv"
    if os.path.exists(local_filename):
        if redownload == True:
            os.remove(local_filename)
        else:
            return False

    url = 'https://mops.twse.com.tw/mops/web/t163sb04'
    form_data = {
        'year': f'{y}',
        'season': f'0{season}',
        'TYPEK': 'sii',
        'step': '1',
        'firstin': 'true',
        'off': '1',
        'isQuery': 'Y'
    }

    response1 = requests.post(url, data=form_data, headers=headers)
    html_content = response1.content

    # print the response text (the content of the requested file):

    soup = BeautifulSoup(html_content, 'html.parser')
    # print(soup)
    # filename = soup.find('input', {'name': 'filename'})['value']
    if soup is None:
        print("EPS soup not found")
        return False

    file_list = soup.find_all('input', {'name': 'filename'})
    file_list = list(set(file_list))
    url = "https://mops.twse.com.tw/server-java/t105sb02"
    content_list = []

    t = 10
    for f in file_list:
        # print(f['value'])
        response2 = None
        while response2 is None:
            try:

                response2 = requests.post(url, data={
                    'step': "10",
                    'firstin': "true",
                    'filename': f['value'],
                }, headers=headers)
                TIME.sleep(t)
            except Exception as e:
                print(e)
                t += 10
                importlib.reload(requests)

        # print the response text (the content of the requested file):
        response2.raise_for_status()
        content_list.append(response2.content)

    content_cat = b''.join(content_list)

    with open(f"{settings['data_root']}/EPS/eps{y}Q{season}.csv", "wb") as file:
        file.write(content_cat)
    # print(content_cat)
    return True


def download_BOOK(y, season):

    local_filename = f"{settings['data_root']}/BOOK/book{y}Q{season}.csv"
    if os.path.exists(local_filename):
        if redownload == True:
            os.remove(local_filename)
        else:
            return False

    url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb05'
    form_data = {
        'year': f'{y}',
        'season': f'0{season}',
        'TYPEK': 'sii',
        'step': '1',
        'firstin': 'true',
        'off': '1',
        'isQuery': 'Y'
    }

    response1 = requests.post(url, data=form_data, headers=headers)
    html_content = response1.content

    # print the response text (the content of the requested file):

    soup = BeautifulSoup(html_content, 'html.parser')
    # print(soup)
    # filename = soup.find('input', {'name': 'filename'})['value']
    file_list = soup.find_all('input', {'name': 'filename'})

    url = "https://mops.twse.com.tw/server-java/t105sb02"
    content_list = []

    file_list = list(set(file_list))
    t = 10
    for f in file_list:
        # print(f['value'])
        response2 = None
        while response2 is None:
            try:

                response2 = requests.post(url, data={
                    'step': "10",
                    'firstin': "true",
                    'filename': f['value'],
                }, headers=headers)
                TIME.sleep(t)
            except Exception as e:
                print(e)
                t += 10
                importlib.reload(requests)

        # print the response text (the content of the requested file):
        response2.raise_for_status()
        content_list.append(response2.content)

    content_cat = b''.join(content_list)

    with open(f"{settings['data_root']}/BOOK/book{y}Q{season}.csv", "wb") as file:
        file.write(content_cat)
    return True


def download_ETF_div(year):
    # print(f"download ETF divident {year}")
    local_filename = f"{settings['data_root']}/ETFdiv/ETFdiv{year}.csv"
    if os.path.exists(local_filename):
        if redownload == True:
            os.remove(local_filename)
        else:
            return True

    url = 'https://www.twse.com.tw/rwd/zh/ETF/etfDiv?response=json'
    form_data = {

        'startDate': f'{year}0101',
        'endDate': f'{year}0101'
    }

    response1 = requests.post(url, data=form_data, headers=headers)
    html_content = response1.content
    # print the response text (the content of the requested file):

    json_content = json.loads(html_content)
    head = ['證券代號', '證券簡稱', '除息交易日', '收益分配基準日', '收益分配發放日',
            '收益分配金額 (每1受益權益單位)', '收益分配標準 (102年度起啟用)', '公告年度']
    data = json_content["data"]
    data.insert(0, head)
    # filename = soup.find('input', {'name': 'filename'})['value']

    with open(local_filename, "w", encoding="utf-8") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL, delimiter=",")
        for r in data:
            # print(r)
            writer.writerow((r[0], r[1], r[2], r[4], r[5]))

    return True


"""
def download_listed_json_file(date):

    url = 'http://www.twse.com.tw/exchangeReport/' \
          'MI_INDEX?response=json&date={}&type=ALLBUT0999'.format(
              date.strftime('%Y%m%d'))
    fname = date.strftime('%Y_%m_%d')
    local_filename = f"{settings['data_root']}/listed_data/{fname}.json'
    if os.path.exists(local_filename):
        if redownload == True:
            os.remove(local_filename)
        else:
            return True
    return download_file(url, local_filename)
    
def download_OTC_json_file(y, m, d):
    url = 'https://www.tpex.org.tw/web/stock' \
        '/aftertrading/daily_close_quotes/' \
        'stk_quote_result.php?l=zh-tw&o=json&d={}'.format(
            toDate_slash(y, m, d))
    # print(url)
    json_fname = f"{settings['data_root']}/OTC_data/{y}_{m}_{d}.json"
    return download_file(url, json_fname)
"""
