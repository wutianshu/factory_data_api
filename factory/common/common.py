#!/usr/bin/env python
# coding:utf-8

import re
from deng.tools import Tools


def extract_func_desc(desc):
    """从apidoc格式的函数描述中提取真正的函数描述"""
    if desc is None:
        return ''
    if '@api ' not in desc:
        return desc.strip()
    e = r'@api {(.*?)} (\S*?) (.*?)\n'
    obj = re.search(e, desc)
    try:
        api_desc = obj.groups()[-1]
    except AttributeError as e:
        return desc.strip()
    return api_desc


# 上下班时间
working_time = [
    (1, '10:00', '11:00'),
    (2, '10:00', '12:00'),
    (3, '10:00', '13:00'),
    (4, '10:00', '14:00'),
    (5, '09:00', '14:00'),
    (7, '10:00', '17:00'),
    (8, '10:00', '18:00'),
    (1, '08:00', '09:00'),
    (1, '16:00', '17:00'),
    (1, '20:00', '21:00')
]

# 性别
gender_list = [
    {'gender': '男', 'value': 1},
    {'gender': '女', 'value': 2},
    {'gender': '未知', 'value': 0}
]
