#!/usr/bin/env python
# coding=utf-8
"""
Author: DENGQINGYONG
Time:   18/1/18 09:00
Desc:
"""
import json
import flask
import logging
import platform
#
# from flask_cors import CORS
from flask_apscheduler import APScheduler
from werkzeug.exceptions import NotFound
from flask_sqlalchemy import SQLAlchemy
from flask import current_app, request

from factory.net import NetTools
from factory.config import config
from factory.log import console, log_handler, err_handler, env
from factory.common.common import extract_func_desc
from factory.common.exceptions import FactoryException

from flask_login import LoginManager,current_user

PYTHON_VERSION = platform.python_version()
print('{0}当前python版本：{1}'.format('=' * 8, PYTHON_VERSION))

# 获取日志操作句柄
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# 添加日志采集器
logger.addHandler(console)
if env == 'production':
    logger.addHandler(log_handler)
    logger.addHandler(err_handler)

db = SQLAlchemy()
scheduler = APScheduler()


def create_app(env):
    """工厂函数, 返回app程序对象"""
    app = flask.Flask(__name__)

    # 指定的配置不存在时的默认加载方案
    if env not in iter(list(config.keys())):
        env = 'default'

    # 将配置读取到flask对象中
    app.config.from_object(config[env])
    config[env].init_app(app)

    logger.info('成功加载配置：{}'.format(config[env]))

    scheduler.init_app(app)
    scheduler.start()

    # 数据库
    db.app = app
    db.init_app(app)

    # 调试开关
    disable_exception = app.config.get('EXCEPTION')

    # 注册蓝图

    # app.register_blueprint(jzso, url_prefix='/api/jzso')
    # # app.register_blueprint(sign_order, url_prefix='/api/sign')
    # from factory.WeChatRemind import wxremind
    # app.register_blueprint(wxremind, url_prefix='/api/remind')
    # # app.register_blueprint(sign_order, url_prefix='/api/sign')
    # from factory.jzcloud import jzcloud
    # app.register_blueprint(jzcloud, url_prefix='/api/jzcloud')

    # 统计模块
    if app.config.get('STATIS'):
        try:
            from factory.statis import statis
            app.register_blueprint(statis, url_prefix='/api/statis')
        except disable_exception as e:
            logger.error('{0}启动【statis】模块失败，跳过！{0}'.format('×' * 15))
            logger.exception(e)
        else:
            logger.info('{0}【statis】模块启动成功{0}'.format('√' * 15))

    # 登录模块
    # if app.config.get('AUTH'):
    try:
        from factory.auth import auth
        app.register_blueprint(auth, url_prefix='/api/auth')
    except disable_exception as e:
        logger.error('{0}启动【auth】模块失败，跳过！{0}'.format('×' * 15))
        logger.exception(e)
    else:
        logger.info('{0}【auth】模块启动成功{0}'.format('√' * 15))

    # 工具1
    if app.config.get('TOOLS1'):
        try:
            from factory.tools1 import tools1
            app.register_blueprint(tools1, url_prefix='/api/tools1')
        except disable_exception as e:
            logger.error('{0}启动【tools1】模块失败，跳过！{0}'.format('×' * 15))
            logger.exception(e)
        else:
            logger.info('{0}【tools1】模块启动成功{0}'.format('√' * 15))

    # 工具2
    if app.config.get('TOOLS2'):
        try:
            from factory.tools2 import tools2
            app.register_blueprint(tools2, url_prefix='/api/tools2')
        except disable_exception as e:
            logger.error('{0}启动【tools2】模块失败，跳过！{0}'.format('×' * 15))
            logger.exception(e)
        else:
            logger.info('{0}【tools2】模块启动成功{0}'.format('√' * 15))

    return app


app = create_app(env=env)
login_manager = LoginManager(app)

from factory.auth.views import User


@login_manager.user_loader  # 定义获取登录用户的方法,flask-login必须实现的方法
def load_user(user_id):
    return User.get(user_id)


# CORS(app)
# 加载顶层视图函数，缺少下面的语句会导致views中的视图函数注册失败
from .views import *


