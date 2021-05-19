# coding: utf-8
from application import db, app


class PayOrder(db.Model):
    __tablename__ = 'pay_order'
    __table_args__ = (
        db.Index('idx_member_id_status', 'member_id', 'status'),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_sn = db.Column(db.String(40), nullable=False, unique=True, server_default=db.FetchedValue(), info='?????')
    member_id = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='??id')
    total_price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='??????')
    yun_price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='????')
    pay_price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='??????')
    pay_sn = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='??????')
    prepay_id = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='?????id')
    note = db.Column(db.Text, nullable=False, info='????')
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='1????? 0 ?? -1 ???? -2 ??? -9 ????  -8 ???  -7 ???????')
    express_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='?????-8 ??? -7 ?????? 1????? 0???')
    express_address_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='????id')
    express_info = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue(), info='????')
    comment_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='????')
    pay_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='??????')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????????')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????')

    @property
    def pay_status(self):
        tmp_status = self.status
        if self.status == 1:
            tmp_status = self.express_status
            if self.express_status == 1 and self.comment_status == 0:
                # 确认收货 待评价
                tmp_status = -5
            if self.express_status == 1 and self.comment_status == 1:
                # 确认收获 已评价
                tmp_status = 1
        return tmp_status

    @property
    def status_desc(self):
        # 状态描述
        return app.config['PAY_STATUS_DISPLAY_MAPPING'][str(self.pay_status)]

    @property
    def order_number(self):
        # 订单号，将当前时间格式化作为订单号
        order_number = self.created_time.strftime("%Y%m%d%H%M%S")
        order_number = order_number + str(self.id).zfill(5)
        return order_number
