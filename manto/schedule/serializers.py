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
import json

from rest_framework import serializers
from manto.schedule.models import *


class Jsonserializer(serializers.JSONField):
    """json序列化器"""
    default_error_messages = {
        'invalid_json': ('无效的json数据格式')
    }

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            json.loads(data)
        except (TypeError, ValueError):
            self.fail('invalid_json')
        return data


class ScheduleSequenceSerializer(serializers.ModelSerializer):
    gmt_created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    gmt_modified = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ScheduleSequence
        fields = '__all__'


class ScheduleConfigSerializer(serializers.ModelSerializer):
    clean_table = Jsonserializer()
    ready_table = Jsonserializer()
    assert_table = Jsonserializer()
    gmt_created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    gmt_modified = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ScheduleConfig
        fields = '__all__'


class ScheduleDispatchListSerializer(serializers.ModelSerializer):
    gmt_created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    gmt_modified = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ScheduleDispatchList
        fields = '__all__'


class ScheduleDispatchDetailSerializer(serializers.ModelSerializer):
    gmt_created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    gmt_modified = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ScheduleDispatchDetail
        fields = '__all__'


class ScheduleResultSerializer(serializers.ModelSerializer):
    result_info = Jsonserializer()
    gmt_created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    gmt_modified = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ScheduleResult
        fields = '__all__'
