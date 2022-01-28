#!/usr/bin/env python
# coding:utf-8
"""统计对象模型
"""
import json,datetime
import logging
from deng.tools import Tools

from factory import db


# 获取日志句柄
logger = logging.getLogger(__name__)


class APICallStatis(db.Model):
    """API接口调用统计对象模型"""
    __tablename__ = "api_call_statis"
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(64), unique=True, nullable=False)
    count = db.Column(db.Integer, default=0)
    module = db.Column(db.String(32), nullable=False)
    method = db.Column(db.String(32), nullable=False)
    path = db.Column(db.String(32), unique=True, nullable=False)
    last_access_time = db.Column(db.DateTime, default=Tools.get_current_time())

    def call_count(self):
        """接口调用计数"""
        self.count += 1
        self.last_access_time = Tools.get_current_time()
        return self.save()

    def to_json(self):
        """将对象转换成json"""
        user_json = {'endpoint': self.endpoint,
                     'count': self.count,
                     'module': self.module,
                     'method': self.method,
                     'path': self.path,
                     'lastAccessTime': str(self.last_access_time)
                     }
        return user_json

    def to_str(self):
        """将对象转换成字符串"""
        user_str = json.dumps(self.to_json(), ensure_ascii=False)
        return user_str

    def __repr__(self):
        """将用户对象格式化输出"""
        return self.to_str()

    def save(self):
        """保存修改"""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            logger.exception(e)
            logger.error('更新接口【{0}】调用计数失败，请检查！'.format(self.endpoint))
            db.session.rollback()
            return False
        else:
            return True


class APICallItems(db.Model):
    """API接口调用明细对象模型"""
    __tablename__ = "api_call_statis_items"
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(64), nullable=False)
    module = db.Column(db.String(32), nullable=False)
    method = db.Column(db.String(32), nullable=False)
    path = db.Column(db.String(32), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now())
    user_name = db.Column(db.String(32), nullable=True)

    def to_json(self):
        """将对象转换成json"""
        user_json = {'endpoint': self.endpoint,
                     'module': self.module,
                     'method': self.method,
                     'path': self.path,
                     'user_name': self.user_name,
                     'create_time': str(self.create_time)
                     }
        return user_json

    def to_str(self):
        """将对象转换成字符串"""
        user_str = json.dumps(self.to_json(), ensure_ascii=False)
        return user_str

    def __repr__(self):
        """将用户对象格式化输出"""
        return self.to_str()

    def save(self):
        """保存修改"""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            logger.exception(e)
            logger.error('更新接口【{0}】调用计数失败，请检查！'.format(self.endpoint))
            db.session.rollback()
            return False
        else:
            return True
