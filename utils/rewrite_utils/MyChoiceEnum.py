#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
=================================================
@Project -> File   ：camus-server -> urls
@IDE    ：PyCharm
@Author ：Lance
@Date   ：2020/3/3 8:56 上午
@Desc   ：check readme.md
==================================================
"""

from enum import Enum, EnumMeta


class ChoiceEnumMeta(EnumMeta):
    def __iter__(self):
        """重写enum源类, 适用于model"""
        return ((tag.name, tag.value) for tag in super().__iter__())


class ChoiceEnum(Enum, metaclass=ChoiceEnumMeta):
    """
    Enum for Django ChoiceField use.

    Usage::
        class Languages(ChoiceEnum):
            ch = "Chinese"
            en = "English"
            fr = "French"
        class MyModel(models.Model):
            language = models.CharField(max_length=20, choices=Colors)
    """


class MyChoiceEnumUtil:
    def __init__(self, my_enum):
        self.my_enum = my_enum

    def get_key_from_enum_value(self, my_enum_value):
        my_enum_key = None
        for key, value in self.my_enum:
            if value == my_enum_value:
                my_enum_key = key

        return my_enum_key


if __name__ == '__main__':
    pass
