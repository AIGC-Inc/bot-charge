#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
@time: 2023/5/4 16:32
@Project ：chatgpt-on-wechat
@file: test.py
"""
import os

HOST = '114.116.46.25'
PORT = '3306'
DATABASE = 'visbus'
USERNAME = 'visbus'
PASSWORD = 'naftHnRJHAWnA4yh'
DB_URI = 'mysql+mysqldb://{}:{}@{}:{}/{}'.format(USERNAME, PASSWORD, HOST, PORT, DATABASE)


def create_models():
    # flask-sqlacodegen "mysql+mysqldb://visbus:naftHnRJHAWnA4yh@114.116.46.25/visbus?charset=utf8mb4" --tables buy_combo,buy_user_order,buy_user_permissions --outfile "api/model.py" --flask
    project_path = os.getcwd()
    print(project_path)
    model_path = os.path.join(project_path, 'model.py')
    cmd = 'flask-sqlacodegen --flask {}'.format(DB_URI)
    try:
        output = os.popen(cmd)
        resp = output.buffer.read().decode(encoding='utf-8')
        content = str(resp)
        output.close()
        # w+ 读写权限
        with open(model_path, 'w+', encoding='utf-8') as f:
            f.write(content)
        print('create models successfully!')
    except Exception as e:
        print(e)


create_models()
