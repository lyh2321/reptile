import pymysql
import json
import os
from pathlib import Path

config = {
    "host": "10.25.10.14",
    "port": 3306,
    "user": "root",
    "password": "Weihu2020@!",
    "database": "lexuss"
}

db = pymysql.connect(**config)
cursor = db.cursor()


def exam(userid, vid):
    db.ping()
    cursor.execute(
        "select count(*) from t_ex_examuser where userid='%s' and examid='%s';" % (userid, vid))
    count = 0
    resultss = cursor.fetchall()
    for rows in resultss:
        # print(rows[0])
        count = int(rows[0])
    if (count == 0):
        print("select count(*) from t_ex_examuser where userid='%s' and examid='%s';" % (userid, vid.upper()))


def start(file):
    text = ''
    if os.path.exists(file + str('/access')):
        text = ''
    else:
        return 1;

    with open(file + str('/access'), encoding='utf-8') as file_obj:
        contents = file_obj.read()
        text = contents.rstrip()

    jsontext = json.loads(text)
    for t in jsontext:
        usercode = t['userCode']
        courseid = t['id']
        type = t['type']

        # 1 kaoshi 2 kecheng

        db.ping()
        cursor.execute(
            "select id from t_sys_userinfo where usercode='%s' ;" % (usercode))
        userid = ''
        resultss = cursor.fetchall()
        for rows in resultss:
            userid = rows[0]

        if (type == '1'):
            exam(userid, courseid)
            continue;

        db.ping()
        cursor.execute(
            "select count(*) from t_my_course where userid='%s' and courseid='%s';" % (userid, courseid))
        count = 0
        resultss = cursor.fetchall()
        for rows in resultss:
            # print(rows[0])
            count = int(rows[0])
        if (count == 0):
            print("select count(*) from t_my_course where userid='%s' and courseid='%s';" % (userid, courseid.upper()))
            # db.ping()
            #  db.commit()
        # if (count > 1):
        # print('id:', row[0], 'chapterid:', row[1])


for root, dirs, files in os.walk('./'):
    start(root)
