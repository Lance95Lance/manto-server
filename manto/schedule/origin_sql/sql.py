#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
=================================================
@Project -> File   ：camus-server -> sql
@IDE    ：PyCharm
@Author ：Lance
@Date   ：2020/3/31 10:53 上午
@Desc   ：
==================================================
"""


class ScheduleResultSql:
    def __init__(self):
        pass

    def select_project_with_case_count(self):
        SLECET_PROJECT_WITH_CASE_COUNT = """
                
                SELECT project_base.*, count(case_base.id) as case_count
        FROM project_base
                 LEFT JOIN case_base ON project_base.id = case_base.project_id
        group by project_base.id
                """

        return SLECET_PROJECT_WITH_CASE_COUNT
