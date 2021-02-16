import pymysql
import json

config = {
    "host": "127.0.0.1",
    "port": 10001,
    "user": "root",
    "password": "123456",
    "database": "lexuss"
}

db = pymysql.connect(**config)
cursor = db.cursor()


db.ping()
cursor.execute("select markid from tmp_t_ex_examuser_answer_20201223_1 GROUP BY markid")
resultss = cursor.fetchall()
for rows in resultss:
    rows[0]
    db.ping()
    cursor.execute("select * from t_ex_examuser_status GROUP BY markid")

