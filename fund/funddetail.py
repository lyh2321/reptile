from utils import getHtml
from utils import savesql
from utils import getsql
import utils
import json


def getdetail(id):
    html = getHtml('http://fund.eastmoney.com/' + id + '.html')

    # 基金前十持仓
    for num in range(1, 11):
        print(num)
        print(html('#position_shares > div.poptableWrap > table > tr:eq(' + str(num) + ')').html())

    # 基金经理人

    # 每日业绩



fundlist = getsql('select id from fund where status=1 limit 1')
for id in fundlist:
    getdetail(str(id[0]))
