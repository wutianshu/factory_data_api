#!/usr/bin/env python
# coding:utf-8
"""API调用统计模块
"""

from flask import Blueprint

statis = Blueprint('statis', __name__)

from . import views
