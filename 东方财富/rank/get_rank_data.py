#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : get_rank_data.py
# @Author: Jox
# @Time  : 2024/08/30
# @Desc  : 获取东方财富的股票人气榜数据

import execjs
import requests
import re
import os
import logging
import time
import random
from datetime import datetime
from fake_useragent import UserAgent
import pandas as pd
from openpyxl import Workbook

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def ensure_directory_exists(directory):
    """确保指定目录存在，如果不存在则创建目录"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"目录 {directory} 已创建。")
    else:
        logging.info(f"目录 {directory} 已存在。")


def read_js_file(file_path):
    """
    读取指定路径的JavaScript文件内容。

    参数:
    - file_path: 文件路径，默认为'./get_rank_data.js'

    返回:
    - 文件内容的字符串
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = ''.join(file.readlines())
            logging.info(f"成功读取文件 {file_path}")
            return file_content
    except FileNotFoundError:
        logging.error(f"错误：文件 {file_path} 未找到。")
    except PermissionError:
        logging.error(f"错误：没有权限读取 {file_path}。")
    except Exception as e:
        logging.error(f"读取文件时发生未知错误：{e}")
        return None


ua = UserAgent().random  # 动态生成 User-Agent


def get_secids(page, type_value='1'):
    """
    获取 secids

    参数:
    - page: 页码
    - type_value: 请求参数 type 的值, 默认为 '1'

    返回:
    - secids: 返回的 secids 值
    """
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://guba.eastmoney.com/',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': ua,
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    # 获取当前日期和时间，并进行格式化
    now = datetime.now()
    v = now.strftime("%Y_%m_%d_%H") + f"_{now.minute // 30}"

    params = {
        'type': type_value,  # 动态传入 type 的值
        'sort': '0',
        'page': page,
        'v': v
    }

    response = requests.get(
        'https://gbcdn.dfcfw.com/rank/popularityList.js',
        headers=headers,
        params=params
    )
    logging.info(f"请求已发送，正在获取 secids (Page: {page}, Type: {type_value})")

    popularityList = re.findall(r"popularityList='(.*?)'", response.text)[0]

    js_code = read_js_file('./get_secids.js')
    if js_code is None:
        return None

    codeT = execjs.compile(js_code).call('Getparameter', popularityList)

    try:
        codes = [t['code'] for t in codeT]
        logging.info("成功提取代码。")
    except KeyError as e:
        logging.error(f"Error: {e} not found")
        return None

    s = ','.join(codes)
    secids = execjs.compile(js_code).call('getHQSecIdByMutiCode', s)

    return secids


def get_data(secids):
    """
    获取数据并返回 JSON 格式

    参数:
    - secids: 股票 secids

    返回:
    - JSON 数据
    """
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://guba.eastmoney.com/',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': ua,
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    params = {
        'fltt': '2',
        'np': '3',
        'ut': 'a79f54e3d4c8d44e494efb8f748db291',
        'invt': '2',
        'secids': secids,
        'fields': 'f1,f2,f3,f4,f12,f13,f14,f152,f15,f16',
    }

    response = requests.get(
        'https://push2.eastmoney.com/api/qt/ulist.np/get',
        headers=headers,
        params=params
    )
    logging.info(f"获取数据成功")

    return response.json()


def process_and_save_data(rank_data, type_mapping):
    """
    处理并保存数据

    参数:
    - rank_data: 包含不同股票市场数据的字典
    - type_mapping: 股票市场类型映射表
    """
    # 保存到 Excel 文件中，每个类型的数据在不同的 sheet 中
    datetime_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_file = f"./data/{datetime_str}_rank_data.xlsx"

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        data_written = False  # 标记是否有数据被写入

        for type_value, type_name in type_mapping.items():
            data_list = rank_data.get(type_value, [])
            if not data_list:
                logging.warning(f"{type_name} 数据为空，跳过保存。")
                continue

            # 字段标签映射
            field_map = {
                "f2": "最新价",
                "f3": "涨跌幅(%)",
                "f4": "涨跌额",
                "f12": "代码",
                "f14": "股票名称",
                "f15": "最高价",
                "f16": "最低价",
            }
            converted_data = []
            for item in data_list[0]['data']['diff']:
                converted_item = {field_map[key]: value for key, value in item.items() if key in field_map}
                converted_data.append(converted_item)

            # 将数据存储到 DataFrame 中
            df = pd.DataFrame(converted_data)
            df.index += 1  # 从1开始的索引

            # 保存每个类型的数据到 Excel 的不同 sheet
            df.to_excel(writer, sheet_name=type_name, index_label="当前排名")
            logging.info(f"已将 {type_name} 数据保存到 {output_file} 中的 {type_name} sheet。")
            data_written = True  # 标记有数据被写入

    if not data_written:
        logging.error("所有股票市场的数据均为空，程序将退出。")
        return  # 退出程序

    logging.info(f"所有数据已成功保存到 {output_file} 中。")


if __name__ == '__main__':
    # 确保 data 目录存在
    ensure_directory_exists("./data")

    # 遍历不同类型 (0- A股, 1- 港股, 2- 美股)
    type_mapping = {0: 'A股', 1: '港股', 2: '美股'}
    rank_data = {}

    for type_value, type_name in type_mapping.items():
        logging.info(f"开始处理 {type_name} 数据。")
        data_list = []
        for i in range(1, 2):
            secids = get_secids(str(i), type_value=type_value)
            if secids is None:
                logging.error(f"获取 {type_name} 数据时发生错误，跳过此类型。")
                continue
            data = get_data(secids)
            data_list.append(data)

            # 添加随机延迟，防止访问频繁
            delay = random.uniform(1, 3)
            logging.info(f"随机延迟 {delay:.2f} 秒...")
            time.sleep(delay)

        rank_data[type_value] = data_list

    # 处理并保存数据
    process_and_save_data(rank_data, type_mapping)
