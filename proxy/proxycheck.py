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
# s.mount('http://', HTTPAdapter(max_retries=1))
# s.mount('https://', HTTPAdapter(max_retries=1))

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
        page = s.get(url=url, headers=headers, timeout=5, proxies=proxy, verify=False)
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


def updateproxy(id, targetip, success, fail, response):
    db.ping()
    sql = "update t_sys_proxy set targetip='%s',success=success+'%s',fail=fail+'%s',response='%s',lastdt='%s' where id='%s'" % (
        targetip, success, fail, response, getNow(), id)
    print(sql)
    cursor.execute(sql)
    db.commit()

    checkproxy(id)


def checkproxy(id):
    db.ping()
    sql = "update t_sys_proxy set status=0 where id='%s' and fail>3 and success/fail<3;" % (
        id)
    print(sql)
    cursor.execute(sql)
    db.commit()


def selectproxy():
    db.ping()
    sql = "select id,ip,port,targetip from t_sys_proxy where status!=0;"
    cursor.execute(sql)
    return cursor.fetchall()


def go():
    db = pymysql.connect(**config)
    cursor = db.cursor()
    print("开始运行" + getNow())

    proxylist = selectproxy()

    for proxy in proxylist:
        start = time.time()

        value = getHtmlProxy("https://httpbin.org/ip", proxy[1] + ':' + proxy[2])

        elapsed = str(time.time() - start)
        print("Time used:", elapsed)

        targetip = proxy[3]

        success = 0
        fail = 0
        if value == None:
            fail = 1
        else:
            success = 1
            targetip = value.text()
            targetip = targetip[targetip.index(",") + 2:len(targetip) - 3]

        # print(targetip)
        updateproxy(proxy[0], targetip, success, fail, elapsed)

    cursor.close()
    db.close()


def getNow():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def getNowd():
    return time.strftime("%Y%m%d%H%M%S", time.localtime())


# go()

print('启动成功')
schedule.every(60*6).minutes.do(go)
while True:
    schedule.run_pending()
    time.sleep(1)
