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
from multiprocessing import Pool

obligate1 = ''
cityname = ''

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}

config = {
    "host": "172.17.32.16",
    "user": "root",
    "password": "123456",
    "database": "lj"
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
        xqUrl = doc('.sellListContent>li:eq(' + str(i) + ')>div>.flood>.positionInfo>a').attr('href')
        getLjXqHtml(xqUrl, obligate1)
        getLjErshoufangDetailHtml(url, obligate1)
        vals = value.split('|')
        fs = followInfo.split(' / ')

        # insertlianjiadetail(pid, name, url, image, vals[0].strip(), vals[1].strip(), vals[2].strip(), vals[3].strip(),
        #                     vals[4].strip() if len(vals) > 4 else '',
        #                     alt, flood, fs[0], fs[1], price, unitPrice)


def insertlianjia(id, name, url, totalnumber, p, a):
    db.ping()
    sql = "insert into lianjia (id,name,url,totalnumber,p,a,ctdt,obligate1) values ('%s','%s','%s','%s','%s','%s','%s','%s');" % (
        id, name, url, totalnumber, p, a, getNow(), obligate1)
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except BaseException:
        print('error sql : ' + sql)


def insertlianjiadetail(pid, name, url, image, xq, fx, dx, cx, zx, dz, lx, gz, sj, price, mqjg):
    db.ping()
    sql = "insert into lianjiadetail_" + cityname + " (id,pid,name,url,image,`小区`,`房型`,`大小`,`朝向`,`装修`,`地址`,`楼形`,`关注人数`,`时间`,price,`每平价格`,obligate1,ctdt) values (UUID(),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
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
        cursor.execute("create table lianjiadetail_" + cityname + " select * from lianjiadetail_sh where id='1'")
        db.commit()
    except BaseException:
        print('')
    db.ping()
    try:
        cursor.execute("create table lianjiaxq_" + cityname + " select * from lianjiadetail_sh where id='1'")
        db.commit()
    except BaseException:
        print('')


def lianjiandict():
    db.ping()
    sql = "select val from t_sys_dict where type='lianjiannum' and status=1 order by seq;"
    cursor.execute(sql)
    return cursor.fetchall()


def run(city):
    global cityname
    cityname = str(city).replace(".", "")
    # 批次号
    global obligate1
    obligate1 = getNowd()

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



def getNow():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def getNowd():
    return time.strftime("%Y%m%d%H%M%S", time.localtime())


# 获取链家二手房详情页数据。
# param:url 由ljpage方法中爬取的二手房详情页。
def getLjErshoufangDetailHtml(url, obligate1):
    doc = getHtml(url)
    if doc == None:
        return
    countList = selectDetailUrlExist(url)
    for item in countList:
        for it in item:
            if it >= 1:
                return
    name = doc('.sellDetailHeader>div>div>div.title>h1').text()
    describe = doc('.sellDetailHeader>div>div>div.title>div').text()
    image = doc('#topImg>div.imgContainer>img').attr("src")
    小区 = doc('.overview>div.content>div.aroundInfo>div.communityName>a.info').text()
    房型 = doc('.overview>div.content>div.houseInfo>div.room>div.mainInfo').text()
    大小 = doc('.overview>div.content>div.houseInfo>div.area>div.mainInfo').text()
    朝向 = doc('.overview>div.content>div.houseInfo>div.type>div.mainInfo').text()
    装修 = doc('#introduction>div>div>div.base>div.content>ul>li:nth-child(9)>span').text()
    地址 = doc('.overview>div.content>div.aroundInfo>div.areaName>span.info').text()
    楼形 = doc('#introduction>div>div>div.base>div.content>ul>li:nth-child(2)>span').text()
    关注人数 = doc('#favCount').text() + "人关注"
    时间 = doc('#introduction>div>div>div.transaction>div.content>ul>li:nth-child(1)>span:nth-child(2)').text()
    price = doc('.overview>div.content>div.price>span.total').text() + "万"
    每平价格 = doc('.overview>div.content>div.price>div.text>div.unitPrice>span').text()
    obligate1 = obligate1
    pid = "46bd453a-7a31-42f7-a4ec-ca3e94f963b1"
    ctdt = getNow()
    parentList = selectUuidExistInXq(小区)
    for item in parentList:
        for it in item:
            if it == None:
                return
            else:
                insertLianjiaDetail(name, describe, url, image, it, 小区, 房型, 大小, 朝向, 装修, 地址, 楼形, 关注人数, 时间, price, 每平价格,
                                    obligate1, pid, ctdt)


# 检查id在lianjiadetail表里的唯一性
def selectUuidExistInDetail(id):
    db.ping()
    sql = "select count(id) from lianjiadetail_" + cityname + " where id='%s'" % (
        id
    )
    print(sql)
    cursor.execute(sql)
    return cursor.fetchall()


# 根据小区名称查小区id,实现lianjiaxq表和lianjiadetail的逻辑关联
def selectUuidExistInXq(小区):
    db.ping()
    sql = "select id from  lianjiaxq_" + cityname + " where name='%s'" % (
        小区.replace('\'', ' '),
    )
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except BaseException:
        print('error sql : ' + sql)


# 插入数据到lianjiadetail表里
def insertLianjiaDetail(name, describe, url, image, parent_id, 小区, 房型, 大小, 朝向, 装修, 地址, 楼形, 关注人数, 时间, price, 每平价格,
                        obligate1, pid, ctdt):
    db.ping()
    sql = "insert into lianjiadetail_" + cityname + " (id,`name`,`describe`,`url`,`image`,`parent_id`,`小区`,`房型`,`大小`,`朝向`,`装修`,`地址`,`楼形`,`关注人数`,`时间`,`price`,`每平价格`,obligate1,pid,ctdt) values(UUID(),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
        name,
        describe,
        url,
        image,
        parent_id,
        小区,
        房型,
        大小,
        朝向,
        装修,
        地址,
        楼形,
        关注人数,
        时间,
        price,
        每平价格,
        obligate1,
        pid,
        ctdt
    )
    try:
        cursor.execute(sql)
        db.commit()
    except BaseException:
        print('error sql : ' + sql)


