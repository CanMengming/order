"""
    美食管理
"""
from flask import Blueprint, request, jsonify, redirect
from common.libs.Helper import ops_render, getDictFilterField
from common.libs.UrlManager import UrlManager
from common.libs.Helper import iPagination
from common.models.food.FoodCat import FoodCat
from common.models.food.Food import Food
from common.models.food.FoodStockChangeLog import FoodStockChangeLog
from common.libs.Helper import getCurrentTime
from common.libs.food.FoodService import FoodService
from application import db, app
from decimal import Decimal
from sqlalchemy import or_

route_food = Blueprint('food_page', __name__)


# 美餐管理列表
@route_food.route("/index", methods=['GET', 'POST'])
def index():
    resp_data = {}
    req = request.values
    query = Food.query

    # 获取搜索关键字(用于搜索)
    if 'mix_kw' in req:
        # 定义规则rule然后进行查询（美餐名、标签名）——混合查询
        rule = or_(Food.name.ilike("%{0}%".format(req['mix_kw'])), Food.tags.ilike("%{0}%".format(req['mix_kw'])))
        query = query.filter(rule)
        # 复杂查询

    # 获取美餐状态用于搜索查询
    if 'status' in req and int(req['status']) > -1:
        query = query.filter(Food.status == int(req['status']))

    # 获取美餐种类用于搜素
    if 'cat_id' in req and int(req['cat_id']) > 0:
        query = query.filter(Food.cat_id == int(req['cat_id']))

    """ 
            p值来自于pagenation.html中
            {% for idx in pages.range %}
                    {% if idx == pages.current %}
                        <li class="active"><a href="javascript:void(0);">{{ idx }}</a></li>
                    {% else %}
                        <li><a href="{{ pages.url }}&p={{idx}}">{{ idx }}</a></li>
                    {% endif %}
            {% endfor %}
            {% if pages.is_next == 1 %}
                 <li>
                    <a href="{{ pages.url }}&p={{ pages.total_pages }}" ><span>尾页</span></a>
                 </li>
            {%  endif %}
        """
    page = int(req['p']) if ('p' in req and req['p']) else 1

    page_params = {
        # query.count()获取总页数
        'total': query.count(),
        # 每页展示数据个数
        'page_size': app.config['PAGE_SIZE'],
        # 当前页数(前端页面传递)
        'page': page,
        # 想展示多少页(一般显示10页)
        'display': app.config['PAGE_DISPLAY'],
        # 希望每页url地址是什么？----整体路径--------------：/account/index?&p=2
        'url': request.full_path.replace("&p={}".format(page), "")
        # 将里面的p参数进行替换掉——页面url地址http://192.168.43.199:8999/account/index?&p=2
    }
    '''
                例如：选择第5页的时候，前面有5个和后面有5个
                # 计算半圆
                semi = int(math.ceil(display / 2))

                if page - semi > 0:
                    ret['from'] = page - semi
                else:
                    ret['from'] = 1

                if page + semi <= total_pages:
                    ret['end'] = page + semi
                else:
                    ret['end'] = total_pages
    '''

    # iPagination()封装的分页方法
    pages = iPagination(page_params)
    # 每页偏移量，例如：第一页展示1~15个数据，偏移0，第二页展示15~30个数据，偏移量为15
    offset = (page - 1) * app.config['PAGE_SIZE']
    limit = app.config['PAGE_SIZE'] * page
    # 例如：第3页，offset=(3-1)*15=30   limit=3*15=45

    # 根据uid查询所有管理员数据(返回列表)
    list = query.order_by(Food.id.asc()).all()[offset:limit]  # 注：2.desc()倒序排列  asc()顺序排列

    """
        def getDictFilterField(db_model, select_field, key_field, id_list):
            pass
        通过select_key即"id"字段查询出FoodCat所有在id_list中的id对应的FoodCat对象
        例如：getDictFilterField(FoodCat, "id", "id", [])根据id查询出所有FoodCat对象作为dict字典的value值，id作为key值
            返回值：{"1": FoodCat, "2": FoodCat, "3", FoodCat}
            如何获取对应的FoodCat的name？
            cat_mapping[item.cat_id].name
    """
    cat_mapping = getDictFilterField(FoodCat, "id", "id", [])

    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['search_con'] = req
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    resp_data['cat_mapping'] = cat_mapping
    resp_data['current'] = 'index'

    return ops_render("food/index.html", resp_data)


# 美食详情
@route_food.route("/info", methods=['GET', 'POST'])
def info():
    resp_data = {}

    req = request.args
    id = int(req.get("id"), 0)
    reback_url = UrlManager.buildUrl("/food/index")

    if id< 1:
        return redirect(reback_url)

    info = Food.query.filter_by(id=id).first()
    if not info:
        return redirect(reback_url)

    # 查询库存指定商品库存变更表
    stock_change_list = FoodStockChangeLog.query.filter(FoodStockChangeLog.food_id == id).order_by(FoodStockChangeLog.id.desc()).all()

    resp_data['info'] = info
    resp_data['stock_change_list'] = stock_change_list
    resp_data['current'] = 'index'

    return ops_render("food/info.html", resp_data)


