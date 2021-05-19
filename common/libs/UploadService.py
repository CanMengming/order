"""
    文件上传方法封装
"""
from application import app, db
from common.libs.Helper import getCurrentTime
import os, stat, uuid
from common.models.Image import Image


class UploadService:

    @staticmethod
    def uploadByFile(file):
        resp = {
            'code': 200,
            'msg': '操作成功',
            'data': {}
        }
        config_upload = app.config['UPLOAD']

        # 定义存放上传文件的目录
        # filename = secure_filename(file.filename)   # secure_filename()方法获取安全文件名
        filename = file.filename        # 如果使用上述secure_filename()方法则无法上传含有中文名的文件
        ext = filename.split(".", 1)[1]
        """ 
            获取文件扩展名    
            1.split(".", 1)——以.作为分割，且从第一个点开始，将文件名分为两个部分
            [0]文件名  [1]取出文件扩展名
        """
        if ext not in config_upload['ext']:
            # 判断上传的文件类型是否在指定的文件类型中？
            resp['code'] = -1
            resp['msg'] = "不允许的扩展类型文件"

            return resp

        # upload文件夹中希望以日期(每一天)作为标识存放的文件，文件名为时间戳生成唯一文件名

        # 首先保证文件夹存在
        root_path = app.root_path + config_upload['prefix_path']    # 路径——/home/www/order/web/static/upload/

        # 以日期作为文件名(年  月  日)
        file_dir = getCurrentTime("%Y%m%d")

        save_dir = root_path + file_dir

        if not os.path.exists(save_dir):
            # 判断文件夹是否存在
            os.makedirs(save_dir)       # 不存在则创建该文件夹
            os.chmod(save_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)
            """
                os.chmod()更改文件或目录的权限
                1.stat.S_IRWXU——拥有者有全部权限(权限掩码)0o700
                2.stat.S_IRGRP——组用户有读权限0o040
                3.stat.S_IRWXO——其他用户有全部权限(权限掩码)0o007
            """

        # 拼接文件名——以uuid(根据硬件和时间生成一个不重复的字符串)统一进行生成
        file_name = str(uuid.uuid4()).replace("-", "") + "." + ext
        file.save("{0}/{1}".format(save_dir, file_name))    # 路径 + 文件名即可正常存储

        # 将上传的图片存储至image数据表
        model_image = Image()
        model_image.file_key = file_dir + "/" + file_name
        # file_dir——日期文件名   file_name——uuid生成的唯一字符串
        model_image.created_time = getCurrentTime()
        db.session.add(model_image)
        db.session.commit()

        resp['data'] = {
            'file_key': model_image.file_key
        }
        # 日期 + 文件名

        return resp
