# coding: utf-8
from application import db


class StatDailyMember(db.Model):
    __tablename__ = 'stat_daily_member'
    __table_args__ = (
        db.Index('idx_date_member_id', 'date', 'member_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, info='??')
    member_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='??id')
    total_shared_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='???????')
    total_pay_money = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='???????')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????????')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????')
