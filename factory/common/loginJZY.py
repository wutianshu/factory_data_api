# -*- coding:utf-8 -*-

"""
# 功能简要说明
# 登录基类
# 需要鉴权的类继承此类，cookie信息交由session自动维护
"""
import logging, requests, random, time, os, pymysql
from requests import Session, Response
from requests_html import HTMLSession
from requests.cookies import RequestsCookieJar
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from .redis_tools import redis_handler
from deng.tools import Tools
from .exceptions import PermissionsException, ServiceUnavailableException, ResponseFormatException

# 日志句柄
logger = logging.getLogger(__name__)
# 禁用ssl警告
disable_warnings(InsecureRequestWarning)


class LoginJZY(object):
    INIT_PHONE = 14400000001

    def __init__(self, phone, env='stable', online_urm_se=requests.session()):
        logger.debug('初始化LoginJZY类实例')
        if len(str(phone)) != 0 and len(str(phone)) != 11:
            raise PermissionError('手机号码错误')
        try:
            int(phone)
        except:
            phone = self.get_phone()
        # 线上urm的session，从綫上前端传过来的
        self.online_urm_se = online_urm_se
        self.env = env
        self.phone = str(phone)
        self.phone_key = 'jzy' + self.env + self.phone
        self.dj_appversion = '1.1.1'
        self.djbusiness = '301'
        self.dj_appid = '32'
        self.djclient = '409'
        self.session = Session()
        self.protocol = 'https://'

        if env == 'stable' or env == 'betaa':
            self.login_domain = 'login-betaa.test.cn'
        elif env == 'box':
            self.login_domain = 'login-box.test.cn'
        elif env == 'online':
            self.login_domain = 'login-online.test.cn'
        else:
            self.login_domain = 'login-betaa.test.cn'

        if env == 'stable':
            self.crm_domain = 'server-stable.test.cn'
        elif env == 'betaa':
            self.crm_domain = 'server-betaa.test.cn'
        elif env == 'box':
            self.crm_domain = 'server-alprod.test.cn'
        elif env == 'online':
            self.crm_domain = 'server-online.test.cn'
        else:
            self.crm_domain = 'server-betaa.test.cn'

        self.touch_code_path = '/getcode'
        self.touch_code_url = "{}{}{}".format(self.protocol, self.login_domain, self.touch_code_path)
        self.touch_code_params = {"mobile": self.phone, 'bu': '112', 'newVersion': '1'}
        self.login_path = '/login'
        self.login_url = "{}{}{}".format(self.protocol, self.login_domain, self.login_path)
        self.login_params = {"mobile": self.phone, "code": "", 'bu': '112'}

        self.login()  # 登录
        # 如果未关联公司返回False，如果关联了公司返回关联公司信息,该参数是登录后获取到的信息，如果更新公司后需重新获取
        self.relation_company_info = self.is_company_relation()

        # 管理后台登录(这是测试环境的)可以查询短信验证码
        sso_login = LoginSSO(username='username', password='password')
        sso_login.login()
        self.urm_session = sso_login.session

    def login(self):
        if self.login_from_redis():  # 从redis进行了登录
            if not self.init():  # redis登录失败，
                self.login_from_request()
                if self.init():  # 登录成功
                    return True
                else:
                    # 仍然登录异常
                    raise PermissionsException('登录异常，需要排查')
            else:  # 用redis中的cookie登录成功了
                return True
        else:  # 没有进入redis
            self.login_from_request()
            if self.init():  # 登录成功
                return True
            else:  # 仍然登录异常
                raise PermissionsException('登录异常，需要排查')

    def login_from_request(self):
        '''
        获取验证码，登录
        :return:
        '''
        # 清空cookie，由于使用redis时已经带入了可能无效的cookie
        imei = self.get_random_imei()
        self.session.cookies = RequestsCookieJar()
        self.session.cookies.set('tolen', '')
        self.session.cookies.set('djfrtappversion', self.dj_appversion)
        self.session.cookies.set('business', self.djbusiness)
        # 先查询一次该手机的所有验证码数目
        msg_count_1 = self.get_sms_info(self.phone)['count']
        # 请求获取验证码
        res1 = self.session.post(url=self.touch_code_url, data=self.touch_code_params, verify=False)
        if int(res1.json()['code']) == 100:
            raise PermissionsException('{}需要输入图形验证码，无法自动登录'.format(self.phone))
        elif int(res1.json()['code']) == 0:
            logger.info('{}:请求获取验证码成功'.format(self.phone))
            # 循环获取验证码
            code = self.get_sms_code(self.phone, msg_count_1=msg_count_1)
            self.login_params['code'] = code
            # 登录
            res2 = self.session.post(url=self.login_url, data=self.login_params, verify=False)
            if res2.json()['code'] == 0:
                logger.info('{}:request登录结果:{}'.format(self.phone, str(res2.json()['desc'])))
                # 把返回的token存入cookie中
                self.session.cookies.set('uid', res2.json()['dj_psuid'])
                self.session.cookies.set('exp', res2.json()['djfrtexp'])
                self.session.cookies.set('tok', res2.json()['djfrttok'])
                self.session.cookies.set('appVersion', self.dj_appversion)
                # self.session.cookies.set('dj_appversion', self.dj_appversion)
                # 把cookies存入redis
                self.set_redis_cookie()
            else:
                raise PermissionsException('使用request请求登录失败')
        else:
            raise PermissionsException('请求获取验证码未知异常')

    def login_from_redis(self):
        '''
        如果redis中有入参phone，则从redis中取cookie
        :return:
        '''
        if redis_handler.hkeys(self.phone_key):
            cookie_dict = {}
            l = redis_handler.hkeys(name=self.phone_key)
            for i in l:
                cookie_dict[i.decode('utf-8')] = redis_handler.hget(name=self.phone_key, key=i).decode('utf-8')
            self.cookie = requests.utils.cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True)
            self.session.cookies = self.cookie
            logger.info('{}:redis中获取到cookie：{}'.format(self.phone, str(cookie_dict)))
            return True
        else:
            logger.info('{}:redis中没有获取到cookie'.format(self.phone))
            return False

    def is_company_relation(self):
        '''
        是否关联公司
        :return:
        '''
        init_path = '/associated'
        init_url = '{}{}{}'.format(self.protocol, self.crm_domain, init_path)
        res0 = self.session.get(url=init_url, verify=False)
        self.check_all(res0)
        logger.debug(res0.text)
        try:
            res0.json()['data']['auditStatus']
        except:
            # 如果没有data说明该账号没有关联过公司
            return False
        else:
            relation_company = {}
            relation_company['auditStatus'] = res0.json()['data']['auditStatus']  # 公司状态，1：启用 2：被禁用
            relation_company['comDataStatus'] = res0.json()['data']['comDataStatus']  # 公司资料状态，1：已完善 2：未完善'
            relation_company['staffStatus'] = res0.json()['data']['staffStatus']  # 经纪人状态：1启用，2禁用
            relation_company['whetherMaster'] = res0.json()['data']['whetherMaster']  # 是否是主账号1：是，2：否
            relation_company['comNo'] = res0.json()['data']['comNo']  # 公司id
            relation_company['comFullName'] = res0.json()['data']['comFullName']  # 公司全称
            return relation_company

    def init(self):
        '''检查是否登录成功'''
        init_path = '/associated'
        init_url = '{}{}{}'.format(self.protocol, self.crm_domain, init_path)
        res = self.session.get(url=init_url, verify=False)
        self.check_response_status(res)
        self.check_response_format(res)
        if int(res.json()['status']) == -101:
            # 登录无效
            logger.info('{}:检验登录结果为【失败】'.format(self.phone))
            self.remove_redis()
            return False
        else:
            logger.info('{}:检验登录结果为【成功】'.format(self.phone))
            return True

    def remove_redis(self):
        # 删除redis中数据
        if redis_handler.hkeys(name=self.phone_key):
            redis_handler.delete(self.phone_key)
            logger.info('{}:删除redis中的无效cookie'.format(self.phone))

    def set_redis_cookie(self):
        '''
        把seesion中携带的cookie存入redis
        :return:
        '''
        # 把cookie对象转换为字典，方便存入redis
        cookie_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
        logger.info('{}:把cookie存入redis:'.format(self.phone, str(cookie_dict)))
        # cookie存入redis
        for k in cookie_dict:
            redis_handler.hset(name=self.phone_key, key=k, value=cookie_dict[k])

    def redis_random_policy_no(self):
        if redis_handler.get('policy_no'):
            policy_no = int(redis_handler.get('policy_no'))
            redis_handler.set('policy_no', str(policy_no + 1))
            return 'TEST000' + str(policy_no)
        else:
            redis_handler.set('policy_no', '1000000000001')

    def get_sms_info(self, phone):
        if self.env == 'stable' or self.env == 'betaa':
            code_domain = 'test-manager.cn'
            data = {'phoneno': int(phone), 'env': 'offline'}
            code_path = '/smscode'
            code_url = '{}{}{}'.format(self.protocol, code_domain, code_path)
            res = self.session.get(url=code_url, params=data, verify=False)
        elif self.env == 'box' or self.env == 'online':
            code_domain = 'online-manager.com'
            data = {'phoneno': int(phone), 'env': 'online'}
            code_path = '/smscode'
            code_url = '{}{}{}'.format(self.protocol, code_domain, code_path)
            logger.info(code_url)
            logger.info(data)
            logging.info(self.online_urm_se.headers)
            logging.info(self.online_urm_se.cookies)
            res = self.online_urm_se.get(url=code_url, params=data, verify=False)
        else:
            raise PermissionError('环境参数有误')
        self.check_response_status(res)
        self.check_response_format(res)
        try:
            len(res.json()['factory_data'])
        except:
            sms_count = 0
        else:
            sms_count = len(res.json()['factory_data'])
        result = {'count': sms_count, 'info': res.json()}
        return result

    def get_sms_code(self, phone, msg_count_1):
        # msg_count_1 = self.get_sms_info(phone)['count']
        # touch send get code message
        # res1 = self.session.get(url=self.touch_code_url, params=self.touch_code_params, verify=False)
        # self.check_all(res1)
        count = 0
        while True:
            sms_info = self.get_sms_info(phone)
            msg_count_2 = sms_info['count']
            if msg_count_1 == msg_count_2:
                count = count + 1
                if count > 5:
                    raise PermissionError('{}获取验证码循环次数超过5次'.format(phone))
                time.sleep(2)
                continue
            else:
                code = sms_info['info']['factory_data'][0]['msgCode']
                break
        return code

    @classmethod
    def get_phone(cls):
        """获取可用的手机号码"""
        logger.debug(cls.get_phone.__doc__)
        # 从redis中获取电话号码
        phone = redis_handler.get('jzy_phone')
        if phone is None or len(phone) != 11:
            redis_handler.set('jzy_phone', cls.INIT_PHONE)
            return str(cls.INIT_PHONE)
        else:
            phone_next = int(phone) + 1
            redis_handler.set('jzy_phone', phone_next)
            return str(int(phone))

    def get_random_imei(self):
        '''
        :return:用随机14位数字生成15为imei码
        '''
        random_14 = ''.join(str(random.choice(range(10))) for _ in range(14))
        digit15 = 0
        for num in range(14):
            if num % 2 == 0:
                digit15 = digit15 + int(random_14[num])
            else:
                digit15 = digit15 + (int(random_14[num]) * 2) % 10 + (int(random_14[num]) * 2) / 10
        digit15 = int(digit15) % 10
        if digit15 == 0:
            digits14 = random_14 + str(digit15)
        else:
            digits14 = random_14 + str(10 - digit15)
        return digits14

    @staticmethod
    def extract_body_string(res):
        """提取返回结果中的错误信息"""
        logger.debug(LoginJZY.extract_body_string.__doc__)
        return '【系统返回结果：\n{0}】'.format(
            Tools.clean_img(res.html.text.strip()).replace('&nbsp', ' ').replace('<br>', '\n'))

    def check_all(self, res):
        """一次性检查所有项"""
        # self.check_session(res)
        self.check_response_status(res)
        self.check_response_format(res)
        self.check_response_status_0(res)

    def check_response_status(self, res):
        """
        # 检查接口响应是否异常
        :param res:
        :return:
        """
        _msg = ''
        if not isinstance(res, Response):
            logger.warning('传入的检查对象不是Response类型，请检查！')
            return None
        if res.status_code == 502:
            _msg = '服务【{}】不可用，请检查服务是否启动'.format(self.login_domain.split('.')[0])
        elif res.status_code == 404:
            _msg = '找不到接口：{}，请检查地址是否变更'.format(res.url)
        elif res.status_code >= 400:
            Tools.format_print(res)
            _msg = '接口响应异常，请检查！接口返回内容：{}'.format(self.extract_body_string(res))
        else:
            return True
        logger.error(_msg)
        raise ServiceUnavailableException(_msg)

    def check_response_status_0(self, res):
        logger.debug(res.text)
        if res.status_code == 200 and int(res.json()['status']) != 0:
            _msg = '接口响应异常：{}'.format(res.json()['message'])
            raise ServiceUnavailableException(_msg)

    def check_response_format(self, res):
        """
        # 检查接口响应是否为json格式
        :param res:
        :return:
        """
        if not isinstance(res, Response):
            logger.warning('传入的检查对象不是Response类型，请检查！')
            return None
        try:
            result = res.json()
        except Exception as e:
            _msg = '接口{}响应格式不是JSON，接口返回内容：\n{}'.format(res.url.split('?')[0], self.extract_body_string(res))
            if logger.parent.level > 10:
                Tools.format_print(res)
            logger.warning(_msg)
            raise ResponseFormatException(_msg)
        return result
