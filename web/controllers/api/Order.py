"""
    订单页面
"""
from web.controllers.api import route_api
from flask import request, jsonify, g
from application import app, db
import json, decimal
from common.models.food.Food import Food
from common.models.pay.PayOrder import PayOrder
from common.models.member.OauthMemberBind import OauthMemberBind
from common.models.member.MemberAddress import MemberAddress
from common.libs.UrlManager import UrlManager
from common.libs.pay.PayService import PayService
from common.libs.member.CartService import CartService
from common.libs.pay.WeChatService import WeChatService
from common.libs.Helper import getCurrentTime


# 订单信息展示
@route_api.route("/order/info", methods=['GET', 'POST'])
def orderInfo():
    resp = {
        'code': 200,
        'msg': "操作成功",
        'data': {}
    }
    req = request.values
    params_goods = req['goods'] if 'goods' in req else None
    member_info = g.member_info

    params_goods_list = []
    if params_goods:
        params_goods_list = json.loads(params_goods)

    food_dict = {}
    for item in params_goods_list:
        """
            小程序端传递的JSON数据
            type: cart
            goods: [{"id":8,"price":"66.00","number":3},{"id":7,"price":"120.00","number":2}]
        """
        food_dict[item['id']] = item['number']
        # goods中的id作为key，number作为value值

    food_ids = food_dict.keys()   # 取出所有key值（即所有id值）
    food_list = Food.query.filter(Food.id.in_(food_ids)).all()      # 查询出所有food_ids中所有id值的Food信息

    yun_price = pay_price = decimal.Decimal(0.00)       # 价格都是用decimcal格式数据

    data_food_list = []
    if food_list:
        for item in food_list:
            """
                data: {
                    goods_list: [
                        {
                            id:22,
                            name: "小鸡炖蘑菇",
                            price: "85.00",
                            pic_url: "/images/food.jpg",
                            number: 1,
                        }
                    ],
                    default_address: {
                        name: "明华俊",
                        mobile: "12345678901",
                        detail: "江苏省常州市江苏理工学院",
                    },
                    yun_price: "1.00",
                    pay_price: "85.00",
                    total_price: "86.00",
                    params: null
                },
            """
            tmp_data = {
                "id": item.id,
                "name": item.name,
                "price": str(item.price),
                "pic_url": UrlManager.buildImageUrl(item.main_image),
                "number": food_dict[item.id]
            }
            pay_price = pay_price + item.price* int( food_dict[item.id])
            data_food_list.append(tmp_data)

    # 数据库表中获取默认地址
    address_info = MemberAddress.query.filter_by(is_default=1, member_id=member_info.id, status=1).first()
    if address_info:
        detail = "{0}{1}{2}{3}".format(address_info.province_str, address_info.city_str, address_info.area_str, address_info.address)
        default_address = {
            "id": address_info.id,
            "name": address_info.nickname,
            "mobile": address_info.mobile,
            "detail": detail
        }

    resp['data']['food_list'] = data_food_list
    resp['data']['pay_price'] = str(pay_price)
    resp['data']['yun_price'] = str(yun_price)
    resp['data']['total_price'] = str(pay_price + yun_price)
    resp['data']['default_address'] = default_address

    return jsonify(resp)


# 下单操作
@route_api.route("/order/create", methods=['POST', 'GET'])
def orderCreate():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    req = request.values

    type = req['type'] if 'type' in req else None
    note = req['note'] if 'note' in req else None
    params_goods = req['goods'] if 'goods' in req else None
    express_address_id = req['express_address_id'] if 'express_address_id' in req and req['express_address_id'] else 0

    items = []
    if params_goods:
        items = json.loads(params_goods)    # 将JSON格式数据转换成为list类型

    if len(items)< 1:
        resp['code'] = -1
        resp['msg'] = "下单失败：没有选择商品"

        return jsonify(resp)

    address_info = MemberAddress.query.filter_by(id=express_address_id).first()
    if not address_info or address_info.status == 0:
        # 地址信息不存在或状态==0
        resp['code'] = -1
        resp['msg'] = "下单失败：快递地址不正确"

        return jsonify(resp)

    member_info = g.member_info
    params = {
        'note': note,
        'express_address_id': express_address_id,
        'express_info': {
            "name": address_info.nickname,
            "mobile": address_info.mobile,
            "detail": "{0}{1}{2}{3}".format(address_info.province_str, address_info.city_str,
                                            address_info.area_str, address_info.address)
        }
    }

    target = PayService()
    resp = target.createOrder(member_info.id, items, params)
    # 创建订单——(member_info.id(用户id), items(购物车数据), params(note，运费，收货地址等)), 注：返回reap  JSON格式数据

    # 创建订单后，删除购物车内数据
    if resp['code'] == 200 and type == 'cart':
        # 购物车页面提交订单，而不是商品详情页面直接购买
        CartService.delItems(member_info.id, items)

    return jsonify(resp)


