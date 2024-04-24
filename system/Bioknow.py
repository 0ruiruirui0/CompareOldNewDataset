# -*- coding: utf-8 -*-
__author__ = "ruijing.li"

import pandas as pd
import logging
from common.func import read_excel
from common.func import compare_data_common, get_compare_variables_Common
from common.Sorter import Sorter


class Bioknow:
    def __init__(self, path_Old: str, path_New: str, label_dict: dict, dataset_name: str, not_compare_variables: list,
                 KEEP_DELETE_DATA: bool, COLOUR: bool, myConfig,visit_order):
        self.path_Old = path_Old
        self.path_New = path_New
        self.label_dict = label_dict
        self.dataset_name = dataset_name
        self.not_compare_variables = not_compare_variables
        self.KEEP_DELETE_DATA = KEEP_DELETE_DATA
        self.COLOUR = COLOUR
        self.meta = {}
        self.myConfig = myConfig
        self.visit_order = visit_order

    @property
    def data(self):
        data_Old = self.Data_Clean_OLD()
        data_New = self.Data_Clean_NEW()
        seq = data_New.columns.tolist()

        logging.warning("当前旧数据集{0}变量OID{1}".format(self.dataset_name, data_Old.columns.tolist()))
        logging.warning("当前新数据集{0}变量OID{1}".format(self.dataset_name, data_New.columns.tolist()))

        filtered_not_compare_variables = [var.upper() for var in self.not_compare_variables if var.upper() in data_New]
        logging.warning("当前不参与比较变量{0}".format(filtered_not_compare_variables))
        Compare_Variables = get_compare_variables_BK(data_New, filtered_not_compare_variables)

        data = compare_data_BK(data_Old, data_New, Compare_Variables, filtered_not_compare_variables, self.KEEP_DELETE_DATA,
                               self.COLOUR, self.myConfig,self.visit_order)
        data_renamed = rename_BK(data, seq, self.label_dict)
        data_renamed = data_renamed.drop_duplicates(keep='first')
        return data_renamed

    def Data_Clean_OLD(self):
        data = read_excel(self.path_Old, self.dataset_name)
        data.columns = data.columns.str.upper()
        return data

    def Data_Clean_NEW(self):
        data = read_excel(self.path_New, self.dataset_name)
        data.columns = data.columns.str.upper()
        return data


def rename_BK(data: pd.DataFrame, seq: list, sas_label: dict):
    seq2 = list(map(lambda x: x.lower(), seq))
    keep_columns = [*seq2, *["Flag"]]
    data1 = data[keep_columns]
    seq3 = list(map(lambda x: x.upper(), data1.columns))
    Upper_Dict = dict(zip(data1.columns, seq3))
    data_renamed = data1.rename(columns=Upper_Dict)
    data_renamed = data_renamed.rename(columns=sas_label)
    data_renamed = data_renamed.rename(
        columns={"FLAG": "Flag", "STUDYCODE": "研究代码", "SITEID": "中心编号", "SUBJID": "受试者代码",
                 "VISITOID": "访视编号", "VISITNAME": "访视名称", "SVNUM": "访视内名称", "TNAME": "表名称", "TID": "表",
                 "RECORDID": "记录ID", "SUBTRID": "子表记录ID", "CSN": "序号"})
    return data_renamed


def get_compare_variables_BK(data: pd.DataFrame, not_compare_variables: list):
    system = ["STUDYCODE", "SITEID", "SUBJID", "VISITOID", "VISITNAME", "SVNUM", "TNAME", "TID", "RECORDID", "SUBTRID",
              "CSN"]
    compare_variables = get_compare_variables_Common(data, not_compare_variables, system)
    return compare_variables


