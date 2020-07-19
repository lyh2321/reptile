# 导入需要使用到的模块
import urllib.request
import re
import pandas as pd
import pymysql
import os
from pyquery import PyQuery as pq
import time
import requests
import schedule
from requests.adapters import HTTPAdapter
import uuid

obligate1 = ''

requests.packages.urllib3.disable_warnings()
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}

config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456",
    "database": "library"
}
db = pymysql.connect(**config)
cursor = db.cursor()


def getHtml(url):
    try:
        print(url)
        page = s.get(url=url, headers=headers, timeout=10)
        page.encoding = 'utf-8'
        print(page.status_code)
        html = page.text
        doc = pq(html)
        return doc
    except requests.exceptions.RequestException as e:
        print(e)
    return None


def getHtmlProxy(url, ip):
    print(url)
    proxy = {
        'http': ip,
        'https': ip
    }
    print(proxy)
    try:
        page = s.get(url=url, headers=headers, timeout=30, proxies=proxy, verify=False)
        page.encoding = 'utf-8'
        print(page.status_code)
        if page.status_code != 200:
            return None
        html = page.text
        doc = pq(html)
        return doc
    except requests.exceptions.RequestException as e:
        print(e)
    return None


def insertproxy(url, name, targetip, ip, port, ctdt, success, fail, lastdt, status, response, position, anonymous):
    leng = len(selectproxy(ip, port))
    print(leng)
    if leng != 0:
        return
    db.ping()
    sql = "insert into t_sys_proxy(id,url,name,targetip,ip,port,ctdt,success,fail,lastdt,status,response,position,anonymous) values (UUID(),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
        url, name, targetip, ip, port, ctdt, success, fail, lastdt, status, response, position, anonymous)
    print(sql)
    cursor.execute(sql)
    db.commit()


def selectproxy(ip, port):
    db.ping()
    sql = "select id from t_sys_proxy where ip='%s' and port='%s' and status=1;" % (
        ip, port)
    print(sql)
    cursor.execute(sql)
    return cursor.fetchall()


def go():
    # 批次号
    global obligate1
    obligate1 = getNowd()

    db = pymysql.connect(**config)
    cursor = db.cursor()
    print("开始运行" + getNow())

    url = "http://www.89ip.cn/tqdl.html?num=3000&address=&kill_address=&port=&kill_port=&isp="

    doc = getHtml(url);
    ips = doc('.layui-col-md8>div>div').html()
    iparray = ips.split('<br/>');

    for ip in iparray:
        ip = ip.strip()

        start = time.time()

        value = getHtmlProxy("https://httpbin.org/ip", ip)

        elapsed = str(time.time() - start)
        print("Time used:", elapsed)

        if value == None:
            continue
        targetip = value.text()
        targetip = targetip[targetip.index(",") + 2:len(targetip) - 3]
        # print(targetip)
        insertproxy(url, '', targetip, ip[:ip.index(":")], ip[ip.index(":") + 1:], getNow(), 1, 0, getNow(), 1,
                    elapsed[:elapsed.index(".")], '', 2)

    cursor.close()
    db.close()


def getNow():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def getNowd():
    return time.strftime("%Y%m%d%H%M%S", time.localtime())


go()


# print('启动成功')
#
# schedule.every().day.at("00:01").do(go)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
