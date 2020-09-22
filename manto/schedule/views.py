from django.shortcuts import render
import logging

# Create your views here.
from rest_framework.views import APIView
import json

from manto.schedule.handler.schedule_model_handler import ScheduleModelHandler as smh
from manto.schedule.handler.db2_handler import Db2Handler
from manto.schedule.serializers import ScheduleConfigSerializer, ScheduleConfig, ScheduleDispatchListSerializer, \
    ScheduleDispatchDetailSerializer, ScheduleResultSerializer, ScheduleSequenceSerializer
from manto.schedule.models import ScheduleDispatchList as sdl_model, ScheduleDispatchDetail
from utils.web_function.model_util import ModelUtil
from utils.web_function.common_util import CommonUtil
from utils.web_function.CommonResponse import BaseResponse
from rest_framework.response import Response
from manto.schedule.handler.schedule_flow_handler import ScheduleFlowHandler

logger = logging.getLogger('manto.common')


class ScheduleConfigList(APIView):
    """设定表接口"""

    def get(self, request):
        """获取所有设定"""

        result = ScheduleConfig.objects.all()
        serializer = ScheduleConfigSerializer(result, many=True)

        return Response(BaseResponse(data=serializer.data).context())

    def post(self, request):
        """
        新增设定
        """

        logger.info(f"增加case >>>>>> 新增设定,入参：{request.data}")
        format_request_data = {
            'batch_group_name': request.data.get('batch_group_name', None),
            "batch_group_desc": request.data.get('batch_group_desc', None),
            'job': request.data.get('job', None),
        }

        model_handler = smh()
        old_seq_no = model_handler.get_seq_no()
        config_data = []

        try:
            for jobs_info in format_request_data['job']:
                data = {
                    "case_id": str(old_seq_no + 1).zfill(7),
                    "batch_group_name": format_request_data['batch_group_name'],
                    "batch_group_desc": format_request_data['batch_group_desc'],
                    "pacakge_name": jobs_info['pacakge_name'],
                    "batch_job_name": jobs_info['batch_job_name'],
                    "batch_job_desc": jobs_info['batch_job_desc'],
                    "batch_job_param": jobs_info['batch_job_param'],
                    "priority": jobs_info['priority'],
                    "clean_table": json.dumps(jobs_info['batch_data']['clean']['table']),
                    "ready_table": json.dumps(jobs_info['batch_data']['ready']['table']),
                    "assert_table": json.dumps(jobs_info['batch_data']['assert']['table']),
                }

                schedule_config_serializer = ScheduleConfigSerializer(data=data)

                if schedule_config_serializer.is_valid():
                    config_data.append(ScheduleConfig(**schedule_config_serializer.data))
                else:
                    logger.error(f"增加case >>>>>> 序列化失败 {schedule_config_serializer.errors}")

                    return Response(
                        BaseResponse(code=400,
                                     message=f"增加case >>>>>> 序列化失败 {schedule_config_serializer.errors}").context())

        except Exception as e:
            logger.error(repr(e))
            return Response(BaseResponse(code=400, message=repr(e)).context())

        try:

            # 批量写入表中
            ScheduleConfig.objects.bulk_create(config_data)
        except Exception as e:
            logger.error(repr(e))
            return Response(BaseResponse(code=400, message=f"增加case >>>>>> 批量写入表失败 {repr(e)}").context())
        else:
            if model_handler.set_seq_no(old_seq_no):
                return Response(BaseResponse(message="增加case >>>>>> 新增设定成功").context())


