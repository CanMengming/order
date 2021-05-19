# coding: utf-8
from application import db, app
"""
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
"""


class FoodCat(db.Model):
    __tablename__ = 'food_cat'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='????')
    weight = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='??')
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='?? 1??? 0???')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????????')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????')

    # 虚拟字段
    @property
    def status_desc(self):
        # 菜品种类状态  0-已删除 1-正常
        return app.config['STATUS_MAPPING'][str(self.status)]
