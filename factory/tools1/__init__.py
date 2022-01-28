#!/usr/bin/env python
# coding:utf-8
"""功能简要说明
"""
from flask import Blueprint
# from factory.common.dbtools import DBTools

import os,logging

logger = logging.getLogger(__name__)



tools1 = Blueprint('tools1', __name__)
# 实例化数据库操作类
# dbtools = DBTools()


# 必须在当前包的__init__文件中导入，否则引用
from .views import *
