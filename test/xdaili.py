#!/usr/bin/python3
import sys
import time
import hashlib
import requests
import urllib3
from lxml import etree

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_version = sys.version_info

is_python3 = (_version[0] == 3)

orderno = "ZF20207248658M9kMo5"
secret = "f1d382adec694f84ae3f618eaf934b2e"

ip = "forward.xdaili.cn"
port = "80"

ip_port = ip + ":" + port

timestamp = str(int(time.time()))
string = ""
string = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp

if is_python3:
    string = string.encode()

md5_string = hashlib.md5(string).hexdigest()
sign = md5_string.upper()
#print(sign)
auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp

#print(auth)
proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
headers = {"Proxy-Authorization": auth, "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"}
r = requests.get("https://httpbin.org/ip", headers=headers, proxies=proxy, verify=False,allow_redirects=False)
r.encoding='utf8'
print(r.status_code)
print(r.text)
if r.status_code == 302 or r.status_code == 301 :
    loc = r.headers['Location']
    print(loc)
    r = requests.get(loc, headers=headers, proxies=proxy, verify=False, allow_redirects=False)
    r.encoding='utf8'
    print(r.status_code)
    print(r.text)
