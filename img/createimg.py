import cv2
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import pymysql
import time

config = {
    "host": "172.20.0.26",
    "user": "root",
    "password": "123456",
    "database": "ahgb"
}
db = pymysql.connect(**config)
cursor = db.cursor()

fontpathfile = '/Users/lyh/Documents/my/fonts/'
imgpath = '/Users/lyh/Documents/WechatIMG654.jpeg'
saveimgpath = '/Users/lyh/Documents/'


def drawString(text, draw):
    for val in text.split("#position<"):
        if val is None or val == '':
            continue

        # 字体位置
        fl = val[0: val.find(">#")].split(",")
        val = val[val.find(">#color<") + 8:]
        # 字体颜色
        color = val[0: val.find(">#")].split(",")
        # 字体大小
        val = val[val.find(">#font<") + 7:]
        fontsize = val[0: val.find(">#")]
        # 字体类型
        val = val[val.find(">#typeface<") + 11:]
        ttf = val[0: val.find(">")]
        # 内容
        val = val[val.find(">") + 1:]

        font = ImageFont.truetype(str(fontpathfile) + str(ttf) + ".ttf", int(fontsize))
        draw.text((int(fl[1]), int(fl[0])), val, font=font, fill=(int(color[0]), int(color[1]), int(color[2])))


def createimg(name, score, number, imgname):
    bk_img = cv2.imread(imgpath)
    img_pil = Image.fromarray(bk_img)
    draw = ImageDraw.Draw(img_pil)
    text = '#position<230,94>#color<0,0,0>#font<34>#typeface<方正隶书简体>#<name>#position<238,#nameleft>#color<0,0,0>#font<26>#typeface<思远黑体>同志：#position<286,574>#color<0,0,0>#font<26>#typeface<方正楷体简体>#<score>#position<430,90>#color<0,0,0>#font<16>#typeface<方正楷体简体>编号：#<number>'
    text = text.replace('#<name>', name).replace('#<number>', number).replace('#<score>', score).replace("\r|\n", "")
    if name.find(' ') == -1:
        text = text.replace("#nameleft", str(90 + 34 * len(name) + 10))
    else:
        text = text.replace("#nameleft", str(90 + 34 * 3))
    drawString(text, draw)
    bk_img = np.array(img_pil)
    cv2.imwrite(saveimgpath + imgname + ".jpg", bk_img)


def credits():
    db.ping()
    sql = "select id,createusername,credithour,userinfoid,boundary from t_ct_credit where techingplanid='9980C4FE-F688-4BC1-A41A-435E0B982FCB' and type=1 ;"
    cursor.execute(sql)
    return cursor.fetchall()


def saveCertificateUser(boundary, createusername, createuserinfo, img, identifier, pid):
    db.ping()
    sql = "insert into `t_cf_certificateuser` ( `id`, `boundary`, `createusername`, `createuserinfo`, `status`, `certificateid`, `ctdt`, `imgpath`, `name`, `pid`, `userid`, `username`, `identifier`) values ( UUID(),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % \
          (boundary, createusername, createuserinfo, 0, identifier, getNow(), img, pid,createuserinfo,createusername,identifier)
    try:
        cursor.execute(sql)
        db.commit()
    except BaseException:
        print('error sql : ' + sql)


def getNow():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


num = 0
for credit in credits():
    identifier = "2020" + credit['boundary'][0:7] + str(num)
    createimg(credit['createusername'], credit['credithour'], identifier, credit['id'])
    saveCertificateUser(credit['boundary'], credit['createusername'], credit['userinfoid'], credit['id'], identifier,
                        credit['id'])
    num = num + 1