# 支付
@route_api.route("/order/pay", methods=['POST', 'GET'])
def orderPay():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    member_info = g.member_info
    req = request.values
    order_sn = req['order_sn'] if 'order_sn' in req else ''     # 获取前台传输的订单号

    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()    # 查询指定订单号的订单信息
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍后再试1!!"

        return jsonify(resp)

    oauth_bind_info = OauthMemberBind.query.filter_by(member_id=member_info.id).first()
    if not oauth_bind_info:
        resp['code'] = -1
        resp['msg'] = '系统繁忙，请稍后再试2!!'

        return jsonify(resp)

    config_mina = app.config['MINA_APP']
    notify_url = app.config['APP']['domain'] + config_mina['callback_url']     # 回调地址

    target_wechat = WeChatService(merchant_key=config_mina['pay_key'])  # merchant_key微信支付key值
    # 请求参数(传入必要的参数)
    data = {
        "appid": config_mina['appid'],
        "mch_id": config_mina['mch_id'],
        'nonce_str': target_wechat.get_nonce_str(),
        "body": "微信小程序订餐",
        "out_trade_no": pay_order_info.order_sn,
        "total_fee": int(pay_order_info.total_price * 100),
        "notify_url": notify_url,
        "trade_type": "JSAPI",
        "openid": oauth_bind_info.openid
    }
    """ 
        注：1.total_fee以分为单位，数据库中以圆为单位
            2.out_trade_no——商户系统内部订单号，要求32个字符内，只能是数字、大小写字母_-|* 且在同一个商户号下唯一
            3.total_fee——订单总金额，单位为分
            4.spbill_create_ip终端ip——支持IPV4和IPV6两种格式的IP地址。用户的客户端IP(123.12.12.123)
            5.notify_url——异步接收微信支付结果通知的回调地址，通知url必须为外网可访问的url，不能携带参数
            6.trade_type——JSAPI -JSAPI支付、NATIVE -Native支付、APP -APP支付
            7.openid——此参数为微信用户在商户对应appid下的唯一标识
    """
    pay_info = target_wechat.get_pay_info(data)     # 调用WeChatService中下单操作

    """
    get_pay_info()方法——返回的列表值
    pay_sign_data = {
                'timeStamp': pay_data.get('out_trade_no'),  # 商户系统内部订单号--order_sn
                'nonceStr': pay_data.get('nonce_str'),      # 随机字符串
                'package': 'prepay_id={0}'.format(prepay_id),  # 微信生成的预支付会话标识
                'signType': 'MD5',
                'paySign': paySign,     # 生成签名
                'prepay_id': prepay_id  # 微信生成的预支付会话标识
            }
    """

    # 保存prepay_id为了后面发送模板消息
    pay_order_info.prepay_id = pay_info['prepay_id']

    db.session.add(pay_order_info)
    db.session.commit()

    resp['data']['pay_info'] = pay_info

    return jsonify(resp)


