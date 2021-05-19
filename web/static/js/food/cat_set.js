;
var food_cat_set_ops = {
    init:function () {
        this.eventBind();
    },
    eventBind:function () {
        $(".wrap_cat_set .save").click(function () {

            var btn_target = $(this);
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在处理!!请不要重复处理~~");
                return;
            }

            var name_target = $(".wrap_cat_set input[name=name]");
            var name = name_target.val();

            var weight_target = $(".wrap_cat_set input[name=weight]");
            var weight = weight_target.val();


            if (!name || name.length < 1) {
                common_ops.tip("请输入符合规范的种类名~~!", name_target);
                return false;
            }

            if (parseInt(weight) < 1) {
                common_ops.tip("请输入符合规范的种类权重，并且至少要大于1~~!", weight_target);
                return false;
            }

            btn_target.addClass("disabled");

            var data = {
                name: name,
                weight: weight,
                // 获取set.html页面传递的name=id的值(set.html页面显示<input type="hidden" name="id" value="{{ info.uid }}">)
                id: $(".wrap_cat_set input[name=id]").val()
            };
            $.ajax({
                url:common_ops.buildUrl("/food/cat-set"),
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
                            window.location.href = common_ops.buildUrl("/food/cat");
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
    food_cat_set_ops.init();
});