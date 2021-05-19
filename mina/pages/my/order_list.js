var app = getApp();
Page({
    data: {
        statusType: ["待付款", "待发货", "待确认", "待评价", "已完成","已关闭"],
        status:[ "-8","-7","-6","-5","1","0" ],
        currentType: 0,
        tabClass: ["", "", "", "", "", ""]
    },
    statusTap: function (e) {
        var curType = e.currentTarget.dataset.index;
        this.data.currentType = curType;
        this.setData({
            currentType: curType
        });
        this.getPayOrder();
    },
    orderDetail: function (e) {
        // 该组件的id即为order_sn(订单号)
        wx.navigateTo({
            url: "/pages/my/order_info?order_sn="+e.currentTarget.dataset.id
        })
    },
    // 生命周期函数--监听页面加载
    onLoad: function (options) {


    },
    // 生命周期函数--监听页面初次渲染完
    onReady: function () {

    },
    onShow: function () {
        var that = this;
         /**
        that.setData({
            order_list: [
                {
					status: -8,
                    status_desc: "待支付",
                    date: "2021-03-01 22:30:23",
                    order_number: "20210301223023001",
                    note: "记得周六发货",
                    total_price: "85.00",
                    goods_list: [
                        {
                            pic_url: "/images/food.jpg"
                        },
                        {
                            pic_url: "/images/food.jpg"
                        }
                    ]
                }
            ]
        });
          */
        this.getPayOrder();
    },
    // 生命周期函数--监听页面隐藏

    onHide: function () {

    },
    // 生命周期函数--监听页面卸载
    onUnload: function () {

    },
    // 页面相关事件处理函数--监听用户下拉动作
    onPullDownRefresh: function () {

    },
    // 页面上拉触底事件的处理函数
    onReachBottom: function () {

    },
    // 获取订单信息进行列表展示
    getPayOrder: function () {
        var that = this;
        wx.request({
            url: app.buildUrl("/my/order"),
            header: app.getRequestHeader(),
            /**
             *  data: {
                statusType: ["待付款", "待发货", "待收货", "待评价", "已完成","已关闭"],
                status:[ "-8","-7","-6","-5","1","0" ],
                currentType: 0,——当前选中的状态数值
                tabClass: ["", "", "", "", "", ""]
                }
             */
            data: {
              status: that.data.status[that.data.currentType]
            },
            success: function(res) {
                var resp = res.data;
                if(resp.code!= 200){
                    app.alert({"content": resp.msg});
                    return;
                }

                that.setData({
                    order_list: resp.data.pay_order_list
                });
            }
        });
    },
    // 去支付
    toPay: function (e) {
        var that = this;
        // 注：e.currentTarget.dataset.id为前台"马上付款"按钮的id值(即item.order_sn)
        wx.request({
            url: app.buildUrl("/order/pay"),
            header: app.getRequestHeader(),
            data: {
                order_sn: e.currentTarget.dataset.id
            },
            method: "POST",
            success: function(res) {
                var resp = res.data;
                if(resp.code!= 200){
                    app.alert({"content": resp.msg});
                    return;
                }
                var pay_info = resp.data.pay_info;
                wx.requestPayment({
                    'timeStamp': pay_info.timeStamp,
                    'nonceStr': pay_info.nonceStr,
                    'package': pay_info.package,
                    'signType': 'MD5',
                    'paySign': pay_info.paySign,
                    'success': function (res) {
                    },
                    'fail': function (res) {
                    }
                });
            }
        });
    },
    // 取消订单
    orderCancel: function (e) {
        this.orderOps(e.currentTarget.dataset.id, "cancel", "确认取消订单吗？");
    },
    // 确认收货
    orderConfirm: function (e) {
        this.orderOps(e.currentTarget.dataset.id, "confirm", "确认收到货吗？");
    },
    // 评价
    orderComment: function (e) {
        // 使用微信小程序自带的方法实现页面跳转
        wx.navigateTo({
            url: "/pages/my/comment?order_sn=" + e.currentTarget.dataset.id
        });
    },
    // 动作统一处理
    orderOps: function (order_sn, act, msg) {
        // 注：order_sn—订单号、act—动作、msg—信息提示
        var that = this;
        var params = {
            "content": msg,
            "cb_confirm": function () {
                wx.request({
                    url: app.buildUrl("/order/ops"),
                    header: app.getRequestHeader(),
                    data: {
                        order_sn: order_sn,
                        act: act
                    },
                    method: "POST",
                    success: function (res) {
                        var resp = res.data;
                        app.alert({"content": resp.msg});

                        if ( resp.code == 200) {
                            that.getPayOrder();     // 列表重新获取一遍订单列表
                        }
                    }
                });
            }
        }

        // 提示后端返回的信息
        app.tip(params)
    }
})
