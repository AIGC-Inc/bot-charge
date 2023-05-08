#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
@time: 2023/5/4 10:34
@file: api_config.py
@software: PyCharm
"""
# 数据库信息 本地
HOST = 'localhost'
PORT = '3306'
DATABASE = 'bot_charge'
USERNAME = 'bot_charge'
PASSWORD = '123'
api_port = 6089  # 服务端口
# 线上
# HOST = '114.116.46.25'
# PORT = '3306'
# DATABASE = 'visbus'
# USERNAME = 'visbus'
# PASSWORD = 'naftHnRJHAWnA4yh'

DB_URI = 'mysql+mysqldb://{}:{}@{}:{}/{}'.format(USERNAME, PASSWORD, HOST, PORT, DATABASE)
DB_CHARSET = "utf8"

SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
