#!/usr/bin/env python
# coding:utf-8
"""API接口调用统计视图层
"""
import logging, datetime
from flask import request, jsonify

from .models import APICallStatis, APICallItems
from . import statis
from flask_login import current_user, mixins

# 定义日志hander
logger = logging.getLogger(__name__)


@statis.before_app_request
def api_call_count():
    # 忽略列表
    ignore_endpoint_list = ['favicon', None]
    current_endpoint = request.endpoint
    current_path = request.path
    current_module = None
    current_method = None
    if current_endpoint:
        current_module = current_endpoint.strip().split('.')[0]
        current_method = current_endpoint.strip().split('.')[-1]
    if request.endpoint in ignore_endpoint_list or \
            current_module in ignore_endpoint_list or \
            current_path in ignore_endpoint_list:
        return

    if not current_user.is_authenticated:
        user_name = 'Anonymous'
    else:
        user_name = current_user.to_json().get('userName')
    try:
        items = APICallItems(endpoint=current_endpoint,
                             module=current_module,
                             method=current_method,
                             path=current_path,
                             create_time=datetime.datetime.now(),
                             user_name=user_name)
        items.save()

        api = APICallStatis.query.filter_by(endpoint=current_endpoint).first()
        if api is None:
            api = APICallStatis(endpoint=current_endpoint,
                                module=current_module,
                                method=current_method,
                                path=current_path)
            api.save()
        api.call_count()
    except Exception as e:
        logger.exception(e)
        logger.error('接口访问统计模块【statis】在记录接口访问次数时报错，跳过……')


@statis.route('/info')
def api_call_info():
    api_name = request.values.get('api')
    if api_name:
        api_name = api_name.strip()
    else:
        return jsonify({'factory_status': False,
                        'factory_message': '必须携带api参数',
                        'factory_node': 'statis'})

    api = APICallStatis.query.filter_by(endpoint=api_name).first() or \
          APICallStatis.query.filter_by(path=api_name).first() or \
          APICallStatis.query.filter_by(method=api_name).first()
    if api:
        return jsonify(api.to_json())
    else:
        return jsonify({'factory_status': False,
                        'factory_message': '没有找到你请求的接口【{}】统计信息'.format(api_name),
                        'factory_node': 'statis'})
