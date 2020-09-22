#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime
import time


class CommonUtil:
    def __init__(self):
        pass

    def get_current_week(self):
        monday, sunday = datetime.date.today(), datetime.date.today()

        one_day = datetime.timedelta(days=1)
        while monday.weekday() != 0:
            monday -= one_day
        while sunday.weekday() != 6:
            sunday += one_day
        # 返回当前的星期一和星期天的日期
        return monday, sunday

    def get_date_extrapolation(self, date, days):
        # 日期转换
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        # 选择要提前的天数
        change_time = date + datetime.timedelta(days=days)
        # 格式化处理
        change_time_format = change_time.strftime('%Y-%m-%d')

        return change_time_format

    def get_date_interval(self, begin_date, end_date):

        begin_date = time.strptime(begin_date, '%Y-%m-%d')

        end_date = time.strptime(end_date, '%Y-%m-%d')

        interval_date = datetime.datetime(end_date[0], end_date[1], end_date[2]) - datetime.datetime(begin_date[0],
                                                                                                     begin_date[1],
                                                                                                     begin_date[2])
        # 转换interval_date类型
        data = interval_date.days

        return data

    def generate_dispatch_no(self, job_name='ALL'):
        """获取时间戳-job_name"""
        return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + '-' + job_name


if __name__ == '__main__':
    # datetime.strptime("2016-06-07", "%Y-%m-%d")
    # print(CommonUtil().get_date_interval('2018-01-01', '2018-02-12'))
    # print(CommonUtil().get_current_week())
    print(CommonUtil().generate_dispatch_no())
