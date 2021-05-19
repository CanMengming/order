# coding: utf-8
from application import db



class PayOrderItem(db.Model):
    __tablename__ = 'pay_order_item'

    id = db.Column(db.Integer, primary_key=True)
    pay_order_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), info='??id')
    member_id = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='??id')
    quantity = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='???? ??1?')
    price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='???????? * ??')
    food_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), info='???id')
    note = db.Column(db.Text, nullable=False, info='????')
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='???1??? 0 ??')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????????')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????')
