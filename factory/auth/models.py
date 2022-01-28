#!/usr/bin/env python
# coding:utf-8
"""user对象模型
"""
import json, datetime
import logging
from flask_login import UserMixin, AnonymousUserMixin
from deng.tools import Tools
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from factory import db

# 获取日志句柄
logger = logging.getLogger(__name__)


class User(UserMixin, db.Model):
    """用户对象模型"""
    __tablename__ = 'user'
    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64))
    phone = db.Column(db.BigInteger, unique=True, nullable=False)
    email = db.Column(db.String(64))
    # created_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now, index=True)
    create_time = db.Column(db.DateTime, default=Tools.get_current_time())

    def __init__(self, user_info):
        self.init_user(user_info)

    def init_user(self, user_info):
        """初始化用户对象模型"""
        params_list = 'username,password,phone,email'.split(',')
        params_set = set(params_list)
        user_set = set(user_info.keys())
        if params_set.issubset(user_set):
            pass
        else:
            logger.warning('用户信息不规范，缺少一些信息，请检查！')
            Tools.format_print(user_info)
        # 赋值
        self.username = user_info['userName']
        self.password = user_info['password']
        self.phone = int(user_info['phone'])
        self.email = user_info.get('email')
        self.create_time = Tools.get_current_time()

    def verify_password(self, password):
        """密码验证"""
        if self.password is None:
            return False
        return check_password_hash(self.password, password)

    def get_id(self):
        """获取用户ID"""
        return self.id

    @staticmethod
    def get(user_id):
        """根据用户ID获取用户实体，为 login_user 方法提供支持"""
        if not user_id:
            return None
        try:
            return User.query.get(user_id)
        except:
            return None

    @staticmethod
    def get_by_name(user_name):
        """根据用户ID获取用户实体，为 login_user 方法提供支持"""
        if not user_name:
            return None
        try:
            u = User.query.filter(User.username == user_name).first()
            if u:
                return u
            else:
                return None
        except:
            return None

    def to_json(self):
        """将对象转换成json"""
        user_json = {
            'phone': self.phone,
            'userName': self.username,
            'id': self.id,
            'email': self.email,
            'password': self.password
        }
        return user_json

    def to_str(self):
        """将对象转换成字符串"""
        user_str = json.dumps(self.to_json(), ensure_ascii=False)
        return user_str

    def update_userinfo(self, user_info):
        self.init_user(user_info)
        result = self.save_user()
        if not result:
            logger.error('更新用户【{}】信息失败，请检查！'.format(self.username))
        return result

    def __repr__(self):
        """将用户对象格式化输出"""
        return self.to_str()

    def save_user(self):
        """保存用户对象修改"""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            logger.exception(e)
            logger.error('保存用户【{0}】失败，请检查！'.format(self.username))
            db.session.rollback()
            return False
        else:
            return True
