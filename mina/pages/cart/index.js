//index.js
var app = getApp();
Page({
    data: {},
    onLoad: function () {
    },
    onShow: function(){
        this.getCartList();
    },
    //每项前面的选中框
    selectTap: function (e) {
        var index = e.currentTarget.dataset.index;
        var list = this.data.list;
        if (index !== "" && index != null) {
            list[ parseInt(index) ].active = !list[ parseInt(index) ].active;
            this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
        }
    },
    //计算是否全选了
    allSelect: function () {
        var list = this.data.list;
        var allSelect = false;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            if (curItem.active) {
                allSelect = true;
            } else {
                allSelect = false;
                break;
            }
        }
        return allSelect;
    },
    //计算是否都没有选
    noSelect: function () {
        var list = this.data.list;
        var noSelect = 0;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            if (!curItem.active) {
                noSelect++;
            }
        }
        if (noSelect == list.length) {
            return true;
        } else {
            return false;
        }
    },
    //全选和全部选按钮
    bindAllSelect: function () {
        var currentAllSelect = this.data.allSelect;
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            list[i].active = !currentAllSelect;
        }
        this.setPageData(this.getSaveHide(), this.totalPrice(), !currentAllSelect, this.noSelect(), list);
    },
    // 购物车加数量
    jiaBtnTap: function (e) {
        var that = this;
        var index = e.currentTarget.dataset.index;
        var list = that.data.list;
        list[parseInt(index)].number++;
        that.setPageData(that.getSaveHide(), that.totalPrice(), that.allSelect(), that.noSelect(), list);
        this.setCart(list[parseInt(index)].food_id, list[parseInt(index)].number);
    },
    // 购物车减数量
    jianBtnTap: function (e) {
        var index = e.currentTarget.dataset.index;
        var list = this.data.list;
        if (list[parseInt(index)].number > 1) {
            list[parseInt(index)].number--;
            this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
            this.setCart(list[parseInt(index)].food_id, list[parseInt(index)].number)
        }
    },
    //编辑默认全不选
    editTap: function () {
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            curItem.active = false;
        }
        this.setPageData(!this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
    },
    //选中完成默认全选
    saveTap: function () {
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            curItem.active = true;
        }
        this.setPageData(!this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
    },
    getSaveHide: function () {
        return this.data.saveHidden;
    },
    // 购物车总价格计算
    totalPrice: function () {
        var list = this.data.list;
        var totalPrice = 0.00;
        for (var i = 0; i < list.length; i++) {
            if ( !list[i].active) {
                continue;
            }
            // 计算购物车内所有商品总价格（将每个美餐(价格*数量)的价格相加）
            totalPrice = totalPrice + parseFloat( list[i].price * list[i].number );
        }
        return totalPrice;
    },
    setPageData: function (saveHidden, total, allSelect, noSelect, list) {
        this.setData({
            list: list,
            saveHidden: saveHidden,
            totalPrice: total,
            allSelect: allSelect,
            noSelect: noSelect,
        });
    },
    //去结算
    toPayOrder: function () {
        var data = {
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
        wx.navigateTo({
            // 将data数据解析成JSON格式进行前后端传递
            url: "/pages/order/index?data=" + JSON.stringify(data)
        });
    },
    //如果没有显示去光光按钮事件
    toIndexPage: function () {
        wx.switchTab({
            url: "/pages/food/index"
        });
    },
    //选中删除的数据
    deleteSelected: function () {
        var list = this.data.list;
        var cart_ids = [];
        var goods = [];
        list = list.filter(function ( item ) {
            if( item.active ){
                // 当前商品被选中添加至goods内，然后传递至后台进行统一处理
                goods.push({
                    "id": item.food_id
                });
            }
            return !item.active;
        });
        this.setPageData( this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
        //发送请求到后台删除数据

        wx.request({
            url: app.buildUrl("/cart/del"),
            header: app.getRequestHeader(),
            method: 'POST',
            data: {
                goods: JSON.stringify(goods)
            },
            success: function(res) {

            }
        });
    },
    //获取购物车列表
    getCartList: function () {
        var that = this;
        /**
        this.setData({
            list: [
                {
                    "id": 1080,
					"food_id":"5",
                    "pic_url": "/images/food.jpg",
                    "name": "小鸡炖蘑菇-1",
                    "price": "85.00",
                    "active": true,
                    "number": 1
                },
                {
                    "id": 1081,
					"food_id":"6",
                    "pic_url": "/images/food.jpg",
                    "name": "小鸡炖蘑菇-2",
                    "price": "85.00",
                    "active": true,
                    "number": 1
                }
            ],
            saveHidden: true,
            totalPrice: "85.00",
            allSelect: true,
            noSelect: false,
        });
         */

        wx.request({
            url: app.buildUrl("/cart/index"),
            header: app.getRequestHeader(),
            success: function(res) {
                var resp = res.data;
                if(resp.code!= 200){
                    app.alert({"content": resp.msg});
                    return;
                }

                that.setData({
                    list: resp.data.list,
                    saveHidden: true,
                    totalPrice: 0.00,
                    allSelect: true,
                    noSelect: false
                });
                that.setPageData( that.getSaveHide(), that.totalPrice(), that.allSelect(), that.noSelect(), that.data.list);

            }
        });
    },
    //购物车内添加、减美餐操作
    setCart: function (food_id, number) {
        var that = this;
        var data = {
            "id": food_id,
            "number": number
        };
        wx.request({
            url: app.buildUrl("/cart/set"),
            header: app.getRequestHeader(),
            method: 'POST',
            data: data,
            success: function(res) {
                var resp = res.data;

            }
        });
    }

});
