import pymysql
import pymongo
import sys

myclient = pymongo.MongoClient("mongodb://172.20.0.30:20000/")
mydb = myclient["ahgb"]

config = {
    "host": "172.20.0.26",
    "user": "root",
    "password": "123456",
    "database": "ahgb"
}
db = pymysql.connect(**config)
cursor = db.cursor()


def delcredits(userid, compulsorycredithour, electivecredithour):
    db.ping()
    credithour = compulsorycredithour + electivecredithour
    sql = "update t_ct_credit set credithour=credithour-%s,compulsorycredithour=compulsorycredithour-%s,electivecredithour=electivecredithour-%s,thematicclassnum=thematicclassnum-1,type=0 where userinfoid='%s' and status=1;" % (
        credithour, compulsorycredithour, electivecredithour, userid)
    print(sql)
    cursor.execute(sql)
    sql = "UPDATE t_ct_credit SET `type` = 1 WHERE userinfoid ='%s' AND credithour >= reachcredithour AND compulsorycredithour >= reachcompulsorycredithour AND electivecredithour >= reachelectivecredithour AND thematicclassnum >= reachthematicclassnum AND thematcclasscoursehour>=reachthematcclasscoursehour AND `type`=0 AND status=1" % (
        userid)
    cursor.execute(sql)


for userid in str(sys.argv[3]).split(','):
    mycol = mydb["t_cd_creditdetail_" + userid[34:]]
    compulsorycredithour = 0
    electivecredithour = 0
    for x in mycol.find(
            {}, {'userinfoid': userid, 'type': 3, 'ctdt': {'$gte': sys.argv[1], '$lte': sys.argv[2]}}):
        if (x['ctype'] == 0):
            electivecredithour += x['credithour']
        else:
            compulsorycredithour += x['credithour']

    print(electivecredithour)
    print(compulsorycredithour)
    print(electivecredithour + compulsorycredithour)
    if ((electivecredithour + compulsorycredithour) > 0):
        delcredits(userid, compulsorycredithour, electivecredithour)
