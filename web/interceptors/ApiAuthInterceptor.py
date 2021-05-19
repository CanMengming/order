"""
    小程序会员拦截器
    api认证——api请求认证不是api请求不会进行认证
"""
from application import app
from flask import request, g, jsonify
from common.models.member.Member import Member
from common.libs.member.MemberService import MemberService
import re


@app.before_request
def before_request():
    # 小程序端哪些页面是不需要过滤
    api_ignore_urls = app.config['API_IGNORE_URLS']
    path = request.path
    if "/api" not in path:
        return

    member_info = check_member_login()

    # 当前用户对象存入g.current_user内
    g.member_info = None
    if member_info:
        g.member_info = member_info

    # 登录页面无需重定向
    pattern = re.compile('%s' % "|".join(api_ignore_urls))
    if pattern.match(path):
        return

    if not member_info:
        # 用户token值返回False，则页面返回登录页面
        resp = {
            'code': -1,
            'msg': '未登录',
            'data': {}
        }
        return jsonify(resp)

    return


# 判断用户是否已登录
def check_member_login():
    # 存在于字典则取出value值，否则返回""空值
    auth_cookie = request.headers.get("Authorization")
    # 获取小程序缓存cache中的token值

    if auth_cookie is None:
        return False

    # token值——f714bfbc85a9e8e49f97b8887d2719d4#1
    auth_info = auth_cookie.split("#")
    if len(auth_info) != 2:
        return False

    # 根据uid查询数据库用户信息
    try:
        member_info = Member.query.filter_by(id=auth_info[1]).first()
    except Exception:
        return False

    # 根据uid无法查询出该用户信息
    if member_info is None:
        return False

    # 查询的member_info对象的加密后的token值，与小程序中的token不一致
    if auth_info[0] != MemberService.geneAuthCode(member_info):
        return False

    # 登录状态校验(登录时删除账户则立即退出)
    if member_info.status != 1:
        return False

    return member_info