class ScheduleConfigDetail(APIView):
    """修改对应设定"""

    # TODO:这个接口后续再提供，目前先进行主功能的完善
    def put(self, request, pk):
        logger.info(f"batch任务 >>>>>> 修改设定,入参：设定ID：{pk}")
        logger.info(f"batch任务 >>>>>> 修改设定,入参：{request.data}")

        try:

            format_request_data = {
                'batch_desc': request.data.get('batch_desc', None),
                "batch_group_name": request.data.get('batch_group_name', None),
                "batch_param": request.data.get('batch_param', None),
                'batch_job_name': request.data.get('batch_job_name', None),
                'clean_table': json.dumps(request.data['batch_data']['clean']['table']),
                'ready_table': json.dumps(request.data['batch_data']['ready']['table']),
                'assert_table': json.dumps(request.data['batch_data']['assert']['table']),
            }
        except Exception as e:
            logger.error(repr(e))
            return Response(BaseResponse(code=400, message=repr(e)).context())
        else:

            serializer = ScheduleConfigSerializer(ScheduleConfig.objects.get(id=pk), data=format_request_data)
            if serializer.is_valid():
                serializer.save()
                return Response(BaseResponse(message="修改成功").context())
            return Response(BaseResponse(code=500, message=serializer.errors).context())


class ScheduleDispatchList(APIView):
    """任务列表接口"""

    def post(self, request):
        """任务调度"""
        batch_job_name = request.POST.get('batch_job_name', None)
        logger.info(f"batch任务 >>>>>> 任务调度接口,入参：{batch_job_name}")

        model_handler = smh()

        if ModelUtil(sdl_model).check_data_exist(is_done=False)[0]:
            return Response(BaseResponse(code=400, message="有任务运行中,请稍后重试").context())

        is_all_schedule_flag = False
        # 跑全部任务
        if batch_job_name == '' or batch_job_name is None:
            logger.info(f"batch任务 >>>>>> 调度批量任务")
            # 任务调度增加一条主任务
            dispatch_no = CommonUtil().generate_dispatch_no()
            is_all_schedule_flag = True
        else:
            logger.info(f"batch任务 >>>>>> 调度单个任务")
            # 任务调度增加一条主任务
            dispatch_no = CommonUtil().generate_dispatch_no(batch_job_name)

        sdls_serializer = ScheduleDispatchListSerializer(data={"dispatch_no": dispatch_no})

        if sdls_serializer.is_valid():
            sdls_serializer.save()
        else:
            return Response(BaseResponse(code=400, message=sdls_serializer.errors).context())

        # 任务明细增加对应明细任务
        # 查询对应的设定
        if is_all_schedule_flag:
            config_data = model_handler.get_all_schedule_config()
        else:
            config_data = model_handler.filter_schedule_config({"batch_job_name": batch_job_name})

        dispatch_detail = []

        for data in config_data:
            pks = {
                "dispatch_no": dispatch_no,
                "schedule_config_id": data.id
            }
            dispatch_detail.append(ScheduleDispatchDetail(**pks))

        try:
            # 批量写入任务明细表中
            ScheduleDispatchDetail.objects.bulk_create(dispatch_detail)
        except Exception as e:
            logger.error(repr(e))
            return Response(BaseResponse(code=400, message=repr(e)).context())

        # 开始进行数据清理

        # 创建db2链接
        db2_handler = Db2Handler()
        for get_config in config_data:
            # 循环清理表数据
            for table_name in json.loads(get_config.clean_table):
                db2_handler.clean_data(table_name)

            # 写表记录完成状态
            model_handler.set_dispath_detail_flag(dispatch_no, get_config.id, "is_clean")

            # 循环准备表数据
            for config_dict in json.loads(get_config.ready_table):
                db2_handler.ready_data(config_dict['name'], config_dict['tag'])

            model_handler.set_dispath_detail_flag(dispatch_no, get_config.id, "is_ready")

        db2_handler.close_conn()

        logger.info("batch任务 >>>>>> 任务调度成功")
        return Response(BaseResponse(message="任务调度成功").context())


class GetDispatchNoByDate(APIView):
    """根据日期获取任务号"""

    def get(self, request):
        """获取指定日期的验证数据"""
        date = request.GET.get('date', None)
        if date is None:
            return Response(BaseResponse(code=400, message="日期必填!").context())

        return Response(BaseResponse(data=smh().filter_schedule_dispatch_no_by_date(date)).context())


