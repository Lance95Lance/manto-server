#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
=================================================
@Project -> File   ：camus-server -> model_utils
@IDE    ：PyCharm
@Author ：Lance
@Date   ：2020/3/18 2:48 下午
@Desc   ：model工具类
==================================================
"""
import logging

logger = logging.getLogger('camus.common')


class ModelUtil:
    def __init__(self, model_class):
        self.model_class = model_class

    def check_data_exist(self, **kwargs) -> tuple:
        """
        检查数据是否存在:
        存在返回: (True，查询结果query)
        不存在返回: (False, 文案)
        """
        try:
            return True, self.model_class.objects.get(**kwargs)
        except self.model_class.DoesNotExist:
            # 不存在返回False
            return False, '示例不存在'

