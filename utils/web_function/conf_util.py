#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
=================================================
@Project -> File   ：camus-server -> urls
@IDE    ：PyCharm
@Author ：Lance
@Date   ：2020/3/3 8:56 上午
@Desc   ：配置工具类,用于处理各种配置的数据
==================================================
"""

from utils.rewrite_utils.MyChoiceEnum import ChoiceEnum


class ConfUtil:
    def __init__(self, enum_class):
        self.enum_class = enum_class

    def get_enum_dict(self) -> dict:
        """
        获取枚举类的配置项
        :return: dict
        """
        enum_dict = {}
        # 循环取出枚举的配置项
        for key, value in self.enum_class:
            enum_dict[key] = value

        return enum_dict
