"""
    下单服务
"""
import decimal, time, hashlib, random, json
from application import app, db
from common.models.food.Food import Food
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderCallBackData import PayOrderCallbackData
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.member.MemberAddress import MemberAddress
from common.models.food.FoodSaleChangeLog import FoodSaleChangeLog
from common.libs.Helper import getCurrentTime
from common.libs.food.FoodService import FoodService
from common.libs.queue.QueueService import QueueService


class PayService():

    def __init__(self):
        pass

    # 下单操作(member_id会员id， items商品列表， params额外字段)
    def createOrder(self, member_id, items=None, params=None):
        resp = {
            'code': 200,
            'msg': '操作成功',
            'data': {}
        }

        pay_price = decimal.Decimal(0.00)
        continue_cnt = 0    # 默认没有选中的商品
        food_ids = []
        for item in items:
            if decimal.Decimal(item['price'])< 0:
                continue_cnt += 1
                continue
            pay_price = pay_price + decimal.Decimal(item['price']) * int(item['number'])  # 支付价格
            food_ids.append(item['id'])

        # 跳过的次数大于商品的数量
        if continue_cnt >= len(items):
            resp['code'] = -1
            resp['msg'] = "商品items为空"

            return resp

        yun_price = params['yun_price'] if 'yun_price' in params else 0  # 运费（参数传输）
        note = params['note'] if 'note' in params else None  # 备注
        express_address_id = params['express_address_id'] if 'express_address_id' in params else '' # 收货地址id
        express_info = params['express_info'] if 'express_info' in params else {}   # 收货地址信息

        yun_price = decimal.Decimal(yun_price)
        total_price = pay_price + yun_price     # 实际付的价格（商品费用+运费）

        """
            并发处理
            1.乐观锁——表中增加一个字段，每次update进行字段的判断
            2.悲观锁(本系统使用)——select语句查询时，会锁住这个表记录（事务处理）
        """
        try:
            # 事务 行级别锁，将food_ids中所有记录锁住，其他将无法再查询该记录
            tmp_food_list = db.session.query(Food).filter(Food.id.in_(food_ids)).with_for_update().all()

            # 订单主表
            tmp_foods_stock_mapping = {}
            for tmp_item in tmp_food_list:
                tmp_foods_stock_mapping[tmp_item.id] = tmp_item.stock

            model_pay_order = PayOrder()
            model_pay_order.member_id = member_id
            model_pay_order.order_sn = self.getOrderSn()    # 生成随机订单号
            model_pay_order.total_price = total_price
            model_pay_order.yun_price = yun_price
            model_pay_order.pay_price = pay_price
            model_pay_order.note = note
            model_pay_order.status = -8     # -8 待支付
            model_pay_order.express_status = -8     # 快递状态，-8 待支付

            address_info = MemberAddress.query.filter_by(id=express_address_id)
            model_pay_order.express_address_id = express_address_id
            model_pay_order.express_info = json.dumps(express_info)     # 将一个对象(例如列表类型)转化为str类型数据

            model_pay_order.updated_time = model_pay_order.created_time = getCurrentTime()
            db.session.add(model_pay_order)
            db.session.flush()

            # 订单
            for item in items:
                tmp_left_stock = tmp_foods_stock_mapping[item['id']]

                if decimal.Decimal(item['price']) < 0:
                    # 购买的商品价格< 0
                    continue
                if int(item['number']) > int(tmp_left_stock):
                    # 数量不足
                    food_info = Food.query.filter_by(id=item['id']).first()
                    raise Exception("您购买的美食--%s--太火爆，剩余：%s，而您购买：%s" % (food_info.name,tmp_left_stock, item['number']))

                # 修改美食库存
                # 商品剩余库存 = 剩余库存 - 购买的个数
                tmp_ret = Food.query.filter_by(id=item['id']).update({
                    "stock": int(tmp_left_stock) - int(item['number'])
                })

                if not tmp_ret:
                    raise Exception("下单失败，请重新下单")

                # 订单从表数据修改
                tmp_pay_item = PayOrderItem()
                tmp_pay_item.pay_order_id = model_pay_order.id
                tmp_pay_item.member_id = member_id
                tmp_pay_item.quantity = item['number']      # 购买数量
                tmp_pay_item.price = item['price']
                tmp_pay_item.food_id = item['id']       # 美食id
                tmp_pay_item.note = note        # 调用方法时传递的note
                tmp_pay_item.updated_time = tmp_pay_item.created_time = getCurrentTime()
                db.session.add(tmp_pay_item)

                # 库存变更表
                FoodService.setStockChangedLog(item['id'], -item['number'], "在线购买")

            db.session.commit()

            # 数据返回后台
            resp['data'] = {
                'id': model_pay_order.id,
                'order_sn': model_pay_order.order_sn,
                'total_price': str(total_price)
            }
        except Exception as e:
            # 出现异常后，进行数据回滚
            db.session.rollback()
            print(e)
            resp['code'] = -1
            resp['msg'] = "下单失败请重新下单"
            resp['msg'] = str(e)

            return resp

        return resp

    # 关闭订单
    def closeOrder(self, pay_order_id=0):
        if pay_order_id< 1:
            return False

        pay_order_info = PayOrder.query.filter_by(id=pay_order_id, status=-8).first()
        if not pay_order_info:
            return False

        pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_id).all()
        if pay_order_items:
            for item in pay_order_items:
                # 取消订单从表中所有与pay_order_id相同的订单
                item.status = 0

                # 归还美食库存信息
                quantity = item.quantity
                tmp_food_info = Food.query.filter_by(id=item.food_id).first()
                tmp_food_info.stock += quantity
                tmp_food_info.updated_time = getCurrentTime()
                db.session.add(tmp_food_info)
                db.session.commit()
                FoodService.setStockChangedLog(item.food_id, -quantity, "订单取消")

        pay_order_info.status = 0
        pay_order_info.updated_time = getCurrentTime()
        db.session.add(pay_order_info)
        db.session.commit()

        return True

    # 生成随机订单号
    def getOrderSn(self):
        m = hashlib.md5()
        sn = None
        while True:
            str = "%s-%s" % (int(round(time.time() * 100)), random.randint(0, 9999999))
            m.update(str.encode("utf-8"))
            sn = m.hexdigest()
            if not PayOrder.query.filter_by(order_sn=sn).first():
                # 如果当前order_sn不存在与数据库表内，则跳出死循环
                break

        return sn

    # 订单支付成功操作
    def orderSuccess(self, pay_order_id=0, params=None):
        """
        将pay_order数据表中该订单的status——>1(支付完成)  express_status——>-7(已支付代发货)
        :param pay_order_id:
        :param params:
        :return:
        """
        try:
            pay_order_info = PayOrder.query.filter_by(id=pay_order_id).first()
            if not pay_order_info or pay_order_info.status not in [-8, -7]:
                # -8——待支付  -7——完成支付待确认
                return True

            pay_order_info.pay_sn = params['pay_sn'] if params and 'pay_sn' in params else ''   # 第三方流水号
            pay_order_info.status = 1
            pay_order_info.express_status = -7      # -7——快递状态：待确认
            pay_order_info.pay_time = pay_order_info.updated_time = getCurrentTime()

            db.session.add(pay_order_info)
            db.session.commit()

            # 美食售卖变更表、库存变更表
            pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_id).all()     # 查询订单中所有具体美食信息
            for order_item in pay_order_items:
                # 美食库存变更表——FoodSaleChangeLog
                tmp_model_sale_log = FoodSaleChangeLog()
                tmp_model_sale_log.food_id = order_item.id
                tmp_model_sale_log.quantity = order_item.quantity
                tmp_model_sale_log.price = order_item.price
                tmp_model_sale_log.member_id = order_item.member_id
                tmp_model_sale_log.created_time = getCurrentTime()

                db.session.add(tmp_model_sale_log)

            db.session.commit()
        except Exception as e:
            # 操作异常数据库事务回滚
            db.session.rollback()
            return False

        QueueService.addQueue("pay", {
            "member_id": pay_order_info.member_id,
            "pay_order_id": pay_order_info.id
        })

    # 添加订单支付回调表信息
    def addPayCallbackData(self, pay_order_id=0, type='pay', data=''):
        model_callback_data = PayOrderCallbackData()
        model_callback_data.pay_order_id = pay_order_id
        if type == "pay":
            # 支付
            model_callback_data.pay_data = data     # 支付回调信息
            model_callback_data.refund_data = ''  # 退款回调信息
        else:
            # 退款
            model_callback_data.refund_data = data  # 退款回调信息
            model_callback_data.pay_data = ''     # 支付回调信息

        model_callback_data.created_time = model_callback_data.updated_time = getCurrentTime()

        db.session.add(model_callback_data)
        db.session.commit()
