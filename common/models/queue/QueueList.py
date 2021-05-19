# coding: utf-8
from application import db


class QueueList(db.Model):
    __tablename__ = 'queue_list'

    id = db.Column(db.Integer, primary_key=True)
    queue_name = db.Column(db.String(30), nullable=False, server_default=db.FetchedValue(), info='????')
    data = db.Column(db.String(500), nullable=False, server_default=db.FetchedValue(), info='????')
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='?? -1 ??? 1 ???')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????????')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='????')
