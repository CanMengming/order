"""

"""
from flask import request, g
from common.models.log.AppAccessLog import AppAccessLog
from common.models.log.AppErrorLog import AppErrorLog
from common.libs.Helper import getCurrentTime
import json
from application import db


class LogService():
    @staticmethod
    def addAccessLog():
        # 添加浏览记录
        target = AppAccessLog()
        target.target_url = request.url     # request.url通过request获取当前url地址
        target.referer_url = request.referrer       # request.referer通过request获取上一个访问的url地址
        target.ip = request.remote_addr     # request.remote_addr获取远程ip地址
        target.query_params = json.dumps(request.values.to_dict())

        if 'current_user' in g and g.current_user is not None:
            target.uid = g.current_user.uid

        target.ua = request.headers.get("User_Agent")
        target.created_time = getCurrentTime()

        db.session.add(target)
        db.session.commit()

        return True

    @staticmethod
    def addErrorLog(content):
        # 添加错误记录
        target = AppErrorLog()
        target.target_url = request.url  # request.url通过request获取当前url地址
        target.referer_url = request.referrer  # request.referer通过request获取上一个访问的url地址
        target.query_params = json.dumps(request.values.to_dict())
        target.content = content

        if 'current_user' in g and g.current_user is not None:
            target.uid = g.current_user.uid

        target.created_time = getCurrentTime()

        db.session.add(target)
        db.session.commit()

        return True
