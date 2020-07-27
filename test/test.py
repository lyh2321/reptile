import requests
from requests.adapters import HTTPAdapter


obligate1 = ''

requests.packages.urllib3.disable_warnings()
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}

def getHtmlProxy(url, ip):
    print(url)
    proxy = {
        'http': ip,
        'https': ip
    }
    # print(proxy)
    try:
        page = s.get(url=url, headers=headers, timeout=30, proxies=proxy, verify=False)
        page.encoding = 'utf-8'
        print(page.status_code)
        if page.status_code != 200:
            return None
        html = page.text

        # doc = pq(html)
        return html
    except requests.exceptions.RequestException as e:
        print(e)
    return None


print(getHtmlProxy("https://httpbin.org/ip", '113.194.134.24:9999'))