import pymysql

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
cursor.execute("select userid,chapterid from tmp_louyh_1103_2;")
results = cursor.fetchall()
for row in results:
    db.ping()
    cursor.execute(
        "select count(*) from t_lms_userchapterstatistics where userid='%s' and chapterid='%s';" % (row[0], row[1]))
    count = 0
    resultss = cursor.fetchall()
    for rows in resultss:
        print(rows[0])
        count = int(rows[0])
    if (count == 0):
        db.ping()
        cursor.execute(
            "insert into t_lms_userchapterstatistics_s select * from tmp_t_lms_userchapterstatistics_20201103_1 where userid='%s' and chapterid='%s' limit 1;" % (
                row[0], row[1]))
        db.commit()
    if (count > 1):
        print('id:', row[0], 'chapterid:', row[1])
