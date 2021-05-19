;
var account_set_ops = {
    init:function () {
        this.eventBind();
    },
    eventBind:function () {
        $(".wrap_account_set .save").click(function () {

            var btn_target = $(this);
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在处理!!请不要重复处理~~");
                return;
            }

            var nickname_target = $(".wrap_account_set input[name=nickname]");
            var nickname = nickname_target.val();

            var mobile_target = $(".wrap_account_set input[name=mobile]");
            var mobile = mobile_target.val();

            var email_target = $(".wrap_account_set input[name=email]");
            var email = email_target.val();

            var login_name_target = $(".wrap_account_set input[name=login_name]");
            var login_name = login_name_target.val();

            var login_pwd_target = $(".wrap_account_set input[name=login_pwd]");
            var login_pwd = login_pwd_target.val();

            if (!nickname || nickname.length < 1) {
                common_ops.tip("请输入符合规范的姓名!", nickname_target);
                return false;
            }

            if (!mobile || mobile.length != 11) {
                common_ops.tip("请输入符合规范的手机号!", mobile_target);
                return false;
            }

            if (!email || email.length < 1) {
                common_ops.tip("请输入符合规范的邮箱!", email_target);
                return false;
            }

            if (!login_name || login_name.length < 0) {
                common_ops.tip("请输入符合规范的登录名!", login_name_target);
                return false;
            }

            if (!login_pwd || login_pwd.length < 6) {
                common_ops.tip("请输入不少于6位的密码!", login_pwd_target);
                return false;
            }

            btn_target.addClass("disabled");

            var data = {
                nickname: nickname,
                mobile: mobile,
                email:email,
                login_name: login_name,
                login_pwd: login_pwd,
                // 获取set.html页面传递的name=id的值(set.html页面显示<input type="hidden" name="id" value="{{ info.uid }}">)
                id: $(".wrap_account_set input[name=id]").val()
            };
            $.ajax({
                url:common_ops.buildUrl("/account/set"),
                type:'POST',
                data:data,
                dataType:'json',
                success:function (res) {
                    // 登录成功后去除btn_target中的disabled数值
                  btn_target.removeClass("disabled");

                  var callback = null;
                  if (res.code == 200){
                        // 返回的ajax的code==200(登录成功)
                        callback = function () {
                            // 提交修改数据后，刷新当前页面，展示修改的数据
                            window.location.href = common_ops.buildUrl("/account/index");
                        }
                  }
                  // 实现登录成功弹窗，并进行edit页面刷新
                  common_ops.alert(res.msg, callback);
                }

            });

        });
    }

};


$(document).ready(function () {
    account_set_ops.init();
});