"""
    小程序会员服务
"""
import random, string, hashlib, requests, json
from application import app


class MemberService():

    # 生成16位的salt码
    @staticmethod
    def geneSalt(length=16):
        """
        choice() 方法返回一个列表，元组或字符串的随机项

        实例
        #!/usr/bin/python3
        import random

        print ("从 range(100) 返回一个随机数 : ",random.choice(range(100)))
        print ("从列表中 [1, 2, 3, 5, 9]) 返回一个随机元素 : ", random.choice([1, 2, 3, 5, 9]))
        print ("从字符串中 'Runoob' 返回一个随机字符 : ", random.choice('Runoob'))
        以上实例运行后输出结果为：

        从 range(100) 返回一个随机数 :  68
        从列表中 [1, 2, 3, 5, 9]) 返回一个随机元素 :  2
        从字符串中 'Runoob' 返回一个随机字符 :  u
        :param length:
        :return:
        """
        keylist = [random.choice((string.ascii_letters + string.digits)) for i in range(length)]
        # random.choice((string.ascii_letters + string.digits)) for i in range(length)--循环产生16位随机字符
        return ("".join(keylist))

    # token值加密
    @staticmethod
    def geneAuthCode(member_info=None):
        # 根据member_info的id、salt、status三个值获取加密token值

        m = hashlib.md5()
        str = "%s-%s-%s" % (member_info.id, member_info.salt, member_info.status)
        m.update(str.encode("utf-8"))
        return m.hexdigest()

    @staticmethod
    def getWechatOpenid(code):
        # 临时登录凭证校验接口是一个HTTPS接口
        # 开发者服务器使用临时登录凭证code获取本次登录会话秘钥session_key和当前小程序唯一标识openid等
        url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code" \
            .format(app.config['MINA_APP']['appid'], app.config['MINA_APP']['appkey'], code)

        # Python中如何快速的发送一个请求出去？     使用requests扩展(pip install requests)
        r = requests.get(url)
        res = json.loads(r.text)
        openid = None

        if 'openid' in res:
            openid = res['openid']

        return openid
