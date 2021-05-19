"""
    链接管理器同一封装
"""
from application import app
import time


class UrlManager(object):

    @staticmethod
    def buildUrl(path):
        return path

    @staticmethod
    def buildStaticUrl(path):
        """
        注意修改此处代码
        path = path + "?ver=" + "2021030300"
        return UrlManager.buildUrl(path)
        """
        release_version = app.config.get('RELEASE_VERSION')
        ver = "%s" % (int(time.time())) if not release_version else release_version
        path = "/static" + path + "?ver=" + ver
        return UrlManager.buildUrl(path)

    @staticmethod
    def buildImageUrl(path):
        app_config = app.config['APP']

        # url = "域名"——统一配置 + "图片前缀——/static/upload/" + "key——path"
        url = app_config['domain'] + app.config['UPLOAD']['prefix_url'] + path
        return url
