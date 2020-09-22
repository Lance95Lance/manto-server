# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : Liuchangzhao
# @FILE     : schedule_model_handler.py
# @Time     : 6/24/2020 下午 01:17
# @Software : PyCharm
import json
import logging
import datetime
from django.core.exceptions import ObjectDoesNotExist
from manto.schedule.models import ScheduleConfig, ScheduleDispatchList, ScheduleDispatchDetail, ScheduleResult, \
    ScheduleSequence
from manto.schedule.serializers import ScheduleConfigSerializer, ScheduleDispatchListSerializer, \
    ScheduleDispatchDetailSerializer, ScheduleResultSerializer, ScheduleSequenceSerializer

logger = logging.getLogger('manto.common')


class ScheduleModelHandler:
    def __init__(self):
        pass

    def get_seq_no(self):
        return ScheduleSequence.objects.all()[0].seq_no

    def get_all_schedule_config(self):
        return ScheduleConfig.objects.all().order_by('batch_group_name', 'priority')

    def get_all_schedule_config_by_pk(self, pk):
        return ScheduleConfig.objects.get(pk=pk)

    def get_all_no_asserted_dispatch(self, args):
        return ScheduleDispatchDetail.objects.filter(**args)

    def get_schedule_config(self, kwargs):
        return ScheduleConfig.objects.get(**kwargs)

    def filter_schedule_config(self, kwargs):
        return ScheduleConfig.objects.filter(**kwargs).order_by('batch_group_name', 'priority')

    def filter_schedule_dispatch_no_by_date(self, date):

        data = ScheduleDispatchList.objects.filter(
            gmt_created__startswith=datetime.datetime.strptime(date, '%Y-%m-%d').date()).order_by("-id")

        serializer = ScheduleDispatchListSerializer(data, many=True)

        return serializer.data

    def filter_report_by_dispatch_no(self, dispatch_no):

        result = []
        sr = ScheduleResult.objects.filter(
            dispatch_no=dispatch_no)

        # serializer = ScheduleResultSerializer(data=sr, many=True).data
        schedule_config_id_list = []

        # 先取出此天的所有跑过的schedule_config_id
        for data in sr:
            schedule_config_id_list.append(data.schedule_config_id)

        # 再遍历此list进行数据拼接
        for schedule_config_id in set(schedule_config_id_list):
            tmp_data = []
            for assert_detail in sr:
                if assert_detail.schedule_config_id == schedule_config_id:
                    tmp_data.append({
                        "dispatch_no": assert_detail.dispatch_no,
                        "assert_table_status": assert_detail.status,
                        "result": json.loads(assert_detail.result_info)
                    })

            # 取出所有的任务号
            schedule_dispatch_list = []
            for i in tmp_data:
                schedule_dispatch_list.append(i["dispatch_no"])

            # group_by dispatch_no 排序
            final_result = []
            for i in set(schedule_dispatch_list):
                tmp_result_data = []
                for x in tmp_data:
                    if x["dispatch_no"] == i:
                        tmp_result_data.append(x["result"])
                final_result.append(
                    {
                        "dispatch_no": i,
                        "result": tmp_result_data
                    }
                )

            config_data = ScheduleConfig.objects.get(id=schedule_config_id)

            # 根据细项判断对应case是否验证通过,通过为true,不通过为False,
            case_status = True
            for i in tmp_data:
                if not i["assert_table_status"]:
                    case_status = False

            result.append(
                {
                    "batch_group_name": config_data.batch_group_name,
                    "batch_group_desc": config_data.batch_group_desc,
                    "batch_job_name": config_data.batch_job_name,
                    "batch_job_desc": config_data.batch_job_desc,
                    "priority": config_data.priority,
                    "case_status": case_status,
                    "assert_result": final_result
                }
            )

        result.sort(key=lambda x: x['priority'])
        result.sort(key=lambda x: x['batch_group_name'])

        return result

    def filter_schedule_result_by_date(self, date):
        result = []
        sr = ScheduleResult.objects.filter(
            gmt_created__startswith=datetime.datetime.strptime(date, '%Y-%m-%d').date())
        # serializer = ScheduleResultSerializer(data=sr, many=True).data
        schedule_config_id_list = []

        # 先取出此天的所有跑过的schedule_config_id
        for data in sr:
            schedule_config_id_list.append(data.schedule_config_id)

        # 再遍历此list进行数据拼接
        for schedule_config_id in set(schedule_config_id_list):
            tmp_data = []
            for assert_detail in sr:
                if assert_detail.schedule_config_id == schedule_config_id:
                    tmp_data.append({
                        "dispatch_no": assert_detail.dispatch_no,
                        "result": json.loads(assert_detail.result_info)
                    })

            # 取出所有的任务号
            schedule_dispatch_list = []
            for i in tmp_data:
                schedule_dispatch_list.append(i["dispatch_no"])

            final_result = []
            for i in set(schedule_dispatch_list):
                tmp_result_data = []
                for x in tmp_data:
                    if x["dispatch_no"] == i:
                        tmp_result_data.append(x["result"])
                final_result.append(
                    {
                        "dispatch_no": i,
                        "result": tmp_result_data
                    }
                )

            config_data = ScheduleConfig.objects.get(id=schedule_config_id)
            result.append(
                {
                    "batch_group_name": config_data.batch_group_name,
                    "batch_group_desc": config_data.batch_group_desc,
                    "batch_job_name": config_data.batch_job_name,
                    "batch_job_desc": config_data.batch_job_desc,
                    "priority": config_data.priority,
                    "assert_result": final_result
                }
            )

        result.sort(key=lambda x: x['priority'])
        result.sort(key=lambda x: x['batch_group_name'])

        return result

    def set_dispath_detail_flag(self, dispatch_no, schedule_config_id, flag_field):
        result = ScheduleDispatchDetail.objects.get(dispatch_no=dispatch_no, schedule_config_id=schedule_config_id)

        serializer = ScheduleDispatchDetailSerializer(
            result,
            data={"dispatch_no": dispatch_no,
                  "schedule_config_id": schedule_config_id,
                  flag_field: True}  # 1为完成, 0为未完成
        )

        if serializer.is_valid():
            serializer.save()
            logger.info(f"设置对应调度明细 {flag_field} 状态为:已完成")

            return True
        logger.error(f"设置对应调度明细 {flag_field} 状态失败: {repr(serializer.errors)}")
        return False

    def set_dispath_list_flag(self):
        try:
            result = ScheduleDispatchList.objects.get(is_done=False)
        except ObjectDoesNotExist as e:
            logger.error(f"没有查询到对应主任务 {repr(e)}")
            return False

        serializer = ScheduleDispatchListSerializer(
            result,
            data={"id": result.id,
                  "dispatch_no": result.dispatch_no,
                  "is_done": True}  # 1为完成, 0为未完成
        )

        if serializer.is_valid():
            serializer.save()
            logger.info(f"设置对主调度任务 {result.dispatch_no} 状态为:已完成")

            return True
        logger.error(f"设置对应主调度任务 {result.dispatch_no} 完成状态失败: {repr(serializer.errors)}")
        return False

    def set_seq_no(self, old_seq_no):

        seq_data = ScheduleSequence.objects.get(id=1)
        serializer = ScheduleSequenceSerializer(seq_data, data={"seq_no": old_seq_no + 1})
        if serializer.is_valid():
            serializer.save()
            logger.info("修改成功")
            return True

        logger.error(f"修改seq_no失败{serializer.errors}")
        return False
