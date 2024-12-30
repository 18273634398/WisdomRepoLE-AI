# ===========================================================================================================
# Author    ：LuShangWu
# Date      ：2024-12-29
# Version   ：1.0
# Description：用于联网学习内容
# Copyright  ：LuShangWu
# License   ：MIT
# Remark   :
# ===========================================================================================================
import random
from System.settings import timeout,maxLearn
import requests
from bs4 import BeautifulSoup

# 随机UserAgent
userAgents = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
]

'''
功能：通过网络搜索引擎搜索关键字，并获取相关文档内容
参数：keyword：搜索关键字
返回值：搜索结果文档内容(resultDoc:List)
部分内部参数：
    timeout：网络请求超时时间
    maxLearn：最大学习文档数量
'''
def learnByWeb(keyword):
    print("[网页搜索引擎]正在搜索："+keyword)
    resultDoc = []
    try:
        # 目标网页的URL
        url = f'https://cn.bing.com/search?q={keyword}&form=QBLH&sp=-1&lq=0&pq={keyword}&sc=12-3&qs=n&sk=&cvid=BEFC73E223194AC6BAF9D7AAD7090066&ghsh=0&ghacc=0&ghpl='
        headers={
            'User-Agent': userAgents[random.randint(0, len(userAgents) - 1)],
                 'Connection': 'keep-alive',
                 'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
            }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        temp = soup.find('div',id='b_content')
        list = temp.find('ol',id='b_results')
        a_tags = list.findAll('a')
        # 提取 href 属性值
        href_values = [a['href'] for a in a_tags if 'href' in a.attrs]
        visited_urls = set()
        for href in href_values:
            if href not in visited_urls and len(visited_urls) < maxLearn:
                visited_urls.add(href)
                print(href)
                response = requests.get(href, timeout=timeout)
                if response.status_code == 200:
                    encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else 'utf-8'
                    soup = BeautifulSoup(response.content, 'html.parser', from_encoding=encoding)
                    text = soup.get_text(separator=' ', strip=True)
                    print(f"[网页搜索引擎]获取到文档内容：{text}")
                    resultDoc.append(text)
                else:
                    print('Failed to retrieve the webpage')

    except Exception as e:
        print(e)
    return resultDoc

if __name__ == '__main__':
    keyword = input("请输入搜索关键字：")
    resultDoc = learnByWeb(keyword)
    print(resultDoc)
