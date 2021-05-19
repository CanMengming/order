"""
    统一渲染方法
"""
from flask import g, render_template
import time, datetime


def ops_render(template, context={}):
    # 传入两个参数 template--上下文模板文件，context--上下文变量

    if 'current_user' in g:
        context['current_user'] = g.current_user

    return render_template(template, **context)


# 自定义分页类
def iPagination(params):
    import math

    ret = {
        # 是否有上一页
        "is_prev": 1,
        # 是否有下一页
        "is_next": 1,
        # 从多少页到多少页
        "from": 0,
        "end": 0,
        # 当前页
        "current": 0,
        # 总共多少页
        "total_pages": 0,
        # 每页大小
        "page_size": 0,
        # 总共的记录数
        "total": 0,
        # url地址
        "url": params['url']
    }

    total = int(params['total'])
    page_size = int(params['page_size'])
    page = int(params['page'])
    display = int(params['display'])
    total_pages = int(math.ceil(total / page_size))
    total_pages = total_pages if total_pages > 0 else 1
    if page <= 1:
        ret['is_prev'] = 0

    if page >= total_pages:
        ret['is_next'] = 0

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

    ret['current'] = page
    ret['total_pages'] = total_pages
    ret['page_size'] = page_size
    ret['total'] = total
    ret['range'] = range(ret['from'], ret['end'] + 1)
    return ret


# 获取当前时间
def getCurrentTime(format="%Y-%m-%d %H:%M:%S"):
    # 获得当前时间时间戳
    now = int(time.time())
    # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime(format, timeArray)

    return otherStyleTime


# 根据某个字段获取一个dict
def getDictFilterField(db_model, select_field, key_field, id_list):
    """
    将某一个结果集按照某个字段构造成一个数组dict
    select_field——希望查询哪个字段
    key_field——希望作为字典dict的key字段
    id_list——希望这个字段等于哪些词
    """
    ret = {}
    query = db_model.query
    if id_list and len(id_list) > 0:
        query = query.filter(select_field.in_(id_list))

    list = query.all()
    if not list:
        return ret

    for item in list:
        if not hasattr(item, key_field):
            break
        """
            >>>class A(object):
            ...     bar = 1
            ... 
            >>> a = A()
            >>> getattr(a, 'bar')        # 获取属性 bar 值
            1
        """
        ret[getattr(item, key_field)] = item

    return ret


# 从对象列表取出我们所需要的字段数据
def selectFilterObject(obj, field):
    ret = []
    for item in obj:
        if not hasattr(item, field):
            # item不在field字段内，跳出当前循环
            break

        """
            >>>class A(object):
            ...     bar = 1
            ... 
            >>> a = A()
            >>> getattr(a, 'bar')        # 获取属性 bar 值
            1
        """
        if getattr(item, field) in ret:
            # 结果集ret中已经存在item

            # 获取MemberCart对象的field（例如：id）指定属性数据值
            continue

        ret.append(getattr(item, field))

    return ret


#
def getDictListFilterField(db_model, select_filed, key_field, id_list):
    ret = {}
    query = db_model.query
    if id_list and len(id_list) > 0:
        query = query.filter(select_filed.in_(id_list))

    list = query.all()
    if not list:
        return ret
    for item in list:
        if not hasattr(item, key_field):
            break
        if getattr(item, key_field) not in ret:
            ret[getattr(item, key_field)] = []

        ret[getattr(item, key_field)].append(item)

    return ret


# 获取格式化的当天时间
def getFormatDate(date=None, format="%Y-%m-%d %H:%M:%S"):
    if date is None:
        date = datetime.datetime.now()

    return date.strftime(format)
