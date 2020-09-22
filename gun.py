# -*- coding: utf-8 -*-
# @Time    : 2018-10-23 22:55
# @Author  : Lance
# @File    : gun.py

import gevent.monkey

gevent.monkey.patch_all()

import multiprocessing

debug = False
daemon = True  # 守护者模式
loglevel = 'error'  # 日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置
bind = '0.0.0.0:4396'
pidfile = 'gunicorn.pid'
accesslog = 'gunicorn-default.log'
errorlog = 'gunicorn-error.log'

# 启动的进程数
workers = 3
worker_class = 'gunicorn.workers.ggevent.GeventWorker'

x_forwarded_for_header = 'X-FORWARDED-FOR'
