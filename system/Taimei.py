# -*- coding: utf-8 -*-
__author__ = "ruijing.li"

import logging

import pandas as pd
from common.func import read_sas
from common.func import compare_data_common, get_compare_variables_Common, rename_common
from common.Sorter import Sorter


class taimei:
    def __init__(self, path_Old: str, path_New: str, dataset_name: str, not_compare_variables: list,
                 KEEP_DELETE_DATA: bool, COLOUR: bool, myConfig,visit_order):
        self.path_Old = path_Old
        self.path_New = path_New
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

        Compare_Variables = get_compare_variables_TM(data_New, filtered_not_compare_variables)
        data = compare_data_TM(data_Old, data_New, Compare_Variables, filtered_not_compare_variables,
                               self.KEEP_DELETE_DATA,
                               self.COLOUR, self.myConfig,self.visit_order)
        data_renamed = rename_common(data, seq, self.meta)
        data_renamed = data_renamed.drop_duplicates(keep='first')
        return data_renamed

    def Data_Clean_OLD(self):
        data, meta = read_sas(self.path_Old, self.dataset_name)
        self.meta.update(meta.column_names_to_labels)
        data.columns = data.columns.str.upper()
        return data

    def Data_Clean_NEW(self):
        data, meta = read_sas(self.path_New, self.dataset_name)
        self.meta.update(meta.column_names_to_labels)
        data.columns = data.columns.str.upper()
        return data


def get_compare_variables_TM(data: pd.DataFrame, not_compare_variables: list):
    system = ["PSTUDYID", "SITEID",  "SUBJID",  "VISTOID", "VISTREP",  "FORMOID", "FORMREP","RECREP"]# "SITENM","VISIT","FORMNM",
    compare_variables = get_compare_variables_Common(data, not_compare_variables, system)
    return compare_variables

def compare_data_TM(OldData: pd.DataFrame, NewData: pd.DataFrame, Variables: list,
                    not_compare_variables: list, KEEP_DELETE_DATA: bool, COLOUR: bool, myconfig,visit_order) -> pd.DataFrame:
    system_variables = ["PSTUDYID", "SITEID", "SUBJID", "VISTOID", "VISTREP", "FORMOID", "FORMREP", "RECREP"]#"SITENM",
    # system_not_compare = ["VISIT", "FORMNM"]
    system_not_compare = []
    data_all = compare_data_common(OldData, NewData, Variables, not_compare_variables, system_variables,
                                   system_not_compare, KEEP_DELETE_DATA, COLOUR)
    data_clean = clean_sort_data_tm(data_all, myconfig,visit_order)
    return data_clean

def clean_sort_data_tm(data: pd.DataFrame, myconfig,visit_order) -> pd.DataFrame:
    if visit_order is not None:
        data_clean = pd.merge(data, visit_order, how="left", on="vistoid")
        data_clean = data_clean.replace("nan", "").replace("None", "")
        # #to update
        data_clean["visitno"] = data_clean["visitno"].astype(float, errors='ignore')
        #
        data_clean["vistrep"] = data_clean["vistrep"].astype(float, errors='ignore')
        data_clean["formrep"] = data_clean["formrep"].astype(float, errors='ignore')
        data_clean["recrep"] = data_clean["recrep"].astype(float, errors='ignore')
        SORT_COLUMNS = ["siteid", "subjid", 'visitno', "vistrep", "formrep", "recrep"]
        data_clean = data_clean.sort_values(by=SORT_COLUMNS)
        data_clean = Sorter(data_clean, myconfig).data
        # #to update
        data_clean["visitno"] = data_clean["visitno"].astype(int, errors='ignore').astype(str, errors='ignore')
        #
        data_clean["vistrep"] = data_clean["vistrep"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean["formrep"] = data_clean["formrep"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean["recrep"] = data_clean["recrep"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean = data_clean.drop(columns="visitno")
    else:
        data_clean = data.replace("nan", "").replace("None", "")
        data_clean["vistrep"] = data_clean["vistrep"].astype(float, errors='ignore')
        data_clean["formrep"] = data_clean["formrep"].astype(float, errors='ignore')
        data_clean["recrep"] = data_clean["recrep"].astype(float, errors='ignore')
        SORT_COLUMNS = ["siteid", "subjid","vistrep", "formrep", "recrep"]
        data_clean = data_clean.sort_values(by=SORT_COLUMNS)
        data_clean = Sorter(data_clean, myconfig).data
        data_clean["vistrep"] = data_clean["vistrep"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean["formrep"] = data_clean["formrep"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean["recrep"] = data_clean["recrep"].astype(int, errors='ignore').astype(str, errors='ignore')
    return data_clean
