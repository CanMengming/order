SERVER_PORT = 8999
DEBUG = False       # 生产环境默认不开启debug模式
SQLALCHEMY_ECHO = False      # 是否打印输出全部SQL语句

AUTH_COOKIE_NAME = "imooc_food"

# 过滤Url
IGNORE_URLS = [
    "^/user/login"
]

IGNORE_CHECK_LOGIN_URLS = [
    "^/static",
    "^/favicon.ico"
]

PAGE_SIZE = 12
PAGE_DISPLAY = 10

STATUS_MAPPING = {
    "1": "正常",
    "0": "已删除"
}

MINA_APP = {
    'appid': '',
    'appkey': '',
    'pay_key': '',
    'mch_id': '',
    'callback_url': '/api/order/callback'
}

""" 
    1.ext——支持哪些扩展文件类型(即能上传哪些类型文件)
    2.prefix_path——前缀path
"""
UPLOAD = {
    'ext': ['jpg', 'gif', 'bmp', 'jpeg', 'png', 'JPG', 'GIF', 'BMP', 'JPEG', 'PNG'],
    'prefix_path': '/web/static/upload/',
    'prefix_url': '/static/upload/'
}

APP = {
    'domain': 'http://192.168.43.199:8999'
}

API_IGNORE_URLS = [
    "^/api"
]

PAY_STATUS_MAPPING = {
    "1": "已支付",
    "-8": "待支付",
    "0": "已关闭"
}

PAY_STATUS_DISPLAY_MAPPING = {
    "0": "订单关闭",
    "1": "支付成功",
    "-8": "待支付",
    "-7": "待发货",
    "-6": "待确认",
    "-5": "待评价"
}


