# 导入需要使用到的模块
# coding=utf8

import pymysql
from pyquery import PyQuery as pq
from requests.adapters import HTTPAdapter
import random
import sys
import time
import hashlib
import requests
import urllib3
import traceback
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_version = sys.version_info

is_python3 = (_version[0] == 3)

orderno = "ZF20207307423uShoW7"
secret = "f1d382adec694f84ae3f618eaf934b2e"

ip = "forward.xdaili.cn"
port = "80"

ip_port = ip + ":" + port

timestamp = str(int(time.time()))
string = ""
string = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp

if is_python3:
    string = string.encode()

md5_string = hashlib.md5(string).hexdigest()
sign = md5_string.upper()

auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp

proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
headers = {"Proxy-Authorization": auth,
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"}

# ------- 配置数据

obligate1 = ''
cityname = ''

config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456",
    "database": "anjuke"
}
db = pymysql.connect(**config)
cursor = db.cursor()


def getHtml(url):
    try:
        print(url)
        if (url.find("javascript:;") > -1):
            print('javascript，跳过')
            return None
        # page = s.get(url=url, headers=getHeaders(), timeout=10)
        # page.encoding = 'utf-8'
        # print(page.status_code)
        r = requests.get(url, headers=headers, proxies=proxy, verify=False, allow_redirects=False)
        r.encoding = 'utf8'
        html = r.text
        doc = pq(html)

        if (doc('error-page').text().find("网页抓取工具访问安居客网站") > -1):
            print('等待ip切换')
            time.sleep(5)
            return getHtml(url)

        if (doc('title').text().find("验证") > -1):
            print('等待验证')
            time.sleep(5)
            return getHtml(url)

        return doc
    except BaseException as e:
        print(e)
        print('错误等待')
        time.sleep(5)
        return getHtml(url)
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
    sql = "select id from t_community_" + cityname + " where  url='%s' ;" % (url)
    print(sql)
    cursor.execute(sql)
    if len(cursor.fetchall()) == 0:
        doc = getHtml(url);
        sql = "insert into t_community_" + cityname + "(id,name,url,price,`物业类型`,`物业费`,`竣工时间`,`绿化率`,`总户数`,`容积率`,`所属商圈`,ctdt,obligate1) values (UUID(),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
            doc('body > div.container > div.price-mod > div.comm-tit > h1').text().strip(),
            url,
            doc(
                'body > div.container > div.price-mod > div.price-infos-mod > a.item.main-item > div > p.price').text().strip(),
            doc('body > div.container > div.comm-mod.comm-brief-mod > div > span:nth-child(1)').text().replace("物业类型：",
                                                                                                               "").strip(),
            doc('body > div.container > div.comm-mod.comm-brief-mod > div > span:nth-child(2)').text().replace("物业费：",
                                                                                                               "").strip(),
            doc('body > div.container > div.comm-mod.comm-brief-mod > div > span:nth-child(3)').text().replace("竣工时间：",
                                                                                                               "").strip(),
            doc('body > div.container > div.comm-mod.comm-brief-mod > div > span:nth-child(4)').text().replace("绿化率：",
                                                                                                               "").strip(),
            doc('body > div.container > div.comm-mod.comm-brief-mod > div > span:nth-child(5)').text().replace("  ",
                                                                                                               "").replace(
                "总户数：", "").strip(),
            doc('body > div.container > div.comm-mod.comm-brief-mod > div > span:nth-child(6)').text().replace("容积率：",
                                                                                                               "").strip(),
            doc('body > div.container > div.comm-mod.comm-brief-mod > div > span:nth-child(7)').text().replace("所属商圈：",
                                                                                                               "").strip(),
            getNow(), obligate1)
        print(sql)
        cursor.execute(sql)
        db.commit()


def inserthousedetail(doc, url):
    db.ping()
    sql = "insert into t_anjukedetail_" + cityname + "(id,name,url,image,`小区`,communityurl,`房型`,`大小`,`朝向`,`装修`,`地址`,`楼形`,`时间`,price,`每平价格`,obligate1,ctdt) values (UUID(),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
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
        db.ping()
        sql = "select id from t_anjukedetail_" + cityname + " where  url='%s' ;" % (url)
        print(sql)
        cursor.execute(sql)
        if len(cursor.fetchall()) == 0:
            housedetaildoc = getHtml(url)
            if (not housedetaildoc is None):
                try:
                    inserthousedetail(housedetaildoc, url)
                    insertcommunity(housedetaildoc('.info-long-item:eq(1)>a').attr('href'))
                except BaseException:
                    traceback.print_exc()
                    print("错误跳过")
        else:
            print("存在跳过")


def run():
    url = "https://m.anjuke.com/" + cityname + "/sale/"

    doc = getHtml(url)
    if doc == None:
        return None

    createtable(cityname)

    list0 = gethasmore0(doc)
    list1 = gethasmore1(doc)

    for list in list0:
        vals0 = list.split(',')
        for list in list1:
            vals1 = list.split(',')
            urls = url + vals1[0] + vals0[0]
            print(urls)
            for page in range(1, 60):
                url(urls + '?page=' + str(page))


def gethouse(url):
    doc01 = getHtml(url)
    if (doc01('.noresult').text().find("暂无相关内容") > -1):
        return
    housedetail(doc01)


def createtable(cityname):
    db.ping()
    try:
        cursor.execute("create table t_anjukedetail_" + cityname + " select * from anjukedetail where id='1'")
        db.commit()
    except BaseException:
        print('')
    db.ping()
    try:
        cursor.execute("create table t_community_" + cityname + " select * from community where id='1'")
        db.commit()
    except BaseException:
        print('')


def go():
    global obligate1
    obligate1 = getNowd()
    global cityname
    cityname = 'sh'
    run()


def getNow():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def getNowd():
    # return time.strftime("%Y%m%d%H%M%S", time.localtime())
    return time.strftime("%Y%m%d", time.localtime())


# go()

if __name__ == "__main__":
    obligate1 = getNowd()
    cityname = 'sh'

    process_pool = ProcessPoolExecutor(2)  # 定义5个进程
    url = "https://m.anjuke.com/" + cityname + "/sale/"

    doc = getHtml(url)

    createtable(cityname)

    list0 = gethasmore0(doc)
    list1 = gethasmore1(doc)
    list0.reverse()

    for list in list0:
        vals0 = list.split(',')
        for list in list1:
            vals1 = list.split(',')
            urls = url + vals1[0] + vals0[0]
            print(urls)
            for page in range(1, 60):
                process_pool.submit(gethouse, (urls + '?page=' + str(page)))

# schedule.every().day.at("00:01").do(go)

# # print('启动成功')

# while True:
#     schedule.run_pending()
#     time.sleep(1)
