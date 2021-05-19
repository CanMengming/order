DEBUG = True        # 测试环境下开启debug模式
SQLALCHEMY_ECHO = True      # 是否打印输出全部SQL语句

# 测试环境下配置数据库
SQLALCHEMY_DATABASE_URI = 'mysql://root:qq276713@127.0.0.1/food_db'   # 使用Linux本地food_db数据库
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENCODING = "utf8mb4"        # sql的编码设置为utf-8

# RELEASE_VERSION = "20210321"    # 版本号(这样以后每次上线或者通过自动化脚本进行改变)

