"""
用户收货地址
"""
from web.controllers.api import route_api
from application import app, db
from flask import request, jsonify, g
from common.models.member.MemberAddress import MemberAddress
from common.libs.Helper import getCurrentTime


# 编辑设置地址
@route_api.route("/my/address/set", methods=['POST'])
def myAddressSet():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    req = request.values
    id = int(req['id']) if 'id' in req and req['id'] else 0
    nickname = req['nickname'] if 'nickname' in req else ''
    mobile = req['mobile'] if 'mobile' in req else ''
    address = req['address'] if 'address' in req else ''

    province_id = int(req['province_id']) if ('province_id' in req and req['province_id']) else 0
    province_str = req['province_str'] if 'province_str' in req else ''
    province_index = int(req['province_index']) if 'province_index' in req else 0

    print("----------------------------------------------", province_index)

    city_id = int(req['city_id']) if ('city_id' in req and req['city_id']) else 0
    city_str = req['city_str'] if 'city_str' in req else ''
    city_index = int(req['city_index']) if 'city_index' in req else 0
    district_id = int(req['district_id']) if ('district_id' in req and req['district_id']) else 0
    district_str = req['district_str'] if 'district_str' in req else ''
    district_index = int(req['district_index']) if 'district_index' in req else 0

    member_info = g.member_info

    if not nickname:
        resp['code'] = -1
        resp['msg'] = "请填写联系人姓名~~"

        return jsonify(resp)

    if not mobile:
        resp['code'] = -1
        resp['msg'] = "请填写手机号码~~"

        return jsonify(resp)

    if province_id < 1:
        resp['code'] = -1
        resp['msg'] = "请选择地区~~"

        return jsonify(resp)

    if city_id < 1:
        resp['code'] = -1
        resp['msg'] = "请选择地区~~"

        return jsonify(resp)

    if district_id < 1:
        # 例如某些直辖市没有三级区
        district_str = ''

    if not address:
        resp['code'] = -1
        resp['msg'] = "请填写详细地址~~"

        return jsonify(resp)

    if not member_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍后再试~~"

        return jsonify(resp)

    address_info = MemberAddress.query.filter_by(id=id, member_id=member_info.id).first()
    if address_info:
        model_address = address_info
    else:
        default_address_count = MemberAddress.query.filter_by(is_default=1, member_id=member_info.id, status=1).count()
        # 计算表中默认地址个数
        model_address = MemberAddress()
        model_address.member_id = member_info.id
        model_address.is_default = 1 if default_address_count == 0 else 0
        # is_default设置为1前提是MemberAddress表中只有一条数据
        model_address.created_time = getCurrentTime()

    model_address.nickname = nickname
    model_address.mobile = mobile
    model_address.address = address
    model_address.province_id = province_id
    model_address.province_str = province_str
    model_address.province_index = province_index
    model_address.city_id = city_id
    model_address.city_str = city_str
    model_address.city_index = city_index
    model_address.area_id = district_id
    model_address.area_str = district_str
    model_address.area_index = district_index

    model_address.updated_time = getCurrentTime()

    db.session.add(model_address)
    db.session.commit()

    return jsonify(resp)


# 选择默认地址
@route_api.route("/my/address/ops", methods=['GET', 'POST'])
def myAddressOps():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    member_info = g.member_info
    req = request.values
    id = int(req['id']) if 'id' in req else 0
    act = req['act'] if 'act' in req else ''

    if int(id) < 1 or not member_info:
        resp['code'] = -1
        resp['msg'] = '系统繁忙，请稍后再试~~'

        return jsonify(resp)

    address_info = MemberAddress.query.filter_by(id=id, member_id=member_info.id).first()
    if not address_info:
        resp['code'] = -1
        resp['msg'] = '系统繁忙，请稍后再试~~'

        return jsonify(resp)

    if act == "del":
        # 地址删除操作
        address_info.status = 0
        address_info.updated_time = getCurrentTime()

        db.session.add(address_info)
        db.session.commit()
    elif act == "default":
        # 设置默认地址操作
        MemberAddress.query.filter_by(member_id=member_info.id).update({'is_default': 0})   # 将该用户所有is_default值置为0
        address_info.is_default = 1
        address_info.updated_time = getCurrentTime()

        db.session.add(address_info)
        db.session.commit()

    return jsonify(resp)


# 收货地址信息
@route_api.route("/my/address/info")
def myAddressInfo():
    resp = {
        'code': 200,
        'msg': '操作成功~~',
        'data': {}
    }
    req = request.values
    id = int(req['id']) if 'id' in req else 0
    member_info = g.member_info

    if id < 1 or not member_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍后再试~~"

        return jsonify(resp)

    address_info = MemberAddress.query.filter_by(id=id).first()
    if not address_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍后再试~~"

        return jsonify(resp)

    resp['data']['info'] = {
        "nickname": address_info.nickname,
        "mobile": address_info.mobile,
        "address": address_info.address,
        "province_id": address_info.province_id,
        "province_str": address_info.province_str,
        "province_index": address_info.province_index,
        "city_id": address_info.city_id,
        "city_str": address_info.city_str,
        "city_index": address_info.city_index,
        "area_id": address_info.area_id,
        "area_str": address_info.area_str,
        "area_index": address_info.area_index
    }

    return jsonify(resp)
