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
import json
import urllib

obligate1 = ''

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}

cookies = {
    'lmspd_user': '4d91956b282a626e564a96fb078ca70b162c2fa932495e6950c133f8aab5f0b1bc6edd5c07ec56c04886b30555df992f42efc084ad24313d320ff8cf3f8a62d4'
}

config = {
    "host": "10.10.20.02",
    "user": "root",
    "password": "123456",
    "database": "lal"
}
db = pymysql.connect(**config)
cursor = db.cursor()


def getHtml(url):
    try:
        print(url)
        page = s.get(url=url, headers=headers, cookies=cookies, timeout=10)
        page.encoding = 'utf-8'
        # print(page.status_code)
        html = page.text
        doc = pq(html)
        return doc
    except requests.exceptions.RequestException as e:
        print(e)
    return None


def getJson(url):
    try:
        # print(url)
        page = s.get(url=url, headers=headers, cookies=cookies, timeout=10)
        page.encoding = 'utf-8'
        # print(page.status_code)
        html = page.text
        return html
    except requests.exceptions.RequestException as e:
        print(e)
    return None


def insertcourse(c, categoryid):
    db.ping()
    sql = "INSERT INTO `t_lms_course`(`id`, `createUserinfo`, `status`, `tenantid`, `categoryid`, `code`, `commentcount`, `coursecut`, `ctdt`, `descript`, `imgpath`, `keywords`, `learncut`, `name`, `scoreavg`, `scorecount`, `studytype`, `totaltime`, `updt`, `viewcut`) VALUES " \
          "('%s', '1', 1, '1', '%s', '%s', 0, 1, '%s', '', '%s', '', 0, '%s', 0, 0, 0, '%s', '1', 1);" % (
              c['id'], categoryid, c['serialNumber'], c['timeCreated'], c['coursePicture'], c['courseName'],
              c['totalPlayLength'])
    # print(sql)
    cursor.execute(sql)
    db.commit()


def insertcoursechapter(c):
    db.ping()
    sql = "INSERT INTO `t_lms_subcourse`(`id`, `createUserinfo`, `status`, `tenantid`, `name`, `resourcepath`, `sorting`, `time`, `type`, `course_id`) VALUES " \
          "('%s', '1', 1, '1', '%s', '%s', 0, '%s', 1, '%s');" % (
        c['id'],c['scoTitle'],c['id']+'.mp4',c['playLength'],c['course_id'])
    # print(sql)
    cursor.execute(sql)
    db.commit()


def go():
    db = pymysql.connect(**config)
    cursor = db.cursor()
    # print("开始运行" + getNow())

    list = ['85a76f25b77e380d931fc6ec1fd98829', '9398bb212c3d07bdffc7b2dba5425ce6', '7b5c95a087a7c720ac2ab230e861f316',
            '21646e16a2967276ef3b6a43ddde3139']

    for id in list:
        getjson = getJson(
            'http://zaixianxuexi.ct-edu.com.cn/portal/train/course/info/pagelist.json?start=0&size=100&status=Audit&showHidden=false&containSub=true&keywords=&catalog_id=' + id + '&_=1578134848469')
        print(json.loads(getjson))

        for course in json.loads(getjson)['content']:
            # print(course)
            coursejson = json.loads(getJson(
                'http://zaixianxuexi.ct-edu.com.cn/portal/train/course/section/list.json?course_id=' + course['id']))

            # print(course)
            insertcourse(course, id);
            # print(coursejson[0])
            insertcoursechapter(coursejson[0]);

    cursor.close()
    db.close()


go()
