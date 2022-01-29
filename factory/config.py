#!/usr/bin/env python
# coding:utf-8

import os
import platform
import datetime


class Config(object):
    # flask表单密钥
    SECRET_KEY = "CSTEST_2022"
    # 防止返回的json中汉字被转码
    JSON_AS_ASCII = False

    # 模块化加载
    # 统计模块开关
    STATIS = True
    # Inpass权限开关
    AUTH = True
    # 工具模块1开关
    TOOLS1 = True
    # 工具模块2开关
    TOOLS2 = True

    PYTHON_VERSION = platform.python_version()
    # 调试语句：需要忽略模块加载异常时赋值为Exception，需要查看模块加载详细异常信息时赋值为ZeroDivisionError
    EXCEPTION = Exception

    # DB地址
    DB_HOST = '127.0.0.1'
    # DB端口
    DB_PORT = 3306  # 给默认值，防止windows平台下报错
    # DB用户名
    DB_USER = 'root'
    # DB密码
    DB_PASS = '123456'
    # DB数据库
    DB_NAME = 'factory_data'

    # 数据库
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # if AUTH or STATIS:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}?charset=utf8mb4'.format(DB_USER,
                                                                                           DB_PASS,
                                                                                           DB_HOST,
                                                                                           DB_PORT,
                                                                                           DB_NAME)

    # 定时任务
    JOBS = [
        {
            'id': 'task1',
            'func': 'factory:task.task_demo.task1',
            'trigger': 'interval',
            'seconds': 5  # 单位为秒
        },
        {
            'id': 'task2',
            'func': 'factory:task.task_demo.task2',
            'args': [datetime.datetime.now()],
            'trigger': 'cron',  # 指定任务触发器 cron
            'day_of_week': '0-4',  # 每周1至周5晚上6点执行
            'hour': 18,
            'minute': 00
        }
    ]
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
    SCHEDULER_API_ENABLED = True
    SCHEDULER_API_PREFIX = '/scheduler'
    SCHEDULER_ALLOWED_HOSTS = ['*']

    # SCHEDULER_EXECUTORS = {'default': {'type': 'threadpool', 'max_workers': 10}}

    @staticmethod
    def init_app(app):
        pass


class ProdConfig(Config):
    """off93上运行配置文件"""
    pass


# 可以各自新建一个自己的配置文件，只加载自己相应的模块
# 新建后需要将其追回到下面的config字典中
class DevConfig(Config):
    """调试公用配置"""
    STATIS = True
    AUTH = True
    TOOLS1 = True
    TOOLS2 = True


# 需要在本机设置一个环境变量：key=CSTEST_ENV, value=dengqingyong
# 没有这个环境变量时默认取ProdConfig配置，加载所以模块
config = {
    "production": ProdConfig,
    "default": DevConfig,
}
