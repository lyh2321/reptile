# 导入需要使用到的模块
# coding=utf8
import urllib.request
import re
import pymysql
import os
from pyquery import PyQuery as pq
import time
import requests
import schedule
from requests.adapters import HTTPAdapter
import uuid
import random

obligate1 = ''

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

proxies={
    'http':'http://127.0.0.1:58591',
}

config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456",
    "database": "anjuke"
}
db = pymysql.connect(**config)
cursor = db.cursor()

headers = open(r"./headers.txt", 'r').readlines()


def getHtml(url):
    try:
        print(url)
        page = s.get(url=url, headers=getHeaders(), timeout=10)
        page.encoding = 'utf-8'
        # print(page.status_code)
        html = page.text
        doc = pq(html)

        if (doc('title').text().find("验证") > -1):
            print('等待验证')
            time.sleep(300)
            return getHtml(url)

        return doc
    except requests.exceptions.RequestException as e:
        print(e)
    return None


def getHeaders():
    h = {
        'User-Agent': headers[random.randint(0, len(headers) - 1)].strip()
    }
    return h


# 售价
def gethasmore0(doc):
    list = []
    num = doc('.js-options-price>div').size()
    print(num)
    for i in range(1, num):
        rule = '.js-options-price>div:eq(' + str(i) + ')>a'
        value = doc(rule).attr("href")
        end_pos = value.rfind('/') - 1
        start_pos = value.rfind('/', 0, end_pos)
        filename = value[start_pos + 1:]
        values = doc(rule).text()

        list.append(filename + ',' + values)
    return list


# 区域
def gethasmore1(doc):
    list = []
    num = doc('.js-region-list>div').size()
    for i in range(1, num):
        rule = '.js-region-list>div:eq(' + str(i) + ')'
        values = doc(rule).text()
        value = ''
        if (doc(rule).attr("data-id") is None):
            value = doc(rule).attr("data-href")
        else:
            value = doc('#blockinfo-' + doc(rule).attr("data-id") + '>div:eq(0)>a').attr('href');

        end_pos = value.rfind('/') - 1
        start_pos = value.rfind('/', 0, end_pos)
        filename = value[start_pos + 1:]

        list.append(filename + ',' + values)
    return list


def insertcommunity(url):
    db.ping()
    sql = "select id from community where obligate1='%s' and url='%s' ;" % (obligate1, url)
    print(sql)
    cursor.execute(sql)
    if len(cursor.fetchall()) == 0:
        doc = getHtml(url);
        sql = "insert into community(id,name,url,price,`物业类型`,`物业费`,`竣工时间`,`绿化率`,`总户数`,`容积率`,`所属商圈`,ctdt,obligate1) values (UUID(),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
            doc('body > div.container > div.price-mod > div.comm-tit > h1').text().strip(),
            url,
            doc('body > div.container > div.price-mod > div.price-infos-mod > a.item.main-item > div > p.price').text().strip(),
            doc('body > div.container > div.comm-mod.comm-brief-mod > div > span:nth-child(1)').text().replace("物业类型：","").strip(),
            doc('body > div.container > div.comm-mod.comm-brief-mod > div > span:nth-child(2)').text().replace("物业费：","").strip(),
            doc('body > div.container > div.comm-mod.comm-brief-mod > div > span:nth-child(3)').text().replace("竣工时间：","").strip(),
            doc('body > div.container > div.comm-mod.comm-brief-mod > div > span:nth-child(4)').text().replace("绿化率：","").strip(),
            doc('body > div.container > div.comm-mod.comm-brief-mod > div > span:nth-child(5)').text().replace("  ","").replace("总户数：","").strip(),
            doc('body > div.container > div.comm-mod.comm-brief-mod > div > span:nth-child(6)').text().replace("容积率：", "").strip(),
            doc('body > div.container > div.comm-mod.comm-brief-mod > div > span:nth-child(7)').text().replace("所属商圈：", "").strip(),
            getNow(), obligate1)
        print(sql)
        cursor.execute(sql)
        db.commit()


def inserthousedetail(doc, url):
    db.ping()
    sql = "insert into anjukedetail(id,name,url,image,`小区`,communityurl,`房型`,`大小`,`朝向`,`装修`,`地址`,`楼形`,`时间`,price,`每平价格`,obligate1,ctdt) values (UUID(),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
        doc('.house-address').text(),
        url,
        doc('#img-list>li:eq(0)>img').attr('src'),
        doc('.info-long-item:eq(1)>a').text().strip(),
        doc('.info-long-item:eq(1)>a').attr("href"),
        doc('body > div.house-info-wrap > div > div.house-data > span:nth-child(3)').text().strip(),
        doc('body > div.house-info-wrap > div > div.house-data > span.fr').text().strip(),
        doc('body > div.house-basic-info-wrap.content-wrap > ul > li:nth-child(2)').text().replace("朝向", "").strip(),
        doc('body > div.house-basic-info-wrap.content-wrap > ul > li:nth-child(4)').text().replace("装修", "", 1).strip(),
        doc('.info-long-item:eq(1)').text().split("（")[1].replace("）", "").strip(),
        doc('body > div.house-basic-info-wrap.content-wrap > ul > li:nth-child(3)').text().replace("楼层", "").strip(),
        doc('body > div.house-overview.content-wrap > div.top-title > div.title-right.release-date').text().strip(),
        doc('body > div.house-info-wrap > div > div.house-data > span.fl').text().strip(),
        doc('body > div.house-basic-info-wrap.content-wrap > ul > li:nth-child(1)').text().replace("单价", "").strip(),
        str(obligate1), str(getNow()))
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except BaseException:
        print('error sql : ' + sql)


def lianjiandict():
    db.ping()
    sql = "select val from t_sys_dict where type='lianjiannum' and status=1 order by seq;"
    cursor.execute(sql)
    return cursor.fetchall()


def housedetail(doc):
    for i in range(0, doc('#searchHide>.list>a').length):
        url = str(doc('#searchHide>.list>a:eq(' + str(i) + ')').attr('href')).split("?")[0]
        housedetaildoc = getHtml(url)
        if (not housedetaildoc is None):
            inserthousedetail(housedetaildoc, url)
            insertcommunity(housedetaildoc('.info-long-item:eq(1)>a').attr('href'))


def run(city):
    url = "https://m.anjuke.com/" + city + "/sale/"

    doc = getHtml(url)
    if doc == None:
        return None

    list0 = gethasmore0(doc)
    list1 = gethasmore1(doc)

    for list in list0:
        vals0 = list.split(',')
        for list in list1:
            vals1 = list.split(',')
            urls = url + vals1[0] + vals0[0]
            print(urls)
            for page in range(1, 999999):
                doc01 = getHtml(urls + '?page=' + str(page))
                if (doc01('.searchHide>div>.noresult').text().find("暂无相关内容") > -1):
                    break
                housedetail(doc01)


def go():
    global obligate1
    obligate1 = getNowd()
    run('sh')


def getNow():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def getNowd():
    return time.strftime("%Y%m%d%H%M%S", time.localtime())


go()

# schedule.every().day.at("00:01").do(go)

# # print('启动成功')

# while True:
#     schedule.run_pending()
#     time.sleep(1)
