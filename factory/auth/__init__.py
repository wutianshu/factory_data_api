#!/usr/bin/env python
# coding:utf-8
"""登陆
"""
from flask import Blueprint

auth = Blueprint('auth', __name__)


# SESSION有效期
EXPIRYTIME = 15 * 24 * 60 * 60

from . import views
