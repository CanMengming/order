;
var upload = {
    error: function (msg) {
        common_ops.alert(msg);
    },
    success: function (file_key) {
        // 上传成功拼一张图放在上传旁边
        if (!file_key) {
            return;
        }
        var html = '<img src="' + common_ops.buildPicUrl(file_key) + '"/>'
                + '<span class="fa fa-times-circle del del_image" data="' + file_key + '"></span>';

        if ($(".upload_pic_wrap .pic-each").size() > 0) {
            // 如果里面没有图片，直接在里面增加一个图片
            $(".upload_pic_wrap .pic-each").html(html);
        } else {
            // 如果有图片则可以进行编辑
            $(".upload_pic_wrap").append('<span class="pic-each">' + html + '</span>');
        }
        food_set_ops.delete_img();
    }
};


var food_set_ops = {
  init: function () {
      this.eventBind();
      this.initEditor();
  },
  // 事件绑定方法
  eventBind:function () {
      var that = this;

      // 无刷新上传
      $(".wrap_food_set .upload_pic_wrap input[name=pic]").change(function () {
          $(".wrap_food_set .upload_pic_wrap").submit();
      });

      // 菜品分类下拉选择样式绑定
      $(".wrap_food_set  select[name=cat_id]").select2({
          language: 'zh-CN',
          width: '100%'
      });

      // 标签样式绑定
      $(".wrap_food_set input[name=tags]").tagsInput({
            width: 'auto',
            height: 40,
            onAddTag: function (tag) {
            },
            onRemoveTag: function (tag) {
            }
      });

      // 前端美食设置合法性判断
      $(".wrap_food_set .save").click(function () {
            var btn_target = $(this);
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在处理!!请不要重复提交~~");
                return;
            }

            var cat_id_target = $(".wrap_food_set select[name=cat_id]");
            var cat_id = cat_id_target.val();

            var name_target = $(".wrap_food_set input[name=name]");
            var name = name_target.val();

            var price_target = $(".wrap_food_set input[name=price]");
            var price = price_target.val();

            // 描述内容（从编辑器中获取描述内容）
            var summary = $.trim(that.ue.getContent());

            var stock_target = $(".wrap_food_set input[name=stock]");
            var stock = stock_target.val();

            var tags_target = $(".wrap_food_set input[name=tags]");
            var tags = $.trim(tags_target.val());

            if (parseInt(cat_id) < 1) {
                common_ops.tip("请选择分类~~", cat_id_target);
                return;
            }

            if (name.length < 1) {
                common_ops.alert("请输入符合规范的名称~~");
                return;
            }

            if (parseFloat(price) <= 0) {
                common_ops.tip("请输入符合规范的售卖价格~~", price_target);
                return;
            }

            if ($(".wrap_food_set .pic-each").size() < 1) {
                common_ops.alert("请上传封面图~~");
                return;
            }

            if (summary.length < 5) {
                common_ops.tip("请输入描述，并不能少于5个字符~~", price_target);
                return;
            }

            if (parseInt(stock) < 1) {
                common_ops.tip("请输入符合规范的库存量~~", stock_target);
                return;
            }

            if (tags.length < 1) {
                common_ops.alert("请输入标签，便于搜索~~");
                return;
            }

            btn_target.addClass("disabled");

            var data = {
                cat_id: cat_id,
                name: name,
                price: price,
                main_image: $(".wrap_food_set .pic-each .del_image").attr("data"),
                summary: summary,
                stock: stock,
                tags: tags,
                id: $(".wrap_food_set input[name=id]").val()
            };

            $.ajax({
                url: common_ops.buildUrl("/food/set"),
                type: 'POST',
                data: data,
                dataType: 'json',
                success: function (res) {
                    btn_target.removeClass("disabled");
                    var callback = null;
                    if (res.code == 200) {
                        callback = function () {
                            window.location.href = common_ops.buildUrl("/food/index");
                        }
                    }
                    common_ops.alert(res.msg, callback);
                }
            });

      });
  },
  // 编辑器初始化方法
  initEditor: function() {
      var that = this;
      // 将set.html中id=editor的标签编辑框---->可视化编辑器
      that.ue = UE.getEditor('editor', {
          // toolbar显示部分功能
          toolbars: [
        [ 'undo', 'redo', '|',
            'bold', 'italic', 'underline', 'strikethrough', 'removeformat', 'formatmatch', 'autotypeset', 'blockquote', 'pasteplain', '|', 'forecolor', 'backcolor', 'insertorderedlist', 'insertunorderedlist', 'selectall',  '|','rowspacingtop', 'rowspacingbottom', 'lineheight'],
        [ 'customstyle', 'paragraph', 'fontfamily', 'fontsize', '|',
            'directionalityltr', 'directionalityrtl', 'indent', '|',
            'justifyleft', 'justifycenter', 'justifyright', 'justifyjustify', '|', 'touppercase', 'tolowercase', '|',
            'link', 'unlink'],
        [ 'imagenone', 'imageleft', 'imageright', 'imagecenter', '|',
            'insertimage', 'insertvideo', '|',
            'horizontal', 'spechars','|','inserttable', 'deletetable', 'insertparagraphbeforetable', 'insertrow', 'deleterow', 'insertcol', 'deletecol', 'mergecells', 'mergeright', 'mergedown', 'splittocells', 'splittorows', 'splittocols' ]
            ],
          // 自动保存
          enableAutoSave: true,
          // 自动保存间隔时间，单位ms
          saveInterval: 60000,
          // [默认值：true] 是否启用元素路径，默认是显示
          elementPathEnabled: false,
          // [默认值：900] 编辑器在页面上的z-index层级的基数，默认是900
          zIndex: 4,
          //后端配置项地址配置
          serverUrl: common_ops.buildUrl( '/upload/ueditor')
      });
  },

  // 封面图片上传后删除方法
  delete_img: function () {
      $(".wrap_food_set .del_image").unbind().click(function () {
          // 父类进行移除
          $(this).parent().remove();
      });
  }
};

$(document).ready(function () {
    food_set_ops.init();
});