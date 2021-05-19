"""
    application.py封装类，封装app、db这些变量
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
import os


class Application(Flask):
    def __init__(self, import_name, template_folder=None, root_path=None):
        # 调用父类__init__()函数
        # template_folder模板文件路径、static_folder静态文件路径
        super(Application, self).__init__(import_name, template_folder=template_folder, root_path=root_path,
                                          static_folder=None)
        # 设置从哪里加载配置文件
        self.config.from_pyfile('config/base_setting.py')

        # 如何实现加载指定环境的配置文件？什么时候加载local_setting，什么时候加载base_setting等
        if "ops_config" in os.environ:
            self.config.from_pyfile('config/%s_setting.py' % os.environ['ops_config'])

        db.init_app(self)


db = SQLAlchemy()
app = Application(__name__, template_folder=os.getcwd() + "/web/templates/", root_path=os.getcwd())

manager = Manager(app)

'''
    函数模板——使得html文件也能够调用buildStaticUrl()函数
    注：使得python的函数能够注入到html中使用
'''
from common.libs.UrlManager import UrlManager
app.add_template_global(UrlManager.buildStaticUrl, 'buildStaticUrl')
app.add_template_global(UrlManager.buildUrl, 'buildUrl')
app.add_template_global(UrlManager.buildImageUrl, 'buildImageUrl')
# 将两个函数注入到模板内

