# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : Liuchangzhao
# @FILE     : db2_handler.py
# @Time     : 6/24/2020 上午 09:10
# @Software : PyCharm
import json
import logging

from utils.base_utils.db2_util import Db2Util

logger = logging.getLogger('manto.common')


class Db2Handler(Db2Util):
    def __init__(self):
        super(Db2Handler, self).__init__()

    def clean_data(self, origin_table_name):
        """清理数据"""
        if self.truncate_sql(origin_table_name):
            logger.info(f"Db2Handler >>> 执行truncate {origin_table_name} 结束")

        return True

    def ready_data(self, ready_table_name, ready_tag):
        """准备数据"""

        search_result = self.search_sql(ready_table_name, ready_tag)

        if search_result[0]:
            logger.info(f"Db2Handler >>> 查询ready表数据 {ready_table_name} 成功")
            if self.insert_sql(ready_table_name.replace('TC', ''), search_result[1], search_result[2])[0]:
                return True

        return False

    def get_assert_list(self, assert_table_name, auxiliary_table, main_table, index, vars_flag, assert_flag,
                        index_error=False):

        result = {
            'origin': {
                'table_name': assert_table_name.replace('AR', ''),
                'table_data': ""
            },
            "assert": {
                'table_name': assert_table_name,
                'table_data': ""
            },
            'assert_flag': assert_flag
        }


        # 如果vars_flag为真,则assert_data是main_table
        # 如果vars_flag为假,则origin_data是main_table
        if index_error and vars_flag:
            result['assert']['table_data'] = [main_table[index]]
        elif index_error and vars_flag is False:
            result['origin']['table_data'] = [main_table[index]]
        elif index_error is False:
            result['origin']['table_data'] = [auxiliary_table[index] if vars_flag is True else main_table[index]]
            result['assert']['table_data'] = [main_table[index] if vars_flag is True else auxiliary_table[index]]

        return result

    def get_assert_result(self, assert_table_name: str, assert_tag: str, order: str, eliminate: []):
        """验证数据"""
        orgin_data, assert_data = self.get_assert_sql(assert_table_name.replace('AR', ''), assert_table_name,
                                                      assert_tag, order, eliminate)

        vars_flag = True

        main_table, auxiliary_table = assert_data, orgin_data

        # 如果源表数据length>验证表length,进行变量互换
        if len(orgin_data) > len(assert_data):
            vars_flag = False
            main_table, auxiliary_table = orgin_data, assert_data

        asset_result = []

        # 用length最大的list进行循环取下标
        for index, data in enumerate(main_table):
            assert_flag = True

            try:
                for k, v in data.items():
                    if k != 'TAG':
                        if v != auxiliary_table[index][k]:
                            assert_flag = False
            except IndexError as e:
                # 数组越界直接set False
                assert_flag = False
                asset_result.append(
                    self.get_assert_list(assert_table_name, auxiliary_table, main_table, index, vars_flag,
                                         assert_flag, index_error=True))
            else:
                asset_result.append(
                    self.get_assert_list(assert_table_name, auxiliary_table, main_table, index, vars_flag,
                                         assert_flag))

        return json.dumps(asset_result)


if __name__ == '__main__':
    # Db2Handler().clean_and_input(origin_table_name='CXLKA.DTKA0270', ready_table_name='CXLKA.TCDTKA0270',
    #                              ready_tag='nav')
    db2_handler = Db2Handler()
    db2_handler.get_assert_result(assert_table_name='CXLKA.ARDTKA0270', assert_tag='nav', order='CUSTOMER_NUMBER', eliminate=["USE_DATE", "SERVICE_ITEM_CD"])
    db2_handler.close_conn()