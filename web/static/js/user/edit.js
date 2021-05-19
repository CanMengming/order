;
var user_edit_ops = {
    init:function () {
        this.eventBind();
    },
    eventBind:function () {
        $(".user_edit_wrap .save").click(function () {

            var btn_target = $(this);
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在处理!!请不要重复处理~~");
                return;
            }

            var nickname_target = $(".user_edit_wrap input[name=nickname]");
            var nickname = nickname_target.val();

            var email_target = $(".user_edit_wrap input[name=email]");
            var email = email_target.val();

            if (!nickname || nickname.length < 2) {
                common_ops.tip("请输入符合规范的姓名!", nickname_target);
                return false;
            }

            if (!email || email.length < 2) {
                common_ops.tip("请输入符合规范的邮箱!", email_target);
                return false;
            }

            btn_target.addClass("disabled");

            var data = {
                nickname: nickname,
                email:email
            };
            $.ajax({
                url:common_ops.buildUrl("/user/edit"),
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
                            window.location.href = window.location.href;
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
    user_edit_ops.init();
});