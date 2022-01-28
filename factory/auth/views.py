#!/usr/bin/env python
# coding:utf-8
"""登陆模块视图函数
"""

import logging
from flask import redirect, request, jsonify, make_response, url_for, g, current_app, Response
from flask import render_template, redirect, url_for, request

from flask_login import LoginManager, login_required, current_user
from flask_login import login_user

from flask import redirect, request, jsonify, make_response, url_for, g, current_app, Response
from . import auth, EXPIRYTIME

from werkzeug.security import generate_password_hash
from .models import User

logger = logging.getLogger(__name__)


@auth.route('/login', methods=('GET', 'POST'))  # 登录
def login():
    emsg = ''
    user_name = request.values.get('name')
    password = request.values.get('password')
    user = User.get_by_name(user_name)  # 从用户数据中查找user对象

    if user is None:
        emsg = "用户名有误"
        status = -1002
    else:
        if user.verify_password(password=password):  # 校验密码
            login_user(user)  # 创建用户 Session
            emsg = "登录成功"
            status = 0
        else:
            emsg = "用户名或密码密码有误"
            status = -1003
    result = {
        "data": "",
        "message": emsg,
        "status": status
    }
    return jsonify(result)


@auth.route('/register', methods=('GET', 'POST'))  # 注册
def register():
    user_name = request.values.get('name')
    password = generate_password_hash(request.values.get('password'))
    email = request.values.get('email')
    phone = request.values.get('phone')
    user_info = {
        'userName': user_name,
        'password': password,
        'email': email,
        'phone': phone
    }
    user = User(user_info)
    user.save_user()
    result = {
        "data": "",
        "message": "注册成功",
        "status": 0
    }
    return jsonify(result)


@auth.route('/userinfo', methods=('GET', 'POST'))
@login_required
def userinfo():
    logger.debug(current_user)
    result = {
        "data": {
            'user_info': current_user.to_json()
        },
        "message": '请求成功',
        "status": 0
    }
    return jsonify(result)
