import pandas as pd
import numpy as np
import pandas_datareader.data as web
from datetime import datetime
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False # 用来正常显示负号

# 初始数据
# 创建字典
myDict = {'谷歌': 'GOOG', '苹果': 'AAPL','阿里巴巴':'BABA','腾讯': '0700.hk'}

# 时间
start = datetime(2017,1,1)
end = datetime(2017,12,31)

df = web.DataReader("600068.SS", 'yahoo', start, end)

print(df.head())
