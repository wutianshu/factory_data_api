#!/usr/bin/env python
# coding:utf-8

from deng.tools import Tools


class FactoryException(Exception):
    def __init__(self, message, node=None):
        self.factory_status = False
        self.factory_node = node
        self.factory_message = Tools.clean_img(message)
        self.check_node()

    def __str__(self):
        return '状态：{0}，节点：{1}，错误信息：{2}'.format(self.factory_status, self.factory_node, self.factory_message)

    def to_dict(self):
        return {'factory_status': self.factory_status,
                'factory_node': self.factory_node,
                'factory_message': self.factory_message}

    def check_node(self):
        if self.factory_node is None:
            if isinstance(self, ResponseFormatException):
                self.factory_node = '接口响应格式检查'
            elif isinstance(self, ServiceUnavailableException):
                self.factory_node = '服务可用性检查'
            elif isinstance(self, PageParsingException):
                self.factory_node = 'html页面解析'
            elif isinstance(self, ReleaseLogException):
                self.factory_node = '上线记录'
            else:
                self.factory_node = '未知节点'


class PageParsingException(FactoryException):
    pass


class ResponseFormatException(FactoryException):
    pass


class ServiceUnavailableException(FactoryException):
    pass


class BusinessBaseException(FactoryException):
    pass


class CSCustomerException(FactoryException):
    pass


class JZClueException(FactoryException):
    pass


class JZOrderException(FactoryException):
    pass


class JZSoException(FactoryException):
    pass


class ClueException(FactoryException):
    pass


class OrderException(FactoryException):
    pass


class PermissionsException(FactoryException):
    pass


class CSCRMClueException(FactoryException):
    pass


class OMSOrderException(FactoryException):
    pass


class OrderDetailsException(FactoryException):
    pass


class CsafterException(FactoryException):
    pass


class CSWorkerException(FactoryException):
    pass


class YSAdminException(FactoryException):
    pass


class DjoyException(FactoryException):
    pass


class ReleaseLogException(FactoryException):
    pass

class JZVisitException(FactoryException):
    pass
