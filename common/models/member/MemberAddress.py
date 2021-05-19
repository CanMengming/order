# coding: utf-8
from application import db



class MemberAddress(db.Model):
    __tablename__ = 'member_address'
    __table_args__ = (
        db.Index('idx_member_id_status', 'member_id', 'status'),
    )

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='??id')
    nickname = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='?????')
    mobile = db.Column(db.String(11), nullable=False, server_default=db.FetchedValue(), info='???????')
    province_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='?id')
    province_str = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='???')
    province_index = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='?Index??')
    city_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='??id')
    city_str = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='???')
    city_index = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='??Index??')
    area_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='??id')
    area_str = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='????')
    area_index = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='??Index??')
    address = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='????')
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='???? 1??? 0???')
    is_default = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='????')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????????')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????')
