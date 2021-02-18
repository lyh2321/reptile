from utils import getHtml
from utils import savesql
import utils
import json

fundlist = getHtml('http://fund.eastmoney.com/js/fundcode_search.js').text().replace('var r = ', '').strip()[:-1]
print(fundlist)

for flist in json.loads(fundlist):
    print(flist[0], flist[1], flist[2], flist[3], flist[4])
    sql = "insert into fund (id,abbreviation,name,type,alias,ctdt,status) values ('%s','%s','%s','%s','%s','%s','%s');" % (
        flist[0], flist[1], flist[2], flist[3], flist[4], utils.getNow(), 1)
    savesql(sql)
