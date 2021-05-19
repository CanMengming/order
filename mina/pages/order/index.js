//获取应用实例
var app = getApp();

Page({
    data: {
        goods_list: [],
        default_address: null,
        yun_price: "0.00",
        pay_price: "0.00",
        total_price: "0.00",
        params: null,
        note: '',
        express_address_id: 0
    },
    onShow: function () {
        var that = this;
        this.getOrderInfo();
    },
    onLoad: function (e) {
        var that = this;
        this.setData({
            params: JSON.parse(e.data)
        });
    },
    // 订单提交
    createOrder: function (e) {
        wx.showLoading();
        var that = this;
        /**
             * 购物车页面传递的数据type，goods
             * var data = {
                type: "cart",
                goods: []
            };

            var list = this.data.list;
            for (var i = 0; i < list.length; i++) {
                if (!list[i].active) {
                    // 如果商品没有被选中则不添加至goods元组内
                    continue;
                }
                data['goods'].push({
                    "id": list[i].food_id,
                    "price": list[i].price,
                    "number": list[i].number
                });
            }
             * @type {{goods: string, type: *}}
         */
        var data = {
            type: this.data.params.type,
            goods: JSON.stringify(this.data.params.goods),
            note: this.data.note,
            express_address_id: that.data.express_address_id
        };

        wx.request({
            url: app.buildUrl("/order/create"),
            header: app.getRequestHeader(),
            data: data,
            method: "POST",
            success: function(res) {
                wx.hideLoading();
                var resp = res.data;
                if (resp.code!= 200){
                    app.alert({'content': resp.msg});
                    return;
                }

                wx.navigateTo({
                    url: "/pages/my/order_list"
                });
            }
        });
    },
    addressSet: function () {
        wx.navigateTo({
            url: "/pages/my/addressSet"
        });
    },
    selectAddress: function () {
        wx.navigateTo({
            url: "/pages/my/addressList"
        });
    },
    // 获取请求订单信息展示
    getOrderInfo: function () {
        var that = this;
        /**
         * 购物车页面传递的数据type，goods
         * var data = {
            type: "cart",
            goods: []
        };

        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            if (!list[i].active) {
                // 如果商品没有被选中则不添加至goods元组内
                continue;
            }
            data['goods'].push({
                "id": list[i].food_id,
                "price": list[i].price,
                "number": list[i].number
            });
        }
         * @type {{goods: string, type: *}}
         */
        var data = {
            type: this.data.params.type,
            goods: JSON.stringify(this.data.params.goods)
        };
        wx.request({
            url: app.buildUrl("/order/info"),
            header: app.getRequestHeader(),
            data: data,
            method: "POST",
            success: function(res) {
                var resp = res.data;
                if (resp.code != 200){
                    app.alert({"content": resp.msg});
                    return;
                }

                that.setData({
                    /**
                     *  data: {
                                goods_list: [
                                    {
                                        id:22,
                                        name: "小鸡炖蘑菇",
                                        price: "85.00",
                                        pic_url: "/images/food.jpg",
                                        number: 1,
                                    }
                                ],
                                default_address: {
                                    name: "明华俊",
                                    mobile: "12345678901",
                                    detail: "江苏省常州市江苏理工学院",
                                },
                                yun_price: "1.00",
                                pay_price: "85.00",
                                total_price: "86.00",
                                params: null
                            },
                     */
                    goods_list: resp.data.food_list,
                    default_address: resp.data.default_address,
                    yun_price: resp.data.yun_price,
                    pay_price: resp.data.pay_price,
                    total_price: resp.data.total_price
                });

                if (that.data.default_address) {
                    that.setData({
                       express_address_id: that.data.default_address.id
                    });
                }
            }
        });
    },
    remarkInput:function( e ){
        this.setData({
            note: e.detail.value
        });
    }

});
