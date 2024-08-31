#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : decrypt_data.py
# @Author: Jox
# @Time  : 2024/08/31
# @Desc  : 本脚本从指定的URL获取并解密金融融资交易数据，格式化后保存为Excel文件。

import requests
import subprocess
import json
import pandas as pd
import logging
import time
import random
from functools import partial
from datetime import datetime

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 确保所有的subprocess调用使用UTF-8编码
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
import execjs

from utils import read_js_file, ensure_directory_exists

# 定义HTTP请求的头信息
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': 'https://www.swhysc.com/swhysc/financial/marginTradingList?channel=00010017000300020001&listId=2',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}


# 预先加载和编译JavaScript文件
def load_js_decrypt_function(js_file_path):
    """
    预先加载并编译JavaScript代码，只执行一次。
    :param js_file_path: JavaScript文件路径。
    :return: 编译后的JavaScript函数。
    """
    logging.info("加载并编译JavaScript文件...")
    js_code = read_js_file(js_file_path)
    if js_code is None:
        logging.error("无法加载JavaScript代码，请检查路径")
        raise ValueError("无法加载JavaScript代码，请检查 'decrypt.js' 的路径和内容")
    return execjs.compile(js_code)


def fetch_and_decrypt_data(page_num, page_size, decrypt_function):
    """
    从服务器获取加密数据并使用JavaScript解密。

    :param page_num: 要获取的页码。
    :param page_size: 每页包含的记录数量。
    :param decrypt_function: 预编译的JavaScript解密函数。
    :return: 解密后的JSON数据。
    """
    logging.info(f"开始获取第 {page_num} 页的数据...")

    params = {
        'pageNum': page_num,
        'pageSize': page_size
    }

    try:
        # 发送HTTP GET请求
        response = requests.get(
            'https://www.swhysc.com/swhysc/interface/dsinfo/v1/margin/deposit/ratio',
            headers=headers,
            params=params
        )

        # 检查请求是否成功
        response.raise_for_status()

        if not response.text:
            logging.error("响应文本为空")
            raise ValueError("响应文本为空")

        # 调用预编译的JavaScript函数解密数据
        en_data = str(response.text)
        decrypted_data = decrypt_function.call('de', en_data)

        logging.info(f"第 {page_num} 页数据获取并解密成功")

        return json.loads(decrypted_data)

    except requests.exceptions.RequestException as e:
        logging.error(f"请求第 {page_num} 页数据时发生错误: {e}")
        raise


def format_and_save_data(data_list, output_file):
    """
    格式化数据并保存为Excel文件。

    :param data_list: 解密后的数据列表。
    :param output_file: 保存的Excel文件名。
    """
    logging.info("开始格式化数据并保存为Excel文件...")

    # 提取并格式化所有记录，直接创建DataFrame
    df = pd.DataFrame([{
        "市场": item['market'],
        "证券代码": item['secuCode'],
        "证券简称": item['secuName'],
        "融资保证金比例": f"{float(item['rzRatio']) * 100:.0f}%",  # 转换为百分比格式
        "融券保证金比例": f"{float(item['rqRatio']) * 100:.0f}%"  # 转换为百分比格式
    } for item in data_list])

    # 将DataFrame保存为Excel文件
    df.to_excel(output_file, index=False)
    logging.info(f"数据已成功保存到 {output_file}")


def main():
    page_size = 10  # 设置每页记录数量
    total_pages = 5  # 设置要抓取的总页数
    all_data = []

    # 预先加载和编译JavaScript解密函数
    decrypt_function = load_js_decrypt_function('./decrypt.js')

    for page_num in range(1, total_pages + 1):
        logging.info(f"正在处理第 {page_num} 页...")

        # 添加随机延迟，防止访问过于频繁
        delay = random.uniform(0, 2)
        logging.info(f"等待 {delay:.2f} 秒后再进行请求")
        time.sleep(delay)

        try:
            data = fetch_and_decrypt_data(page_num, page_size, decrypt_function)
            all_data.extend(data['data']['dataList'])
        except Exception as e:
            logging.error(f"处理第 {page_num} 页时出错: {e}")
            continue

    # 生成带有当前日期和时间的文件名
    current_time = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    output_file = f"./data/{current_time}.xlsx"

    # 保存数据为Excel文件
    format_and_save_data(all_data, output_file)


if __name__ == "__main__":
    # 确保 data 目录存在
    ensure_directory_exists("./data")
    main()
