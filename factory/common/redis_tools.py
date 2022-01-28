#!/usr/bin/env python
# coding:utf-8
"""功能简要说明
"""
import os
from redis import Redis, ConnectionPool

# local_redis
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASS = ''



def get_redis_handler():
    """获取redis连接池"""
    pool = ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS)
    redis_obj = Redis(connection_pool=pool)

    if redis_obj.ping():
        return redis_obj
    else:
        return None


redis_handler = get_redis_handler()

if __name__ == '__main__':
    redis_handler.set('tmp', 'tmp')
    redis_handler.get('tmp')
