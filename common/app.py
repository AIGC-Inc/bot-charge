#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
@time: 2023/5/4 11:28
@Project ：chatgpt-on-wechat
@file: app.py
"""
import sys
import traceback
from functools import wraps
from timeit import default_timer
from flask import Flask, jsonify, request
import config
from models import *


def api_try(fn):
    @wraps(fn)
    def f(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            msg = ''.join(traceback.TracebackException.from_exception(e).format())
            print(msg, file=sys.stderr)
            print(sys._getframe().f_lineno, sys._getframe().f_code.co_name)
            return jsonify(result=str(e), ok=False)

    return f


def create_app():
    app1 = Flask(__name__)
    # 加载配置文件
    app1.config.from_object(config)

    # db绑定app
    db.init_app(app1)
    # models导入数据库
    # with app1.app_context():
    # db.drop_all()
    # db.create_all()
    return app1


app = create_app()


@app.route('/check-user', methods=["GET"])
@api_try
def check_User_Permissions():
    info_dict = request.values.to_dict()
    print(info_dict)
    user_perms = UserPermissions.query.filter_by(user_id=info_dict.get("user_id"), bot_id=info_dict.get("bot_id"),
                                                 status=1).first()
    # return 'Hello World!'
    print(type(user_perms), user_perms)
    if user_perms:
        return jsonify(result=True)
    else:
        return jsonify(result=False)


@app.route('/user-charge', methods=["GET"])
@api_try
def user_Charge():
    return 'Hello World!'


app.run(port=8089, host='0.0.0.0', debug=True)
