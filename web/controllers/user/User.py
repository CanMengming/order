"""
    用户管理页面
"""
from flask import Blueprint, request, jsonify, make_response, redirect, g
from common.models.User import User
from common.libs.user.UserService import UserService
import json
from application import app, db
from common.libs.UrlManager import UrlManager
from common.libs.Helper import ops_render

# 使用蓝图功能配置url地址
route_user = Blueprint('user_page', __name__)


# 登录
@route_user.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # ops_render()方法——页面渲染   参数—传入指定html文件
        return ops_render("user/login.html")

    # req字典存储request内值
    req = request.values

    # 定义json数值用于返回值html页面
    resp = {'code': 200, 'msg': '登录成功', 'data': {}}
    '''
    login.html文件
    <div class="form-group">
        <input type="text" name="login_name" class="form-control" placeholder="请输入登录用户名">
    </div>
    <div class="form-group">
        <input type="password" name="login_pwd" class="form-control" placeholder="请输入登录密码">
    </div>
    '''
    # 如果'login_name'作为key值在req字典内则返回对应的value值
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

    # 用户名不为空判断
    if login_name is None or len(login_name) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入正确的登录用户名~~"

        return jsonify(resp)

    # 密码不为空判断
    if login_pwd is None or len(login_pwd) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入正确的登录密码~~"

        return jsonify(resp)

    # 验证用户名是否存在——根据用户名查询用户信息
    user_info = User.query.filter_by(login_name=login_name).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "请输入正确的用户名或密码~1~"

        return jsonify(resp)

    if user_info.status != 1:
        resp['code'] = -1
        resp['msg'] = "当前用户已删除，请联系管理员进行处理"

        return jsonify(resp)

    # 验证登录密码(加密算法)
    '''
        登录密码为：用户输入的密码与加密字符串进行加密，得到新密码存储至数据库内
    '''
    if user_info.login_pwd != UserService.genePwd(login_pwd, user_info.login_salt):
        resp['code'] = -1
        resp['msg'] = "请输入正确的用户名或密码~2~"

        return jsonify(resp)

    response = make_response(json.dumps(resp))
    response.set_cookie(app.config['AUTH_COOKIE_NAME'], "%s#%s" % (UserService.geneAuthCode(user_info), user_info.uid))

    return response


# 修改账户信息(姓名、邮箱)
@route_user.route("/edit", methods=['GET', 'POST'])
def edit():
    if request.method == 'GET':
        return ops_render("user/edit.html", {'current': 'edit'})

    resp = {
        'code': 200,
        'msg': "操作成功",
        'data': {}
    }

    req = request.values
    nickname = req['nickname'] if 'nickname' in req else None
    email = req['email'] if 'email' in req else None

    if nickname is None or len(nickname) <= 0:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的姓名~~"
        return jsonify(resp)

    if email is None or len(email) <= 0:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的邮箱名~~"
        return jsonify(resp)

    # 对象user_info进行数据修改
    user_info = g.current_user
    user_info.nickname = nickname
    user_info.email = email

    # 提交数据库表修改请求
    db.session.add(user_info)
    db.session.commit()

    return jsonify(resp)


# 修改密码
@route_user.route("/reset-pwd", methods=['GET', 'POST'])
def resetPwd():
    if request.method == 'GET':
        return ops_render("user/reset_pwd.html", {'current': 'reset-pwd'})

    # 密码修改
    resp = {
        'code': 200,
        'msg': "操作成功",
        'data': {}
    }

    req = request.values
    old_password = req['old_password'] if 'old_password' in req else None
    new_password = req['new_password'] if 'new_password' in req else None

    if old_password is None or len(old_password) <= 0:
        resp['code'] = -1
        resp['msg'] = "请输入原密码~~"
        return jsonify(resp)

    if new_password is None or len(new_password) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入不少于6位的新密码~~"
        return jsonify(resp)

    if old_password == new_password:
        resp['code'] = -1
        resp['msg'] = "请重新输入新密码(新旧密码不允许相同)~~"
        return jsonify(resp)

    user_info = g.current_user
    if UserService.genePwd(old_password, user_info.login_salt) != user_info.login_pwd:
        resp['code'] = -1
        resp['msg'] = '请输入正确的旧密码~~'
        return jsonify(resp)

    # 对象user_info进行数据修改
    new_login_password = UserService.genePwd(new_password, user_info.login_salt)
    user_info.login_pwd = new_login_password

    # 提交数据库表修改请求
    db.session.add(user_info)
    db.session.commit()

    # 刷新cookie
    response = make_response(json.dumps(resp))
    response.set_cookie(app.config['AUTH_COOKIE_NAME'], "%s#%s" % (UserService.geneAuthCode(user_info), user_info.uid)
                        , 60 * 60 * 24 * 15)    # 默认cookie值保存在浏览器15天

    return response


@route_user.route("/logout")
def logout():
    # 实现登出操作

    # 页面重定向至/user/login
    response = make_response(redirect(UrlManager.buildUrl("/user/login")))
    # 删除response中的cookie值
    response.delete_cookie(app.config['AUTH_COOKIE_NAME'])
    return response
