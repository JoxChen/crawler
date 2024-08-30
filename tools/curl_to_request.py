# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : curl_to_request.py
# @Author: Jox
# @Time  : 2024/08/31
# @Desc  : curl转requests
import re
import urllib.parse

def curl_to_requests(curl_command):
    """
    将 curl 命令转换为 requests.get() 请求。

    参数:
        curl_command (str): 包含 curl 请求的字符串。

    返回:
        str: 对应的 requests.get() 请求的 Python 代码。
    """
    # 去除 curl 命令和 URL 之外的部分
    curl_command = curl_command.strip().replace("\\", "")

    # 获取 URL
    url_match = re.search(r"curl\s+'(.+?)'", curl_command)
    url = url_match.group(1) if url_match else ""

    # 解析 URL 和查询参数
    parsed_url = urllib.parse.urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    params = dict(urllib.parse.parse_qsl(parsed_url.query))

    # 初始化请求部分
    headers = {}
    cookies = {}

    # 匹配所有的标头 (-H)
    headers_matches = re.findall(r"-H\s+'([^']+)'", curl_command)
    for header in headers_matches:
        key, value = header.split(": ", 1)
        if key.lower() == 'cookie':
            cookie_pairs = value.split("; ")
            for cookie_pair in cookie_pairs:
                c_key, c_value = cookie_pair.split("=", 1)
                cookies[c_key] = c_value
        else:
            headers[key] = value

    # 匹配所有的参数 (--data 或者 --data-urlencode)
    data_match = re.search(r"--data(?:-urlencode)?\s+'([^']+)'", curl_command)
    if data_match:
        data = data_match.group(1)
        data_params = dict(pair.split('=', 1) for pair in data.split('&'))
        params.update(data_params)

    # 构造 requests.get() 请求
    code = "import requests\n\n"
    code += "cookies = {\n"
    code += ",\n".join([f"    '{k}': '{v}'" for k, v in cookies.items()])
    code += "\n}\n\n"

    code += "headers = {\n"
    code += ",\n".join([f"    '{k}': '{v}'" for k, v in headers.items()])
    code += "\n}\n\n"

    code += "params = {\n"
    code += ",\n".join([f"    '{k}': '{v}'" for k, v in params.items()])
    code += "\n}\n\n"

    code += f"response = requests.get(\n    '{base_url}',\n    headers=headers,\n    cookies=cookies,\n    params=params\n)\n"
    code += "\nprint(response.text)"

    return code


def read_curl_from_file(file_path):
    """
    从文件中读取 curl 命令。

    参数:
        file_path (str): 文件路径。

    返回:
        str: 文件中的 curl 命令。
    """
    with open(file_path, 'r') as file:
        curl_command = file.read().strip()
    return curl_command


if __name__ == "__main__":
    file_path = 'curl.txt'  # 假设 curl 命令存储在这个文件中
    curl_command = read_curl_from_file(file_path)

    python_code = curl_to_requests(curl_command)
    print(python_code)
