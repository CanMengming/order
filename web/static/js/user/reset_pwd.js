;
var mod_pwd_ops = {
  init:function () {
      this.eventBind();
  },
  eventBind:function () {
      $("#save").click(function () {

          var btn_target = $(this);
          if (btn_target.hasClass("disabled")) {
              common_ops.alert("正在处理!!请不要重复处理~~");
              return;
          }

          /*
           * <div class="form-group">
                <label class="col-lg-2 control-label">新密码:</label>
                <div class="col-lg-10">
                    <input type="password" id="new_password" class="form-control" value="">
                </div>
            </div>

            对于id属性直接使用#old_password，直接获取值
           */
          var old_password_target = $("#old_password");
          var old_password = old_password_target.val();

          var new_password_target = $("#new_password");
          var new_password = new_password_target.val();

          if (!old_password) {
              common_ops.alert("请输入原密码!~~");
              return false;
          }

          if (!new_password || new_password.length < 6) {
              common_ops.alert("请输入不少于6位的新密码!~~");
              return false;
          }

          btn_target.addClass("disabled");

          var data = {
              old_password : old_password,
              new_password : new_password
          };
          $.ajax({
              url:common_ops.buildUrl("/user/reset-pwd"),
              type:'POST',
              data:data,
              dataType:'json',
              success:function (res) {
                  //登录成功去除btn_target对象中的disabled值
                  btn_target.removeClass("disabled");

                  var  callback = null;
                  if (res.code == 200) {
                      // 后端返回表示修改成功(如果后端不返回json数据则不执行if中的操作)
                      callback = function() {
                          // 提交数据后，页面跳转至登录界面
                          window.location.href = window.location.href;
                      }
                  }
                  // 成功后实现弹窗，显示修改成功
                  common_ops.alert(res.msg, callback);
              }
          });
      });

  }
};

$(document).ready(function () {
    mod_pwd_ops.init();
});