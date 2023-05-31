#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
@time: 2023/5/4 11:28
@file: app.py
"""
import json
import sys
import os
from datetime import datetime, timedelta
import traceback
from functools import wraps
from zoneinfo import ZoneInfo
from sqlalchemy import exc, func
from flask import Flask, jsonify, request, redirect, render_template, url_for, session
from gevent import pywsgi
from models import *

config_path = os.path.join(os.path.dirname(__file__), "config.json")
conf = json.load(open(config_path, "r", encoding="utf-8"))


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


def creat_app():
    app1 = Flask(__name__)
    # 加载配置文件
    db_conf = conf["db_conf"]
    app1.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://{}:{}@{}:{}/{}'.format(db_conf.get("username"),
                                                                                     db_conf.get("password"),
                                                                                     db_conf.get("host"),
                                                                                     db_conf.get("port"),
                                                                                     db_conf.get("database"))
    app1.config['SCHEDULER_TIMEZONE'] = ZoneInfo('Asia/Shanghai')
    # db绑定app
    db.init_app(app1)
    return app1


app = creat_app()
app.secret_key = 'secret'


def get_combo():
    return BuyCombo.query.order_by(BuyCombo.combo_id.desc()).limit(100).all()


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        login_time = session.get('login_time')
        # 检查登录状态和时间
        if not session.get('logged_in') or login_time and login_time < datetime.now().timestamp() - conf.get(
                "login_time", 10) * 60 * 60 * 24:
            return redirect('/login')
        return func(*args, **kwargs)

    return wrapper


def search(req: object) -> object:
    page = req.args.get('page', 1)
    per_page = 100
    filters = []
    user_id = req.args.get('user_id')
    print("user_id", user_id)
    if user_id:
        filters.append(BuyUserPermission.user_id.like('%{}%'.format(user_id)))
    userid = req.args.get('user')
    print("userid", userid)
    if userid:
        filters.append(BuyUserPermission.user_id == userid)
    expire_time = req.args.get('expire_time')
    print("expire_time", expire_time, datetime.now().replace(hour=0, minute=0, second=0) + timedelta(1))
    if expire_time:
        filters.append(
            BuyUserPermission.expire_time >= datetime.now().replace(hour=0, minute=0, second=0) + timedelta(1))
    agent_id = req.args.get('agent_id')
    print("agent_id", agent_id)
    if agent_id:
        filters.append(BuyUserPermission.agent_id == agent_id)
    print(filters)
    return BuyUserPermission.query.filter(*filters).order_by(BuyUserPermission.update_time.desc()).paginate(
        page=int(page), per_page=per_page)


@app.route('/check-user', methods=["GET"])
@api_try
def check_User_Permissions():
    info_dict = request.values.to_dict()
    print(info_dict)
    user_id = info_dict.get("user_id")
    agent_id = info_dict.get("agent_id")
    user_perms = BuyUserPermission.query.filter_by(user_id=user_id, agent_id=agent_id).first()
    print(type(user_perms), user_perms)
    if user_perms:
        update_time = user_perms.update_time
        print(update_time, type(update_time))
        # 判断是否失效
        if update_time.date() < datetime.now().date():
            combo = BuyCombo.query.filter_by(agent_id=agent_id).first()
            if user_perms.expire_time > datetime.now():
                if user_perms.margin < combo.upper_limit:
                    user_perms.margin = combo.upper_limit
                user_perms.update_time = datetime.now()
                db.session.commit()
                return jsonify(result="1")
            else:
                if user_perms.margin < combo.free_quota:
                    user_perms.margin = combo.free_quota
                user_perms.update_time = datetime.now()
                db.session.commit()
                if combo.free_quota > 0:
                    return jsonify(result="1")
                else:
                    return jsonify(result="0")
        else:
            if user_perms.margin > 0:
                return jsonify(result="1")
            else:
                return jsonify(result="0")
    else:
        try:
            combo = BuyCombo.query.filter_by(agent_id=agent_id).first()
            user1 = BuyUserPermission(user_id=user_id, agent_id=agent_id, margin=combo.free_quota, status=1,
                                      use_count=0, expire_time=datetime.now(), create_time=datetime.now(),
                                      update_time=datetime.now())
            db.session.add(user1)
            db.session.commit()
            if combo.free_quota > 0:
                return jsonify(result="1")
            else:
                return jsonify(result="0")
        except Exception as e:
            print("check-user", e)
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
        print("user-charge", e)
        db.session.rollback()
        return jsonify(result=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in conf["users"].keys() and password == conf["users"].get(username, ""):
            # 登录成功,设置session
            session['logged_in'] = True
            session['username'] = username
            session['login_time'] = datetime.now().timestamp()
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error=True)
    return render_template('login.html')


@app.route('/')
@login_required
def index():
    return render_template('base.html')


@app.route('/combo/')
@login_required
def combo():
    combos = BuyCombo.query.limit(100).all()
    results = BuyUserPermission.query.filter(
        BuyUserPermission.expire_time >= datetime.now().replace(hour=0, minute=0, second=0) + timedelta(1)).group_by(
        BuyUserPermission.agent_id).with_entities(BuyUserPermission.agent_id, func.count(BuyUserPermission.id)).all()
    # print(results)
    pay_count = {}
    for item in results:
        pay_count[item[0]] = item[1]
    print(pay_count)
    return render_template('combo.html', combos=combos, pay_count=pay_count)


@app.route('/combo/add', methods=['POST'])
@login_required
def add_combo():
    agent_id = request.form['agent_id']
    combo_name = request.form['combo_name']
    try:
        new_combo = BuyCombo(agent_id=agent_id, combo_name=combo_name, combo_price=request.form['combo_price'],
                             free_quota=request.form['free_quota'], allot_time=request.form['allot_time'],
                             corp_id=request.form['corp_id'], secret=request.form['secret'],
                             upper_limit=request.form['upper_limit'], create_time=datetime.now(),
                             update_time=datetime.now())
        db.session.add(new_combo)
        db.session.commit()
        return redirect(url_for('combo'))
    except exc.IntegrityError as e:
        print("sqlalchemy.InternalError", e)
        db.session.rollback()
        return jsonify(result="重复添加，%s, 应用ID: %s" % (combo_name, agent_id))
    except exc.OperationalError as e:
        print("sqlalchemy.OperationalError", e)
        db.session.rollback()
        return jsonify(result="处理数据库异常，%s, 应用ID: %s" % (combo_name, agent_id))
    except exc.DataError as e:
        print("sqlalchemy.DataError", e)
        db.session.rollback()
        return jsonify(result="数据异常，%s, 应用ID: %s" % (combo_name, agent_id))
    except Exception as e:
        print("add_combo", e)
        db.session.rollback()
        return jsonify(result="添加套餐失败，%s, 应用ID: %s" % (combo_name, agent_id))


@app.route('/combo/update/<int:combo_id>', methods=['POST'])
@login_required
def update_combo(combo_id):
    try:
        combo = BuyCombo.query.filter_by(combo_id=combo_id).update(
            {"combo_price": request.form["combo_price"], "allot_time": request.form["allot_time"],
             "upper_limit": request.form["upper_limit"], "free_quota": request.form["free_quota"],
             "combo_name": request.form["combo_name"], "update_time": datetime.now()})
        db.session.commit()
        return redirect(url_for('combo'))
    except Exception as e:
        print("update_combo", e)
        db.session.rollback()
        return jsonify(result="修改套餐：%s 失败" % request.form['combo_name'])


@app.route('/combo/delete/<int:combo_id>')
@login_required
def delete_combo(combo_id):
    try:
        combo = BuyCombo.query.filter(BuyCombo.combo_id == combo_id).delete()
        db.session.commit()
        return redirect(url_for('combo'))
    except Exception as e:
        print("delete_combo", e)
        db.session.rollback()
        return jsonify(result="删除套餐ID：%s 失败" % combo_id)


@app.route('/permission')
@login_required
def permission():
    # req_data = request.values.to_dict()
    # page = request.args.get('page', 1, type=int)
    # per_page = 10
    #
    # filters = []
    # user_id = request.args.get('user_id')
    # if user_id:
    #     filters.append(BuyUserPermission.user_id.like('%{}%'.format(request.args.get('user_id'))))
    # expire_time = request.args.get('expire_time')
    # if expire_time:
    #     filters.append(BuyUserPermission.expire_time > expire_time)
    # print(expire_time)
    # agent_id = request.args.get('agent_id')
    # if agent_id:
    #     filters.append(BuyUserPermission.agent_id == agent_id)
    # print(filters)
    # permissions = BuyUserPermission.query.filter(*filters).order_by(BuyUserPermission.update_time.desc()).paginate(
    #     page=page, per_page=per_page)
    permissions = search(request)
    return render_template('permission.html', permissions=permissions, combos=get_combo())


@app.route('/search')
@login_required
def search_permission():
    req_data = request.values.to_dict()
    # page = request.args.get('page', 1, type=int)
    # per_page = 10
    # filters = []
    # user_id = request.args.get('user_id')
    # if user_id:
    #     filters.append(BuyUserPermission.user_id.like('%{}%'.format(user_id)))
    # expire_time = request.args.get('expire_time')
    # if expire_time:
    #     filters.append(BuyUserPermission.expire_time > expire_time)
    # print(expire_time)
    # agent_id = request.args.get('agent_id')
    # if agent_id:
    #     filters.append(BuyUserPermission.agent_id == agent_id)
    # print(filters)
    # permissions = BuyUserPermission.query.filter(*filters).order_by(BuyUserPermission.update_time.desc()).paginate(
    #     page=page, per_page=per_page)
    permissions = search(request)
    print(req_data)
    if req_data.get("page", ""):
        req_data.pop("page")
    return render_template('search.html', permissions=permissions, req_data=req_data, combos=get_combo())


@app.route('/permission/add', methods=['POST'])
@login_required
def add_permission():
    req_dict = request.values.to_dict()
    # print(req_dict)
    if req_dict.get("back_url", ""):
        if [i for i in ["add", "update", "invalid"] if i in req_dict.get("back_url")]:
            req_dict.pop("back_url")
        # back_req = "/" + req_dict.get("back_url").split("/")[-1]
    print(req_dict)
    user_id = request.form.get('user_id')
    agent_id = request.form.get('agent_id')
    try:
        user1 = BuyUserPermission(user_id=user_id, agent_id=agent_id, status=1,
                                  margin=request.form.get('margin'), expire_time=request.form.get('expire_time'),
                                  use_count=0, create_time=datetime.now(), update_time=datetime.now())
        db.session.add(user1)
        db.session.commit()
        return render_template('user_permis.html', permission=user1, combos=get_combo(), back_req=req_dict)
        # return redirect(url_for('permission'))
    except exc.IntegrityError as e:
        print("MySQLdb.InternalError", e)
        db.session.rollback()
        return jsonify(result="重复添加，用户：%s, 应用ID: %s" % (user_id, agent_id))
    except exc.OperationalError as e:
        print("MySQLdb.OperationalError", e)
        db.session.rollback()
        return jsonify(result="处理数据库异常，用户：%s, 应用ID: %s" % (user_id, agent_id))
    except exc.DataError as e:
        print("MySQLdb.DataError", e)
        db.session.rollback()
        return jsonify(result="数据异常，用户：%s, 应用ID: %s" % (user_id, agent_id))
    except Exception as e:
        print("add_permission", e)
        db.session.rollback()
        return jsonify(result="添加权限失败，用户：%s, 应用ID: %s" % (user_id, agent_id))


@app.route('/permission/invalid', methods=["POST"])
@login_required
def invalid_permission():
    req_dict = request.values.to_dict()
    # print(req_dict)
    # back_req = ""
    if req_dict.get("back_url", ""):
        if [i for i in ["add", "update", "invalid"] if i in req_dict.get("back_url")]:
            req_dict.pop("back_url")
    #     # back_req = "/" + req_dict.get("back_url").split("/")[-1]
    print(req_dict)
    try:
        permission = BuyUserPermission.query.filter_by(id=req_dict.get("permission_id")).update(
            {"margin": 0, "update_time": datetime.now(), "expire_time": datetime.now() - timedelta(1)})
        db.session.commit()
        _perm = BuyUserPermission.query.filter_by(id=req_dict.get("permission_id")).first()
        return render_template('user_permis.html', permission=_perm, combos=get_combo(), back_req=req_dict)
        # return redirect(url_for('permission'))
    except Exception as e:
        print("invalid_permission", e)
        db.session.rollback()
        return jsonify(result="失效失败")


@app.route('/permission/update', methods=['POST'])
@login_required
def update_permission():
    req_dict = request.values.to_dict()
    # back_req = ""
    if req_dict.get("back_url", ""):
        if [i for i in ["add", "update", "invalid"] if i in req_dict.get("back_url")]:
            req_dict.pop("back_url")
        # back_req = "/" + req_dict.get("back_url").split("/")[-1]
    # up_user = {}
    print(req_dict)
    perm_id = request.args.get('id')
    margin = request.form.get('margin')
    # if margin:
    #     up_user["margin"] = margin
    # expire_time = request.form.get('expire_time')
    # if expire_time:
    #     up_user["expire_time"] = expire_time
    # update_time = request.form.get('update_time')
    # if update_time:
    #     up_user["update_time"] = update_time
    date_num = request.form.get('date_num', type=int)
    try:
        user_perms = BuyUserPermission.query.filter_by(id=perm_id).first()
        if date_num:
            expire_time = user_perms.expire_time
            print(expire_time, type(expire_time))
            # 判断是否失效
            if expire_time.date() < datetime.now().date():
                expire_time = datetime.now() + timedelta(date_num)
            else:
                expire_time += timedelta(date_num)
            user_perms.expire_time = expire_time
        if margin:
            user_perms.margin = margin
        user_perms.update_time = datetime.now()
        # else:
        #     user_update = BuyUserPermission.query.filter(BuyUserPermission.id == request.args.get('id')).update(up_user)
        db.session.commit()
        print(user_perms.update_time)
        _perm = BuyUserPermission.query.filter_by(id=perm_id).first()
        return render_template('user_permis.html', permission=_perm, combos=get_combo(), back_req=req_dict)
        # return redirect(url_for('permission'))
    except Exception as e:
        print("update_permission", e)
        db.session.rollback()
        return jsonify(result="修改用户：%s 失败" % request.args.get('id'))


# python app.py >charge.log 2>&1 &
server = pywsgi.WSGIServer(('0.0.0.0', conf["port"]), app)
server.serve_forever()
