# -*- coding:utf-8 -*-
import logging
from factory.tools1 import tools1
import requests, time
from flask import request, jsonify
from flask_login import current_user, login_required

from factory.statis.models import APICallStatis

logger = logging.getLogger(__name__)


@tools1.route('/test', methods=['POST', 'GET'])
@login_required
def test():
    par1 = request.values.get('par1', '')
    par2 = request.values.get('par2', '')
    logger.debug('开始工具1测试的接口测试')
    result = {
        "data": {
            'par1': par1,
            'par2': par2
        },
        "message": '请求成功',
        "status": 0
    }
    return jsonify(result)


@tools1.route('/getapi-table', methods=['POST', 'GET'])
def get_table():
    data = APICallStatis.query.all()
    info = []
    for d in data:
        info.append({'endpoint': d.endpoint, 'count': d.count, 'path': d.path, 'module': d.module, 'method': d.method,
                     'id': d.id})
    res = {"data": info, "message": "ok", "status": 0}
    return jsonify(res)
