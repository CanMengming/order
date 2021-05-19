"""
    微信服务封装——下单支付动作封装
"""
import hashlib, requests, uuid, json, datetime
import xml.etree.ElementTree as ET
from application import app, db
from common.libs.Helper import getCurrentTime
from common.models.pay.OauthAccessToken import OauthAccessToken


class WeChatService():

    def __init__(self, merchant_key=None):
        self.merchant_key = merchant_key

    # 支付签名
    def create_sign(self, pay_data):
        """
        生产签名
        1、签名算法
        （签名校验工具）
        签名生成的通用步骤如下：

        第一步，设所有发送或者接收到的数据为集合M，将集合M内非空参数值的参数按照参数名ASCII码从小到大排序（字典序），
        使用URL键值对的格式（即key1=value1&key2=value2…）拼接成字符串stringA。

        特别注意以下重要规则：
        ◆ 参数名ASCII码从小到大排序（字典序）；
        ◆ 如果参数的值为空不参与签名；
        ◆ 参数名区分大小写；
        ◆ 验证调用返回或微信主动通知签名时，传送的sign参数不参与签名，将生成的签名与该sign值作校验。
        ◆ 微信接口可能增加字段，验证签名时必须支持增加的扩展字段

        第二步，在stringA最后拼接上key得到stringSignTemp字符串，并对stringSignTemp进行MD5运算，再将得到的字符串所有字符转换为大写，
        得到sign值signValue。 注意：密钥的长度为32个字节。

        假设传送的参数如下：

        appid： wxd930ea5d5a258f4f
        mch_id： 10000100
        device_info： 1000
        body： test
        nonce_str： ibuaiVcKdpRxkhJA

        第一步：对参数按照key=value的格式，并按照参数名ASCII字典序排序如下：
        stringA="appid=wxd930ea5d5a258f4f&body=test&device_info=1000&mch_id=10000100&nonce_str=ibuaiVcKdpRxkhJA";

        第二步：拼接API密钥：
        MD5签名方式：
        stringSignTemp=stringA+"&key=192006250b4c09247ec02edce69f6a2d" //注：key为商户平台设置的密钥key
        sign=MD5(stringSignTemp).toUpperCase()="9A0A8659F005D6984697E2CA0A9CF3B7" //注：MD5签名方式

        HMAC-SHA256签名方式：
        stringSignTemp=stringA+"&key=192006250b4c09247ec02edce69f6a2d" //注：key为商户平台设置的密钥key
        sign=hash_hmac("sha256",stringSignTemp,key).toUpperCase()="6A9AE1657590FD6257D693A078E1C3E4BB6BA4DC30B23E0EE2496E54170DACD6"
        //注：HMAC-SHA256签名方式，部分语言的hmac方法生成结果二进制结果，需要调对应函数转化为十六进制字符串。
        :param pay_data:
        :return:
        """

        # 1.发送参数按照ASCII大小排序，拼接stringA= "key=value&key=value"字符串
        # 2.stringSignTemp = stringA+ "&key= ***" 注：key为商户平台秘钥key值
        #   sign = MD5(stringSignTemp).toUpperCase()  注：toUpperCase()转为大写字符串

        stringA = '&'.join(["{0}={1}".format(k, pay_data.get(k)) for k in sorted(pay_data)])
        # 注：1.stringA结果展示：stringA = "appid=wxd930ea5d5a258f4f&body=test&device_info=1000&mch_id=10000100";
        # 注：2.pay_data传递的数据为dict字典格式
        # 注：3."".join()——将字典格式转化为str字符串类型

        stringSignTemp = "{0}&key={1}".format(stringA, self.merchant_key)
        sign = hashlib.md5(stringSignTemp.encode("utf-8")).hexdigest()      # md5算法获取sign

        # upper()——字符串转化为大写字符
        return sign.upper()

    # dict字典类型数据转化为xml格式
    def dict_to_xml(self, dict_data):
        xml = ["<xml>"]
        for k, v in dict_data.items():
            xml.append("<{0}>{1}</{0}>".format(k, v))
        xml.append("</xml>")

        return "".join(xml)

    # 将xml数据转化为dict字典格式数据
    def xml_to_dict(self, xml_data):
        xml_dict = {}
        root = ET.fromstring(xml_data)

        for child in root:
            xml_dict[child.tag] = child.text

        return xml_dict

    # 生成随机字符串
    def get_nonce_str(self):
        return str(uuid.uuid4()).replace("-", "")

    # 获取支付信息
    def get_pay_info(self, pay_data=None):
        """
        获取支付信息
        注： pay_data为dict字典格式
        :return:
        """

        sign = self.create_sign(pay_data)       # 获取sign签名
        pay_data['sign'] = sign
        xml_data = self.dict_to_xml(pay_data)   # 将sign字典类型签名转化为xml格式

        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"      # 微信统一下单URL接口
        # 需要指定xml，否则微信将无法识别
        headers = {
            "Content-Type": "application/xml"
        }
        r = requests.post(url=url, data=xml_data.encode("utf-8"), headers=headers)      # post发送请求
        r.encoding = "utf-8"

        app.logger.info(r.text)

        if r.status_code == 200:
            prepay_id = self.xml_to_dict(r.text).get("prepay_id")
            pay_sign_data = {
                'appId': pay_data.get('appId'),
                'timeStamp': pay_data.get('out_trade_no'),  # 商户系统内部订单号--order_sn
                'nonceStr': pay_data.get('nonce_str'),       # 随机字符串
                'package': 'prepay_id={0}'.format(prepay_id),  # 微信生成的预支付会话标识
                'signType': 'MD5',
            }
            # 注：1.package——统一下单接口返回的 prepay_id 参数值，提交格式如：prepay_id=***
            pay_sign = self.create_sign(pay_sign_data)      # 统计sign签名
            pay_sign_data.pop('appId')
            pay_sign_data['paySign'] = pay_sign
            pay_sign_data['prepay_id'] = prepay_id

            return pay_sign_data

        return False

    # 获取AccessToken
    def getAccessToken(self):
        """
        获取小程序全局唯一后台接口调用凭据（access_token）
        返回——JSON 数据包
        正常返回
        {"access_token":"ACCESS_TOKEN","expires_in":7200}
        错误时返回
        {"errcode":40013,"errmsg":"invalid appid"}

        access_token 的存储与更新
        1.access_token 的存储至少要保留 512 个字符空间；

        2.access_token 的有效期目前为 2 个小时，需定时刷新，重复获取将导致上次获取的 access_token 失效；

        3.建议开发者使用中控服务器统一获取和刷新 access_token，其他业务逻辑服务器所使用的 access_token 均来自于该中控服务器，
        不应该各自去刷新，否则容易造成冲突，导致 access_token 覆盖而影响业务；

        4.access_token 的有效期通过返回的 expires_in 来传达，目前是7200秒之内的值，中控服务器需要根据这个有效时间提前去刷新。
        在刷新过程中，中控服务器可对外继续输出的老 access_token，此时公众平台后台会保证在5分钟内，新老 access_token 都可用，
        这保证了第三方业务的平滑过渡；

        5.access_token 的有效时间可能会在未来有调整，所以中控服务器不仅需要内部定时主动刷新，
        还需要提供被动刷新 access_token 的接口，这样便于业务服务器在API调用获知 access_token 已超时的情况下，
        可以触发 access_token 的刷新流程。
        :return:
        """
        token = None

        # 查询当前OauthAccessToken表是否存在未过期的access_token值
        token_info = OauthAccessToken.query.filter(OauthAccessToken.expired_time >= getCurrentTime()).first()   # 过期时间大于当前时间
        if token_info:
            token = token_info.access_token
            return token

        config_mina = app.config['MINA_APP']
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}".format(
            config_mina['appid'], config_mina['appkey']
        )
        # 向该URL地址发送POST请求，获取Access_Token

        r = requests.get(url=url)
        if r.status_code != 200 or not r.text:
            return token

        data = json.loads(r.text)       # loads将json格式数据转化为list列表类型

        now = datetime.datetime.now()
        date = now + datetime.timedelta(seconds=data['expires_in'] - 200)     # expires_in——凭证有效时间，单位：秒。目前是7200秒之内的值。
        model_token = OauthAccessToken()
        model_token.access_token = data['access_token']
        model_token.expired_time = date.strftime("%Y-%m-%d  %H:%M:%S")      # expired_time——过期时间
        model_token.created_time = getCurrentTime()

        db.session.add(model_token)
        db.session.commit()

        return data['access_token']
