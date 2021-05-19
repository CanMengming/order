"""
    后台管理主界面
"""
import datetime
from flask import Blueprint
from common.models.stat.StatDailySite import StatDailySite
from common.libs.Helper import ops_render, getFormatDate

route_index = Blueprint('index_page', __name__)


# 蓝牙方式注册路由
@route_index.route("/")
def index():
    # 获取当前用户对象
    # current_user = g.current_user

    resp_data = {
        'data': {
            'finance': {
                'today': 0,
                'month': 0
            },
            'member': {
                'today_new': 0,
                'month_new': 0,
                'total': 0
            },
            'order': {
                'today': 0,
                'month': 0
            },
            'share': {
                'today': 0,
                'month': 0
            }
        }
    }

    now = datetime.datetime.now()
    date_before_30day = now + datetime.timedelta(days=-30)
    date_from = getFormatDate(date=date_before_30day, format="%Y-%m-%d")
    date_to = getFormatDate(date=now, format="%Y-%m-%d")

    list = StatDailySite.query.filter(StatDailySite.date <= date_to, StatDailySite.date >= date_from)\
        .order_by(StatDailySite.id.asc()).all()

    data = resp_data['data']
    if list:
        for item in list:
            data['finance']['month'] += item.total_pay_money            # 每月财务
            data['member']['month_new'] += item.total_new_member_count  # 最近30天新增会员数量
            data['member']['total'] = item.total_member_count           # 每月总会员数量
            data['order']['month'] += item.total_order_count            # 每月订单数量
            data['share']['month'] += item.total_shared_count           # 每月分享数量

            if getFormatDate(date=item.date, format="%Y-%m-%d") == date_to:
                # 数据时间 == 当天时间(显示当天数据)
                data['finance']['today'] = item.total_pay_money
                data['member']['today_new'] = item.total_new_member_count
                data['order']['today'] = item.total_order_count
                data['share']['today'] = item.total_shared_count

    return ops_render("index/index.html", resp_data)