class GetReportByDispatchNo(APIView):
    """根据任务号获取指定assert报告"""

    def get(self, request):
        """获取指定日期的验证数据"""
        dispatch_no = request.GET.get('dispatch_no', None)
        if dispatch_no is None or dispatch_no == '':
            return Response(BaseResponse(code=400, message="任务号必填!!!").context())

        return Response(BaseResponse(data=smh().filter_report_by_dispatch_no(dispatch_no)).context())


class ScheduleAssertion(APIView):
    """数据比对接口"""

    def get(self, request):
        """获取指定日期的验证数据"""
        date = request.GET.get('date', None)
        if date is None:
            return Response(BaseResponse(code=400, message="日期必填!").context())

        return Response(BaseResponse(data=smh().filter_schedule_result_by_date(date)).context())

    def post(self, request):
        """对已clean和已ready的任务进行验证数据"""
        batch_job_name = request.POST.get('batch_job_name', None)
        logger.info(f"batch任务 >>>>>> 数据验证接口,入参：{batch_job_name}")

        model_handler = smh()
        # 验证全部任务
        if batch_job_name == '' or batch_job_name is None:
            logger.info(f"batch任务 >>>>>> 验证批量任务")
            # 任务调度增加一条主任务
            no_asserted_dispatch = model_handler.get_all_no_asserted_dispatch(
                {"is_assert": False, "is_clean": True, "is_ready": True})
        else:
            logger.info(f"batch任务 >>>>>> 验证单个任务")
            # 任务调度增加一条主任务
            config_data = model_handler.get_schedule_config(
                {"batch_job_name": batch_job_name})
            no_asserted_dispatch = smh().get_all_no_asserted_dispatch(
                {"is_assert": False, "schedule_config_id": config_data.id, "is_clean": True,
                 "is_ready": True})

        logger.info(f"batch任务 >>>>>> 数据验证, 总共需要验证 {len(no_asserted_dispatch)} 个任务")

        if len(no_asserted_dispatch) == 0:
            return Response(BaseResponse(code=400, message="无对应未完成的验证任务").context())

        db2_handler = Db2Handler()

        try:
            # 先取任务明细
            for dispatch_detail in no_asserted_dispatch:
                schedule_config_data = model_handler.get_all_schedule_config_by_pk(dispatch_detail.schedule_config_id)
                # 根据设定ID取对应的配置项
                for need_assert_data in json.loads(schedule_config_data.assert_table):
                    result = db2_handler.get_assert_result(assert_table_name=need_assert_data['name'],
                                                           assert_tag=need_assert_data['tag'],
                                                           order=need_assert_data['order'],
                                                           eliminate=need_assert_data['eliminate'])
                    logger.info(f"验证设定 {schedule_config_data.batch_job_name} 完成")

                    serializer = ScheduleResultSerializer(data={
                        "dispatch_no": dispatch_detail.dispatch_no,
                        "schedule_config_id": dispatch_detail.schedule_config_id,
                        "result_info": result
                    })

                    if serializer.is_valid():
                        serializer.save()
                        # 回写任务明细表验证状态
                        model_handler.set_dispath_detail_flag(dispatch_detail.dispatch_no,
                                                              dispatch_detail.schedule_config_id,
                                                              "is_assert")
        except Exception as e:
            db2_handler.close_conn()

            logger.error(repr(e))
            return Response(BaseResponse(code=400, message=repr(e)).context())
        else:
            db2_handler.close_conn()

            no_asserted_dispatch = smh().get_all_no_asserted_dispatch(
                {"is_assert": False, "is_clean": True,
                 "is_ready": True})

            if len(no_asserted_dispatch) == 0:
                model_handler.set_dispath_list_flag()
            return Response(BaseResponse(message="数据验证成功").context())


class ScheduleRun(APIView):
    def post(self, request):
        case_id = request.POST.get('case_id', None)
        sfh = ScheduleFlowHandler(case_id)

        # 执行任务流
        flag, message = sfh.flow_control()
        if flag is False:
            return Response(BaseResponse(message=message).context())

        return Response(BaseResponse(message="任务调度成功").context())
