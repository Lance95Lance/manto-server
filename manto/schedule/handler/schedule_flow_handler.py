# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : Liuchangzhao
# @FILE     : schedule_flow_handler.py
# @Time     : 6/30/2020 上午 10:42
# @Software : PyCharm
import json
import logging
from manto.schedule.models import ScheduleDispatchDetail
from utils.web_function.model_util import ModelUtil
from manto.schedule.handler.schedule_model_handler import ScheduleModelHandler as smh
from manto.schedule.handler.db2_handler import Db2Handler
from manto.schedule.serializers import ScheduleConfigSerializer, ScheduleConfig, ScheduleDispatchListSerializer, \
    ScheduleDispatchDetailSerializer, ScheduleResultSerializer, ScheduleSequenceSerializer
from manto.schedule.models import ScheduleDispatchList as sdl_model, ScheduleDispatchDetail
from utils.web_function.model_util import ModelUtil
from utils.web_function.common_util import CommonUtil
from utils.web_function.CommonResponse import BaseResponse
from rest_framework.response import Response

logger = logging.getLogger('manto.common')


class ScheduleFlowHandler:
    def __init__(self, case_id):
        self.db2_handler = Db2Handler()
        self.model_handler = smh()
        self.case_id = case_id
        self.is_all_schedule_flag = True if case_id == "" or case_id is None else False
        self.need_run_data = None
        self.dispatch_no = None
        self.schedule_config_id = None
        self.need_assert_data = None

    def flow_control(self):
        """流程控制"""

        logger.info(f"----------------------------进入flow Control------------------------------")

        # 捞取待run的数据集
        flag, message = self.search_need_run_data()
        if flag is False:
            return False, message

        scs_searializer = ScheduleConfigSerializer(self.need_run_data, many=True)

        # 增加一条主任务
        self.set_dispath_list()

        try:
            for data in scs_searializer.data:

                logger.info(f"--------------进入明细调度-------------")

                self.schedule_config_id = data["id"]

                logger.info(f"目前处理的batch为 {data['batch_group_desc']} : {data['batch_job_desc']}")
                logger.info(f"{data['batch_group_name']} - {data['batch_job_name']} - {data['batch_job_param']}")

                flag, message = self.clean_and_ready(data["clean_table"],
                                                     data["ready_table"])
                if flag is False:
                    logger.error(f"清理准备数据失败, 配置项id {self.schedule_config_id} {message}")
                    continue

                flag, message = self.run_batch()
                if flag is False:
                    logger.error(f"run batch 失败, 配置项id {self.schedule_config_id} {message}")
                    continue

                flag, message = self.assert_data(data["assert_table"])
                if flag is False:
                    logger.error(f"数据验证失败, 配置项id {self.schedule_config_id} {message}")
                    continue

                logger.info(f"此batch处理结束")

        except Exception as e:
            return False, f"配置项id {self.schedule_config_id}, 错误信息{repr(e)}"
        else:
            # 处理完毕,回写主任务状态
            self.set_dispath_list_is_done()
            self.db2_handler.close_conn()
        return True, "执行成功"

    def search_need_run_data(self):
        """根据入参捞取需要处理的数据集, 按照优先级排序"""

        if ModelUtil(sdl_model).check_data_exist(is_done=False)[0]:
            return False, "有任务运行中,请稍后重试"

        # 查询对应的设定
        if self.is_all_schedule_flag:
            config_data = self.model_handler.get_all_schedule_config()
        else:
            config_data = self.model_handler.filter_schedule_config({"case_id": self.case_id})

        if len(config_data) == 0:
            return False, "未查询到对应case"

        logger.info(f"取数成功, 总共 {len(config_data)} 条batch")

        self.need_run_data = config_data
        return True, "执行成功"

    def set_dispath_list(self):
        if self.is_all_schedule_flag:
            logger.info(f"任务调度开始 >>>>>> 调度批量任务")
            # 任务调度增加一条主任务
            self.dispatch_no = CommonUtil().generate_dispatch_no()
        else:
            logger.info(f"任务调度开始 >>>>>> 调度单个任务")
            # 任务调度增加一条主任务
            self.dispatch_no = CommonUtil().generate_dispatch_no(self.case_id)

        # 任务调度,表中增加调度数据
        sdls_serializer = ScheduleDispatchListSerializer(data={"dispatch_no": self.dispatch_no})

        # 任务主表insert一条数据
        if sdls_serializer.is_valid():
            sdls_serializer.save()
        else:
            return False, sdls_serializer.errors

    def set_dispath_list_is_done(self):
        # 处理完单个任务再捞一遍所有的待assert任务
        need_assert_data = smh().get_all_no_asserted_dispatch(
            {"dispatch_no": self.dispatch_no, "is_assert": False, "is_clean": True,
             "is_ready": True})

        # 若assert任务为0即为全部处理完毕
        if len(need_assert_data) == 0:
            self.model_handler.set_dispath_list_flag()
            return True, "执行成功"

    def clean_and_ready(self, clean_table, ready_table):
        """任务调度"""
        logger.info(f"clean_and_ready >>>>>> 开始进行清理和准备数据")

        # 任务明细表insert一条数据
        sdd_serializer = ScheduleDispatchDetailSerializer(data={
            "dispatch_no": self.dispatch_no,
            "schedule_config_id": self.schedule_config_id
        })

        if sdd_serializer.is_valid():
            sdd_serializer.save()
        else:
            return False, sdd_serializer.errors

        # 开始进行数据清理
        # 循环清理表数据
        for table_name in json.loads(clean_table):
            self.db2_handler.clean_data(table_name)

        # 写表记录完成状态
        self.model_handler.set_dispath_detail_flag(self.dispatch_no, self.schedule_config_id, "is_clean")

        # 循环准备表数据
        for config_dict in json.loads(ready_table):
            self.db2_handler.ready_data(config_dict['name'], config_dict['tag'])

        self.model_handler.set_dispath_detail_flag(self.dispatch_no, self.schedule_config_id, "is_ready")

        return True, "执行成功"

    def run_batch(self):
        """任务调度"""
        logger.info(f"***调用shell 进行 run batch***")

        return True, "清理和数据准备完毕"

    def assert_data(self, assert_table):
        logger.info(f"assert_data >>>>>> 开始进行数据验证")

        self.need_assert_data = smh().get_all_no_asserted_dispatch(
            {"dispatch_no": self.dispatch_no, "is_assert": False, "schedule_config_id": self.schedule_config_id,
             "is_clean": True,
             "is_ready": True})

        if len(self.need_assert_data) == 0:
            return False, "无对应未完成的验证任务"

        try:
            # 根据设定ID取对应的配置项
            for need_assert_data in json.loads(assert_table):
                result = self.db2_handler.get_assert_result(assert_table_name=need_assert_data['name'],
                                                            assert_tag=need_assert_data['tag'],
                                                            order=need_assert_data['order'],
                                                            eliminate=need_assert_data['eliminate'])

                status = True

                for i in json.loads(result):
                    if not i["assert_flag"]:
                        status = False

                serializer = ScheduleResultSerializer(data={
                    "dispatch_no": self.dispatch_no,
                    "schedule_config_id": self.schedule_config_id,
                    "result_info": result,
                    "status": status
                })

                if serializer.is_valid():
                    serializer.save()
                    # 回写任务明细表验证状态
                    self.model_handler.set_dispath_detail_flag(self.dispatch_no,
                                                               self.schedule_config_id,
                                                               "is_assert")
        except Exception as e:
            logger.error(repr(e))
            return False, f"{repr(e)}"
        else:
            return True, "执行成功"
