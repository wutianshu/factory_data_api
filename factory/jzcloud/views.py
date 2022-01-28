# -*- coding:utf-8 -*-
import logging
from factory.jzcloud import jzcloud
import requests, time
from flask import request, jsonify
from .jzcloud import JZCloud
import pymysql
from factory import db
from factory.jzcloud import tool
from sqlalchemy import func

logger = logging.getLogger(__name__)






@jzcloud.route('/addStaff', methods=['POST', 'GET'])
def add_staff():
    admin_phone = request.values.get('adminphone', '')
    staff_phone = request.values.get('staffphone', '')
    env = request.values.get('env', 'stable')

    if len(str(staff_phone)) != 0 and len(str(staff_phone)) != 11:
        raise PermissionError('手机号码错误')
    try:
        int(staff_phone)
    except:
        staff_phone = JZCloud.get_phone()

    handler = JZCloud(phone=admin_phone, env=env)
    _admin_phone = handler.phone
    res = handler.create_company()
    company_id = res['data']['company_id']
    company_name = res['data']['company_name']
    handler.add_staff(staff_phone)

    # handler.improve_company_data()  # 添加公司需要审核的信息
    result = {
        "status": 0,
        "message": "ok",
        "data": {
            "company_id": company_id,
            "company_name": company_name,
            "admin_phone": _admin_phone,
            "staff_phone": staff_phone
        }
    }
    return jsonify(result)
