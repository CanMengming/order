from flask import Blueprint, request, jsonify
from application import app
import json, re
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.models.Image import Image

route_upload = Blueprint("upload_page", __name__)


@route_upload.route("/ueditor", methods=['GET', 'POST'])
def ueditor():
    # 上传文件一定是POST，但是获取配置文件时GET

    # 如何获取配置文件并返回？
    req = request.values
    action = req['action'] if 'action' in req else None

    if action == 'config':
        root_path = app.root_path  # /order路径
        config_path = "{0}/web/static/plugins/ueditor/upload_config.json".format(root_path)  # 获取配置文件路径

        """
            出现无法解析json配置文件的原因？
            1.json数据都是key:value，但是json中没有备注的这个方式，而配置文件upload_config.json中含有很多备注
            
            解决方法：
            1.引入正则表达式，将备注替换为""(空)
        """
        with open(config_path) as fp:
            try:
                # re.sub("", "", fp.read())——""(第一个空格)正则表达式  ""(第二个空格)替换为空格  fp.read()从什么内容中进行操作
                # r'\/\*.*\*/'——\转义字符  \(转义)/\(转义)*——匹配注释开头/*   .*匹配任意多个字符   \(转义)*/——匹配注释结尾*/
                config_data = json.loads(re.sub(r'\/\*.*\*/', "", fp.read()))
            except:
                config_data = {}
        return jsonify(config_data)

    if action == 'uploadimage':
        # 上传图片操作

        return uploadImage()

    if action == 'listimage':

        return listImage()

    return "upload"


# 封面图片无刷新上传
@route_upload.route("/pic", methods=['GET', 'POST'])
def uploadPic():
    """
        与图片上传动作类似
        唯一不同的是：想使你的值能够返回出去的话，调用的方法不一样
        iframe——如果想将值传出来的话，需要通过在iframe中调用编辑页面方法才可以，然后进行传值
    :return:
    """

    # 获取请求文件的表单
    file_target = request.files

    upfile = file_target['pic'] if 'pic' in file_target else None

    callback_target = 'window.parent.upload'
    if upfile is None:
        """
            不返回json字符串，返回js事件，让在iframe里面的js能够调用上层的js
        """
        return "<script type='text/javascript'>{0}.error('{1}')</script>".format(callback_target, "上传失败")

    ret = UploadService.uploadByFile(upfile)
    if ret['code'] != 200:
        return "<script type='text/javascript'>{0}.error('{1}')</script>".format(callback_target, "上传失败" + ret['msg'])

    # 上传成功
    return "<script type='text/javascript'>{0}.success('{1}')</script>".format(callback_target, ret['data']['file_key'])


# 图片上传动作
def uploadImage():
    # 返回固定格式的json数据
    resp = {
        'state': 'SUCCESS',
        'url': '',
        'title': '',
        'original': ''
    }
    # 注：status状态必须返回SUCCESS，失败则随便返回一个什么值

    file_target = request.files
    # 注：key:value值  获取上传文件名——返回值([('upfile', <FileStorage: 'login.jpg' ('image/jpeg')>)])
    upfile = file_target['upfile'] if 'upfile' in file_target else None
    if upfile is None:
        # 没有获取到上传文件的文件类型
        resp['state'] = "上传失败"

        return jsonify(resp)

    ret = UploadService.uploadByFile(upfile)
    if ret['code'] != 200:
        resp['state'] = "上传失败：" + ret['msg']

        return jsonify(resp)

    resp['url'] = UrlManager.buildImageUrl(ret['data']['file_key'])

    """
        为了能够实现在线展示，需要将每次上传的图片进行存储
    """

    return jsonify(resp)


# 在线图片展示
def listImage():
    """
        从数据库表image中取出图片数据进行展示
    :return:
    """
    resp = {
        'state': 'SUCCESS',
        'list': [],
        'start': 0,
        'total': 0
    }

    req = request.values

    start = int(req['start']) if 'start' in req else 0
    page_size = int(req['size']) if 'size' in req else 20

    query = Image.query
    if start > 0:
        """
            start下次请求回重新传递一个新的start值
            例如：1.第一次前台start=0，则数据显示后则start=9，再次分页展示传递给下一次展示
        """
        query = query.filter(Image.id < start)

    # 每页显示20条数据(倒序排列，每次最多取20条数据)
    list = query.order_by(Image.id.desc()).limit(page_size).all()
    images = []
    if list:
        for item in list:
            images.append({'url': UrlManager.buildImageUrl(item.file_key)})
            start = item.id     # 不断修改start的值，for循环结束后倒序排列——最后一个id - page_size

    resp['list'] = images
    resp['start'] = start       # start作为下次请求在下展示的start值
    resp['total'] = len(images)

    return jsonify(resp)