#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
@time: 2023/5/4 11:28
@Project ：chatgpt-on-wechat
@file: app.py
"""
import sys
from datetime import datetime
import traceback
import logging
from functools import wraps
from zoneinfo import ZoneInfo
from flask import Flask, jsonify, request
from flask_apscheduler import APScheduler
import api_config
from models import *

scheduler = APScheduler()


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


@scheduler.task('cron', id='my_daily_task', hour=0, minute=0)
def check_task():
    with app.app_context():
        try:
            user_down = BuyUserPermission.query.filter(BuyUserPermission.expire_time < datetime.now()).update(
                {"margin": 3, "update_time": datetime.now()})
            user_up = BuyUserPermission.query.filter(BuyUserPermission.expire_time > datetime.now()).update(
                {"margin": 50, "update_time": datetime.now()})

            db.session.commit()
            print("user_up", type(user_up), user_up)
            print("user_down", type(user_down), user_down)
        except Exception as e:
            print("111111111111", e)
            db.session.rollback()


def creat_app():
    app1 = Flask(__name__)
    # 加载配置文件
    app1.config.from_object(api_config)
    app1.config['SCHEDULER_TIMEZONE'] = ZoneInfo('Asia/Shanghai')
    # db绑定app
    db.init_app(app1)
    return app1


app = creat_app()
scheduler.init_app(app)
scheduler.start()
logging.getLogger('apscheduler.executors.default').setLevel(logging.INFO)


@app.route('/check-user', methods=["GET"])
@api_try
def check_User_Permissions():
    info_dict = request.values.to_dict()
    print(info_dict)
    user_perms = BuyUserPermission.query.filter_by(user_id=info_dict.get("user_id"), agent_id=info_dict.get("agent_id")
                                                   ).first()
    print(type(user_perms), user_perms)
    if user_perms and user_perms.margin > 0:
        return jsonify(result="1")
    elif user_perms and user_perms.margin == 0:
        return jsonify(result="0")
    else:
        try:
            user1 = BuyUserPermission(user_id=info_dict.get("user_id"),
                                      agent_id=info_dict.get("agent_id"),
                                      margin=3,
                                      status=1,
                                      use_count=0,
                                      expire_time=datetime.now(),
                                      create_time=datetime.now())
            db.session.add(user1)
            db.session.commit()
            return jsonify(result="1")
        except Exception as e:
            print("222222", e)
            db.session.rollback()
            return jsonify(result="-1")


@app.route('/user-charge', methods=["GET"])
@api_try
def user_Charge():
    info_dict = request.values.to_dict()
    try:
        user_char = BuyUserPermission.query.filter(BuyUserPermission.user_id == info_dict.get("user_id"),
                                                   BuyUserPermission.agent_id == info_dict.get("agent_id"),
                                                   BuyUserPermission.margin > 0).update(
            {"margin": BuyUserPermission.margin - 1, "update_time": datetime.now()})
        db.session.commit()
        print(type(user_char), user_char)
        if user_char == 1:
            return jsonify(result="1")
        else:
            return jsonify(result="0")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(result=False)


app.run(port=api_config.api_port, host='0.0.0.0', debug=True)
