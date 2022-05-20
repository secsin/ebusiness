# _*_ coding:utf-8 _*_
# @Author : SecSin
# @Time : 2022/5/14 16:15
# @File : goods_spider
# @Project : ebusiness
import requests
from lxml import etree
from requests import RequestException
import pymysql
import time
import re


def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
            'Referer': 'https://www.smzdm.com/',
            'Cookie': 'device_id=1881762830158028368345329299623e56e783862b379508bdf5ad0f15; r_sort_type=score; _ga=GA1.1.855293389.1580283683; _ga_09SRZM2FDD=GS1.1.1623629997.2.0.1623629998.0; __gads=ID=3f67d0b177b41efe:T=1623629998:S=ALNI_MZoXyOZSpjgt0aDJxgMg1VIEL37Hw; smzdm_user_source=4D57C3864E0E3116CDCBDA759833BDE1; __ckguid=ChR5q3EwCPq82637yTtvvc; homepage_sug=a; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221790810ca9d55d-0a192e29e59ffe-d7e163f-3686400-1790810ca9e7e7%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fcn.bing.com%2F%22%2C%22%24latest_landing_page%22%3A%22https%3A%2F%2Fwww.smzdm.com%2F%22%7D%2C%22%24device_id%22%3A%221790810ca9d55d-0a192e29e59ffe-d7e163f-3686400-1790810ca9e7e7%22%7D; __jsluid_s=12d1d8e1489a0874ff9dca2b251e3d9b; ss_ab=ss15; _zdmA.uid=ZDMA.6BdHU28zt.1652518280.2419200; amvid=4ddb85aee5d633655317873691f15fda'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content
    except RequestException:
        return None


def parse_one_page(html, offset):
    html = etree.HTML(html, etree.HTMLParser())
    name = html.xpath('//ul[@id="feed-main-list"]/li/div/div[2]/h5/a[1]/@title')
    price = html.xpath('//ul[@id="feed-main-list"]/li/div/div[2]/h5/a[2]/div/text()')
    # 清洗字符串并将商品价格的数据类型转换为整型
    for i_ in range(len(price)):
        wash_str = re.findall("\d+\.?\d*", price[i_])[0]
        price[i_] = float(wash_str)
    print(price)
    introduce = html.xpath('//ul[@id="feed-main-list"]/li/div/div[2]/div[2]/text()')
    introduce = [a.strip() for a in introduce]
    img_url = html.xpath('//ul[@id="feed-main-list"]/li/div/div[1]/a/img/@src')
    img_url = ['https:' + a for a in img_url]
    img_name = [url.split('/')[-1] for url in img_url]
    # print('+'*50)
    # print(introduce)
    # print('+' * 50)
    # print(img_url)
    zip_goods = zip(name, price, ["upload/" + item for item in img_name], introduce)
    result = write_to_mysql(zip_goods)
    if result:
        save_img(img_url, img_name, offset)


def save_img(img_url, img_name, num):
    for index, url in enumerate(img_url):
        img_bin = get_one_page(url)
        with open("../static/upload/" + img_name[index - 1], 'wb') as f:
            f.write(img_bin)
    print("第" + str(num) + "页保存成功!")


def write_to_mysql(zip_goods):
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='ebusiness')
    # 创建一个cursor对象
    cursor = db.cursor()
    try:
        for row in zip_goods:
            sql = "insert into goods_goods(`name`, `price`, `picture`, `desc`) values(%s, %s, %s, %s)"
            # 执行sql
            cursor.execute(sql, row)
            # 提交
            db.commit()
        return True
    except:
        print("something wrong")
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()


def main(offset):
    url = 'https://search.smzdm.com/?c=home&s=%E7%BB%9D%E5%AF%B9%E5%80%BC&v=b&p=' + str(offset)
    html = get_one_page(url)
    # print(html)
    parse_one_page(html.decode(), offset)
    # for item in parse_one_page(html):
    #     print(item)
    #     write_to_mysql(item)


if __name__ == '__main__':
    for i in range(10):
        main(i + 1)
        time.sleep(5)
