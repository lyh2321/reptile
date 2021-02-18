import pymysql
import pymongo
from pyquery import PyQuery as pq
import requests
from requests.adapters import HTTPAdapter
import traceback
import time

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}

config = {
    # "host": "172.20.0.26",
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456",
    "database": "ahgb"
}
db = pymysql.connect(**config)
cursor = db.cursor()

myclient = pymongo.MongoClient("mongodb://172.20.0.30:20000/")
mydb = myclient["ahgb"]


def getMongo(title, finds):
    return mydb[title].find({}, finds)


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


def saveSql(sql):
    db.ping()
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except BaseException:
        print('error sql : ' + sql)


def getSql(sql):
    db.ping()
    cursor.execute(sql)
    return cursor.fetchall()


def getNow():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
