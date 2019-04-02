"""
 @Time        :   2019-03-28 19:35
 @Author      :   einherjar
 @File        :   enterpriseSpider.py
 @Description :   国家企业信用公示系统
"""
import requests
import json
import time
import execjs
import re
from lxml import etree
import urllib
from bs4 import BeautifulSoup

class enterpriseSpider():
    def __init__(self, searchword):
        self.cookie_url = 'http://www.gsxt.gov.cn/index.html'
        self.post_url = 'http://www.gsxt.gov.cn/corp-query-search-1.html'
        self.session = requests.Session()
        self.refer_url = 'http://www.gsxt.gov.cn'
        self.session.headers = {
            'User_Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'
        }
        self.searchword = searchword
        self.page_list = []
        self.detail_list = []

    def get_cookie(self):
        """
        获取 cookies
        :return:
        """
        response = self.session.get(self.cookie_url)
        js_code1 = response.text
        print(js_code1)
        js_code1 = js_code1.rstrip('\n')
        js_code1 = js_code1.replace('</script>', '')
        js_code1 = js_code1.replace('<script>', '')
        index = js_code1.rfind('}')
        js_code1 = js_code1[0:index + 1]
        js_code1 = 'function getCookie() {' + js_code1 + '}'
        js_code1 = js_code1.replace('eval', 'return')

        js_code2 = execjs.compile(js_code1)
        code = js_code2.call('getCookie')
        code = 'var a' + code.split('document.cookie')[1].split("Path=/;'")[0] + "Path=/;';return a;"
        code = 'window = {}; \n' + code
        js_final = "function getClearance(){" + code + "};"
        ctx = execjs.compile(js_final)
        jsl_clearance = ctx.call('getClearance')
        jsl_cle = jsl_clearance.split(';')[0].split('=')[1]
        self.session.cookies['__jsl_clearance'] = jsl_cle

    def get_pojieparmas(self):
        """
        获取极验接口参数
        :return:
        """
        num = int(time.time() * 1000)
        url = 'http://www.gsxt.gov.cn/SearchItemCaptcha?t={}'.format(num)
        response = self.session.get(url)
        print(response.text)
        json_data = response.text
        dict_data = json.loads(json_data)
        return dict_data

    def get_pojieres(self, data):
        """
        获取极验破解后的结果
        :param data:
        :return:
        """
        url = 'http://jiyanapi.c2567.com/shibie?gt={}&challenge={}&referer=http://www.gsxt.gov.cn&user={}&pass={}&return=json'.format(data['gt'], data['challenge'],
                                                                                                 username, password)
        response = self.session.get(url)
        json_data = response.text
        print(json_data)
        dict_data = json.loads(json_data)
        return dict_data

    def get_search_res(self, data):
        """
        获取查询结果页面
        :param data:
        :return:
        """
        post_params = {
            'geetest_challenge': data.get('challenge'),
            'geetest_validate': data.get('validate'),
            'geetest_seccode': data.get('validate') + '|jordan',
            'tab': 'ent_tab',
            'province': '',
            # token: 在首页的源代码中，有一句注释：#TODO 伪造极验变量
            'token': '2016',
            'searchword': self.searchword
        }
        response = self.session.post(self.post_url, data=post_params)
        print(response.text)
        return response.text

    def parse_page(self, html, data):
        """
        采用 BeautifulSoup 方式解析页面
        :param html:
        :param data:
        :return:
        """
        soup = BeautifulSoup(html, 'lxml')
        class_list = soup.findAll(class_='search_list_item db')
        for class_ in class_list:
            print(class_.select('h1')[0].get_text().strip())
            print(self.refer_url + class_['href'])
            self.detail_list.append(self.refer_url + class_['href'])
        result_num = soup.find(class_='search_result_span1').get_text()
        print(result_num)
        page = int(result_num) // 10
        if int(result_num) % 10:
            page += 1
        url = 'http://www.gsxt.gov.cn/corp-query-search-advancetest.html?geetest_seccode=' + data.get('validate') + '|jordan' \
                + '&tab=ent_tab&province=&geetest_validate=' + data.get('validate') + '&searchword=' + urllib.parse.quote(
                self.searchword) + '&geetest_challenge=' + data.get('challenge') + '&page='
        for i in range(2, page + 1):
            # print(url + str(i))
            self.page_list.append(url + str(i))
        print(self.page_list)


    def run(self):
        self.get_cookie()
        jy_data = self.get_pojieparmas()
        pojie_data = self.get_pojieres(jy_data)
        html = self.get_search_res(pojie_data)
        self.parse_page(html, pojie_data)


if __name__ == "__main__":
    spider = enterpriseSpider('阿里巴巴')
    spider.run()
