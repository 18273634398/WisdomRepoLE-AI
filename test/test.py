import requests
from bs4 import BeautifulSoup

def get_website_html(url):
    """
    获取指定网站的 HTML 内容
    :param url: 目标网站的 URL
    :return: 网站的 HTML 内容
    """
    try:
        # 发送 HTTP GET 请求
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功

        # 返回 HTML 内容
        return response.text

    except requests.exceptions.RequestException as e:
        # 处理请求异常
        print(f"请求失败: {e}")
        return None

def parse_html(html):
    """
    解析 HTML 内容
    :param html: HTML 内容
    :return: BeautifulSoup 对象
    """
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        return soup
    else:
        print("HTML 内容为空，无法解析")
        return None

if __name__ == '__main__':
    # 目标网站 URL
    url = 'http://find.nlc.cn/search/showDocDetails?docId=1697916158806824696&dataSource=cjfd,wpqk&query=%E5%88%98%E6%85%88%E6%AC%A3'

    # 获取 HTML 内容
    html = get_website_html(url)

    if html:
        # 解析 HTML
        soup = parse_html(html)

        # 打印 HTML 内容
        if soup:
            print(soup.prettify())  # 格式化输出 HTML
