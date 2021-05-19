"""
python manager.py runjob -m queue/Index   运行入口
"""
from application import app, db
from common.models.food.Food import Food
from common.models.food.FoodSaleChangeLog import FoodSaleChangeLog
from common.models.queue.QueueList import QueueList
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.member.OauthMemberBind import OauthMemberBind
from common.libs.Helper import getCurrentTime
from common.libs.pay.WeChatService import WeChatService
import json, requests, datetime
from sqlalchemy import func


class JobTask():
    def __init__(self):
        pass

    def run(self, params):
        list = QueueList.query.filter_by(status=-1).order_by(QueueList.id.asc()).limit(1).all()    # 注：状态 -1 待处理 1 已处理
        for item in list:
            if item.queue_name == "pay":
                self.handlePay(item)

            # item.status = 1
            # item.updated_time = getCurrentTime()
            #
            # db.session.add(item)
            # db.session.commit()

    # 发送模板消息处理
    def handlePay(self, item):
        """
        1.选中一个模板将其进行选用，POST方式进行数据提交
        :param item:——QueueList数据库对象
        :return:
        """
        data = json.loads(item.data)    # 将json数据转化为list列表格式
        if 'member_id' not in data or 'pay_order_id' not in data:
            return False

        oauth_bind_info = OauthMemberBind.query.filter_by(member_id=data['member_id']).first()
        if not oauth_bind_info:
            return False

        pay_order_info = PayOrder.query.filter_by(id=data['pay_order_id']).first()
        if not pay_order_info:
            return False

        """
        模板消息例子：
        订单支付成功通知
        备注            点击查看，已购买的商品
        商品名称       【xx商店】商品
        订单金额        0.01元
        订单编号        O2020060520115
        订单状态        下单已支付
        
        备注          {{thing4.DATA}}
        商品名称      {{thing1.DATA}}
        订单金额      {{amount2.DATA}}
        订单编号      {{character_string8.DATA}}
        订单状态      {{phrase11.DATA}}
        """

        pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_info.id).all()
        notice_content = []
        if pay_order_items:
            date_from = datetime.datetime.now().strftime("%Y-%m-01  00:00:00")
            date_to = datetime.datetime.now().strftime("%Y-%m-31  23:59:59")

            for item in pay_order_items:
                tmp_food_info = Food.query.filter_by(id=item.food_id).first()
                if not tmp_food_info:
                    continue

                notice_content.append("【%s %s份】"%(tmp_food_info.name, item.quantity))

                tmp_food_info.total_count += 1

                # 当月数量
                tmp_stat_info = db.session.query(FoodSaleChangeLog, func.sum(FoodSaleChangeLog.quantity).label("total")) \
                    .filter(FoodSaleChangeLog.food_id == item.food_id) \
                    .filter(FoodSaleChangeLog.created_time >= date_from,
                            FoodSaleChangeLog.created_time <= date_to).first()
                tmp_month_count = tmp_stat_info[1] if tmp_stat_info[1] else 0
                tmp_food_info.month_count = tmp_month_count
                db.session.add(tmp_food_info)
                db.session.commit()

        # 拼接模板信息
        keyword1_val = pay_order_info.note if pay_order_info.note else '无'
        keyword2_val = "、".join(notice_content)
        keyword3_val = str(pay_order_info.total_price)
        keyword4_val = str(pay_order_info.order_number)
        keyword5_val = pay_order_info.status_desc

        target_wechat = WeChatService()
        access_token = target_wechat.getAccessToken()   # 获取access_token值

        url = "https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={0}".format(access_token)
        # 往该URL地址POST模板信息请求

        """
        请求参数
        属性	类型	默认值	必填	说明
        access_token	string		是	接口调用凭证
        touser	string		是	接收者（用户）的 openid
        template_id 	string  是	所需下发的订阅模板id
        page	string		否	点击模板卡片后的跳转页面，仅限本小程序内的页面。支持带参数,（示例index?foo=bar）。该字段不填则模板无跳转。
        data	Object		是	模板内容，格式形如 { "key1": { "value": any }, "key2": { "value": any } }
        miniprogram_state	string		否	跳转小程序类型：developer为开发版；trial为体验版；formal为正式版；默认为正式版
        lang	string		否	进入小程序查看”的语言类型，支持zh_CN(简体中文)、en_US(英文)、zh_HK(繁体中文)、zh_TW(繁体中文)，默认为zh_CN
        """
        params = {
          "touser": oauth_bind_info.openid,
          "template_id": "KWE9t6YLKl5MR6czirEaSAReKxJ14rMtdiAnGSCsHI0",
          "page": "pages/my/order_list",
          "form_id": pay_order_info.prepay_id,
          "data": {
              "keyword1": {
                    "value": keyword1_val
                },
                "keyword2": {
                    "value": keyword2_val
                },
                "keyword3": {
                    "value": keyword3_val
                },
                "keyword4": {
                    "value": keyword4_val
                },
                "keyword5": {
                    "value": keyword5_val
                }
          }
        }
        headers = {'Content-Type': 'application/json'}

        # 发送模板信息
        r = requests.post(url=url, data=json.dumps(params).encode("utf-8"), headers=headers)
        r.encoding = "utf-8"
        app.logger.info(r.text)

        return True
