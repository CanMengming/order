"""
事件队列表
"""
from application import app, db
from common.models.queue.QueueList import QueueList
from common.libs.Helper import getCurrentTime
import json


class QueueService():

    # 事件队列表添加数据
    @staticmethod
    def addQueue(queue_name, data=None):
        model_queue = QueueList()
        model_queue.queue_name = queue_name
        if data:
            model_queue.data = json.dumps(data)     # dumps()——将一个对象转换成为字符串
            # 注：json.loads()——将json数据转化为list类型

        model_queue.created_time = model_queue.updated_time = getCurrentTime()

        db.session.add(model_queue)
        db.session.commit()
