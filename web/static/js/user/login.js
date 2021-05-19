;    //javascript中可能会使用压缩，因此加上;则不会将js文件代码压缩
var user_login_ops = {
  init:function() {
    this.eventBind();
  },
  eventBind:function () {
      $(".login_wrap .do-login").click(function () {

          // 避免重复点击登录
          var btn_target = $(this);
          if (btn_target.hasClass("disabled")) {
              common_ops.alert("正在处理，请勿重复登录!");
              return
          }

          // 获取登录输入的用户名、密码
          var login_name = $(".login_wrap input[name=login_name]").val();
          var login_pwd = $(".login_wrap input[name=login_pwd]").val();

          if (login_name == undefined || login_name.length < 1) {
              // 弹出框提示(原因：没有输入用户名)
              common_ops.alert("请输入正确的登录用户名~~");
              return;
          }

          if (login_pwd == undefined || login_pwd.length < 1) {
              common_ops.alert("请输入正确的登录密码~~");
              return;
          }

          // btn_target中添加disabled值，如果已经点击登录按钮，则再次点击不再响应重复点击，以防止重复点击
          /*
           例如：
           1.第一次点击登录后，服务器、网络比较慢没有快速响应，则没有正常实现页面跳转
           2.此时用户则会再次点击登录按钮，由于点击后则会再次执行eventBind()方法
           3.进入第一个判断if (btn_target.hasClass("disabled")) {}，如果btn_target中值为disabled则会提示——不要重复登录
           */
          btn_target.addClass("disabled");

          // 参数都合法进行ajax提交
          $.ajax({
              // 将url提交至/user/login内
              url:common_ops.buildUrl("/user/login"),  //使用buildUrl()链接管理函数
              type:"POST",
              data:{'login_name':login_name,'login_pwd':login_pwd},
              dataType:'json',
              success:function (res) {
                  // 登录成功后去除btn_target中的disabled数值
                  btn_target.removeClass("disabled");

                  var callback = null;
                    if (res.code == 200){
                        // 返回的ajax的code==200(登录成功)
                        callback = function () {
                            // 登录成功跳转至主界面
                            window.location.href = common_ops.buildUrl("/");
                        }
                    }
                    // 实现登录成功弹窗，并点击确定跳转至后台界面
                    common_ops.alert(res.msg, callback)
              }
          });

      });
  }

};

$(document).ready( function () {
   user_login_ops.init();
});