# @app.before_request
# def env_switch():
#     """请求预处理-鉴权"""
#     current_endpoint = request.endpoint
#     # logger.debug('current_endpoint={}'.format(current_endpoint))
#     endpoint_head = None
#     if current_endpoint:
#         endpoint_head = current_endpoint.split('.')[0]
#     # 忽略列表
#     ignore_endpoint_list = ['auth', 'favicon']
#     # 无需鉴权
#     if endpoint_head in ignore_endpoint_list or current_endpoint in ignore_endpoint_list:
#         return
#
#     # 环境参数
#     env = flask.request.values.get('env', None)
#     ipaddr = flask.request.values.get('ipaddr', None)
#     # 环境参数整理
#     if env is None or env.lower() not in ('stable', 'betaa', 'betab', 'dev', 'custom'):
#         flask.g.env = 'stable'
#     else:
#         flask.g.env = env.lower()
#     # ipaddr参数整理
#     if flask.g.env == 'custom':
#         if NetTools.isip(ipaddr):
#             flask.g.ipaddr = ipaddr
#         else:
#             return flask.jsonify({'factory_status': False,
#                                   'factory_node': '环境检查',
#                                   'factory_message': '{}不是合法的IPv4地址'.format(ipaddr)}), 500
#     logger.debug('env={}, ipaddr={}'.format(flask.g.env, ipaddr))


@app.after_request
def jsonp_support2(response):
    """jsonp支持统一处理函数"""
    if request.endpoint == 'favicon':
        return response
    if not response.is_json:
        return response
    logger.debug('统一jsonp处理')
    data = response.response
    mimetype = 'application/json'
    callback = request.values.get('callback', False)
    if callback:
        logger.debug('启用jsonp转换')
        content = '{0}({1})'.format(callback, json.dumps(data, ensure_ascii=False))
        mimetype = 'application/javascript'
    else:
        content = json.dumps(data, ensure_ascii=False)
    return current_app.response_class(content, mimetype=mimetype, headers=response.headers)


@app.after_request
def format_response(response):
    """格式化，规范服务响应格式"""
    if request.endpoint == 'favicon':
        return response
    if request.endpoint == 'tools.getMock':
        return current_app.response_class(response.json, mimetype='application/json', headers=response.headers)

    logger.debug('格式化response')
    if not response.is_json:
        return response
    data_new = dict()
    func = app.view_functions.get(request.endpoint)
    desc = extract_func_desc(func.__doc__)
    data = response.json
    if isinstance(data, dict):
        # 状态位
        if 'factory_status' in data.keys():
            data_new['factory_status'] = data['factory_status']
            del data['factory_status']
        else:
            if ('success' in data.keys() and not data['success']) or \
                    ('message' in data.keys() and '失败' in data['message']) or \
                    ('status' in data.keys() and data['status'] == -1):
                data_new['factory_status'] = False
            else:
                data_new['factory_status'] = True
        # 提示文字
        if 'factory_message' in data.keys():
            data_new['factory_message'] = data['factory_message']
            del data['factory_message']
        else:
            if 'message' in data.keys():
                data_new['factory_message'] = data['message']
            else:
                data_new['factory_message'] = desc
        # 节点信息
        if 'factory_node' in data.keys():
            data_new['factory_node'] = data['factory_node']
            del data['factory_node']
        else:
            data_new['factory_node'] = request.path
        # 数据节点
        if len(data) == 0:
            data_new['factory_data'] = None
        elif 'factory_data' in data.keys():
            data_new['factory_data'] = data['factory_data']
            del data['factory_data']
        else:
            data_new['factory_data'] = data
    else:
        data_new['factory_status'] = True
        data_new['factory_message'] = desc
        data_new['factory_node'] = request.path
        data_new['factory_data'] = data
    return current_app.response_class(data_new, mimetype='application/json')


@app.errorhandler(Exception)
def error_handler_custom(myexception):
    """错误统一处理函数"""
    logger.debug('统一异常处理')
    logger.exception(myexception)
    if isinstance(myexception, FactoryException):
        return flask.jsonify(myexception.to_dict()), 400
    elif isinstance(myexception, NotFound):
        return flask.jsonify({'factory_status': False,
                              'factory_node': 'notfound',
                              'factory_message': str(myexception)}), 404
    else:
        if myexception.code == 401:  # 未登录
            return flask.jsonify({'factory_status': False,
                                  'factory_node': 'notlogin',
                                  'factory_message': str(myexception),
                                  'factory_data': 'notlogin'}), 200
        else:
            return flask.jsonify({'factory_status': False,
                                  'factory_node': 'unknown',
                                  'factory_message': str(myexception)}), 500
