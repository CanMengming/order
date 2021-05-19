"""

"""
from application import db
from common.models.member.MemberCart import MemberCart
from common.libs.Helper import getCurrentTime


class CartService():

    # 购物车信息存储至购物车表内
    @staticmethod
    def setItems(member_id= 0, food_id= 0, number= 0):
        if member_id< 1 or food_id< 1 or number< 1:
            return False

        cart_info = MemberCart.query.filter_by(food_id = food_id, member_id = member_id).first()
        if cart_info:
            # 当前该用户对于该美餐的购物车信息存在于购物车表
            model_cart = cart_info
        else:
            # 不存在与购物车表
            model_cart = MemberCart()
            model_cart.member_id = member_id
            model_cart.created_time = getCurrentTime()

        model_cart.food_id = food_id
        model_cart.quantity = number
        model_cart.updated_time = getCurrentTime()

        db.session.add(model_cart)
        db.session.commit()

        return True

    # 删除购物车内指定美餐
    @staticmethod
    def delItems(member_id=0, items=None):
        if member_id< 1 or not items:
            return False

        for item in items:
            # 将指定member_id(指定用户)，指定food_id(指定添加至购物车的美餐)删除
            MemberCart.query.filter_by(food_id=item['id'], member_id=member_id).delete()

        db.session.commit()

        return True
