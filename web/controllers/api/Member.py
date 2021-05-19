"""
    小程序会员
"""
from web.controllers.api import route_api
from flask import jsonify, request, g
from application import db
from common.models.member.Member import Member
from common.models.member.OauthMemberBind import OauthMemberBind
from common.models.food.WxShareHistory import WxShareHistory
from common.libs.Helper import getCurrentTime
from common.libs.member.MemberService import MemberService


# 登录
@route_api.route("/member/login", methods=['GET', 'POST'])
def login():
    # 登录操作
    resp = {
        'code': 200,
        'msg': '操作成功~~',
        'data': {}
    }

    req = request.values
    code = req['code'] if 'code' in req else None

    nickname = req['nickName'] if 'nickName' in req else None
    sex = req['gender'] if 'gender' in req else 0
    avatar = req['avatarUrl'] if 'avatarUrl' in req else None

    if not code or len(code) < 1:
        resp['code'] = -1
        resp['msg'] = "需要code"

        return jsonify(resp)

    # 获取封装在MemberService中方法的获取openid的方法
    openid = MemberService.getWechatOpenid(code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = "调用微信出现错误"

        return jsonify(resp)

    # 判断是否注册过，注册过直接返回登录信息
    bind_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first()
    if not bind_info:
        # 如果关联表中不存在该openid的数据(根据前台传递的数据，创建Member、OauthMemberBind对象，并存储至数据库)

        model_member = Member()
        model_member.nickname = nickname
        model_member.sex = sex
        model_member.avatar = avatar  # 头像
        model_member.salt = MemberService.geneSalt()
        model_member.created_time = model_member.updated_time = getCurrentTime()

        db.session.add(model_member)
        db.session.commit()

        model_bind = OauthMemberBind()
        model_bind.member_id = model_member.id
        model_bind.type = 1
        model_bind.openid = openid
        model_bind.extra = ''  # 额外字段
        model_bind.created_time = model_bind.updated_time = getCurrentTime()
        db.session.add(model_bind)
        db.session.commit()

        bind_info = model_bind

    # 根据关联表的id（即member表的id）查询出Member对象
    member_info = Member.query.filter_by(id=bind_info.id).first()

    token = "%s#%s" % (MemberService.geneAuthCode(member_info), member_info.id)
    resp['data'] = {'token': token}

    return jsonify(resp)


# 检测是否已经注册
@route_api.route("/member/check-reg", methods=['POST', 'GET'])
def checkReg():
    resp = {
        'code': 200,
        'msg': '操作成功~~',
        'data': {}
    }

    req = request.values
    code = req['code'] if 'code' in req else None
    if not code or len(code) < 1:
        resp['code'] = -1
        resp['msg'] = "需要code"

        return jsonify(resp)

    openid = MemberService.getWechatOpenid(code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = "调用微信出现错误"

        return jsonify(resp)

    bind_info = OauthMemberBind.query.filter_by(openid=openid).first()
    if not bind_info:
        resp['code'] = -1
        resp['msg'] = "未绑定"

        return jsonify(resp)

    member_info = Member.query.filter_by(id=bind_info.id).first()
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "未查询到绑定信息"

        return jsonify(resp)

    # 不返回用户基本信息，而是返回加密的后token信息至前端
    token = "%s#%s" % (MemberService.geneAuthCode(member_info), member_info.id)
    resp['data'] = {'token': token}

    return jsonify(resp)


# 小程序分享
@route_api.route("/member/share", methods=['POST'])
def memberShare():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    req = request.values

    """
    data{
        // 当前界面的url地址（获取带参数的URL地址）
        url: utils.getCurrentPageUrlWithArgs()
    }
    """
    url = req['url'] if 'url' in req else ''

    """
        ApiAuthInterceptor.py拦截器中g变量存储当前小程序登录对象的信息
        member_info = check_member_login()

        # 当前用户对象存入g.current_user内
        g.current_user = None
    """
    member_info = g.member_info
    model_share = WxShareHistory()

    if member_info:
        # model_share用户分享对象的member_id记录小程序会员的id（记录哪个会员分享的）
        model_share.member_id = member_info.id
    model_share.share_url = url
    model_share.created_time = getCurrentTime()
    db.session.add(model_share)
    db.session.commit()

    return jsonify(resp)


# 会员中心信息展示
@route_api.route("/member/info")
def memberInfo():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    member_info = g.member_info

    if not member_info:
        resp['code'] = -1
        resp['msg'] = '系统繁忙，请重试~~'

        return jsonify(resp)

    """
    user_info: {
                nickname: "明华俊",
                avatar_url: "/images/more/logo.png"
            }
    """
    user_info = {
        "nickname": member_info.nickname,
        "avatar_url": member_info.avatar
    }
    resp['data']['user_info'] = user_info

    return jsonify(resp)
