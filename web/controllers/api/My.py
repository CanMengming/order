"""
    个人中心
"""
import json, datetime
from application import app, db
from web.controllers.api import route_api
from flask import g, request, jsonify
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.food.Food import Food
from common.models.member.MemberComments import MemberComments
from common.models.member.MemberAddress import MemberAddress
from common.libs.Helper import selectFilterObject, getDictFilterField
from common.libs.UrlManager import UrlManager
from common.libs.Helper import getCurrentTime


# 订单列表展示
@route_api.route("/my/order", methods=['GET', 'POST'])
def myOrderList():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    member_info = g.member_info
    req = request.values

    status = int(req['status']) if 'status' in req else None     # 获取当前选中的是什么订单状态（已付款、已确认、待评价等）
    query = PayOrder.query.filter_by(member_id=member_info.id)   # 查询当前会员的所有订单表
    """ 
        注：PayOrder表与PayOrderItem表之间的区别？
        1.PayOrder表中每条数据是一次结算的所有商品总和，例如：购物车一次性结算可能有好几个美食
        2.PayOrderItem表一个商品一条数据
    """

    if status == -8:
        # 等待付款状态
        query = query.filter(PayOrder.status == -8)

    elif status == -7:
        # 待发货
        query = query.filter(PayOrder.status == 1, PayOrder.express_status == -7, PayOrder.comment_status == 0)
        # 已付款，未发货，未评论

    elif status == -6:
        # 待确认
        query = query.filter(PayOrder.status == 1, PayOrder.express_status == -6, PayOrder.comment_status == 0)
        # 已付款，待确认，未评价

    elif status == -5:
        # 待评价
        query = query.filter(PayOrder.status == 1, PayOrder.express_status == 1, PayOrder.comment_status == 0)

    elif status == 1:
        # 已完成
        query = query.filter(PayOrder.status == 1, PayOrder.express_status == 1, PayOrder.comment_status == 1)

    else:
        # 已关闭
        query = query.filter(PayOrder.status == 0)

    # 获取订单列表
    pay_order_list = query.order_by(PayOrder.id.desc()).all()

    data_pay_order_list = []
    if pay_order_list:
        pay_order_ids = selectFilterObject(pay_order_list, "id")    # 从pay_order_list中取出其id字段
        pay_order_item_list = PayOrderItem.query.filter(PayOrderItem.pay_order_id.in_(pay_order_ids)).all()
        # 根据PayOrder的订单id获取——所有订单从表信息

        food_ids = selectFilterObject(pay_order_item_list, "food_id")      # 从pay_order_item_list中取出其food_id字段
        food_map = getDictFilterField(Food, Food.id, "id", food_ids)  # 获取指定food_ids的Food对象——{"id", Food}

        pay_order_item_map = {}     # 订单从表map
        if pay_order_item_list:
            # pay_order_item_list所有从表订单数据
            for item in pay_order_item_list:
                # 某一具体订单下数据的增加（美食的具体信息等等）
                if item.pay_order_id not in pay_order_item_map:
                    pay_order_item_map[item.pay_order_id] = []

                # 美食信息   food_map——获取指定food_ids的Food对象——{"id", Food}
                tmp_food_info = food_map[item.food_id]
                """
                    前端数据格式
                    order_list: [
                                    {
                                        status: -8,
                                        status_desc: "待支付",
                                        date: "2021-03-01 22:30:23",
                                        order_number: "20210301223023001",
                                        note: "记得周六发货",
                                        total_price: "85.00",
                                        goods_list: [
                                            {
                                                pic_url: "/images/food.jpg"
                                            }
                                        ]
                                    }
                                ]
                """
                # 往同一订单主表id(pay_order_id)内追加美食数据
                pay_order_item_map[item.pay_order_id].append({
                    "id": item.id,
                    "food_id": item.food_id,
                    "quantity": item.quantity,
                    "pic_url": UrlManager.buildImageUrl(tmp_food_info.main_image),
                    "name": tmp_food_info.name
                })

        for item in pay_order_list:
            # 增加订单
            tmp_data = {
                "status": item.pay_status,
                "status_desc": item.status_desc,
                "date": item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                "order_number": item.order_number,
                "order_sn": item.order_sn,      # 订单号
                "note": item.note,
                "total_price": str(item.total_price),
                "goods_list": pay_order_item_map[item.id]   # 根据item.id即订单主表id，添加具体商品信息
            }

            data_pay_order_list.append(tmp_data)

    resp['data']['pay_order_list'] = data_pay_order_list

    return jsonify(resp)


