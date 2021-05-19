//login.js
//获取应用实例
var app = getApp();
Page({
  data: {
    remind: '加载中',
    angle: 0,
    userInfo: {},
    // regFlag表示是否已经注册
    regFlag: true
  },
  goToIndex:function(){
    wx.switchTab({
      url: '/pages/food/index',
    });
  },
  onLoad:function(){
    wx.setNavigationBarTitle({
      title: app.globalData.shopName
    });
    // 加载时则需要调用checklogin()方法，检测是否已经登录
    this.checkLogin();
  },
  onShow:function(){

  },
  onReady: function(){
    var that = this;
    setTimeout(function(){
      that.setData({
        remind: ''
      });
    }, 1000);
    wx.onAccelerometerChange(function(res) {
      var angle = -(res.x*30).toFixed(1);
      if(angle>14){ angle=14; }
      else if(angle<-14){ angle=-14; }
      if(that.data.angle !== angle){
        that.setData({
          angle: angle
        });
      }
    });
  },
  checkLogin: function(){
      var that = this;
      /**
       * 检测用户是否已经登录过？
       *
       * 调用wx.login()方法来获取code，将code传递至后台，后台通过code获取的openid，如果openid能够从
       *        数据库中查询出来，则表示该用户已经登录过
       */
      wx.login({
          success: function (res) {
              if (!res['code']){
                  app.alert({'content':'登录失败，请再次点击~~'});
                  return;
              }
              wx.request({
                  // 成功后统一将数据发送给后台
                  url: app.buildUrl('/member/check-reg'),
                  header: app.getRequestHeader(),
                  method: 'POST',
                  data: {code : res.code},
                  success: function (res) {
                        if (res.data.code != 200) {
                            // regFlag设置为true表示已经登录，设置为false(返回值!=200)表示未登录
                            that.setData({
                               regFlag: false
                            });
                            // 登录失败（注：此时不返回小程序首页）
                            return;
                        }

                        app.setCache('token', res.data.data.token);
                        // 返回code==200，表示登录成功，跳转至首页
                        that.goToIndex();
                    }
                  });
          }

      });
  },
  login: function (e) {
     var that = this;
    /**
     * console:function( msg ){
        console.log( msg);
       }
     */
    if ( !e.detail.userInfo ) {
      app.alert({'content': '登录失败，请再次点击~~'});
      return;
    }

    // 用户存在，则将数据传递至后端
    var data = e.detail.userInfo;

    wx.login({
       success: function (res) {
         if (!res.code) {
             // 发起网络请求
             app.alert({'content': '登录失败，请再次点击~~!'});
             return;
         }
           data['code'] = res.code;
           // wx.request()方法——发起 HTTPS 网络请求
           wx.request({
                //开发者服务器接口地址
              url: app.buildUrl('/member/login'),
              header: app.getRequestHeader(),
              method: 'POST',
              data: data,
              success: function (res) {
                  /**
                   * 1.只有一个用户的基本信息，是无法注册一个信息的
                   * 2.那么该用户的唯一标准是什么？通过用户名、昵称、头像都不行
                   * 3.success()方法成功后，会返回一个值code，通过code获得openid   注：openid是一个用户的唯一标识
                   *    同一个人关注公众号A、公众号B，在这两个公众号的openid是不一样的，同理不同的小程序openid也不一样
                   *
                   * 因此通过openid作为用户的唯一标识，来识别用户是否已经是注册过的用户？
                   */
                  if (res.data.code != 200){
                      // 登录失败显示弹出信息
                      app.alert({'content': res.data.msg})
                      return;
                  }

                  app.setCache('token', res.data.data.token);
                  // 登录成功跳转至小程序首页
                  that.goToIndex();

              }

            });

       }
    });


  }

});