# 查看是否爬过该url，如果count>=1，则return，检索下一条url.
def selectDetailUrlExist(url):
    db.ping()
    sql = "select count(url) from lianjiadetail_" + cityname + " where  url='%s'" % (
        url
    )
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except BaseException:
        print('error sql : ' + sql)


# xqUrl，进入小区url详情页，获取数据并调用insertLianjiaxq_sh插入数据
def getLjXqHtml(xqUrl, obligate1):
    doc = getHtml(xqUrl)
    if doc == None:
        return
    countList = selectXqUrlExist(xqUrl)
    for item in countList:
        for it in item:
            if it >= 1:
                return
    name = doc('.xiaoquDetailHeader>div>div.detailHeader.fl>h1').text()
    address = doc('.xiaoquDetailHeader>div>div.detailHeader.fl>div').text()
    image = doc('#overviewBigImg').attr("src")
    attention = doc('.xiaoquDetailHeader>div>div.DetailFollow.fr>div').text()
    pricesquare = doc('.xiaoquOverview>div.xiaoquDescribe.fr>div.xiaoquPrice.clear>div>span.xiaoquUnitPrice').text()
    buildingyear = doc(
        '.xiaoquOverview>div.xiaoquDescribe.fr>div.xiaoquInfo>div:nth-child(1)>span.xiaoquInfoContent').text()
    buildingtype = doc(
        '.xiaoquOverview>div.xiaoquDescribe.fr>div.xiaoquInfo>div:nth-child(2)>span.xiaoquInfoContent').text()
    propertycosts = doc(
        '.xiaoquOverview>div.xiaoquDescribe.fr>div.xiaoquInfo>div:nth-child(3)>span.xiaoquInfoContent').text()
    propertycompany = doc(
        '.xiaoquOverview>div.xiaoquDescribe.fr>div.xiaoquInfo>div:nth-child(4)>span.xiaoquInfoContent').text()
    developers = doc(
        '.xiaoquOverview>div.xiaoquDescribe.fr>div.xiaoquInfo>div:nth-child(5)>span.xiaoquInfoContent').text()
    buildingtotal = doc(
        '.xiaoquOverview>div.xiaoquDescribe.fr>div.xiaoquInfo>div:nth-child(6)>span.xiaoquInfoContent').text()
    housetotal = doc(
        '.xiaoquOverview>div.xiaoquDescribe.fr>div.xiaoquInfo>div:nth-child(7)>span.xiaoquInfoContent').text()

    insertLianjiaxq_sh(name, address, xqUrl, image, attention, pricesquare, buildingyear, buildingtype, propertycosts,
                       propertycompany, developers, buildingtotal, housetotal, obligate1)


# 检索该url是否在lianjiaxq表里是唯一的。
def selectXqUrlExist(xqUrl):
    db.ping()
    sql = "select count(url) as count from lianjiaxq_" + cityname + " where url='%s'" % (
        xqUrl
    )
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except BaseException:
        print('error sql : ' + sql)


# 往lianjiaxq表里插入数据
def insertLianjiaxq_sh(name, address, xqUrl, image, attention, pricesquare, buildingyear, buildingtype, propertycosts,
                       propertycompany, developers, buildingtotal, housetotal, obligate1):
    ctdt = getNow()
    db.ping()
    sql = "insert into lianjiaxq_" + cityname + " (id,name,address,url,image,attention,pricesquare,buildingyear,buildingtype,propertycosts,propertycompany,developers,buildingtotal,housetotal,pch,ctdt) values (UUID(),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
        name,
        address,
        xqUrl,
        image,
        attention,
        pricesquare,
        buildingyear,
        buildingtype,
        propertycosts,
        propertycompany,
        developers,
        buildingtotal,
        housetotal,
        obligate1,
        ctdt
    )
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except BaseException:
        print('error sql : ' + sql)


def go():
    po = Pool(8)




    # print("开始运行" + getNow())

    citylist = lianjiandict()
    # getHtml("http://louyh.com/c/addgray.do?ukey=1&title=" + obligate1 + "-爬虫启动")
    for cityd in citylist:
        city = cityd[0]
        createtable()
        try:
            # run(city)
            po.apply_async(run, (city,))
        except BaseException:
            print('error : ' + city)
    # getHtml("http://louyh.com/c/addgray.do?ukey=1&title=" + obligate1 + "-爬虫结束")
    po.close()
    po.join()

if __name__=='__main__':
    go()



# schedule.every().day.at("00:01").do(go)

# # print('启动成功')

# while True:
#     schedule.run_pending()
#     time.sleep(1)
