#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : get_info.py
# @Author: Jox
# @Time  : 2024/09/02
# @Desc  : 获取精灵数据资讯的内容解密并保存为json文件

import requests
import subprocess
from functools import partial
import logging
import json
import time
import random
from datetime import datetime
from utils import read_js_file, ensure_directory_exists

# 配置日志记录：设置日志的基本配置，日志级别为INFO，格式包括时间、日志级别和消息内容
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 修改subprocess.Popen使其默认使用UTF-8编码，确保所有子进程调用都使用UTF-8编码
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
import execjs

# 请求的cookies，headers和params定义（在实际使用时需要根据需求设置）

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.jinglingshuju.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

# 定义获取数据的参数
base_data = {
    "num": "20"  # 每次获取的条数
}

url = "https://vapi.jinglingshuju.com/Data/getNewsList"

def fetch_data(page):
    """
    发送HTTP POST请求获取数据。

    Args:
        page (int): 当前请求的页码。

    Returns:
        str: 返回响应的加密数据部分（'data'字段），如果请求失败或解析失败，返回None。
    """
    try:
        data = base_data.copy()
        data["page"] = str(page)
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # 检查请求是否成功，如果不成功则抛出HTTPError
        response.encoding = 'utf-8'
        return response.json().get('data')  # 返回JSON响应中的'data'字段
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None
    except ValueError:
        logging.error("Failed to parse JSON response")
        return None


def decrypt_data(data):
    """
    使用JavaScript代码解密数据。

    Args:
        data (str): 加密的数据字符串。

    Returns:
        dict: 返回解密后的数据，如果解密失败，返回None。
    """
    try:
        js_code = read_js_file('./decrypt_data.js')
        logging.info('Successfully loaded JavaScript file for decryption.')
        return execjs.compile(js_code).call('de_data', data)  # 调用JS函数解密数据
    except execjs.ProgramError as e:
        logging.error(f"JavaScript execution failed: {e}")
        return None
    except Exception as e:
        logging.error(f"Decryption failed: {e}")
        return None


def save_data_to_file(data, directory="./data"):
    """
    将数据保存为JSON文件，文件名包含当前日期和时间。

    Args:
        data (dict): 需要保存的数据。
        directory (str): 文件保存的目录。
    """
    # 获取当前日期和时间，并将其格式化为文件名的一部分
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"{timestamp}_info.json"  # 文件名格式为"日期_时间_info.json"
    ensure_directory_exists(directory)  # 确保保存数据的目录存在

    file_path = f"{directory}/{filename}"  # 完整的文件路径

    try:
        # 将数据保存为JSON文件
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Data successfully saved to {file_path}")
    except IOError as e:
        logging.error(f"Failed to save data to {file_path}: {e}")


def main():
    """
    主函数：执行数据获取、解密和保存流程。
    """
    start_page = 1  # 起始页码
    end_page = 3    # 结束页码

    for page in range(start_page, end_page + 1):
        logging.info(f"Fetching data for page {page}")
        data = fetch_data(page)  # 获取加密数据
        if data:
            decrypted_data = decrypt_data(data)  # 解密数据
            if decrypted_data:
                save_data_to_file(decrypted_data)  # 保存解密后的数据
            else:
                logging.error(f"Decryption returned None for page {page}")
        else:
            logging.error(f"Failed to fetch data for page {page}")

        # 添加随机延迟，防止访问频繁
        delay = random.uniform(0.5, 1.5)
        logging.info(f"Sleeping for {delay:.2f} seconds to avoid frequent access.")
        time.sleep(delay)


if __name__ == '__main__':
    main()  # 执行主函数
