#!/usr/bin/env python
# coding:utf-8
"""功能简要说明
"""
import os
import sys
import logging.handlers


__all__ = ['log_handler', 'err_handler', 'console', 'env']

log_handler = None
err_handler = None
console = None

# 获取当前运行环境
env = os.environ.get('CSTEST_ENV', None)
if env is None:
    env = 'default'
# debug
# env = 'production'
# 打印环境参数env
print('{0}当前env参数：{1}'.format('=' * 8, env))

# 定义日志显示格式
fmt = "%(asctime)s - %(thread)d - %(name)s - %(funcName)s - %(lineno)s -【%(levelname)s】- %(message)s"
formatter = logging.Formatter(fmt)

# 定义采集器console
console = logging.StreamHandler(sys.stdout)
console.setFormatter(formatter)
console.setLevel(logging.DEBUG)

# 生产环境——定义文件采集器
if env == 'production':
    # 初始化操作,创建日志目录，防止报错
    logs_path = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(logs_path):
        os.mkdir(logs_path)

    # 日志文件名称
    server_log = os.path.join(os.path.dirname(__file__), "logs/server.log")
    error_log = os.path.join(os.path.dirname(__file__), "logs/error.log")

    # 定义handler
    log_handler = logging.handlers.TimedRotatingFileHandler(
        server_log, when="D", backupCount=10, encoding="utf-8"
    )
    err_handler = logging.handlers.TimedRotatingFileHandler(
        error_log, when="D", backupCount=10, encoding="utf-8"
    )

    # 设置handler日志格式
    log_handler.setFormatter(formatter)
    err_handler.setFormatter(formatter)

    # 设置handler日志级别
    err_handler.setLevel(logging.ERROR)
    log_handler.setLevel(logging.INFO)
    console.setLevel(logging.INFO)
