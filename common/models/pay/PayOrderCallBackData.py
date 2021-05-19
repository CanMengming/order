# coding: utf-8
from application import db



class PayOrderCallbackData(db.Model):
    __tablename__ = 'pay_order_callback_data'

    id = db.Column(db.Integer, primary_key=True)
    pay_order_id = db.Column(db.Integer, nullable=False, unique=True, server_default=db.FetchedValue(), info='????id')
    pay_data = db.Column(db.Text, nullable=False, info='??????')
    refund_data = db.Column(db.Text, nullable=False, info='??????')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????????')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????')
