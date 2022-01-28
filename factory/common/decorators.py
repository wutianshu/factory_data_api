#!/usr/bin/env python
# coding:utf-8
"""功能简要说明
作者：dengqingyong
"""
import json
import logging
from functools import wraps
from deng.tools import Tools
from flask import request, current_app, jsonify, redirect, url_for, g

from factory.common.exceptions import *
from factory.common.redis_tools import redis_handler

logger = logging.getLogger(__name__)


def error_handler(func):
    @wraps(func)
    def _error_handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CSCRMClueException as e:
            return jsonify({"cstest_status": False, "cstest_message": str(e), "cstest_node": "创建【月嫂】线索失败！"})
        except OMSOrderException as e:
            return jsonify({"cstest_status": False, "cstest_message": str(e), "cstest_node": "创建【月嫂】订单失败！"})
        except OrderDetailsException as e:
            return jsonify({"cstest_status": False, "cstest_message": str(e), "cstest_node": "【订单详情页】转换成订单对象时出错！"})
        except OrderException as e:
            return jsonify({"cstest_status": False, "cstest_message": str(e), "cstest_node": "创建【保姆】订单失败！"})
        except ClueException as e:
            return jsonify({"cstest_status": False, "cstest_message": str(e), "cstest_node": "创建【保姆】线索失败！"})
        except PermissionsException as e:
            return jsonify({"cstest_status": False, "cstest_message": str(e), "cstest_node": "权限验证失败！"})
        except Exception as e:
            logger.exception(e)
            return jsonify({"cstest_status": False, "cstest_message": str(e), "cstest_node": "未知"})
    return _error_handler


def login_inpass_check(func):
    """验证用户是否已经登陆"""
    @wraps(func)
    def user_verify(*args, **kwargs):
        cstestusername = request.cookies.get('cstestusername')
        current_url = request.url
        # cookie为空时跳转到登陆页面
        if cstestusername is None:
            logger.info('请求没有携带cstestusername cookie信息，跳转到登陆页面')
            return redirect(url_for('auth.user_login', redirect=current_url))

        # 从redis中获取用户对象
        try:
            user_bytes = redis_handler.get(cstestusername)
            user_info = json.loads(user_bytes)
            # logger.debug('类型：{}，值：{}'.format(type(user_bytes), user_bytes))
            logger.info('用户：【{0}】已经登陆！'.format(user_info['userName']))
            g.user = user_info
        except Exception as e:
            # 出错时跳转到登陆页面
            logger.exception(e)
            logger.warning('请求携带的cstestusername cookie信息无效或已过期，跳转到登陆页面')
            return redirect(url_for('auth.user_login', redirect=current_url))
        return func(*args, **kwargs)
    return user_verify


def check_permission(handler):
    def _check_permission(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # logger.debug('{0}开始检查session权限'.format('='*20))
            try:
                handler.login()
                handler.init()
                # raise ClueException('测试调试')
                # logger.debug('{0}session权限检查通过，不需要重新登陆'.format('='*20))
            except PermissionsException as e:
                # logger.warning(e)
                # logger.warning('{0}session权限检查失败，当前会话重新登陆'.format('='*20))
                handler.login()
                handler.init()
            return func(*args, **kwargs)
        return decorated_function
    return _check_permission


def jsonp_support(func):
    @wraps(func)
    def decorated_jsonp(*args, **kwargs):
        callback = request.values.get('callback', False)
        if callback:
            data = func(*args, **kwargs)
            data = data.json
            content = '{0}({1})'.format(callback, data)
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_jsonp

