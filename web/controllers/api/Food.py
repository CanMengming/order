"""
    小程序会员端
"""
from web.controllers.api import route_api
from flask import jsonify, request, g
from common.models.food.FoodCat import FoodCat
from common.models.food.Food import Food
from common.models.member.MemberComments import MemberComments
from common.models.member.Member import Member
from common.models.member.MemberCart import MemberCart
from common.libs.UrlManager import UrlManager
from common.libs.Helper import getCurrentTime, getDictFilterField, selectFilterObject
from sqlalchemy import or_


# 返回main图以及首页分类信息
@route_api.route("/food/index")
def foodIndex():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    # 取出所有正常状态的菜品分类
    cat_list = FoodCat.query.filter_by(status=1).order_by(FoodCat.weight.desc()).all()

    # 所有菜品类别的数据列表(存储字典(存储每个菜品分类信息)——id: *, name: *)
    data_cat_list = []
    """ 前端小程序菜品分类格式
        categories: [
                {id: 0, name: "全部"},
                {id: 1, name: "川菜"},
                {id: 2, name: "东北菜"},
            ]
    """
    data_cat_list.append({
        'id': 0,
        'name': '全部'
    })
    if cat_list:
        for item in cat_list:
            tmp_data = {
                'id': item.id,
                'name': item.name
            }
            data_cat_list.append(tmp_data)

    # 取出最热门的菜品图片用于轮播展示(注：limit(4)只取出四条数据)
    food_list = Food.query.filter(Food.status == 1, Food.stock> 0).order_by(Food.total_count.desc(), Food.id.desc()).limit(4)
    data_food_list = []
    """ 前端小程序图片轮播格式
        // 首页热卖美餐图片轮播
            banners: [
                {
                    "id": 1,
                    "pic_url": "/images/food.jpg"
                },
                {
                    "id": 2,
                    "pic_url": "/images/food.jpg"
                },
                {
                    "id": 3,
                    "pic_url": "/images/food.jpg"
                }
            ],
    """
    if food_list:
        for item in food_list:
            tmp_food_data = {
                'id': item.id,
                'pic_url': UrlManager.buildImageUrl(item.main_image)
            }
            data_food_list.append(tmp_food_data)

    resp['data']['banner_list'] = data_food_list
    resp['data']['cat_list'] = data_cat_list
    return jsonify(resp)


# 返回相关搜索信息
@route_api.route("/food/search")
def foodSearch():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }

    req = request.values
    # 获取前端传递的cat_id(美餐列表)、mix_kw(搜索字段)
    cat_id = int(req['cat_id']) if 'cat_id' in req else 0
    mix_kw = str(req['mix_kw']) if 'mix_kw' in req else ''
    p = int(req['p']) if 'p' in req else 1

    if p < 1:
        # 如果传递的p值小于1，则将p重置为1
        p = 1

    query = Food.query.filter(Food.status == 1, Food.stock > 0)

    page_size = 4
    # 计算页内偏移量
    offset = (p - 1) * page_size
    # 获取美餐种类用于搜素
    if cat_id > 0:
        query = query.filter(Food.cat_id == cat_id)

    if mix_kw:
        # 定义规则rule然后进行查询（美餐名、标签名）——混合查询
        rule = or_(Food.name.ilike("%{0}%".format(mix_kw)), Food.tags.ilike("%{0}%".format(mix_kw)))
        query = query.filter(rule)
        # 复杂查询

    food_list = query.order_by(Food.total_count.desc(), Food.id.desc()).offset(offset).limit(page_size).all()

    # 将food_list转化为前端所需要的json格式数据
    data_food_list = []
    """
        goods: [
                    {
                        "id": 1,
                        "name": "小鸡炖蘑菇-1",
                        "min_price": "15.00",
                        "price": "15.00",
                        "pic_url": "/images/food.jpg"
                    }
                ]
    """
    if food_list:
        for item in food_list:
            tmp_data = {
                'id': item.id,
                'name': item.name,
                'price': str(item.price),
                'min_price': str(item.price),
                'pic_url': UrlManager.buildImageUrl(item.main_image)
            }
            data_food_list.append(tmp_data)

    resp['data']['list'] = data_food_list
    resp['data']['has_more'] = 0 if len(food_list) < page_size else 1
    # 当前取出的Food数据量小于page_size表示数据库中后面没有数据，则返回0，有>=10表示还有数据，则再次请求
    # 注：刚好最后一页数据==10，则多消耗一次判断而少一次sql查询

    return jsonify(resp)


# 美餐详情信息
@route_api.route("/food/info")
def foodInfo():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    req = request.values

    id = int(req['id']) if 'id' in req else 0
    food_info = Food.query.filter_by(id=id).first()
    if not food_info and not food_info.status:
        resp['code'] = -1
        resp['msg'] = "美食已经下架"
        return jsonify(resp)

    member_info = g.member_info
    cart_number = 0
    if member_info:
        # 购物车左下角购物车角标显示该用户添加多少种类美餐至购物车内
        cart_number = MemberCart.query.filter_by(member_id=member_info.id).count()
    """
        "info": {
                "id": 1,
                "name": "小鸡炖蘑菇",
                "summary": '<p>多色可选的马甲</p><p><img src="http://www.timeface.cn/uploads/times/2015/07/071031_f5Viwp.jpg"/></p><p><br/>相当好吃了</p>',
                "total_count": 2,
                "comment_count": 2,
                "stock": 2,
                "price": "80.00",
                "main_image": "/images/food.jpg",
                "pics": [ '/images/food.jpg','/images/food.jpg' ]
            }
    """
    resp['data']['info'] = {
        'id': food_info.id,
        'name': food_info.name,
        'summary': food_info.summary,
        "total_count": food_info.total_count,
        "comment_count": food_info.comment_count,
        "stock": food_info.stock,
        "price": str(food_info.price),
        "main_image": UrlManager.buildImageUrl(food_info.main_image),
        "pics": [UrlManager.buildImageUrl(food_info.main_image)]
    }
    resp['data']['cart_number'] = cart_number

    return jsonify(resp)


# 评价列表信息
@route_api.route("/food/comment")
def commentList():
    resp = {
        'code': 200,
        'msg': "操作成功",
        'data': {}
    }
    req = request.values
    food_id = req['id'] if 'id' in req else 0

    query = MemberComments.query.filter(MemberComments.food_ids.ilike("%_{0}_%".format(food_id)))   # 对评价表的food_ids进行模糊查询
    # select * from member_comments where food_ids like "%_3_%"
    comments_list = query.order_by(MemberComments.created_time.desc()).limit(8).all()

    """
    commentList: [
                {
                    "score": "好评",
                    "date": "2017-10-11 10:20:00",
                    "content": "非常好吃，一直在他们加购买",
                    "user": {
                        "avatar_url": "/images/more/logo.png",
                        "nick": "angellee 🐰 🐒"
                    }
                }
            ]
    """
    data_list = []
    if comments_list:
        member_map = getDictFilterField(Member, Member.id, "id", selectFilterObject(comments_list, "member_id"))
        for item in comments_list:
            if item.member_id not in member_map:
                continue
            tmp_member_info = member_map[item.member_id]    # 用户信息
            tmp_data = {
                "score": item.score_desc,
                "data": item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                "content": item.content,
                "user": {
                    "avatar_url": tmp_member_info.avatar,
                    "nick": tmp_member_info.nickname
                }
            }
            data_list.append(tmp_data)

    resp['data']['list'] = data_list
    resp['data']['count'] = query.count()   # 评价总个数

    return jsonify(resp)
