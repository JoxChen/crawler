# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : utils.py
# @Author: Jox
# @Time  : 2024/08/31
# @Desc  : 存放一些复用工具
import logging
import os

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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

def ensure_directory_exists(directory):
    """确保指定目录存在，如果不存在则创建目录"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"目录 {directory} 已创建。")
    else:
        logging.info(f"目录 {directory} 已存在。")