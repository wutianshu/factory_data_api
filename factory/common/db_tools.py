#!/usr/bin/env python
# coding:utf-8
"""功能简要说明
数据库工具
"""
import logging
import pymysql

# 自定义日志logger
logger = logging.getLogger(__name__)

DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PWD = 'root'
DB_DATABASE_NAME = 'factory_data'
DB_DATABASE_PORT = 3306


def db_query(sql_query):
    db = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PWD,
        database=DB_DATABASE_NAME,
        port=DB_DATABASE_PORT
    )
    cursor = db.cursor()
    cursor.execute(sql_query)
    results = cursor.fetchall()
    db.close()
    return results


def db_submit(sql_submit):
    db = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PWD,
        database=DB_DATABASE_NAME,
        port=DB_DATABASE_PORT
    )
    try:
        cursor = db.cursor()
        cursor.execute(sql_submit)
        db.commit()
    except Exception:
        db.rollback()
    db.close()


if __name__ == '__main__':
    results = db_query('select * from user')
    for row in results:
        user_name = row[0]
        password = row[1]
        print(user_name, password)

    db_submit("update user set password='pbkdf2:sha256:150000$rN7IFq3Q$0970f93080ad23ff076132a13cc56133d7bd2e2fa33e11690de79b41ee457e87' where username='yaya'")
