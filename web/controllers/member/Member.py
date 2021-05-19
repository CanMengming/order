"""
    会员列表
"""
from sqlalchemy import or_
from application import app, db
from flask import Blueprint, request, jsonify, redirect
from common.models.food.Food import Food
from common.models.member.Member import Member
from common.models.member.MemberComments import MemberComments
from common.libs.Helper import iPagination
from common.libs.UrlManager import UrlManager
from common.libs.Helper import getCurrentTime, ops_render, getDictFilterField, selectFilterObject

route_member = Blueprint('member_page', __name__)


# 会员列表首页
@route_member.route("/index")
def index():
    resp_data = {}

    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1  # 当前页数
    query = Member.query

    if 'status' in req and int(req['status']) > -1:
        query = query.filter(Member.status == int(req['status']))

    if 'mix_kw' in req:
        # 定义规则rule然后进行查询（用户名、手机号码）——混合查询
        rule = or_(Member.nickname.ilike("%{0}%".format(req['mix_kw'])))
        query = query.filter(rule)
        # 复杂查询——query = User.query对象的值，用于下面的query查询显示

    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")

    }

    pages = iPagination(page_params)
    offset = (page - 1) * app.config['PAGE_SIZE']
    list = query.order_by(Member.id.asc()).offset(offset).limit(app.config['PAGE_SIZE'])
    # 根据Member.id进行排序order_by()  注：传入偏移量.offset()和每页显示多少数据.limit()

    resp_data['list'] = list  # 循环显示数据
    resp_data['pages'] = pages  # 分页数据
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    resp_data['search_con'] = req  # 用于查询后数据显示在页面从不刷新掉
    resp_data['current'] = 'index'

    return ops_render("member/index.html", resp_data)


# 会员详情
@route_member.route("/info", methods=['GET', 'POST'])
def info():
    resp_data = {}
    req = request.values

    id = req['id'] if 'id' in req and req['id'] else 0

    reback_url = UrlManager.buildUrl("/member/index")
    if int(id) < 1:
        return redirect(reback_url)

    member_info = Member.query.filter_by(id=id).first()
    if not member_info:
        return redirect(reback_url)

    resp_data['info'] = member_info
    resp_data['current'] = 'index'

    return ops_render("member/info.html", resp_data)


# 会员设置
@route_member.route("/set", methods=['GET', 'POST'])
def set():
    if request.method == 'GET':
        resp_data = {}

        req = request.values
        id = int(req['id'] if 'id' in req else 0)
        reback_url = UrlManager.buildUrl("/member/index")

        if id < 0:
            return redirect(reback_url)

        member_info = Member.query.filter_by(id=id).first()
        if not member_info:
            return redirect(reback_url)

        resp_data['info'] = member_info
        resp_data['current'] = 'index'

        return ops_render("member/set.html", resp_data)

    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    req = request.values
    id = req['id'] if 'id' in req else 0
    nickname = req['nickname'] if 'nickname' in req else None

    if nickname is None or len(nickname) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的姓名"

        return jsonify(resp)

    member_info = Member.query.filter_by(id=id).first()
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "指定会员不存在"

        return jsonify(resp)

    member_info.nickname = nickname
    member_info.updated_time = getCurrentTime()

    db.session.add(member_info)
    db.session.commit()

    return jsonify(resp)


# 会员删除、恢复
@route_member.route("/ops", methods=['GET', 'POST'])
def ops():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }

    req = request.values

    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else None

    if not id:
        resp['code'] = -1
        resp['msg'] = "请选择需要操作的账号~~"

        return jsonify(resp)

    if not act:
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试~~"

        return jsonify(resp)

    member_info = Member.query.filter_by(id=id).first()
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "当前账号不存在，请重试~~"

        return jsonify(resp)

    if act == 'remove':
        member_info.status = 0

    if act == 'recover':
        member_info.status = 1

    member_info.updated_time = getCurrentTime()

    db.session.add(member_info)
    db.session.commit()

    return jsonify(resp)


# 会员评价列表
@route_member.route("/comment")
def comment():
    resp_data = {}
    req = request.args
    page = int(req['p']) if ('p' in req and req['p']) else 1
    query = MemberComments.query

    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    pages = iPagination(page_params)
    offset = (page - 1) * app.config['PAGE_SIZE']

    comment_list = query.order_by(MemberComments.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()
    data_list = []
    if comment_list:
        member_map = getDictFilterField(Member, Member.id, "id", selectFilterObject(comment_list, "member_id"))
        food_ids = []
        for item in comment_list:
            tmp_food_ids = (item.food_ids[1:-1]).split("_")
            tmp_food_ids = {}.fromkeys(tmp_food_ids).keys()
            food_ids = food_ids + list(tmp_food_ids)

        food_map = getDictFilterField(Food, Food.id, "id", food_ids)

        for item in comment_list:
            tmp_member_info = member_map[item.member_id]
            tmp_foods = []
            tmp_food_ids = (item.food_ids[1:-1]).split("_")
            for tmp_food_id in tmp_food_ids:
                tmp_food_info = food_map[int(tmp_food_id)]
                tmp_foods.append({
                    'name': tmp_food_info.name,
                })

            tmp_data = {
                "content": item.content,
                "score": item.score,
                "member_info": tmp_member_info,
                "foods": tmp_foods
            }
            data_list.append(tmp_data)
    resp_data['list'] = data_list
    resp_data['pages'] = pages
    resp_data['current'] = 'comment'

    return ops_render("member/comment.html", resp_data)
