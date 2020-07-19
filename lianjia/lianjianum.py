# 导入需要使用到的模块
import urllib.request
import re
import pymysql
import os
from pyquery import PyQuery as pq
import time
import requests
import schedule
from requests.adapters import HTTPAdapter

obligate1 = ''

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}

# citylist = [
#     'nb',  # 宁波
#     'sh',  # 上海
#     'bj',  # 北京
#     'hf',  # 合肥
#     'sz',  # 深圳
#     'wh',  # 武汉
#     'cd',  # 成都
#     'xm',  # 厦门
#     'gz',  # 广州
# ]

config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456",
    "database": "reptile"
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


# 房子数量
def gethousenum(doc):
    return doc('.resultDes>h2>span').text().strip();


# 售价
def gethasmore0(doc):
    list = []
    num = doc('.hasmore:eq(0)>dd>a').size()
    for i in range(0, num):
        rule = '.hasmore:eq(0)>dd>a:eq(' + str(i) + ')'
        value = doc(rule).attr("href")
        value = value.replace('/ershoufang/', '').replace('/', '')
        values = doc(rule).text()

        list.append(value + ',' + values)
    return list


# 面积
def gethasmore1(doc):
    list = []
    num = doc('.hasmore:eq(1)>dd>a').size()
    for i in range(0, num):
        rule = '.hasmore:eq(1)>dd>a:eq(' + str(i) + ')'
        value = doc(rule).attr("href")
        value = value.replace('/ershoufang/', '').replace('/', '')
        values = doc(rule).text()

        list.append(value + ',' + values)
    return list


def insertlianjianum(city, name, number, value, url):
    db.ping()
    sql = "insert into lianjianum(id,city,name,number,ctdt,value,url,obligate1) values (UUID(),'%s','%s','%s','%s','%s','%s','%s');" % (
        city, name, number, getNow(), value, url, obligate1)
    print(sql)
    cursor.execute(sql)
    db.commit()


def lianjiandict():
    db.ping()
    sql = "select val from t_sys_dict where type='lianjiannum' and status=1 order by seq;"
    cursor.execute(sql)
    return cursor.fetchall()


def run(obligate1, city):
    url = "https://" + city + ".lianjia.com/ershoufang/"
    doc = getHtml(url)

    housenum = -1
    if doc != None:
        housenum = gethousenum(doc)
    else:
        return None

    insertlianjianum(city, '全部', str(housenum), 'all', url)
    print(housenum)
    list0 = gethasmore0(doc)
    list1 = gethasmore1(doc)

    for list in list0:
        vals = list.split(',')
        doc0 = getHtml(url + vals[0] + '/')
        housenum = -1
        if doc0 != None:
            housenum = gethousenum(doc0)

        insertlianjianum(city, vals[1], str(housenum), vals[0], url + vals[0] + '/')

    for list in list1:
        vals = list.split(',')
        doc1 = getHtml(url + vals[0] + '/')
        housenum = -1
        if doc1 != None:
            housenum = gethousenum(doc1)

        insertlianjianum(city, vals[1], str(housenum), vals[0], url + vals[0] + '/')

    for list in list0:
        vals0 = list.split(',')
        for list in list1:
            vals1 = list.split(',')
            doc01 = getHtml(url + vals0[0] + vals1[0] + '/')
            housenum = -1
            if doc01 != None:
                housenum = gethousenum(doc01)

            insertlianjianum(city, vals0[1] + ',' + vals1[1], str(housenum), vals0[0] + ',' + vals1[0],
                             url + vals0[0] + vals1[0] + '/')


def go():
    # 批次号
    global obligate1
    obligate1 = getNowd()

    db = pymysql.connect(**config)
    cursor = db.cursor()
    print("开始运行" + getNow())

    citylist = lianjiandict()

    for cityd in citylist:
        city = cityd[0]
        try:
            run(obligate1, city)
        except BaseException:
            print('error : ' + city)

    cursor.close()
    db.close()


def getNow():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def getNowd():
    return time.strftime("%Y%m%d%H%M%S", time.localtime())


go()

# schedule.every().day.at("00:01").do(go)

# print('启动成功')
# schedule.every(60*6).minutes.do(go)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
