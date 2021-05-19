"""
    账户管理页面
"""
from flask import Blueprint, request, redirect, jsonify, g
from common.libs.Helper import ops_render, iPagination, getCurrentTime
from common.models.User import User
from application import app, db
from common.libs.UrlManager import UrlManager
from common.libs.user.UserService import UserService
from sqlalchemy import or_
from common.models.log.AppAccessLog import AppAccessLog

route_account = Blueprint('account', __name__)


# 展示所有管理员列表(数据查询、展示)
@route_account.route("/index")
def index():
    # 注：1.resp_data作为json传递数据
    resp_data = {}

    # 抽取公用变量
    query = User.query

    # 获取当前页数(默认第1页)——由前端页面传递
    req = request.values

    # 获取关键字（用于搜索）
    if 'mix_kw' in req:
        # 定义规则rule然后进行查询（用户名、手机号码）——混合查询
        rule = or_(User.nickname.ilike("%{0}%".format(req['mix_kw'])), User.mobile.ilike("%{0}%".format(req['mix_kw'])))
        query = query.filter(rule)
        # 复杂查询——query = User.query对象的值，用于下面的query查询显示

    # 获取状态（用于搜索查询）
    if 'status' in req and int(req['status']) > -1:
        query = query.filter(User.status == int(req['status']))
        # 用户状态==传递的状态值

    """ 
        p值来自于pagenation.html中
        {% for idx in pages.range %}
                {% if idx == pages.current %}
                    <li class="active"><a href="javascript:void(0);">{{ idx }}</a></li>
                {% else %}
                    <li><a href="{{ pages.url }}&p={{idx}}">{{ idx }}</a></li>
                {% endif %}
        {% endfor %}
        {% if pages.is_next == 1 %}
             <li>
                <a href="{{ pages.url }}&p={{ pages.total_pages }}" ><span>尾页</span></a>
             </li>
        {%  endif %}
    """
    page = int(req['p']) if ('p' in req and req['p']) else 1

    page_params = {
        # query.count()获取总页数
        'total': query.count(),
        # 每页展示数据个数
        'page_size': app.config['PAGE_SIZE'],
        # 当前页数(前端页面传递)
        'page': page,
        # 想展示多少页(一般显示10页)
        'display': app.config['PAGE_DISPLAY'],
        # 希望每页url地址是什么？----整体路径--------------：/account/index?&p=2
        'url': request.full_path.replace("&p={}".format(page), "")
        # 将里面的p参数进行替换掉——页面url地址http://192.168.43.199:8999/account/index?&p=2
    }
    '''
                例如：选择第5页的时候，前面有5个和后面有5个
                # 计算半圆
                semi = int(math.ceil(display / 2))

                if page - semi > 0:
                    ret['from'] = page - semi
                else:
                    ret['from'] = 1

                if page + semi <= total_pages:
                    ret['end'] = page + semi
                else:
                    ret['end'] = total_pages
    '''

    # iPagination()封装的分页方法
    pages = iPagination(page_params)
    # 每页偏移量，例如：第一页展示1~15个数据，偏移0，第二页展示15~30个数据，偏移量为15
    offset = (page - 1) * app.config['PAGE_SIZE']
    limit = app.config['PAGE_SIZE'] * page
    # 例如：第3页，offset=(3-1)*15=30   limit=3*15=45

    # 根据uid查询所有管理员数据(返回列表)
    list = query.order_by(User.uid.asc()).all()[offset:limit]      # 注：2.desc()倒序排列  asc()顺序排列
    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['search_data'] = req
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']

    return ops_render("account/index.html", resp_data)


# 账户详情信息
@route_account.route("/info", methods=['GET', 'POST'])
def info():

    resp_data = {}
    # 获取request中传递的值
    '''
        request.values与request.args区别？
        request.args只取get方式
        request.values将所有参数进行拼装好，放在一个dict字典内
        注：get()方法获取对应前端传递的''值，0为默认值
    '''
    req = request.args
    uid = int(req.get('id', 0))

    reback_url = UrlManager.buildUrl("/account/index")
    if uid < 1:
        # 如果uid<1，则错误，返回列表页面
        return redirect(reback_url)

    # 根据uid查询管理员信息
    user_info = User.query.filter_by(uid=uid).first()
    if not user_info:
        return redirect(reback_url)

    resp_data['info'] = user_info

    query = AppAccessLog.query
    query = query.filter_by(uid=uid)

    page = int(req['p']) if ('p' in req and req['p']) else 1

    page_params = {
        # query.count()获取总页数
        'total': query.count(),
        # 每页展示数据个数
        'page_size': app.config['PAGE_SIZE'],
        # 当前页数(前端页面传递)
        'page': page,
        # 想展示多少页(一般显示10页)
        'display': app.config['PAGE_DISPLAY'],
        # 希望每页url地址是什么？----整体路径--------------：/account/index?&p=2
        'url': request.full_path.replace("&p={}".format(page), "")
        # 将里面的p参数进行替换掉——页面url地址http://192.168.43.199:8999/account/index?&p=2
    }

    # iPagination()封装的分页方法
    pages = iPagination(page_params)
    # 每页偏移量，例如：第一页展示1~15个数据，偏移0，第二页展示15~30个数据，偏移量为15
    offset = (page - 1) * app.config['PAGE_SIZE']
    limit = app.config['PAGE_SIZE'] * page
    # 例如：第3页，offset=(3-1)*15=30   limit=3*15=45

    list = query.order_by(AppAccessLog.created_time.desc())[offset:limit]

    if list:
        resp_data['list'] = list
    resp_data['list'] = list
    resp_data['pages'] = pages

    return ops_render("account/info.html", resp_data)


