# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : Liuchangzhao
# @FILE     : db2_util.py
# @Time     : 6/23/2020 上午 10:35
# @Software : PyCharm

import logging
import ibm_db
import ibm_db_dbi

logger = logging.getLogger('utils')


class Db2Util:
    def __init__(self):
        conn_str = "DATABASE=CXLDB;HOSTNAME=10.20.38.55;PORT=60000;PROTOCOL=TCPIP;UID=db2user;PWD=db2ibmuser;"
        self.ibm_db_conn = ibm_db.connect(conn_str, '', '')
        self.ibm_db_api_conn = ibm_db_dbi.Connection(self.ibm_db_conn)
        self.cur = self.ibm_db_api_conn.cursor()
        self.search_sql_result = []

    def close_conn(self):
        """关闭数据库连接"""
        self.cur.close()
        ibm_db.close(self.ibm_db_conn)

        logger.info("数据库链接皆已关闭")
        return True

    def truncate_sql(self, table_name):
        sql = f"truncate table {table_name} immediate;"
        ibm_db.exec_immediate(self.ibm_db_conn, sql)
        logger.info("删除 原始表数据 成功")
        return True

    def insert_sql(self, table_name, search_result, length):
        """db2的insert_sql方法"""
        # 拼占位符
        placeholder = ""
        for i in range(0, length):
            placeholder += '?,'

        insert_sql = f"insert into {table_name} values({placeholder[:-1]})"

        try:
            stmt_insert = ibm_db.prepare(self.ibm_db_conn, insert_sql)
            ibm_db.execute_many(stmt_insert, search_result)
        except Exception as e:
            logger.error(f"{repr(e)}")
            logger.error(f"insert 数据异常,入参: {table_name, search_result, length}")
            return False, repr(e)
        else:
            logger.info("插入 TC数据->原始表 成功")
            return True, '执行成功'

    def search_sql(self, table_name: str, tag: str):
        """
        读取对应表数据
        :param table_name: 表名(TC开头的数据设定表)
        :param tag: 标记栏位
        :return: Any
        """

        if tag == "":
            sql = f"select * from {table_name}";
        else:
            sql = f"select * from {table_name} where tag = '{tag}'";

        try:
            self.cur.execute(sql)
            row = self.cur.fetchall()
        except Exception as e:
            logger.error(f"search_sql出错{sql}")
            logger.error(f"{repr(e)}")
            return False, repr(e)
        else:
            result = []
            length = 0
            for query_tuple in row:
                list_query_data = list(query_tuple)
                list_query_data.pop()
                length = len(list_query_data)
                result.append(tuple(list_query_data))

            logger.info("读取 TC表数据 成功")

            return True, tuple(result), length

    def search_data_by_assoc(self, table_name: str, tag="", order=""):

        # 如果有tag则加入where条件中
        if tag != '':
            sql = f"select * from {table_name} where tag = '{tag}'"
        else:
            sql = f"select * from {table_name}"

        # 如果有排序列则加入where条件中
        if order != "":
            sql = sql + f' order by {order}'

        try:
            stmt = ibm_db.prepare(self.ibm_db_conn, sql, {ibm_db.SQL_ATTR_CURSOR_TYPE: ibm_db.SQL_CURSOR_KEYSET_DRIVEN})
            result = ibm_db.execute(stmt)

        except Exception as e:
            logger.error(f"search_sql出错{sql}")
            logger.error(f"{repr(e)}")
            return False, repr(e)
        else:
            dict_data_result = []
            i = 1
            row = ibm_db.fetch_assoc(stmt, i)

            while row:
                i += 1
                dict_data_result.append(row)
                row = ibm_db.fetch_assoc(stmt, i)

            logger.info(f"读取 {table_name} 成功")

            return dict_data_result

    def get_assert_sql(self, origin_table_name: str, assert_table_name: str, tag: str, order: str, eliminate: []):
        """
        查询验证表数据和源表数据
        :param origin_table_name:
        :param assert_table_name: 设定表名(AR开头的数据设定表)
        :param tag: 标记栏位
        :param eliminate:
        :param order:
        :return: Any
        """

        orgin_table_data = []
        for i in self.search_data_by_assoc(origin_table_name, order=order):
            orgin_data = {}
            for k, v in i.items():
                # 排除设定中的应该排除的栏位
                if k in eliminate or k == 'TAG':
                    pass
                elif 'time' or 'date' or 'gmt' in k:
                    orgin_data[k] = str(v)
                else:
                    orgin_data[k] = v
            orgin_table_data.append(orgin_data)

        assert_table_data = []
        for i in self.search_data_by_assoc(assert_table_name, tag, order=order):
            assert_data = {}
            for k, v in i.items():
                # 排除设定中的应该排除的栏位
                if k in eliminate or k == 'TAG':
                    pass
                elif 'time' or 'date' or 'gmt' in k:
                    assert_data[k] = str(v)
                else:
                    assert_data[k] = v
            assert_table_data.append(assert_data)
        return orgin_table_data, assert_table_data


if __name__ == '__main__':
    db = Db2Util()
    db.truncate_sql('CXLKA.DTKA0270')
    result = db.search_sql('CXLKA.TCDTKA0270', 'nav')
    db.insert_sql('CXLKA.DTKA0270', result[1], result[2])
    # result = db.get_assert_sql('CXLKA.DTKA0270', 'CXLKA.TCDTKA0270', 'nav', order='CUSTOMER_NUMBER')
    # print(result[0])
    # print(result[1])

    db.close_conn()
