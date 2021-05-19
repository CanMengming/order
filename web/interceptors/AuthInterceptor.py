"""
    拦截器——实现cookie判断拦截
    注：如果是api请求，则进行统一的过滤
"""
from application import app
from flask import request, redirect, g
from common.models.User import User
from common.libs.user.UserService import UserService
from common.libs.UrlManager import UrlManager
import re
from common.libs.LogService import LogService


@app.before_request
def before_request():
    ignore_urls = app.config['IGNORE_URLS']
    ignore_check_login_urls = app.config['IGNORE_CHECK_LOGIN_URLS']

    path = request.path

    # 静态文件不需要判断
    pattern = re.compile('%s' % "|".join(ignore_check_login_urls))
    if pattern.match(path):
        return

    user_info = check_login()

    # 当前用户对象存入g.current_user内
    g.current_user = None
    if user_info:
        g.current_user = user_info

    # 拦截处理动作（加入访问记录）
    LogService.addAccessLog()

    # 登录页面无需重定向
    pattern = re.compile('%s' % "|".join(ignore_urls))
    if pattern.match(path):
        return

    # 当请求url地址中存在/api，则不进行AuthInterceptor拦截器的处理
    if '/api' in path:
        return

    if not user_info:
        # 用户cookie值返回False，则页面返回登录页面
        return redirect(UrlManager.buildUrl("/user/login"))

    return


# 判断用户是否已登录
def check_login():
    cookies = request.cookies  # 字典类型数据
    # 存在于字典则取出value值，否则返回""空值
    auth_cookie = cookies[app.config['AUTH_COOKIE_NAME']] if app.config['AUTH_COOKIE_NAME'] in cookies else None

    if auth_cookie is None:
        return False

    auth_info = auth_cookie.split("#")
    if len(auth_info) != 2:
        return False

    # 根据uid查询数据库用户信息
    try:
        user_info = User.query.filter_by(uid=auth_info[1]).first()
    except Exception:
        return False

    # 根据uid无法查询出该用户信息
    if user_info is None:
        return False

    # 查询的user_info对象的加密后的cookie值，与浏览器中的cookie不一致
    if auth_info[0] != UserService.geneAuthCode(user_info):
        return False

    # 登录状态校验(登录时删除账户则立即退出)
    if user_info.status != 1:
        return False

    return user_info
