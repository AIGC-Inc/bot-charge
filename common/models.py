#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
@time: 2023/5/4 11:45
@Project ：chatgpt-on-wechat
@file: models.py
"""
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


# class User(db.Model):
#     __tablename__ = 'user'  # 表名
#     user_id = db.Column(db.String(100), primary_key=True)  # id，主键
#     user_nickname = db.Column(db.String(40))  # 用户名称
#     create_time = db.Column(db.TIMESTAMP)
#     update_time = db.Column(db.TIMESTAMP)
#
#     def __init__(self, user_id, user_nickname, create_time, update_time):
#         self.user_id = user_id
#         self.user_nickname = user_nickname
#         self.create_time = create_time
#         self.update_time = update_time


# class Bot(db.Model):
#     __tablename__ = 'bot'  # 表名
#     bot_id = db.Column(db.String(100), primary_key=True)  # id，主键
#     bot_nickname = db.Column(db.String(60))  # 机器人名称
#     create_time = db.Column(db.TIMESTAMP)
#     update_time = db.Column(db.TIMESTAMP)
#
#     def __init__(self, bot_id, bot_nickname, create_time, update_time):
#         self.bot_id = bot_id
#         self.bot_nickname = bot_nickname
#         self.create_time = create_time
#         self.update_time = update_time


class Combo(db.Model):
    __tablename__ = 'combo'  # 表名
    combo_id = db.Column(db.String(100), primary_key=True, comment="套餐ID")
    bot_id = db.Column(db.String(100), comment="机器人ID")
    combo_name = db.Column(db.String(20), comment="套餐名称")
    combo_price = db.Column(db.Float, comment="套餐单价/包月费用")
    combo_type = db.Column(db.SmallInteger, comment="套餐类型")
    allot_time = db.Column(db.SmallInteger, comment="使用期限")
    upper_limit = db.Column(db.SmallInteger, comment="使用上限")
    create_time = db.Column(db.TIMESTAMP)
    update_time = db.Column(db.TIMESTAMP)

    def __init__(self, combo_id, bot_id, combo_name, combo_price, combo_type, allot_time, upper_limit, create_time, update_time):
        self.combo_id = combo_id
        self.bot_id = bot_id
        self.combo_name = combo_name
        self.combo_price = combo_price
        self.combo_type = combo_type
        self.allot_time = allot_time
        self.upper_limit = upper_limit
        self.create_time = create_time
        self.update_time = update_time


class UserOrder(db.Model):
    __tablename__ = 'user_order'  # 表名
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(100), index=True, comment="订单ID")
    open_id = db.Column(db.String(100), comment="用户ID")
    bot_id = db.Column(db.String(100), comment="机器人ID")
    combo_id = db.Column(db.String(100), comment="套餐ID")
    order_price = db.Column(db.Float, comment="订单价格")
    combo_num = db.Column(db.SmallInteger, comment="套餐量/使用期限")
    create_time = db.Column(db.TIMESTAMP)
    update_time = db.Column(db.TIMESTAMP)

    def __init__(self, order_id, bot_id, open_id, combo_id, order_price, combo_num, create_time, update_time):
        self.order_id = order_id
        self.open_id = open_id
        self.bot_id = bot_id
        self.combo_id = combo_id
        self.order_price = order_price
        self.create_time = create_time
        self.combo_num = combo_num
        self.update_time = update_time


class UserPermissions(db.Model):
    __tablename__ = 'user_permissions'  # 表名
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment="")
    user_id = db.Column(db.String(100), comment="用户ID")
    bot_id = db.Column(db.String(100), comment="机器人ID")
    margin = db.Column(db.Integer, comment="余量")
    use_count = db.Column(db.Integer, comment="使用次数")
    status = db.Column(db.SmallInteger, comment="权限状态，1有，0失效")
    combo_num = db.Column(db.SmallInteger, comment="套餐量/使用期限")
    create_time = db.Column(db.TIMESTAMP)
    update_time = db.Column(db.TIMESTAMP)

    def __init__(self, user_id, bot_id, margin, use_count, status, create_time, update_time):
        self.user_id = user_id
        self.bot_id = bot_id
        self.margin = margin
        self.use_count = use_count
        self.status = status
        self.create_time = create_time
        self.update_time = update_time


# class DeductionLog(db.Model):
#     __tablename__ = 'deduction_log'  # 表名
#     deduction_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)  # id，主键
#     permissions_id = db.Column(db.BigInteger, db.ForeignKey('user_permissions.id'))  # 用户 id，设置外键
#     deduction_amount = db.Column(db.Integer)
#     create_time = db.Column(db.TIMESTAMP)
#
#     def __init__(self, permissions_id, deduction_amount, create_time):
#         self.permissions_id = permissions_id
#         self.deduction_amount = deduction_amount
#         self.create_time = create_time
