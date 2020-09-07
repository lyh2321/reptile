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
import uuid
import traceback

obligate1 = ''

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
    "database": "reptile"
}
db = pymysql.connect(**config)
cursor = db.cursor()
cityname = ''


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
        traceback.print_exc()
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


# 最大翻页数
def getmaxpage(doc):
    try:
        value = doc('.house-lst-page-box').attr('page-data')
        value = value[value.index(':') + 1:]
        value = value[:value.index(',')]
        return value
    except:
        return None


def ljpage(pid, page, url, val):
    doc = getHtml(url + 'pg' + str(page) + val + '/')
    if doc == None:
        return

    num = doc('.sellListContent>li').size()

    for i in range(0, num):
        url = doc('.sellListContent>li:eq(' + str(i) + ')>a').attr('href')
        image = doc('.sellListContent>li:eq(' + str(i) + ')>a>.lj-lazy').attr("data-original")
        alt = doc('.sellListContent>li:eq(' + str(i) + ')>a>.lj-lazy').attr("alt")
        name = doc('.sellListContent>li:eq(' + str(i) + ')>div>.title').text()
        price = doc('.sellListContent>li:eq(' + str(i) + ')>div>div>.totalPrice').text()
        unitPrice = doc('.sellListContent>li:eq(' + str(i) + ')>div>div>.unitPrice').text()
        value = doc('.sellListContent>li:eq(' + str(i) + ')>div>.address>.houseInfo').text()
        flood = doc('.sellListContent>li:eq(' + str(i) + ')>div>.flood').text()
        followInfo = doc('.sellListContent>li:eq(' + str(i) + ')>div>.followInfo').text()

        vals = value.split('|')
        fs = followInfo.split(' / ')

        insertlianjiadetail(pid, name, url, image, vals[0].strip(), vals[1].strip(), vals[2].strip(), vals[3].strip(),
                            vals[4].strip() if len(vals) > 4 else '',
                            alt, flood, fs[0], fs[1], price, unitPrice)


def insertlianjia(id, name, url, totalnumber, p, a):
    db.ping()
    sql = "insert into lianjia(id,name,url,totalnumber,p,a,ctdt,obligate1) values ('%s','%s','%s','%s','%s','%s','%s','%s');" % (
        id, name, url, totalnumber, p, a, getNow(), obligate1)
    # print(sql)
    cursor.execute(sql)
    db.commit()


def insertlianjiadetail(pid, name, url, image, xq, fx, dx, cx, zx, dz, lx, gz, sj, price, mqjg):
    db.ping()
    sql = "insert into lianjiadetail_" + cityname + "(id,pid,name,url,image,`小区`,`房型`,`大小`,`朝向`,`装修`,`地址`,`楼形`,`关注人数`,`时间`,price,`每平价格`,obligate1,ctdt) values (UUID(),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
        pid,
        name.replace('\'', ' '),
        url, image,
        lx.replace('\'', ' '),
        xq.replace('\'', ' '),
        fx.replace('\'', ' '),
        dx.replace('\'', ' '),
        cx.replace('\'', ' '),
        dz.replace('\'', ' '),
        zx.replace('\'', ' '),
        gz.replace('\'', ' '),
        sj.replace('\'', ' '),
        price.replace('\'', ' '),
        mqjg.replace('\'', ' '),
        obligate1, getNow())
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except BaseException:
        print('error sql : ' + sql)

def createtable():
    db.ping()
    try:
        cursor.execute("create table lianjiadetail_"+cityname+" select * from lianjiadetail where id='1'")
        db.commit()
    except BaseException:
        print('')

def lianjiandict():
    db.ping()
    sql = "select val from t_sys_dict where type='lianjiannum' and status=1 order by seq;"
    cursor.execute(sql)
    return cursor.fetchall()


def run(obligate1, city):
    url = "https://" + city + ".lianjia.com/ershoufang/"

    doc = getHtml(url)

    if doc == None:
        return None

    list0 = gethasmore0(doc)
    list1 = gethasmore1(doc)

    for list in list0:
        vals0 = list.split(',')
        for list in list1:
            vals1 = list.split(',')
            doc01 = getHtml(url + vals0[0] + vals1[0] + '/')
            housenum = -1
            if doc01 != None:
                housenum = gethousenum(doc01)

            id = uuid.uuid4();

            insertlianjia(id, vals0[1] + ',' + vals1[1],
                          url + vals0[0] + vals1[0] + '/',
                          housenum,
                          vals0[0],
                          vals1[0])

            maxpage = getmaxpage(doc01)
            if maxpage == None:
                continue
            for num in range(1, int(maxpage) + 1):
                ljpage(id, num, url, vals0[0] + vals1[0])


def go():
    # 批次号
    global obligate1
    obligate1 = getNowd()

    db = pymysql.connect(**config)
    cursor = db.cursor()
    # print("开始运行" + getNow())

    citylist = lianjiandict()
    getHtml("http://louyh.com/c/addgray.do?ukey=1&title="+obligate1+"-爬虫启动")
    for cityd in citylist:
        city = cityd[0]
        global cityname
        cityname = str(city).replace(".", "")
        createtable()
        try:
            run(obligate1, city)
        except BaseException:
            print('error : ' + city)
    cursor.close()
    db.close()
    getHtml("http://louyh.com/c/addgray.do?ukey=1&title="+obligate1+"-爬虫结束")


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
