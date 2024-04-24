# -*- coding: utf-8 -*-
__author__ = "ruijing.li"

import pandas as pd
import logging
from datetime import datetime
from config import MONTH_CONVERT

class Sorter:
    def __init__(self, dataset: pd.DataFrame, myconfig):
        self.meta = {}
        self.dataset = dataset
        self.sort_fields = myconfig.sort_fieldsOID
        self.sort_order = myconfig.sort_order
        self.sort_dateField = myconfig.sort_dateFields
        self.sort_datetype = myconfig.sort_dateFormat

    @property
    def data(self):
        data = self.dataset
        if len(data) > 0:
            # 所有的排序变量，仅根据数据集有的变量进行排序
            sort_fields = [x.lower() for x in self.sort_fields]
            filtered_sort_fields = [var for var in sort_fields if var in data]
            logging.warning("当前排序变量: {0}".format(filtered_sort_fields))

            # 日期类型的排序变量：生成新日期型变量，使用0000补充未知年，01补充未知月，01补充未知日
            date_fields = [x.lower() for x in self.sort_dateField]
            filtered_date_fields = [var for var in date_fields if var in data]

            logging.warning("其中日期排序变量: {0}".format(filtered_date_fields))

            if len(filtered_date_fields) > 0:
                data_converted = convert_date(data, filtered_date_fields, self.sort_datetype)
            else:
                data_converted = data

            filtered_date_fields_Con = ["{0}{1}".format(var, "_Con") for var in filtered_date_fields]
            date_fields_sort = dict(zip(filtered_date_fields, filtered_date_fields_Con))

            # 使用新生成的变量替换所有排序变量中的位置之后进行排序。
            sort_var = [date_fields_sort[var] if var in date_fields_sort else var for var in filtered_sort_fields]
            data_sorted = data_converted.sort_values(by=sort_var,
                                                     ascending=self.sort_order)
        else:
            data_sorted = data
        return data_sorted


def fill_unknow_date(date: str, datetype):
    day = ""
    month = ""
    year = ""

    if datetype == "dd/MMM/yyyy":
        day = date.split("/")[0].rjust(2,'0')
        month = date.split("/")[1]
        year = date.split("/")[2].rjust(4,'0')
    elif datetype == "dd/mm/yyyy":
        day = date.split("/")[0].rjust(2,'0')
        month = date.split("/")[1].rjust(2,'0')
        year = date.split("/")[2].rjust(4,'0')
    elif datetype == "dd-MMM-yyyy":
        day = date.split("-")[0].rjust(2,'0')
        month = date.split("-")[1]
        year = date.split("-")[2].rjust(4,'0')
    elif datetype == "dd-mm-yyyy":
        day = date.split("-")[0].rjust(2,'0')
        month = date.split("-")[1].rjust(2,'0')
        year = date.split("-")[2].rjust(4,'0')
    elif datetype == "dd MMM yyyy":
        day = date.split()[0].rjust(2,'0')
        month = date.split()[1]
        year = date.split()[2].rjust(4,'0')
    elif datetype == "dd mm yyyy":
        day = date.split()[0].rjust(2, '0')
        month = date.split()[1].rjust(2, '0')
        year = date.split()[2].rjust(4, '0')
    elif datetype == "yyyy/mm/dd":
        year = date.split("/")[0].rjust(4,'0')
        month = date.split("/")[1].rjust(2,'0')
        day = date.split("/")[2].rjust(2,'0')
    elif datetype == "yyyy-mm-dd":
        year = date.split("-")[0].rjust(4,'0')
        month = date.split("-")[1].rjust(2,'0')
        day = date.split("-")[2].rjust(2,'0')
    elif datetype == "yyyy mm dd":
        year = date.split()[0].rjust(4,'0')
        month = date.split()[1].rjust(2,'0')
        day = date.split()[2].rjust(2,'0')

    if day.upper() == "UN":
        day = "01"
    if len(month) == 3:
        month = MONTH_CONVERT[month.upper()]
    if month.upper() == "UN":
        month = "01"
    if year.upper() == "UNKN":
        year = "1900"
    if year.upper() == "UN":
        year = "00"
    if year.upper() == "0000":
        year = "1900"

    date_1 = '{0}-{1}-{2}'.format(year, month, day)
    return date_1


def date_transform(date_str: str, datetype):
    date = None
    if "->" in date_str:
        date_str_1 = date_str.split(" -> ")[1]
    else:
        date_str_1 = date_str
    if len(date_str_1)!= 0 and date_str_1.isspace()!=True:
        date_fillun = fill_unknow_date(date_str_1, datetype)
        date = datetime.strptime(date_fillun, "%Y-%m-%d")
    return date


def convert_date(data: pd.DataFrame, date_fields: list, datetype: str) -> pd.DataFrame:
    for i in date_fields:
        data["{0}{1}".format(i, "_Con")] = data.apply(lambda x: date_transform(x[i], datetype), axis=1)
    return data
