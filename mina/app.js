//app.js
App({
    onLaunch: function () {
    },
    globalData: {
        userInfo: null,
        version: "1.0",
        shopName: "殘梦微信小程序订餐系统",
        // domain统一域名处理
        domain:"http://192.168.43.199:8999/api"
    },
    tip:function( params ){
        var that = this;
        var title = params.hasOwnProperty('title')?params['title']:'提示信息';
        var content = params.hasOwnProperty('content')?params['content']:'';
        wx.showModal({
            title: title,
            content: content,
            success: function(res) {

                if ( res.confirm ) {//点击确定
                    if( params.hasOwnProperty('cb_confirm') && typeof( params.cb_confirm ) == "function" ){
                        params.cb_confirm();
                    }
                }else{//点击否
                    if( params.hasOwnProperty('cb_cancel') && typeof( params.cb_cancel ) == "function" ){
                        params.cb_cancel();
                    }
                }
            }
        })
    },
    alert:function( params ){
        var title = params.hasOwnProperty('title')?params['title']:'提示信息';
        var content = params.hasOwnProperty('content')?params['content']:'';
        wx.showModal({
            title: title,
            content: content,
            showCancel:false,
            success: function(res) {
                if (res.confirm) {//用户点击确定
                    if( params.hasOwnProperty('cb_confirm') && typeof( params.cb_confirm ) == "function" ){
                        params.cb_confirm();
                    }
                }else{
                    if( params.hasOwnProperty('cb_cancel') && typeof( params.cb_cancel ) == "function" ){
                        params.cb_cancel();
                    }
                }
            }
        })
    },
    console:function( msg ){
        console.log( msg);
    },
    getRequestHeader:function(){
        // 获取小程序缓存cache中的token值
        return {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': this.getCache("token")
        }
    },
  buildUrl: function (path, params) {
        var url = this.globalData.domain + path;
        var _paramUrl = "";
        if (params) {

            /*
            例如：
            params = {
                a:"b",
                c:"d"
            };
            结果为："a=b&c=d"
            */
            // 循环取出params中的值
            _paramUrl = Object.keys(params).map(function (k) {
                return [ encodeURIComponent(k), encodeURIComponent(params[k])].join("=");
            }).join("&");

            _paramUrl = "?" + _paramUrl
        }

        return url + _paramUrl;
  },
  getCache:function (key) {
        var value = undefined;
        try {
            var value= wx.getStorageSync(key);
        }catch (e) {
        }

        return value;

  },
  setCache:function (key, values) {
      /**
       * 1.将数据存储在本地缓存中指定的 key 中,会覆盖掉原来该 key 对应的内容。
       * 2.除非用户主动删除或因存储空间原因被系统清理，否则数据都一直可用。
       *
       * 注：单个 key 允许存储的最大数据长度为 1MB，所有数据存储上限为 10MB。
       */
      wx.setStorage({
         key: key,
         data: values
      });
  }
});