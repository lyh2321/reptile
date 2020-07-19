# 导入需要使用到的模块
import urllib.request
import re
import pandas as pd
import pymysql
import os
from pyquery import PyQuery as pq
import time
import datetime

config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456",
    "database": "reptile"
}
db = pymysql.connect(**config)
cursor = db.cursor()

Url = 'http://quote.eastmoney.com/stock_list.html'  # 东方财富网股票数据连接地址
# filepath = '/root/python/data/'  # 定义数据文件保存路径
filepath = '/Users/lyh/Documents/my/data/'  # 定义数据文件保存路径


# 爬虫抓取网页函数
def getHtml(url):
    html = urllib.request.urlopen(url).read()
    html = html.decode('gbk')
    return html


# 抓取网页股票代码函数
def getStackCode(html):
    s = r'<li><a target="_blank" href="http://quote.eastmoney.com/\S\S(.*?).html">'
    pat = re.compile(s)
    code = pat.findall(html)
    return code


def getCodeName(html):
    doc = pq(html)
    value = []

    ulnum = doc('#quotesearch>ul').size()
    for k in range(0, ulnum):
        linum = doc('#quotesearch>ul:eq(' + str(k) + ')>li').size()
        for i in range(0, linum):
            value.append(doc('#quotesearch>ul:eq(' + str(k) + ')>li:eq(' + str(i) + ')').text());
    return value


def getFile(code, date):
    print('正在获取股票%s数据' % code)
    # A类股 0 和B类股 1
    c = '0';
    if (code[0:1] == '0'):
        c = '1';

    url = 'http://quotes.money.163.com/service/chddata.html?code=' + c + code + \
          '&start=' + getymdplus(date) + \
          '&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'
    urllib.request.urlretrieve(url, filepath + code + '.csv')


def getCreate(fileName):
    # 创建数据表，如果数据表已经存在，会跳过继续执行下面的步骤print('创建数据表stock_%s'% fileName[0:6])
    sqlSentence3 = "create table t_rp_stock_%s" % fileName[0:1] + "(日期 date, 股票代码 VARCHAR(10),     名称 VARCHAR(10),\
                           收盘价 float,    最高价    float, 最低价 float, 开盘价 float, 前收盘 float, 涨跌额    float, \
                           涨跌幅 float, 换手率 float, 成交量 bigint, 成交金额 bigint, 总市值 bigint, 流通市值 bigint)"
    try:
        cursor.execute(sqlSentence3)
    except:
        print('数据表已存在！')


def getsave(fileName):
    data = pd.read_csv(filepath + fileName, encoding="gbk")
    length = len(data)
    for i in range(0, length):
        record = tuple(data.loc[i])
        # 插入数据语句
        try:
            sqlSentence4 = "insert into t_rp_stock_%s" % fileName[0:1] + "(日期, 股票代码, 名称, 收盘价, 最高价, 最低价, 开盘价, 前收盘, 涨跌额, 涨跌幅, 换手率, \
                成交量, 成交金额, 总市值, 流通市值) values ('%s',%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" % record
            # 获取的表中数据很乱，包含缺失值、Nnone、none等，插入数据库需要处理成空值
            sqlSentence4 = sqlSentence4.replace('nan', 'null').replace('None', 'null').replace('none', 'null')
            cursor.execute(sqlSentence4)
        except:
            # 如果以上插入过程出错，跳过这条数据记录，继续往下进行
            break


def getNow():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def getymd():
    return time.strftime("%Y%m%d", time.localtime())


def getymdplus(date_string):
    return (datetime.datetime.strptime(date_string, "%Y%m%d") + datetime.timedelta(days=1)).strftime("%Y%m%d")

    #########################开始干活############################


print('start......')

# 实施抓取
print('读取网站......')
html = getHtml(Url)
print('读取列表......')
codeNameList = getCodeName(html);
for codeName in codeNameList:
    print(codeName)
    name = codeName[0:-8]
    code = codeName[-7:-1]
    sql = "insert into t_rp_code(code,name,lastdt,ctdt) values ('%s','%s','%s','%s');" % (code, name, getymd(), getNow())
    date = ''
    try:
        cursor.execute(sql)
        getCreate(code)

        date = str('19000101')
    except:
        # 如果以上插入过程出错，跳过这条数据记录，继续往下进行
        print('code 已存在: ' + code)
        cursor.execute("select lastdt from t_rp_code where code='%s';" % code)
        results = cursor.fetchall()
        for row in results:
            date = row[0]

    getFile(code, date)
    getsave(code + '.csv')
    sql = "update t_rp_code set lastdt = '%s' where code = '%s';" % (getymd(), code)
    cursor.execute(sql)

cursor.close()
db.commit()
db.close()
