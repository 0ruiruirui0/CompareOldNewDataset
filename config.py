# -*- coding: utf-8 -*-
__author__ = "ruijing.li"

import os
from datetime import datetime
import pandas as pd
from common.func import get_dataset_list, get_dataset_list_excel

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
TODAY = datetime.now().strftime("%Y-%m-%d")
# Global Configuration

# dataset
dataset_Old = "OLD"
dataset_New = "NEW"

# input 临时路径，最终用选择/录入的方式取代
# ProjectName = "ALGMYL09010"
# SystemName = "OC"

# ProjectName = "1"
# SystemName = "CIMS"

# ProjectName = "XLS-H02NY-SAII01"
# SystemName = "Taimei"
#
# ProjectName = "SSS06"
# SystemName = "Bioknow"

# input 临时路径，最终用选择/录入的方式取代
# PATH_INPUT_Old = '{0}\\data\\{1}\\{2}\\{3}\\'.format(os.path.abspath(os.curdir), SystemName, ProjectName, dataset_Old)
# PATH_INPUT_New = '{0}\\data\\{1}\\{2}\\{3}\\'.format(os.path.abspath(os.curdir), SystemName, ProjectName, dataset_New)
# test only
# PATH_INPUT_eSpec = '{0}\\data\\{1}\\{2}\\{3}'.format(os.path.abspath(os.curdir),SystemName, ProjectName,"eCRF_specification.xlsx")

# PATH_INPUT_Content = '{0}\\data\\{1}'.format(os.path.abspath(os.curdir),"Content.xlsx")
# PATH_INPUT_eSpec = '{0}\\data\\{1}'.format(os.path.abspath(os.curdir),"eCRF_specification.xlsx")
# PATH_INPUT_not_compare_variables = []

# PATH_OUTPUT = '{0}\\reports\\{1}\\{2}\\{3}\\'.format(os.path.abspath(os.curdir), SystemName, ProjectName,
#                                                      datetime.now().
#                                                      strftime("%Y-%m-%d"))
# DATASET_NAME = os.listdir(PATH_INPUT_New)
# DATASET_LIST = get_dataset_list(DATASET_NAME)
# DATASET_LIST_excel = get_dataset_list_excel(DATASET_NAME)

# if not os.path.exists(PATH_OUTPUT):
#     os.makedirs(PATH_OUTPUT)

# 数据处理需要保留的系统变量
SYSTEM_COLUMNS = ["StudyEnvSiteNumber", "Subject", "InstanceName", "Folder", "FolderSeq", "InstanceRepeatNumber",
                  "DataPageName", "PageRepeatNumber", "RecordPosition", "MinCreated", "MaxUpdated", "SaveTS"]

COMPARE_SYSTEM_COLUMNS = ["StudyEnvSiteNumber", "Subject", "InstanceName", "FolderSeq", "InstanceRepeatNumber",
                          "DataPageName", "PageRepeatNumber", "RecordPosition"]
# 排序用的系统变量

# 最终保留的模板变量
KEEP_COLUMNS = ["studyenvsitenumber", "subject", "instancename", "datapagename", "recordposition"]

SYSTEM_LIST = ["Rave", "Taimei", "OC/RDC", "ClinFlash", "CIMS", "Bioknow"]

YES_NO = ['YES', "NO"]

DATETYPE_DICT = {"dd/MMM/yyyy": '%d/%b/%Y',
                 "dd-MMM-yyyy": '%d-%b-%Y',
                 "dd MMM yyyy": '%d %b %Y',
                 "dd/mm/yyyy": '%d/%m/%Y',
                 "dd-mm-yyyy": '%d-%m-%Y',
                 "dd mm yyyy": '%d %m %Y',
                 "yyyy/mm/dd": "%Y/%m/%d",
                 "yyyy-mm-dd": "%Y-%m-%d",
                 "yyyy mm dd": "%Y %m %d"}

MONTH_CONVERT = {"UNK": '01',
                 "JAN": '01',
                 "FEB": '02',
                 "MAR": '03',
                 "APR": '04',
                 "MAY": '05',
                 "JUN": "06",
                 "JUL": "07",
                 "AUG": "08",
                 "SEP": '09',
                 "OCT": '10',
                 "NOV": '11',
                 "DEC": '12'}