# 支付回调
@route_api.route("/order/callback", methods=['POST', 'GET'])
def orderCallback():
    """
    微信返回的回调信息
    <xml>
        <return_code><![CDATA[SUCCESS]]></return_code>
        <return_msg><![CDATA[OK]]></return_msg>
        <result_code><![CDATA[SUCCESS]]></result_code>
        <mch_id><![CDATA[1609600519]]></mch_id>
        <appid><![CDATA[wx7279c0c7a3120706]]></appid>
        <nonce_str><![CDATA[fsh6THPslkODbA2f]]></nonce_str>
        <sign><![CDATA[4ACD54B185C0F394595184E93EAF8D3E]]></sign>
        <prepay_id><![CDATA[wx18211231580946ae69384f49d55ea90000]]></prepay_id>
        <trade_type><![CDATA[JSAPI]]></trade_type>
    </xml>

    :return:
    """
    """
    支付完成后，微信会把相关支付结果及用户信息通过数据流的形式发送给商户，商户需要接收处理，并按文档规范返回应答。
    注意：
    1、同样的通知可能会多次发送给商户系统。商户系统必须能够正确处理重复的通知。

    2、后台通知交互时，如果微信收到商户的应答不符合规范或超时，微信会判定本次通知失败，重新发送通知，直到成功为止
    （在通知一直不成功的情况下，微信总共会发起多次通知，通知频率为15s/15s/30s/3m/10m/20m/30m/30m/30m/60m/3h/3h/3h/6h/6h
     - 总计 24h4m），但微信不保证通知最终一定能成功。

    3、在订单状态不明或者没有收到微信支付结果通知的情况下，建议商户主动调用微信支付【查询订单API】确认订单状态。
    :return:
    """

    # 返回值
    result_data = {
        'return_msg': 'OK',
        'return_code': 'SUCCESS'
    }

    header = {
        'Content-Type': 'application/xml'
    }
    config_mina = app.config['MINA_APP']
    target_wechat = WeChatService(merchant_key=config_mina['pay_key'])
    callback_data = target_wechat.xml_to_dict(request.data)     # 取出整个POST请求request中所有数据

    app.logger.info(callback_data)
    sign = callback_data['sign']    # 微信支付返回的sign签名
    callback_data.pop('sign')

    gene_sign = target_wechat.create_sign(callback_data)    # 根据数据生成的sign签名

    print("------------------------------------------------", gene_sign)

    app.logger.info(gene_sign)
    # 签名验证
    if sign != gene_sign:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL1'

        return target_wechat.dict_to_xml(result_data), header

    # 支付金钱验证
    order_sn = callback_data['out_trade_no']    # 获取订单号
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
    if not pay_order_info:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL2'

        return target_wechat.dict_to_xml(result_data), header

    # 验证：订单的总价格与支付金额是否一致
    if int(pay_order_info.total_price * 100) != int(callback_data['total_fee']):
        result_data['return_code'] = result_data['return_msg'] = 'FAIL3'

        return target_wechat.dict_to_xml(result_data), header

    # 订单已支付
    if pay_order_info.status == 1:
        return target_wechat.dict_to_xml(result_data), header

    # 调用订单支付成功后，更新订单表信息
    target_pay = PayService()
    target_pay.orderSuccess(pay_order_id=pay_order_info.id, params={'pay_sn': callback_data['transaction_id']})
    # 注：transaction_id——微信订单号

    # 将微信回调的结果放入支付回调信息表(即pay_order_callback_data表)
    target_pay.addPayCallbackData(pay_order_id=pay_order_info.id, type='pay', data=request.data)

    return target_wechat.dict_to_xml(result_data), header


# 取消订单、确认收货
@route_api.route("/order/ops", methods=['POST'])
def orderOps():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    req = request.values
    member_info = g.member_info

    order_sn = req['order_sn'] if 'order_sn' in req else ''
    act = req['act'] if 'act' in req else ''

    payOrder_info = PayOrder.query.filter_by(order_sn=order_sn).first()
    if not payOrder_info:
        resp['code'] = -1
        resp['msg'] = '系统繁忙，请稍后再试'

        return resp

    if act == "cancel":
        # 取消订单
        target_pay = PayService()
        ret = target_pay.closeOrder(pay_order_id=payOrder_info.id)     # 调用PayService()中封装的取消订单方法
        if not ret:
            resp['code'] = -1
            resp['msg'] = '系统繁忙，请稍后再试'

            return resp

    elif act == "confirm":
        # 确认收货
        payOrder_info.express_status = 1    # 快递状态置为1——已确认收货
        payOrder_info.updated_time = getCurrentTime()

        db.session.add(payOrder_info)
        db.session.commit()

    return resp
