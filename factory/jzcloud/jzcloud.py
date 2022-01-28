#!/usr/bin/env python
# coding=utf-8
import logging
import os
import requests
import random
from faker import Faker
from urllib3 import encode_multipart_formdata
from factory.common.loginJZY import LoginJZY
from factory.jzcloud import get_idcards_image_path

logger = logging.getLogger(__name__)
faker = Faker('zh_CN')


class JZCloud(LoginJZY):
    """
    #
    """

    def __init__(self, phone, env='stable', online_urm_se=requests.session()):
        super(JZCloud, self).__init__(phone, env, online_urm_se)
        logger.debug('初始化{}类实例'.format(self.__class__))

    def upload_image(self, is_id=False):
        '''文件上传接口'''
        upload_domain = 'fileupload.test.cn'
        upload_path = 'file-upload'
        upload_url = '{}{}{}'.format('http://', upload_domain, upload_path)

        querystring = {
            "path": '/crm/custom/avatar',
        }
        if is_id:
            idCard = random.choice(get_idcards_image_path())
            file_path = idCard['file_path']
            file_name = os.path.basename(file_path).split('-')[1]
            logger.info(file_path)
        else:
            file_path = random.choice(query_img_jpg())
            file_name = os.path.basename(file_path)
        fields = {
            'file': (file_name, open(file_path, 'rb').read())
        }
        encode_fields = encode_multipart_formdata(fields)
        data = encode_fields[0]
        header = {
            'Content-Type': encode_fields[1]
        }
        res = self.session.post(url=upload_url, headers=header, params=querystring, data=data, verify=False)

        logger.debug(res.text)

        image_url = res.json()['url']
        if is_id:
            return {'url': image_url, 'name': idCard['name'], 'id': idCard['id']}
        else:
            return image_url

    def get_random_customer(self):
        search_path = '/searchCustomer'
        search_url = '{}{}{}'.format(self.protocol, self.crm_domain, search_path)
        data = {
            'pageSize': 10,
            'customerFollowUpStatus': '',
            'orderStatus': '',
            'sortFiled': '',
            'pageNumber': ''
        }
        res = self.session.post(url=search_url, data=data, verify=False)
        self.check_all(res)
        count = len(res.json()['data']['content'])
        try:
            index = random.randrange(count)
        except ValueError:
            raise PermissionError('请确认公司下是否添加了客户')
        customer_crmid = res.json()['data']['content'][index]['customerNo']
        service_type = res.json()['data']['content'][index]['workingModeName']
        if not service_type:
            service_type = '未知'
        service_typeid = res.json()['data']['content'][index]['workingModeId']

        customer_detail_path = '/customerDetail'
        customer_detail_url = '{}{}{}'.format(self.protocol, self.crm_domain, customer_detail_path)
        res = self.session.post(url=customer_detail_url,
                                data={'customerNo': customer_crmid},
                                verify=False)
        self.check_all(res)
        customer_name = res.json()['data']['ecrmCustomerDTO']['customerName']
        customer_phone = res.json()['data']['ecrmCustomerDTO']['customerTel']
        customer_idcard = res.json()['data']['ecrmCustomerDTO']['customerIdentityId']

        customer_info = {
            'customer_crmid': customer_crmid,
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'customer_idcard': customer_idcard,
            'service_type': service_type,
            'service_typeid': service_typeid
        }
        return customer_info
