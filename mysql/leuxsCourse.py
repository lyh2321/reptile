import pymysql
import time

config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456",
    "database": "lexuss"
}
db = pymysql.connect(**config)
cursor = db.cursor()


def userids():
    db.ping()
    sql = "select id from t_sys_userinfo"
    cursor.execute(sql)
    return cursor.fetchall()


def CourseAccess(userid):
    db.ping()
    sql = "select CourseID from Member_CourseAccess where MemberID='%s'" % (userid)
    print(sql)
    cursor.execute(sql)
    return cursor.fetchall()


def mychapter(userid, chapterid):
    db.ping()
    sql = "select id from t_my_coursechapter where userid='%s' and chapterid='%s'" % (userid, chapterid)
    print(sql)
    cursor.execute(sql)
    return cursor.fetchall()


def notmychapter(userid, chapterids):
    db.ping()
    sql = "select id from t_my_coursechapter where userid='" + str(userid) + "' and chapterid not in (" + str(
        chapterids) + ")"
    print(sql)
    cursor.execute(sql)
    return cursor.fetchall()


def lmschapter(userid, chapterid):
    db.ping()
    sql = "select id from t_lms_userchapterstatistics where userid='%s' and chapterid='%s'" % (userid, chapterid)
    print(sql)
    cursor.execute(sql)
    return cursor.fetchall()


def notlmschapter(userid, chapterids):
    db.ping()
    sql = "select id from t_lms_userchapterstatistics where userid='" + str(userid) + "' and chapterid not in (" + str(
        chapterids) + ")"
    print(sql)
    cursor.execute(sql)
    return cursor.fetchall()


def savetmp(val, type, obligate1, obligate2, uid):
    db.ping()
    sql = "insert into tmp(id,val,type,ctdt,obligate1,obligate2,uid) values (UUID(),'%s','%s','%s','%s','%s','%s');" % (
        val, type, getNow(), obligate1, obligate2, uid)
    print(sql)
    cursor.execute(sql)
    db.commit()


def getNow():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


for userid in userids():
    cids = "";
    for chapterids in CourseAccess(userid[0]):
        cids += "'" + str(chapterids[0]) + "',"

        mychapterlen = len(mychapter(userid[0], chapterids[0]))
        lmschapterlen = len(lmschapter(userid[0], chapterids[0]))

        if (mychapterlen != 1):
            savetmp(str(chapterids[0]), 0, mychapterlen, '', str(userid[0]))

        if (lmschapterlen != 1):
            savetmp(str(chapterids[0]), 1, lmschapterlen, '', str(userid[0]))

    if (len(cids) == 0):
        continue
    cids = cids[0:len(cids) - 1]

    notmychapters = notmychapter(userid[0], cids)
    notlmschapters = notlmschapter(userid[0], cids)

    if (len(notmychapters) != 0):
        savetmp(cids.replace("'", "\""), 2, len(notmychapters), '', userid[0])

    if (len(notlmschapters) != 0):
        savetmp(cids.replace("'", "\""), 3, len(notlmschapters), '', userid[0])