# 编辑美食
@route_food.route("/set", methods=['GET', 'POST'])
def set():
    if request.method == 'GET':
        resp_data = {}

        # 获取前台是否传递id字段
        req = request.args
        id = int(req.get('id', 0))
        info = Food.query.filter_by(id=id).first()
        if info and info.status!= 1:
            return redirect(UrlManager.buildUrl("/food/index"))

        # 查询分类信息，用于添加美餐时选择对应的分类
        cat_list = FoodCat.query.all()
        resp_data['cat_list'] = cat_list
        resp_data['current'] = 'index'
        resp_data['info'] = info

        return ops_render("food/set.html", resp_data)

    resp = {
        'code': 200,
        'msg': '操作成功~~',
        'data': ''
    }
    req = request.values
    id = int(req['id']) if 'id' in req and req['id'] else 0
    cat_id = int(req['cat_id']) if 'cat_id' in req else 0
    name = req['name'] if 'name' in req else ''
    price = req['price'] if 'price' in req else ''
    main_image = req['main_image'] if 'main_image' in req else ''
    summary = req['summary'] if 'summary' in req else ''
    stock = int(req['stock']) if 'stock' in req else 0
    tags = req['tags'] if 'tags' in req else ''

    if cat_id < 1:
        resp['code'] = -1
        resp['msg'] = "请选择分类~~"
        return jsonify(resp)

    if name is None or len(name) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的名称~~"
        return jsonify(resp)

    if not price or len( price ) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的售卖价格~~"
        return jsonify(resp)

    # 将价格转化为两位小数
    price = Decimal(price).quantize(Decimal('0.00'))
    if price <= 0:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的售卖价格~~"
        return jsonify(resp)

    if main_image is None or len(main_image) < 3:
        resp['code'] = -1
        resp['msg'] = "请上传封面图~~"
        return jsonify(resp)

    if summary is None or len(summary) < 5:
        resp['code'] = -1
        resp['msg'] = "请输入图书描述，并不能少于5个字符~~"
        return jsonify(resp)

    if stock < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的库存量~~"
        return jsonify(resp)

    if tags is None or len(tags) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入标签，便于搜索~~"
        return jsonify(resp)

    food_info = Food.query.filter_by(id=id).first()
    before_stock = 0
    if food_info:
        # 数据库存在该id美餐
        model_food = food_info
        before_stock = model_food.stock
    else:
        # 数据库中不存在该id美餐(则创建Food对象)
        model_food = Food()
        model_food.status = 1
        model_food.created_time = getCurrentTime()
        
    model_food.cat_id = cat_id
    model_food.price = price
    model_food.name = name
    model_food.main_image = main_image
    model_food.summary = summary
    model_food.stock = stock
    model_food.tags = tags
    model_food.updated_time = getCurrentTime()

    db.session.add(model_food)
    ret = db.session.commit()

    # 库存变更
    FoodService.setStockChangedLog(model_food.id, int(stock) - int(before_stock), "后台修改库存")

    return jsonify(resp)


# 分类列表
@route_food.route("/cat", methods=['GET', 'POST'])
def cat():
    resp_data = {}

    req = request.values
    query = FoodCat.query

    if 'status' in req and int(req['status']) > -1:
        query = query.filter(FoodCat.status == int(req['status']))

    list = query.order_by(FoodCat.id.asc()).all()

    resp_data['list'] = list
    resp_data['current'] = 'cat'
    resp_data['search_data'] = req
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']

    return ops_render("food/cat.html", resp_data)


# 美餐分类编辑
@route_food.route("/cat-set", methods=['GET', 'POST'])
def catSet():

    if request.method == 'GET':
        resp_data = {}

        req = request.args
        id = int(req.get('id', 0))

        info = None
        if id:
            info = FoodCat.query.filter_by(id=id).first()

        resp_data['info'] = info
        resp_data['current'] = 'cat'

        return ops_render("food/cat_set.html", resp_data)

    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }

    req = request.values
    id = req['id'] if 'id' in req else 0
    name = req['name'] if 'name' in req else None
    weight = int(req['weight']) if ('weight' in req and int(req['weight']) > 0) else 1

    if name is None or len(name) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的分类名称"

        return jsonify(resp)

    food_cat_info = FoodCat.query.filter_by(id=id).first()
    if food_cat_info:
        # 编辑菜品类操作
        model_food_cat = food_cat_info
    else:
        # 添加菜品类操作
        model_food_cat = FoodCat()
        model_food_cat.created_time = getCurrentTime()

    model_food_cat.name = name
    model_food_cat.weight = weight
    model_food_cat.updated_time = getCurrentTime()

    db.session.add(model_food_cat)
    db.session.commit()

    return jsonify(resp)


# 删除、恢复美食分类操作
@route_food.route("/cat-ops", methods=['GET', 'POST'])
def catOps():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    req = request.values

    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else None

    if not id:
        resp['code'] = -1
        resp['msg'] = "请选择需要操作的账户~~"

        return jsonify(resp)

    if act not in ['remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = "操作有误请重试~~"

        return jsonify(resp)

    foodCat_info = FoodCat.query.filter_by(id=id).first()
    if not foodCat_info:
        resp['code'] = -1
        resp['msg'] = "不存在该美餐分类"

        return jsonify(resp)

    if act == 'remove':
        foodCat_info.status = 0
    elif act == 'recover':
        foodCat_info.status = 1

    foodCat_info.updated_time = getCurrentTime()

    db.session.add(foodCat_info)
    db.session.commit()

    return jsonify(resp)


# 删除、恢复美食操作
@route_food.route("/ops", methods=['GET', 'POST'])
def ops():
    resp = {
        'code': 200,
        'msg': '操作成功',
        'data': {}
    }
    req = request.values

    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else None

    if not id:
        resp['code'] = -1
        resp['msg'] = "请选择需要操作的账户~~"

        return jsonify(resp)

    if act not in ['remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = "操作有误请重试~~"

        return jsonify(resp)

    food_info = Food.query.filter_by(id=id).first()
    if not food_info:
        resp['code'] = -1
        resp['msg'] = "不存在该美餐"

        return jsonify(resp)

    if act == 'remove':
        food_info.status = 0
    elif act == 'recover':
        food_info.status = 1

    food_info.updated_time = getCurrentTime()

    db.session.add(food_info)
    db.session.commit()

    return jsonify(resp)
