# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : Liuchangzhao
# @FILE     : urls.py
# @Time     : 6/23/2020 上午 09:07
# @Software : PyCharm


from django.urls import path, include
from manto.schedule import views

urlpatterns = [
    path('api/v1/', include([
        path('scheduleConfig', views.ScheduleConfigList.as_view(), name='ScheduleConfigList'),
        path('scheduleConfig/<int:pk>', views.ScheduleConfigDetail.as_view(), name='ScheduleConfigList'),
        path('scheduleRun', views.ScheduleRun.as_view(), name='ScheduleConfigList'),
        # path('scheduleDispatch', views.ScheduleDispatchList.as_view(), name='ScheduleDispatchList'),
        # path('scheduleAssertion', views.ScheduleAssertion.as_view(), name='ScheduleAssertion'),
        # path('assertResult', views.ScheduleAssertion.as_view(), name='ScheduleAssertion'),
        path('getDispatchNoByDate', views.GetDispatchNoByDate.as_view(), name='GetDispatchNoByDate'),
        path('getReportByDispatchNo', views.GetReportByDispatchNo.as_view(), name='GetDispatchNoByDate')
    ]
    ), )
]

