//index.js
//获取应用实例
var app = getApp();
var WxParse = require('../../wxParse/wxParse.js');
var utils = require('../../utils/util.js');


Page({
    data: {
        autoplay: true,
        interval: 3000,
        duration: 1000,
        swiperCurrent: 0,
        hideShopPopup: true,
        buyNumber: 1,
        buyNumMin: 1,
        buyNumMax:1,
        canSubmit: false, //  选中时候是否允许加入购物车
        shopCarInfo: {},
        shopType: "addShopCar",//购物类型，加入购物车或立即购买，默认为加入购物车,
        id: 0,
        shopCarNum: 4,
        commentCount:2
    },
    onLoad: function (e) {
        var that = this;

        that.setData({
            id: e.id    // 给id赋值方便传递给后台进行数据查询
        });

        that.setData({
            "info": {
                // 美食详情信息
            },
            buyNumMax: 2,
            commentList: [
                // 评价信息
            ]
        });

    },
    onShow: function(){
        // 加载时调用getInfo()获取美餐详情
        this.getInfo();
        this.getComments();
    },
    goShopCar: function () {
        wx.reLaunch({
            url: "/pages/cart/index"
        });
    },
    toAddShopCar: function () {
        this.setData({
            shopType: "addShopCar"
        });
        this.bindGuiGeTap();
    },
    tobuy: function () {
        this.setData({
            shopType: "tobuy"
        });
        this.bindGuiGeTap();
    },

    // 美餐添加至购物车
    addShopCar: function () {
        var that = this;
        var data = {
            "id": this.data.info.id,
            "number": this.data.buyNumber
        }
        wx.request({
            url: app.buildUrl("/cart/set"),
            header: app.getRequestHeader(),
            method: 'POST',
            data: data,
            success: function(res) {
                var resp = res.data;
                app.alert({"content": resp.msg});

                that.setData({
                    // hideShopPopup添加完至购物车后隐藏购物车
                    hideShopPopup: true
                });

                // 重新请求一遍getInfo()一遍刷新购物车显示的个数
                that.getInfo();
            }
        });
    },

    // 商品详情页面美餐立即购买
    buyNow: function () {
        var data =  {
            goods: [{
                "id": this.data.info.id,
                "price": this.data.info.price,
                "number": this.data.buyNumber
            }]
        };

        this.setData({
            hideShopPopup: true
        });
        wx.navigateTo({
            url: "/pages/order/index?data=" + JSON.stringify(data)
        });
    },
    /**
     * 规格选择弹出框
     */
    bindGuiGeTap: function () {
        this.setData({
            hideShopPopup: false
        })
    },
    /**
     * 规格选择弹出框隐藏
     */
    closePopupTap: function () {
        this.setData({
            hideShopPopup: true
        })
    },
    numJianTap: function () {
        if( this.data.buyNumber <= this.data.buyNumMin){
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum--;
        this.setData({
            buyNumber: currentNum
        });
    },
    numJiaTap: function () {
        if( this.data.buyNumber >= this.data.buyNumMax ){
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum++;
        this.setData({
            buyNumber: currentNum
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },

    // 美餐详情信息
    getInfo: function () {
        /**
         * 为什么要定义var that = this？
         * 1.js中有作用域，vat that = this，表示当前this作用域为当前这个对象赋值给that
         * 2.而在网络请求时，作用域就会发生改变
         * 3.所以需要var that = this;保存当前作用域
         * @type {getInfo}
         */
        var that = this;
        wx.request({
            url: app.buildUrl("/food/info"),
            header: app.getRequestHeader(),
            data: {
                id: that.data.id
            },
            success: function(res) {
                var resp = res.data;
                if (resp.code!= 200){
                    app.alert({"content": resp.msg});
                    return;
                }

                // 此时为什么使用that而不使用this，因为通过微信传输此时的作用域已经改变了
                that.setData({
                    info: resp.data.info,
                    buyNumMax: resp.data.info.stock,
                    shopCarNum: resp.data.cart_number
                });

                // 评论summary进行渲染
                WxParse.wxParse('article', 'html', that.data.info.summary, that, 5);
            }
        });
    },

    // 评价列表
    getComments: function(){
        var that = this;
        wx.request({
            url: app.buildUrl("/food/comment"),
            header: app.getRequestHeader(),
            data: {
                id: that.data.id
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }

                that.setData({
                    commentCount: resp.data.count,
                    commentList: resp.data.list
                })
            }

        });
    },

    // 转发分享功能
    onShareAppMessage: function () {
        var that = this;

        return {
            title: that.data.info.name,
            path: '/page/food/info?id=' + that.data.info.id,

            success: function (res) {
                // 转发成功（将请求转发至后台）
                wx.request({
                    url: app.buildUrl("/member/share"),
                    header: app.getRequestHeader(),
                    method: 'POST',
                    data: {
                        // 当前界面的url地址（获取带参数的URL地址）
                        url: utils.getCurrentPageUrlWithArgs()
                    },
                    success: function(res) {

                    }

                });
            },
            fail: function (res) {
                // 转发失败
            }
        }
    }
});
