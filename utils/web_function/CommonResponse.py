#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/19 15:14
# @Author  : Lance
# @File    : CommonResponse.py


class BaseResponse(object):
    """基础报文返回类"""

    def __init__(self, code=200, message='success', data=None):
        self.success = code == 200
        self.code = code
        self.message = message
        self.data = data

    def context(self):
        return {
            'code': self.code,
            'message': self.message,
            'success': self.success,
            'data': self.data,
        }


class PageResponse(BaseResponse):
    def __init__(self, entries=None, **page_info):
        self.entries = entries
        self.page_info = page_info
        super(PageResponse, self).__init__()

    def context(self):
        return {
            'code': self.code,
            'message': self.message,
            'success': self.success,
            'data': {
                'entries': self.entries,
                'page': {
                    'current': self.page_info['current'],
                    'pageSize': self.page_info['pageSize'],
                    'totalRecords': self.page_info['totalRecords'],
                }
            },
        }
