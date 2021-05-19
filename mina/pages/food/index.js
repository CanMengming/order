//index.js
//获取应用实例
var app = getApp();
Page({
    data: {
        indicatorDots: true,
        autoplay: true,
        interval: 3000,
        duration: 1000,
        loadingHidden: false, // loading
        swiperCurrent: 0,
        categories: [],
        activeCategoryId: 0,
        goods: [],
        scrollTop: "0",
        loadingMoreHidden: true,
        searchInput: '',
        p: 1,      // 分页处理
        processing: false   // 记录小程序是否正在发送处理
    },
    onLoad: function () {
        var that = this;

        wx.setNavigationBarTitle({
            title: app.globalData.shopName
        });

    },
    scroll: function (e) {
        var that = this, scrollTop = that.data.scrollTop;
        that.setData({
            scrollTop: e.detail.scrollTop
        });
    },

    // onShow()事件——页面进行显示的时候就会调用该方法
    onShow: function(){
        this.getBannerAndCat();
    },

    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },
	listenerSearchInput:function( e ){
	        this.setData({
	            searchInput: e.detail.value
	        });
	 },
    toSearch:function( e ){
	        this.setData({
	            p:1,
	            goods:[],
	            loadingMoreHidden:true
	        });
	        this.getFoodList();
	},
    tapBanner: function (e) {
        if (e.currentTarget.dataset.id != 0) {
            wx.navigateTo({
                url: "/pages/food/info?id=" + e.currentTarget.dataset.id
            });
        }
    },
    toDetailsTap: function (e) {
        wx.navigateTo({
            url: "/pages/food/info?id=" + e.currentTarget.dataset.id
        });
    },

    // 获得后端传递的数据
    getBannerAndCat: function () {
        var that = this;
        wx.request({
            url: app.buildUrl("/food/index"),
            header: app.getRequestHeader(),
            success(res) {
                var resp = res.data;
                if (resp.code != 200){
                    app.alert({"content": resp.msg});
                    return;
                }
                that.setData({
                   banners: resp.data.banner_list,
                   categories: resp.data.cat_list
                });

                // 加载首页时默认加载全部美餐
                that.getFoodList();
            }
        });
    },

    // 分类点击事件
    catClick: function(e){
        this.setData({
            /**
             * 点击时获取分类的id——>item.id
             * <view id="{{item.id}}" class="type-navbar-item {{activeCategoryId == item.id ? 'type-item-on' : ''}}" bindtap="catClick">
                {{item.name}}
                </view>
             */

            activeCategoryId: e.currentTarget.id,
            p: 1,
            goods: [],
            loadingMoreHidden: true
            // 因此需要初始值初始化处理
        });
        // 每次点击分类执行搜索事件
        this.getFoodList();
    },

    // 下拉搜索分页展示功能（实现onReachBottom()函数）
    onReachBottom: function(){
        var that = this;

        // 延时处理（原因：如果一碰到底就进行处理则会有些突兀）——0.5秒
        setTimeout(function () {
            that.getFoodList();
        }, 200);
    },

    // 搜索美餐列表
    getFoodList: function () {
        var that = this;

        /**
         * 什么时候可以发送请求之后端，什么时候不能发送请求至后端？
         * 1.当后端返回数据没有更多数据的时候（数据库内相关数据全部查询出来）
         * 2.前端小程序已经发送了一个请求，正在发送还没有获得后端响应
         */
        if (that.data.processing){
            // processing——true，表示当前已经发送了一个请求
            return;
        }
        if (!that.data.loadingMoreHidden) {
            // loadingMoreHidden——false， !false表示已经查询完数据库中的数据
            return;
        }

        that.setData({
            // 当前正在发送请求
            prcoessing: true
        });
        wx.request({
            url: app.buildUrl("/food/search"),
            header: app.getRequestHeader(),
            data: {
                cat_id: that.data.activeCategoryId,
                mix_kw: that.data.searchInput,
                p: that.data.p  // 当前页数
            },
            success(res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }
                var goods = resp.data.list
                that.setData({
                    goods: that.data.goods.concat(goods),   // 实现数据追加
                    p: that.data.p + 1,  // p值进行统一加1（从而实现分页处理）
                    prcoessing: false    // 处理完毕后processing设置为false——表示并没有请求正在发送
                });

                if (resp.data.has_more == 0){
                    // 表示当前数据全部加载
                    /**
                     * <view hidden="{{loadingMoreHidden ? true : false}}" class="no-more-goods">哥也是有底线的</view>
                     */
                    that.setData({
                        // 显示哥是有底线的（即false不需要隐藏起来）
                        loadingMoreHidden: false
                    });
                }
            }
        });
    }
});
