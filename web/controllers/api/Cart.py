"""
    购物车模块
"""
from web.controllers.api import route_api
from flask import request, jsonify, g
from common.models.food.Food import Food
from common.models.member.MemberCart import MemberCart
from common.libs.member.CartService import CartService
from common.libs.Helper import selectFilterObject, getDictFilterField
from common.libs.UrlManager import UrlManager
import json


# 购物车列表展示
@route_api.route("/cart/index")
def cartIndex():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    member_info = g.member_info

    if not member_info:
        resp['code'] = -1
        resp['msg'] = "未登录"

        return jsonify(resp)

    # 取出该会员所有购物车记录（购物车列表）
    cart_list = MemberCart.query.filter_by(member_id=member_info.id).all()
    """
        前端js页面数据格式
        list: [
                {
                    "id": 1080,
					"food_id": "5",
                    "pic_url": "/images/food.jpg",
                    "name": "小鸡炖蘑菇-1",
                    "price": "85.00",
                    "active": true,
                    "number": 1
                }
            ]
    """
    data_cart_list = []
    if cart_list:
        # 从对象列表取出我们所需要的字段（查询出所有food_id然后进行数据展示）
        food_ids = selectFilterObject(cart_list, "food_id")
        food_map = getDictFilterField(Food, Food.id, "id", food_ids)
        # Food表查询id字段==food_ids，key值为"id"

        for item in cart_list:
            # food_map[item.food_id]获取Food对象
            tmp_food_info = food_map[item.food_id]
            tmp_data = {
                "id": item.id,
                "food_id": item.food_id,
                "number": item.quantity,
                "name": tmp_food_info.name,
                "price": str(tmp_food_info.price),
                "pic_url": UrlManager.buildImageUrl(tmp_food_info.main_image),
                "active": True
            }
            data_cart_list.append(tmp_data)

    resp['data']['list'] = data_cart_list
    return jsonify(resp)


# 购物车添加美餐功能
@route_api.route("/cart/set", methods=['POST'])
def setCart():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    req = request.values

    food_id = int(req['id']) if 'id' in req else 0
    number = int(req['number']) if 'number' in req else 0

    if number < 1 or food_id < 1:
        resp['code'] = -1
        resp['msg'] = '添加购物车失败-1'

        return jsonify(resp)

    # 拦截器中添加member_info至g内
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '添加购物车失败-2'

        return jsonify(resp)

    food_info = Food.query.filter_by(id=food_id).first()
    if not food_info:
        resp['code'] = -1
        resp['msg'] = '添加购物车失败-3'

        return jsonify(resp)
    if number > food_info.stock:
        resp['code'] = -1
        resp['msg'] = '添加购物车失败，库存不足'

        return jsonify(resp)

    ret = CartService.setItems(member_id=member_info.id, food_id=food_id, number=number)
    if not ret:
        resp['code'] = -1
        resp['msg'] = '添加购物车失败-4'

        return jsonify(resp)

    return jsonify(resp)


# 购物车删除功能
@route_api.route("/cart/del", methods=['POST', 'GET'])
def delCart():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    req = request.values

    params_goods = req['goods'] if 'goods' in req else None
    items = []
    if params_goods:
        # 注：json.loads()——解析json字符串，将其变成一个json对象
        items = json.loads(params_goods)

    if not items or len(items)< 1:
        return jsonify(resp)

    member_info = g.member_info     # 拦截器中设置当前登录会员的Member对象
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '删除购物车失败'

        return jsonify(resp)

    # 调用CartService中defItems()删除购物车数据表内的指定美餐
    ret = CartService.delItems(member_id=member_info.id, items=items)

    return jsonify(resp)