# 编辑、添加管理员数据(注：GET--获取数据，POST--表单提交数据)
@route_account.route("/set", methods=["GET", "POST"])
def set():
    default_pwd = "******"

    if request.method == "GET":
        resp_data = {}
        req = request.args

        # 前台传递uid给后台，如果没有传递值则是添加账户否则为编辑账户(需要显示账户信息)
        uid = int(req.get("id", 0))
        info = None
        if uid:
            # 根据前端传入的id查询出对应的User对象(注：uid=0 -- false)
            info = User.query.filter_by(uid=uid).first()
        resp_data['info'] = info
        return ops_render("account/set.html", resp_data)

    resp = {
        'code': 200,
        'msg': '修改成功',
        'data': {}
    }

    req = request.values

    # 用户编辑传递json类型的id值
    id = req['id'] if 'id' in req else 0

    # 从前台edit.js获取对应的管理员信息
    nickname = req['nickname'] if 'nickname' in req else None
    mobile = req['mobile'] if 'mobile' in req else None
    email = req['email'] if 'email' in req else None
    login_name = req['login_name'] if 'login_name' in req else None
    login_pwd = req['login_pwd'] if 'login_pwd' in req else None

    if nickname is None or len(nickname) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的昵称"

        return jsonify(resp)

    if mobile is None or len(mobile) != 11:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的手机号"

        return jsonify(resp)

    if email is None or len(email) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的邮箱"

        return jsonify(resp)

    # login_name登录名不能重复
    if login_name is None or len(login_name) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的登录名"

        return jsonify(resp)
    ''' 
        filter()可以实现更多功能(复杂逻辑)，例如：是否存在于数据库表
        filter_by()——不需要写类   filter()——需要写类，因为不知道是哪个对象
    '''
    # 不等于该id且登录名相同的管理员用户还有没有（编辑用户操作）
    has_in = User.query.filter(User.login_name == login_name, User.uid != id).first()
    # 注：filter_by()中不需要写表名，而filter()需要通过表名获取对应的值
    if has_in:
        # 登录名重复
        resp['code'] = -1
        resp['msg'] = "登录名重复，请重新输入"

        return jsonify(resp)

    if login_pwd is None or len(login_pwd) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入不少于6位的登录密码"

        return jsonify(resp)

    # 判断编辑用户，还是添加用户
    user_info = User.query.filter_by(uid=id).first()
    if user_info:
        """
            1.如果通过编辑进入管理员账户编辑页面，则会传递id值
            2.此时通过id值则可以查询出User对象，并将user_info对象传回给前端页面，用于显示管理员用户信息
        """
        model_user = user_info
    else:
        """
            1.默认id为0，如果查询结果user_info==null，表示数据库中没有该用户
            2.数据库中没有该管理员用户，则说明点击+账户(添加账户进入)
            3.此时需要重新创建User对象，然后插入数据库
        """
        model_user = User()
        model_user.created_time = getCurrentTime()
        model_user.login_salt = UserService.geneSalt()

    model_user.updated_time = getCurrentTime()

    model_user.nickname = nickname
    model_user.email = email
    model_user.mobile = mobile

    model_user.login_name = login_name
    # 将加密后的算法写入数据库
    if login_pwd != default_pwd:
        """
            1.set.html页面通过{{ info.login_pwd }}显示密码，显示加密后的算法
            2.此时不能再对加密后的算法再次进行加密，这样用户回头使用原密码登录后则永远无法成功登录
            3.因此编辑账户信息页面，默认为******字符串，如果用户修改了密码一定不是******字符串，此时将加密后的密码写入数据库
                则没有什么问题
        """
        model_user.login_pwd = UserService.genePwd(login_pwd, model_user.login_salt)

    # 将对象返回给数据库，并添加
    db.session.add(model_user)
    db.session.commit()

    current_id = str(g.current_user.uid)
    if id == current_id:
        resp['msg'] = "由于您修改了当前登录用户的信息，请重新登录谢谢~~"

        return jsonify(resp)

    return jsonify(resp)


@route_account.route("/ops", methods=['GET', 'POST'])
def ops():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    req = request.values

    uid = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else None

    if not uid:
        resp['code'] = -1
        resp['msg'] = "请选择需要操作的账号~~"

        return jsonify(resp)

    if act not in ['remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试~~"

        return jsonify(resp)

    user_info = User.query.filter_by(uid=uid).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "当前账号不存在"

        return jsonify(resp)

    if act == 'remove':
        user_info.status = 0
    elif act == 'recover':
        user_info.status = 1

    # 每次操作数据库修改更新时间
    user_info.updated_time = getCurrentTime()

    db.session.add(user_info)
    db.session.commit()

    return jsonify(resp)
