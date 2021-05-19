//获取应用实例
var app = getApp();
Page({
    data: {},
    onShow: function () {
        var that = this;
        /**
        that.setData({
            addressList: [
                {
                    id:1,
                    name: "明华俊",
                    mobile: "12345678901",
                    detail: "江苏省常州市江苏理工学院",
                    isDefault: 1
                },
                {
                    id: 2,
                    name: "殘梦",
                    mobile: "12345678901",
                    detail: "江苏省扬州市送桥"
                }
            ]
        });
         */
        this.getList();
    },
    // 选中谁就把谁设置为默认地址
    selectTap: function (e) {
      var that = this;
      wx.request({
          url: app.buildUrl("/my/address/ops"),
          header: app.getRequestHeader(),
          method: 'POST',
          data: {
              id: e.currentTarget.dataset.id,
              act: 'default'
          },

          success: function(res) {
              var resp = res.data;
              if (resp.code != 200) {
                  app.alert({"content": resp.msg});
                  return;
              }

              that.setData({
                    addressList: resp.data.list
              });
          }
      });

      wx.navigateBack({});   // 返回上一页中
    },
    // 添加收货地址
    addressSet: function (e) {
        wx.navigateTo({
            url: "/pages/my/addressSet?id=" + e.currentTarget.dataset.id
        })
    },
    // 获取收货地址列表
    getList: function () {
        var that = this;
      wx.request({
          url: app.buildUrl("/my/address/index"),
          header: app.getRequestHeader(),

          success: function(res) {
              var resp = res.data;
              if (resp.code != 200) {
                  app.alert({"content": resp.msg});
                  return;
              }

              that.setData({
                    addressList: resp.data.list
              });
          }
      });
    }
});
