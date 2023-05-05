#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
@time: 2023/5/4 17:32
@Project ：chatgpt-on-wechat
@file: botcharge.py
"""
import json
import os
import requests
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
import plugins
from plugins import *
from common.log import logger
from common.expired_dict import ExpiredDict


@plugins.register(name="BotCharge", desc="调用API接口判断用户权限", desire_priority=990, version="0.1", author="ffwen123")
class BotCharge(Plugin):
    def __init__(self):
        super().__init__()
        curdir = os.path.dirname(__file__)
        config_path = os.path.join(curdir, "config.json")
        self.params_cache = ExpiredDict(60 * 60)
        if not os.path.exists(config_path):
            logger.info('[RP] 配置文件不存在，将使用config.json.template模板')
            config_path = os.path.join(curdir, "config.json.template")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.check_url = config["check_url"]
                self.pay_url = config["pay_url"]
                if not self.check_url:
                    raise Exception("please set your check_url in config or environment variable.")
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[RP] inited")
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                logger.warn(f"[RP] init failed, config.json not found.")
            else:
                logger.warn("[RP] init failed." + str(e))
            raise e

    def on_handle_context(self, e_context: EventContext):
        if e_context['context'].type not in [ContextType.IMAGE_CREATE,
                                             ContextType.IMAGE,
                                             ContextType.VOICE,
                                             ContextType.TEXT]:
            return
        logger.debug("[RP] on_handle_context. content: %s" % e_context['context'].content)
        logger.info("[RP] image_query={}".format(e_context['context'].content))
        reply = Reply()
        try:
            msg = e_context['context']["msg"]
            # 校验用户权限
            check_perm = requests.get(self.check_url, params={"user_id": msg.from_user_id, "bot_id": msg.to_user_id}, timeout=30.05)
            if not check_perm.json().get("result"):
                # 返回余额不足或没有权限
                reply.type = ReplyType.TEXT
                reply.content = self.pay_url.format(msg.to_user_id)
                e_context.action = EventAction.BREAK_PASS  # 事件结束后，跳过处理context的默认逻辑
                e_context['reply'] = reply
        except Exception as e:
            reply.type = ReplyType.ERROR
            reply.content = "[RP] " + str(e)
            e_context['reply'] = reply
            logger.exception("[RP] exception: %s" % e)
            e_context.action = EventAction.CONTINUE