# 订单详情
@route_api.route("/my/order/info")
def myOrderInfo():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    req = request.values
    member_info = g.member_info
    order_sn = req['order_sn'] if 'order_sn' in req else ''

    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn, member_id=member_info.id).first()
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = '系统繁忙，请稍后再试~~'

        return jsonify(resp)

    """
    info: {
                order_sn:"123123",
                status: -8,
                status_desc: "待支付",
                deadline:"2021-04-22 12:00",
                pay_price: "85.00",
                yun_price: 0.00,
                total_price: "85.00",
                address: {
                    name: "明华俊",
                    mobile: "12345678901",
                    address: "江苏省常州市江苏理工学院"
                },
                goods: [
                    {
                        name: "小鸡炖蘑菇",
                        price: "85.00",
                        unit: 1,
                        pic_url: "/images/food.jpg"
                    }
                ]
            }
    """
    express_info = {}
    if pay_order_info.express_info:
        express_info = json.loads(pay_order_info.express_info)      # 将json格式数据解析成为list列表类型

    tmp_deadline = pay_order_info.created_time + datetime.timedelta(minutes=30)     # 计算订单支付的截止时间
    info = {
        "order_sn": pay_order_info.order_sn,
        "status": pay_order_info.pay_status,
        "status_desc": pay_order_info.status_desc,
        "deadline": tmp_deadline.strftime("%Y-%m-%d %H:%M:%S"),
        "pay_price": str(pay_order_info.pay_price),
        "yun_price": str(pay_order_info.yun_price),
        "total_price": str(pay_order_info.total_price),
        "address": express_info,
        "goods": []
    }

    pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_info.id).all()
    if pay_order_items:
        food_ids = selectFilterObject(pay_order_items, "food_id")
        food_map = getDictFilterField(Food, Food.id, "id", food_ids)
        for item in pay_order_items:
            tmp_food_info = food_map[item.food_id]
            tmp_data = {
                "name": tmp_food_info.name,
                "price": str(tmp_food_info.price),
                "unit": item.quantity,
                "pic_url": UrlManager.buildImageUrl(tmp_food_info.main_image)
            }
            info['goods'].append(tmp_data)

    resp['data']['info'] = info

    return jsonify(resp)


# 订单评价
@route_api.route("/my/comment/add", methods=['POST'])
def commentAdd():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    req = request.values
    member_info = g.member_info
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    score = req['score'] if 'score' in req else 10
    content = req['content'] if 'content' in req else ''

    payOrder_info = PayOrder.query.filter_by(member_id=member_info.id, order_sn=order_sn).first()     # 查询出待评价的订单
    if not payOrder_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙请稍后再试!!!"

        return jsonify(resp)

    if payOrder_info.comment_status == 1:
        # 当前订单已经被评价
        resp['code'] = -1
        resp['msg'] = "请勿重复评价!!!"

        return jsonify(resp)

    payOrder_items = PayOrderItem.query.filter_by(pay_order_id=payOrder_info.id).all()
    food_ids = selectFilterObject(payOrder_items, "food_id")    # 获取对象payOrder_itms的所有food_id字段值
    # 修改美食——评价次数
    for item in food_ids:
        tmp_food = Food.query.filter_by(id=item).first()
        if tmp_food:
            tmp_food.comment_count += 1
            tmp_food.updated_time = getCurrentTime()

            db.session.add(tmp_food)
            db.session.commit()

    tmp_food_ids_str = "_".join(str(s) for s in food_ids if s not in [None])
    # 注：如果是5,3   则join后结果为：_5_3

    model_comment = MemberComments()
    model_comment.member_id = member_info.id
    model_comment.food_ids = "_%s_" % tmp_food_ids_str
    model_comment.pay_order_id = payOrder_info.id
    model_comment.score = score
    model_comment.content = content
    model_comment.created_time = getCurrentTime()

    db.session.add(model_comment)
    db.session.commit()

    payOrder_info.comment_status = 1        # 订单数据中comment_status评价状态置为1(表示已经评价过了)
    payOrder_info.updated_time = getCurrentTime()
    db.session.add(payOrder_info)
    db.session.commit()

    return jsonify(resp)


# 获取评价列表
@route_api.route("/my/comment/list")
def myCommentList():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    member_info = g.member_info
    comment_list = MemberComments.query.filter_by(member_id=member_info.id).order_by(MemberComments.id.desc()).all()

    """
    我的评价(前端数据格式)：
    list: [
            {
                date: "2021-03-01 22:30:23",
                order_number: "20210301223023001",
                content: "记得周六发货",
            }
        ]
    """
    data_comment_list = []
    for comment in comment_list:
        tmp_pay_order_info = PayOrder.query.filter_by(id=comment.pay_order_id).first()
        tmp_data = {
            "date": comment.created_time.strftime("%Y-%m-%d %H:%M:%S"),
            "order_number": tmp_pay_order_info.order_number,
            "content": comment.content
        }
        data_comment_list.append(tmp_data)

    resp['data']['list'] = data_comment_list

    return jsonify(resp)


# 收货地址列表
@route_api.route("/my/address/index")
def myAddressList():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    member_info = g.member_info
    member_address_list = MemberAddress.query.filter_by(status=1, member_id=member_info.id)\
        .order_by(MemberAddress.id.asc()).all()

    """
    addressList: [
                {
                    id:1,
                    name: "明华俊",
                    mobile: "12345678901",
                    detail: "江苏省常州市江苏理工学院",
                    isDefault: 1
                },
                {
                    id: 2,
                    name: "殘梦",
                    mobile: "12345678901",
                    detail: "江苏省扬州市送桥"
                }
            ]
    """
    addressList = []
    if member_address_list:
        for item_address in member_address_list:
            tmp_data = {
                "id": item_address.id,
                "name": item_address.nickname,
                "mobile": item_address.mobile,
                "detail": "%s%s%s%s" % (item_address.province_str, item_address.city_str, item_address.area_str,
                                      item_address.address),
                "isDefault": item_address.is_default
            }
            addressList.append(tmp_data)

    resp['data']['list'] = addressList

    return jsonify(resp)
