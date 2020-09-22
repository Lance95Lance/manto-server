#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
=================================================
@Project -> File   ：camus-server -> excel_utils
@IDE    ：PyCharm
@Author ：Lance
@Date   ：2020/3/26 1:41 下午
@Desc   ：
==================================================
"""
import json
import os

from camus.settings.base import FILES_DIR
import xlrd


class ExcelUtils:
    def __init__(self, file_path, sheet_index=0):
        self.file_path = file_path
        self.sheet = xlrd.open_workbook(self.file_path).sheet_by_index(sheet_index)
        self.nrows = self.sheet.nrows
        self.title_row = []
        self.excel_list = []

    def read_excel(self):
        """读取excel"""
        for row_index in range(0, self.nrows):
            if row_index == 0:
                self.title_row = self.sheet.row_values(row_index)
            else:
                excel_dict = {}
                for title_index in range(1, len(self.title_row)):
                    excel_dict[self.title_row[title_index]] = self.sheet.row_values(row_index)[title_index]

                self.excel_list.append(excel_dict)

        return self.excel_list


if __name__ == '__main__':
    ExcelUtils(os.path.join(FILES_DIR, '2020032510241747062.xlsx')).read_excel()
