"""
Job定时处理30分钟内未付款订单
python manager.py runjob -m pay/Index
"""
import datetime
from application import app
from common.models.pay.PayOrder import PayOrder
from common.libs.pay.PayService import PayService


class JobTask():
    def __init__(self):
        pass

    def run(self, params):
        now = datetime.datetime.now()
        date_before_30min = now + datetime.timedelta(minutes=-30)   # 当前时间的前30分钟的时间
        list = PayOrder.query.filter_by(status=-8)\
            .filter(PayOrder.created_time <= date_before_30min.strftime("%Y-%m-%d %H:%M:%S")).all()

        if not list:
            app.logger.info("No data")
            return

        pay_target = PayService()
        for item in list:
            pay_target.closeOrder(pay_order_id=item.id)       # PayService()中封装的关闭订单CloseOrder

        app.logger.info("It's over~~")
