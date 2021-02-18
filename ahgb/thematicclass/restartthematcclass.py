# 重算专题班分数
import sys

sys.path.append('./')
import ahgbutils as u
import json

thematicclassid = '8E98118C-6F97-4969-8459-A529BF7EE9D2'

coursechapterlist = []

sql = "select courseid from t_them_thematicclasscourse where thematicclassid='%s' and `status`=1" % (
    thematicclassid)
courseidlist = u.getSql(sql)
for courseids in courseidlist:
    courseid = courseids[0]
    sql = "select id,courseid,credit from t_cus_coursechapter where courseid='%s';" % (
        courseid)
    for coursechapter in u.getSql(sql):
        coursechapterlist.append(coursechapter)

print(coursechapterlist)

sql = "select reachthematicscore from t_them_thematicclass where  id ='%s'" % (thematicclassid)
reachthematicscore = u.getSql(sql)[0][0]

sql = "select userid,score from t_them_thematicclassuser where study=0 and thematicclassid = '%s' limit 500;" % (
    thematicclassid)
for thematicclassuser in u.getSql(sql):
    userid = thematicclassuser[0]
    score = 0.0
    coursenum = 0

    for coursechapter in coursechapterlist:
        for userchapter in u.getMongo("c_cus_userchap_" + str(coursechapter[1]),
                                      {'userid': userid, 'chapterid': coursechapter[0], 'iscomplete': 1}):
            score += float(coursechapter[2])
            coursenum += 1

    if (thematicclassuser[1] != score):
        print(userid, thematicclassuser[1], score)
        sql = "update t_them_thematicclassuser set coursenum='%s',score='%s',study='%s' where userid='%s' and thematicclassid='%s'" % (
            coursenum, score, 1 if reachthematicscore == score else 0,userid,thematicclassid)
        u.saveSql(sql)

        if (reachthematicscore == score):
            u.getHtml(
                "http://172.20.0.21:8666/pc/thematicclass/savecredit.do?credithour=8.0&content=《2020年中央经济工作会议精神 解读》专题班完成获得学时&contentid=8E98118C-6F97-4969-8459-A529BF7EE9D2&userinfoid=%s&type=3&typed=0&boundary=1000000000000000000000000000000" % (
                    userid))