def compare_data_BK(OldData: pd.DataFrame, NewData: pd.DataFrame, Variables: list,
                    not_compare_variables: list, KEEP_DELETE_DATA: bool, COLOUR: bool, myconfig,visit_order) -> pd.DataFrame:
    system_variables = ["STUDYCODE", "SITEID", "SUBJID", "VISITOID", "SVNUM", "TID", "RECORDID"]
    system_variables_csn = ["STUDYCODE", "SITEID", "SUBJID", "VISITOID", "SVNUM", "TID", "RECORDID", "SUBTRID", "CSN"]
    system_not_compare = ["VISITNAME", "TNAME"]
    if "CSN" in NewData.columns:
        data_all = compare_data_common(OldData, NewData, Variables, not_compare_variables, system_variables_csn,
                                       system_not_compare, KEEP_DELETE_DATA, COLOUR)
        data_all = clean_sort_data_BK_CSN(data_all, myconfig,visit_order)
    else:
        data_all = compare_data_common(OldData, NewData, Variables, not_compare_variables, system_variables,
                                       system_not_compare, KEEP_DELETE_DATA, COLOUR)
        data_all = clean_sort_data_BK(data_all, myconfig,visit_order)
    return data_all


def clean_sort_data_BK(data: pd.DataFrame, myconfig,visit_order) -> pd.DataFrame:
    if visit_order is not None:
        visit_order = visit_order.rename(columns={"vistoid":"visitoid"})
        data_clean = pd.merge(data, visit_order, how="left", on="visitoid")
        data_clean = data_clean.replace("nan", "").replace("None", "")
        data_clean["visitoid"] = data_clean["visitoid"].astype(float, errors='ignore')
        data_clean["tid"] = data_clean["tid"].astype(float, errors='ignore')
        SORT_COLUMNS = ["siteid", "subjid", 'visitno', "visitoid", "tid"]
        data_clean = data_clean.sort_values(by=SORT_COLUMNS)
        data_clean = Sorter(data_clean, myconfig).data
        data_clean["visitoid"] = data_clean["visitoid"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean["tid"] = data_clean["tid"].astype(int, errors='ignore').astype(str, errors='ignore')
    else:
        data_clean = data.replace("nan", "").replace("None", "")
        data_clean["visitoid"] = data_clean["visitoid"].astype(float, errors='ignore')
        data_clean["tid"] = data_clean["tid"].astype(float, errors='ignore')
        SORT_COLUMNS = ["siteid", "subjid", "visitoid", "tid"]
        data_clean = data_clean.sort_values(by=SORT_COLUMNS)
        data_clean = Sorter(data_clean, myconfig).data
        data_clean["visitoid"] = data_clean["visitoid"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean["tid"] = data_clean["tid"].astype(int, errors='ignore').astype(str, errors='ignore')
    return data_clean

def clean_sort_data_BK_CSN(data: pd.DataFrame, myconfig,visit_order) -> pd.DataFrame:
    if visit_order is not None:
        visit_order = visit_order.rename(columns={"vistoid":"visitoid"})
        data_clean = pd.merge(data, visit_order, how="left", on="visitoid")
        data_clean = data_clean.replace("nan", "").replace("None", "")
        data_clean["visitno"] = data_clean["visitno"].astype(float, errors='ignore')
        data_clean["visitoid"] = data_clean["visitoid"].astype(float, errors='ignore')
        data_clean["tid"] = data_clean["tid"].astype(float, errors='ignore')
        data_clean["csn"] = data_clean["csn"].astype(float, errors='ignore')
        SORT_COLUMNS = ["siteid", "subjid", 'visitno', "visitoid", "tid", "csn"]
        data_clean = data_clean.sort_values(by=SORT_COLUMNS)
        data_clean = Sorter(data_clean, myconfig).data
        data_clean["visitno"] = data_clean["visitno"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean["visitoid"] = data_clean["visitoid"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean["tid"] = data_clean["tid"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean["csn"] = data_clean["csn"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean = data_clean.drop(columns="visitno")
    else:
        data_clean = data.replace("nan", "").replace("None", "")
        data_clean["visitoid"] = data_clean["visitoid"].astype(float, errors='ignore')
        data_clean["tid"] = data_clean["tid"].astype(float, errors='ignore')
        data_clean["csn"] = data_clean["csn"].astype(float, errors='ignore')
        SORT_COLUMNS = ["siteid", "subjid", "visitoid", "tid", "csn"]
        data_clean = data_clean.sort_values(by=SORT_COLUMNS)
        data_clean = Sorter(data_clean, myconfig).data
        data_clean["visitoid"] = data_clean["visitoid"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean["tid"] = data_clean["tid"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean["csn"] = data_clean["csn"].astype(int, errors='ignore').astype(str, errors='ignore')
    return data_clean
