#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
@time: 2023/5/4 11:45
@file: models.py
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BuyCombo(db.Model):
    __tablename__ = 'buy_combo'

    combo_id = db.Column(db.Integer, primary_key=True, info='套餐ID')
    agent_id = db.Column(db.String(100), nullable=False, unique=True, info='机器人ID')
    combo_name = db.Column(db.String(20), nullable=False, info='套餐名称')
    combo_price = db.Column(db.Numeric(10, 2), nullable=False, info='套餐单价/包月费用,单位:元')
    combo_type = db.Column(db.SmallInteger, info='套餐类型')
    allot_time = db.Column(db.SmallInteger, nullable=False, info='使用期限(单位:天)')
    upper_limit = db.Column(db.SmallInteger, nullable=False, info='使用上限')
    create_time = db.Column(db.DateTime, nullable=False)
    update_time = db.Column(db.DateTime, nullable=False)
    free_quota = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='体验次数')
    corp_id = db.Column(db.String(255), comment='企业微信的corp_id')
    secret = db.Column(db.String(255), comment='应用的secret')


class BuyUserOrder(db.Model):
    __tablename__ = 'buy_user_order'

    order_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.String(255), info='企业微信用户的user_id')
    out_trade_no = db.Column(db.String(255), index=True, info='订单编号')
    prepay_id = db.Column(db.String(255), nullable=False, unique=True, info='微信支付交易号')
    openid = db.Column(db.String(255), info='用户ID')
    agent_id = db.Column(db.String(255), nullable=False, info='机器人ID')
    combo_id = db.Column(db.Integer, nullable=False, info='套餐ID')
    total_fee = db.Column(db.Numeric(10, 2), nullable=False, info='订单价格(元)，保留两位小数')
    create_time = db.Column(db.DateTime, nullable=False)
    pay_time = db.Column(db.DateTime, nullable=False, info='支付时间')
    pay_status = db.Column(db.Integer, nullable=False, info='支付状态(0:未支付,1:支付完成)')
    update_time = db.Column(db.DateTime, nullable=False)
    trade_type = db.Column(db.String(255), nullable=False, info='支付类型')
    allot_time = db.Column(db.Integer, nullable=False, info='使用期限(天)')
    upper_limit = db.Column(db.Integer, nullable=False, info='使用上限(每天使用上限的次数)')
    callbakxml = db.Column(db.Text)
    browser_type = db.Column(db.Integer, info='支付时使用的浏览器，1:微信浏览器,2:企业微信浏览器')


class BuyUserPermission(db.Model):
    __tablename__ = 'buy_user_permissions'
    __table_args__ = (db.Index('user_id&agent_id', 'user_id', 'agent_id'),)

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False, info='企业微信的userid')
    agent_id = db.Column(db.String(100), nullable=False, info='机器人ID')
    margin = db.Column(db.Integer, nullable=False, info='当天使用余量')
    use_count = db.Column(db.Integer, nullable=False, info='使用次数')
    status = db.Column(db.Integer, nullable=False, info='权限状态，1有，0失效')
    expire_time = db.Column(db.DateTime, info='套餐过期时间')
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    openid = db.Column(db.String(255))
