# -*- coding: utf-8 -*-
# @Time    : 2019-07-24 22:33
# @Author  : Lance
# @File    : prod.py

from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*', ]

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
    #     'NAME': 'manto',  # 你要存储数据的库名，事先要创建之
    #     'USER': 'root',  # 数据库用户名
    #     'PASSWORD': 'root',  # 密码
    #     'HOST': '10.20.59.67',  # 主机
    #     'PORT': '13306',  # 数据库使用的端口
    # }
}