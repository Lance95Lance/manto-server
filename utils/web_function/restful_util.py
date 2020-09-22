#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/19 16:48
# @Author  : Lance
# @File    : restful_util.py
from rest_framework.pagination import PageNumberPagination


class MyPageNumberPagination(PageNumberPagination):
    # 每页显示多少个
    page_size = 20
    # 最大页码数限制
    max_page_size = None
    # URL中每页显示条数的参数
    page_size_query_param = "pageSize"
    # URL中页码的参数
    page_query_param = "pageNum"
