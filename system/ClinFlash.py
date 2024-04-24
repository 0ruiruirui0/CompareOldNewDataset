# -*- coding: utf-8 -*-
__author__ = "ruijing.li"

import pandas as pd
import logging
from common.func import read_sas
from common.func import compare_data_common, get_compare_variables_Common, rename_common
from common.Sorter import Sorter

class ClinFlash:
    def __init__(self, path_old: str, path_new: str, dataset_name: str, not_compare_variables: list,
                 keep_delete_data: bool, colour: bool, myConfig, visit_order):
        self.path_old = path_old
        self.path_new = path_new
        self.dataset_name = dataset_name
        self.not_compare_variables = not_compare_variables
        self.keep_delete_data = keep_delete_data
        self.colour = colour
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

        Compare_Variables = get_compare_variables_cf(data_New, filtered_not_compare_variables)
        data = compare_data_cf(data_Old, data_New, Compare_Variables, filtered_not_compare_variables,
                               self.keep_delete_data,
                               self.colour, self.myConfig, self.visit_order)
        data_renamed = rename_common(data, seq, self.meta)
        # data_renamed = data_renamed.drop_duplicates(keep='first')
        return data_renamed

    def Data_Clean_OLD(self):
        data, meta = read_sas(self.path_old, self.dataset_name)
        self.meta.update(meta.column_names_to_labels)
        data.columns = data.columns.str.upper()
        return data

    def Data_Clean_NEW(self):
        data, meta = read_sas(self.path_new, self.dataset_name)
        self.meta.update(meta.column_names_to_labels)
        data.columns = data.columns.str.upper()
        return data


def get_compare_variables_cf(data: pd.DataFrame, not_compare_variables: list):
    system = ["STUDYID", "SITEID", "SUBJID", "VISIT", "__STUDYEVENTOID", "__STUDYEVENTREPEATKEY", "FORM",
              "__ITEMGROUPOID", "__ITEMGROUPREPEATKEY", "LINE"]
    compare_variables = get_compare_variables_Common(data, not_compare_variables, system)
    return compare_variables


def compare_data_cf(OldData: pd.DataFrame, NewData: pd.DataFrame, Variables: list,
                    not_compare_variables: list, KEEP_DELETE_DATA: bool, COLOUR: bool, myconfig,
                    visit_order) -> pd.DataFrame:
    system_variables_1 = ["STUDYID", "SITEID", "SUBJID", "__STUDYEVENTOID", "__STUDYEVENTREPEATKEY",
                          "__ITEMGROUPOID", "__ITEMGROUPREPEATKEY", "LINE"]
    system_not_compare_1 = ["VISIT", "FORM"]
    system_variables = [x.upper() for x in system_variables_1]
    system_not_compare = [x.upper() for x in system_not_compare_1]

    data_all = compare_data_common(OldData, NewData, Variables, not_compare_variables, system_variables,
                                   system_not_compare, KEEP_DELETE_DATA, COLOUR)
    data_clean = clean_sort_data_cf(data_all, myconfig, visit_order)

    return data_clean


def clean_sort_data_cf(data: pd.DataFrame, myconfig, visit_order) -> pd.DataFrame:
    if visit_order is not None:
        visit_order = visit_order.rename(columns={"vistoid": "__studyeventoid"})
        data_clean = pd.merge(data, visit_order, how="left", on="__studyeventoid")
        data_clean = data_clean.replace("nan", "").replace("None", "")
        data_clean["visitno"] = data_clean["visitno"].astype(float, errors='ignore')
        data_clean["__studyeventrepeatkey"] = data_clean["__studyeventrepeatkey"].astype(float, errors='ignore')
        data_clean["__formrepeatkey"] = data_clean["__formrepeatkey"].astype(float, errors='ignore')
        data_clean["line"] = data_clean["line"].astype(float, errors='ignore')
        SORT_COLUMNS = ["siteid", "subjid", 'visitno', "__studyeventrepeatkey", "__formrepeatkey", "line"]
        data_clean = data_clean.sort_values(by=SORT_COLUMNS)
        data_clean = Sorter(data_clean, myconfig).data
        data_clean["visitno"] = data_clean["visitno"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean["__studyeventrepeatkey"] = data_clean["__studyeventrepeatkey"].astype(int, errors='ignore').astype(
            str,
            errors='ignore')
        data_clean["__formrepeatkey"] = data_clean["__formrepeatkey"].astype(int, errors='ignore').astype(str,
                                                                                                          errors='ignore')
        data_clean["line"] = data_clean["line"].astype(int, errors='ignore').astype(str, errors='ignore')
        data_clean = data_clean.drop(columns="visitno")
    else:
        data_clean = data.replace("nan", "").replace("None", "")
        data_clean["__studyeventrepeatkey"] = data_clean["__studyeventrepeatkey"].astype(float, errors='ignore')
        data_clean["__formrepeatkey"] = data_clean["__formrepeatkey"].astype(float, errors='ignore')
        data_clean["line"] = data_clean["line"].astype(float, errors='ignore')
        SORT_COLUMNS = ["siteid", "subjid", "__studyeventrepeatkey", "__formrepeatkey", "line"]
        data_clean = data_clean.sort_values(by=SORT_COLUMNS)
        data_clean = Sorter(data_clean, myconfig).data
        data_clean["__studyeventrepeatkey"] = data_clean["__studyeventrepeatkey"].astype(int, errors='ignore').astype(
            str,
            errors='ignore')
        data_clean["__formrepeatkey"] = data_clean["__formrepeatkey"].astype(int, errors='ignore').astype(str,
                                                                                                          errors='ignore')
        data_clean["line"] = data_clean["line"].astype(int, errors='ignore').astype(str, errors='ignore')
    return data_clean
