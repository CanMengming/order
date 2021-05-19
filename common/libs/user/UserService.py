"""
    User核心操作
"""
import hashlib, base64, random, string


class UserService():

    @staticmethod
    def genePwd(pwd, salt):
        # 生成加密后密码

        m = hashlib.md5()
        # base64.encodebytes()——加密密码
        # 参数：字节码   如何将字符串转换成为字节码？ pwd.encode("utf-8")
        str = "%s-%s" % (base64.encodebytes(pwd.encode("utf-8")), salt)
        m.update(str.encode("utf-8"))
        return m.hexdigest()

    @staticmethod
    def geneAuthCode(user_info):
        # cookie值加密

        m = hashlib.md5()
        str = "%s-%s-%s-%s" % (user_info.uid, user_info.login_name, user_info.login_pwd, user_info.login_salt)
        m.update(str.encode("utf-8"))
        return m.hexdigest()

    @staticmethod
    def geneSalt(length=16):
        # 生成16位的salt码
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
