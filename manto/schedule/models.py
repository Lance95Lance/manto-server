# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : Liuchangzhao
# @FILE     : urls.py
# @Time     : 6/23/2020 上午 09:07
# @Software : PyCharm

from django.db import models


# Create your models here.


class ScheduleSequence(models.Model):
    """任务序列号"""
    seq_no = models.BigIntegerField(verbose_name='序列号')
    gmt_created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    gmt_modified = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    class Meta:
        db_table = "manto_schedule_sequence"
        ordering = ['gmt_created']


class ScheduleConfig(models.Model):
    """任务设定表"""
    case_id = models.TextField(verbose_name='caseid,补零到百万')
    batch_group_name = models.CharField(verbose_name='批次group名', max_length=255)
    batch_group_desc = models.TextField(verbose_name='批次group描述')
    pacakge_name = models.CharField(verbose_name='代码包名', max_length=255)
    batch_job_name = models.CharField(verbose_name='批次job名', max_length=255)
    batch_job_desc = models.TextField(verbose_name='批次描述')
    batch_job_param = models.CharField(verbose_name='批次参数', max_length=255)
    priority = models.BigIntegerField(verbose_name='batch执行优先级')
    clean_table = models.TextField(verbose_name='需清理的源表json集合:CXLAG.DTAGA008')
    ready_table = models.TextField(verbose_name='准备数据的json集合:CXLAG.TCDTAGA009')
    assert_table = models.TextField(verbose_name='验证数据的json集合:CXLAG.ARDTAGA008')
    gmt_created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    gmt_modified = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    class Meta:
        db_table = "manto_schedule_config"
        ordering = ['gmt_created']
        unique_together = ["batch_group_name", "pacakge_name", "batch_job_name", "batch_job_param"]
        indexes = [
            models.Index(fields=['batch_job_name'], name='sc_idx')
        ]


class ScheduleDispatchList(models.Model):
    """任务总调度列表"""
    dispatch_no = models.CharField(verbose_name='调度号(时间戳-批次名)', unique=True, max_length=255)
    is_done = models.BooleanField(verbose_name='是否完成0/1', default=False)
    gmt_created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    gmt_modified = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    class Meta:
        db_table = "manto_schedule_dispatch_list"
        ordering = ['gmt_created']
        # UniqueConstraint(fields=['teacher_cert_no', 'teacher_name'], name='unique_batch')
        indexes = [
            models.Index(fields=['dispatch_no'], name='sdl_idx')
        ]


class ScheduleDispatchDetail(models.Model):
    """任务调度详情"""
    dispatch_no = models.CharField(verbose_name='调度号(时间戳-批次名)', max_length=255)
    schedule_config_id = models.BigIntegerField(verbose_name='设定表id')
    is_clean = models.BooleanField(verbose_name='是否完成0/1', default=False)
    is_ready = models.BooleanField(verbose_name='是否完成0/1', default=False)
    is_assert = models.BooleanField(verbose_name='是否完成0/1', default=False)
    gmt_created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    gmt_modified = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    class Meta:
        db_table = "manto_schedule_dispatch_detail"
        ordering = ['gmt_created']
        unique_together = ["dispatch_no", "schedule_config_id"]
        indexes = [
            models.Index(fields=['dispatch_no', 'schedule_config_id'], name='sdd_idx')
        ]


class ScheduleResult(models.Model):
    """任务结果"""
    dispatch_no = models.CharField(verbose_name='调度号(时间戳-批次名)', max_length=255)
    schedule_config_id = models.BigIntegerField(verbose_name='设定表id')
    result_info = models.TextField(verbose_name='验证结果json')
    status = models.BooleanField(verbose_name='是否完成0/1')
    gmt_created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    gmt_modified = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    class Meta:
        db_table = "manto_schedule_result"
        ordering = ['gmt_created']
        # UniqueConstraint(fields=['dispatch_no', 'schedule_config_id'], name='unique_sdd')
        indexes = [
            models.Index(fields=['dispatch_no'], name='sr_idx')
        ]
