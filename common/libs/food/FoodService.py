"""
    美食服务
"""
from application import app, db
from common.models.food.FoodStockChangeLog import FoodStockChangeLog
from common.models.food.Food import Food
from common.libs.Helper import getCurrentTime


class FoodService():

    # 美食库存变更
    @staticmethod
    def setStockChangedLog(food_id=0, quantity=0, note=''):
        if food_id < 1:
            # 注：if food_id < 1 or quantity< 1: 逻辑错误——原因：下单时quantity就是小于0
            return False

        food_info = Food.query.filter_by(id=food_id).first()
        if not food_info:
            return False

        model_stock_change = FoodStockChangeLog()
        model_stock_change.food_id = food_info.id
        model_stock_change.unit = quantity    # 下单操作变化数量
        model_stock_change.total_stock = food_info.stock
        model_stock_change.note = note
        model_stock_change.created_time = getCurrentTime()
        db.session.add(model_stock_change)
        db.session.commit()

        return True
