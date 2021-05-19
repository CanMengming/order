"""
实现每日统计
python manager.py runjob -m stat/daily -a member | food | site(动作) -p 2021-05-15(时间)
"""
import random, datetime
from application import app, db
from sqlalchemy import func
from common.models.member.Member import Member
from common.models.food.WxShareHistory import WxShareHistory
from common.models.food.FoodSaleChangeLog import FoodSaleChangeLog
from common.models.stat.StatDailyMember import StatDailyMember
from common.models.stat.StatDailyFood import StatDailyFood
from common.models.stat.StatDailySite import StatDailySite
from common.models.pay.PayOrder import PayOrder
from common.libs.Helper import getFormatDate, getCurrentTime


class JobTask():
    def __init__(self):
        pass

    def run(self, params):
        act = params['act'] if 'act' in params else ''
        date = params['param'] if params['param'] and len(params['param']) > 0 else getFormatDate(format="%Y-%m-%d")
        # 注:params为元组

        app.logger.info(params)     # INFO in daily: {'name': 'stat/daily', 'act': None, 'param': ''}
        app.logger.info(act)
        app.logger.info(date)

        date_from = "00:00:00"
        date_to = "23:59:59"
        func_params = {
            'act': act,
            'date': date,
            'date_from': date_from,
            'date_to': date_to
        }

        if not act:
            # 运行时没有指定动作
            return

        if act == "member":
            # 跑会员统计
            self.statMember(func_params)
        elif act == "food":
            # 跑food美食统计
            self.statFood(func_params)
        elif act == "site":
            # 全站统计
            self.statSite(func_params)
        elif act == "test":
            self.test()

    # 会员统计——当日总分享次数、付款总金额
    def statMember(self, params):
        act = params['act']
        date = params['date']
        date_from = params['date_from']
        date_to = params['date_to']

        app.logger.info("============================================================")
        app.logger.info("act:{0},from:{1},to:{2}".format(act, date_from, date_to))

        member_list = Member.query.all()
        '''
        注：如果用户量比较大，有100万、200万条用户数据？
        1.如果通过query.all()一次性将所有结果集取出来则速度较慢，程序跑的时间比较长
        2.此时可以多启动几个job，例如:通过命令行启动10个job，则对Member表中数据进行求模，除以10
        '''
        if not member_list:
            app.logger.info("No member list")
            return

        for member_info in member_list:
            tmp_stat_member = StatDailyMember.query.filter_by(date=date, member_id=member_info.id).first()
            if tmp_stat_member:
                # 当前StatDailyMember数据存在
                tmp_model_stat_member = tmp_stat_member
            else:
                tmp_model_stat_member = StatDailyMember()
                tmp_model_stat_member.member_id = member_info.id
                tmp_model_stat_member.date = date
                tmp_model_stat_member.created_time = getCurrentTime()

            tmp_stat_pay = db.session.query(func.sum(PayOrder.total_price).label("total_pay_money"))\
                .filter(PayOrder.member_id == member_info.id, PayOrder.pay_status == 1)\
                .filter(PayOrder.created_time >= date_from, PayOrder.created_time <= date_to).first()
            # 会员当日总的支付金额

            tmp_stat_share_count = WxShareHistory.query.filter(WxShareHistory.member_id == member_info.id)\
                .filter(WxShareHistory.created_time >= date_from, WxShareHistory.created_time <= date_to).count()
            # 当日会员分享数量

            tmp_model_stat_member.total_pay_money = tmp_stat_pay[0] if tmp_stat_pay[0] else 0.00
            tmp_model_stat_member.total_shared_count = tmp_stat_share_count

            '''
            为了测试效果模拟数据
            '''
            # tmp_model_stat_member.total_shared_count = random.randint(1, 10)
            # tmp_model_stat_member.total_pay_money = random.randint(500, 800)    # 随机产生数据

            tmp_model_stat_member.updated_time = getCurrentTime()

            db.session.add(tmp_model_stat_member)
            db.session.commit()

        return True

    # Food售卖统计
    def statFood(self, params):
        act = params['act']
        date = params['date']
        date_from = params['date_from']
        date_to = params['date_to']

        app.logger.info("============================================================")
        app.logger.info("act:{0},from:{1},to:{2}".format(act, date_from, date_to))

        stat_food_list = db.session.query(FoodSaleChangeLog.food_id
                                          , func.sum(FoodSaleChangeLog.quantity).label("total_count")
                                          , func.sum(FoodSaleChangeLog.price).label("total_pay_money"))\
            .filter(FoodSaleChangeLog.created_time >= date_from, FoodSaleChangeLog.created_time <= date_to)\
            .group_by(FoodSaleChangeLog.food_id).all()      # group_by()——聚合操作

        if not stat_food_list:
            app.logger.info("No data")
            return

        for item in stat_food_list:
            tmp_food_id = item[0]
            tmp_stat_food = StatDailyFood.query.filter_by(date=date, food_id=tmp_food_id).first()
            if tmp_stat_food:
                tmp_model_stat_food = tmp_stat_food
            else:
                tmp_model_stat_food = StatDailyFood()
                tmp_model_stat_food.food_id = tmp_food_id
                tmp_model_stat_food.date = date
                tmp_model_stat_food.created_time = getCurrentTime()

            tmp_model_stat_food.total_count = item[1]
            tmp_model_stat_food.total_pay_money = item[2]

            # 模拟随机测试数据
            # tmp_model_stat_food.total_count = random.randint(50, 100)
            # tmp_model_stat_food.total_pay_money = random.randint(400, 600)

            tmp_model_stat_food.updated_time = getCurrentTime()

            db.session.add(tmp_model_stat_food)
            db.session.commit()

        return True

    # Site全站统计
    def statSite(self, params):
        act = params['act']
        date = params['date']
        date_from = params['date_from']
        date_to = params['date_to']

        app.logger.info("============================================================")
        app.logger.info("act:{0},from:{1},to:{2}".format(act, date_from, date_to))

        # 总支付金额
        stat_pay = db.session.query(func.sum(PayOrder.total_price).label("total_pay_price"))\
            .filter(PayOrder.status == 1)\
            .filter(PayOrder.created_time >= date_from, PayOrder.created_time <= date_to).first()

        stat_member_count = Member.query.count()
        # 会员总数
        stat_new_member_count = Member.query.filter(Member.created_time <= date_from, Member.created_time <= date_to)\
            .count()
        # 今日注册会员数
        stat_order_count = PayOrder.query.filter_by(status=1)\
            .filter(PayOrder.created_time <= date_from, PayOrder.created_time <= date_to).count()
        # 每日订单总数
        share_count = WxShareHistory.query.filter(WxShareHistory.created_time >= date_from
                                                  , WxShareHistory.created_time <= date_to).count()
        # 每日分享订单总数

        tmp_stat_site = StatDailySite.query.filter_by(date=date).first()
        if tmp_stat_site:
            tmp_model_stat_site = tmp_stat_site
        else:
            tmp_model_stat_site = StatDailySite()
            tmp_model_stat_site.date = date
            tmp_model_stat_site.created_time = getCurrentTime()

        tmp_model_stat_site.total_pay_money = stat_pay[0] if stat_pay[0] else 0.00                     # 总付款
        tmp_model_stat_site.total_member_count = stat_member_count          # 总会员数
        tmp_model_stat_site.total_new_member_count = stat_new_member_count  # 今日新增会员数
        tmp_model_stat_site.total_order_count = stat_order_count            # 总订单数
        tmp_model_stat_site.total_shared_count = share_count                # 总分享数
        tmp_model_stat_site.updated_time = getCurrentTime()

        db.session.add(tmp_model_stat_site)
        db.session.commit()

        return True

    # 计算最近30天的全站数据
    def test(self):
        now = datetime.datetime.now()
        for i in reversed(range(1, 30)):
            date_before = now + datetime.timedelta(days=-i)
            date = getFormatDate(date=date_before, format="%Y-%m-%d")
            tmp_params = {
                'act': 'test',
                'date': date,
                'date_from': date + " 00:00:00",
                'date_to': date + " 23:59:59"
            }

            self.statMember(tmp_params)
            self.statFood(tmp_params)
            self.statSite(tmp_params)
