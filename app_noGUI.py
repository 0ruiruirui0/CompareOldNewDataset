# -*- coding: utf-8 -*-
__author__ = "ruijing.li"

from datetime import datetime
import pandas
import tkinter as tk
from tkinter import ttk
from tkinter import Label
import logging
import os
import sys
from functools import partial
from common.func import select_file
from tkinter import messagebox
import pyreadstat
import openpyxl
from config import ProjectName
from config import SYSTEM_LIST
from config import PATH_OUTPUT
from config import PATH_INPUT_Old, PATH_INPUT_New, PATH_INPUT_Content, PATH_INPUT_not_compare_variables
from config import DATASET_LIST,DATASET_LIST_excel
from common.func import create_content
from common.func import read_content
from common.func import set_worksheet_format
from common.func import highlight_cells, highlight_rows
from common.func import get_dataset_list
from openpyxl.styles import Font

from system.RAVE import Rave
from system.RAVE_LAB import Rave_lab
from system.OC import OC
from system.Taimei import taimei
from system.ClinFlash import ClinFlash
from system.Bioknow import Bioknow
from system.CIMS import cims

LARGE_FONT = ("Arial", 12)
LARGE_FONT_ENTRY = ("Arial", 10)

logger = logging.getLogger()
logger.setLevel(logging.WARNING)

app = tk.Tk()
app.title("Medical Review Listing Report Generator")
app.geometry("1200x260")

frame = tk.Frame(app, width=300, height=300)

str_raw = tk.StringVar(frame)
str_project_name = tk.StringVar(frame)
str_not_compare_variables = tk.StringVar(frame)
str_drop = tk.StringVar(frame)

entry_project_name = tk.Entry(frame, textvariable=str_project_name, width=120, font=LARGE_FONT_ENTRY)
entry_raw = tk.Entry(frame, textvariable=str_raw, width=120, font=LARGE_FONT_ENTRY)
entry_variables = tk.Entry(frame, textvariable=str_not_compare_variables, width=120, font=LARGE_FONT_ENTRY)
entry_drop = tk.Entry(frame, textvariable=str_drop, width=120, font=LARGE_FONT_ENTRY)
# EDC系统下拉框
tkk_system = ttk.Combobox(frame)
tkk_system['values'] = SYSTEM_LIST
tkk_system['state'] = 'readonly'

bt_open_raw = tk.Button(frame,
                        text="请选择源数据：（必填）",
                        command=partial(select_file, str_raw),
                        font=LARGE_FONT,
                        width=30,
                        relief="raised")

if __name__ == '__main__':

# def data_handler():
#     PATH_INPUT_Old = '{0}\\OLD'.format(str_raw.get())
#     PATH_INPUT_New = '{0}\\NEW'.format(str_raw.get())
#     PATH_INPUT_Content = '{0}\\{1}'.format(str_raw.get(),"Content.xlsx")
#     not_compare_variables = entry_variables.get().split(',')
#     drop_variables = entry_drop.get().split(',')
#     def get_variables(variables):
#         if variables[0]!='':
#             return variables
#         else:
#             return []
#     PATH_INPUT_not_compare_variables = get_variables(not_compare_variables)
#     PATH_INPUT_drop_variables = get_variables(drop_variables)
#     ProjectName = entry_project_name.get()
#     System = tkk_system.get()
#
#     if System =='':
#         messagebox.showerror("错误:", "请输入选择EDC系统")
#     elif ProjectName == "":
#         messagebox.showerror("错误:", "请输入项目名称")
#     elif len(PATH_INPUT_Old) == 0 or len(PATH_INPUT_New) == 0:
#         messagebox.showerror("错误:", "请确认是否正确提供OLD+NEW两个数据集")
#     else:
#         try:
#             logging.warning("已选系统: {0}".format(System))
#             logging.warning("比较项目名称: {0}".format(ProjectName))
#             if PATH_INPUT_not_compare_variables!=[]:
#                 logging.warning("不参与比较变量: {0}".format(PATH_INPUT_not_compare_variables))
#             logging.warning("开始清理数据...")
#             PATH_INPUT_Old = PATH_INPUT_Old + "\\"
#             PATH_INPUT_New = PATH_INPUT_New + "\\"
#
#             PATH_OUTPUT = '{0}\\Output\\{1}\\'.format(str_raw.get(), datetime.now().strftime("%Y-%m-%d"))
#
#             DATASET_NAME = os.listdir(PATH_INPUT_New)
#             DATASET_LIST = get_dataset_list(DATASET_NAME)
#
#             if not os.path.exists(PATH_OUTPUT):
#                 os.makedirs(PATH_OUTPUT)

            # if System == "Taimei":
                # for i in DATASET_LIST_excel:
                #     # try:
                #         logging.warning("开始比较数据集{0}".format(i))
                #         locals()[str(i)] = Bioknow(PATH_INPUT_Old, PATH_INPUT_New, i, PATH_INPUT_not_compare_variables).data
                        # locals()[str(i)] = locals()[str(i)].style.apply(highlight_rows, axis=1).applymap(highlight_cells)
                    # except Exception as e:
                    #     logging.warning("不参与的比较变量不在数据集{0}中".format(i))
            #
            # elif System == "OC/RDC":
            #     for i in DATASET_LIST:
            #         # try:
            #             logging.warning("开始比较数据集{0}".format(i))
            #             locals()[str(i)] = OC(PATH_INPUT_Old, PATH_INPUT_New, i, PATH_INPUT_not_compare_variables).data
            #             locals()[str(i)] = locals()[str(i)].drop(columns=PATH_INPUT_drop_variables)
            #             locals()[str(i)] = locals()[str(i)].style.apply(highlight_rows, axis=1).applymap(
            #                 highlight_cells)
            #         # except Exception as e:
            #         #     logging.warning("不参与的比较变量不在数据集{0}中".format(i))
            #
            # elif System == "ClinFlash":
            #     for i in DATASET_LIST:
            #         # try:
            #             logging.warning("开始比较数据集{0}".format(i))
            #             locals()[str(i)] = clinflash(PATH_INPUT_Old, PATH_INPUT_New, i, PATH_INPUT_not_compare_variables).data
            #             locals()[str(i)] = locals()[str(i)].drop(columns=PATH_INPUT_drop_variables)
            #             locals()[str(i)] = locals()[str(i)].style.apply(highlight_rows, axis=1).applymap(
            #                 highlight_cells)
            #         # except Exception as e:
            #         #     logging.warning("不参与的比较变量不在数据集{0}中".format(i))
            #
            # elif System == "Rave":
            #     for i in DATASET_LIST:
            #         # try:
            #             logging.warning("开始比较数据集{0}".format(i))
            #             if i =="lab":
            #                 locals()[str(i)] = Rave_lab(PATH_INPUT_Old, PATH_INPUT_New, i, PATH_INPUT_not_compare_variables).data
            #                 locals()[str(i)] = locals()[str(i)].drop(columns=PATH_INPUT_drop_variables)
            #             else:
            #                 locals()[str(i)] = Rave(PATH_INPUT_Old, PATH_INPUT_New, i, PATH_INPUT_not_compare_variables).data
            #                 locals()[str(i)] = locals()[str(i)].drop(columns=PATH_INPUT_drop_variables)
            #             locals()[str(i)] = locals()[str(i)].style.apply(highlight_rows, axis=1).applymap(
            #                     highlight_cells)
                    # except Exception as e:
                    #     logging.warning("不参与的比较变量不在数据集{0}中".format(i))
            # 输出

                file = f"{ProjectName}_Medical Review Listing_{datetime.now().strftime('%Y-%m-%d')}.xlsx"

                with pandas.ExcelWriter("{0}\\{1}".format(PATH_OUTPUT, file),
                                            datetime_format="yyyy/mm/dd hh:mm:ss",
                                            date_format="yyyy/mm/dd",
                                            ) as writer:
                        logging.warning("开始输出...")
                        # 有目录文件就生成目录，没有就跳过
                        try:
                            FORMS = read_content(PATH_INPUT_Content)
                            pandas.DataFrame().to_excel(writer, "Contents", index=False)
                            logging.warning("正在生成目录...")
                            content = writer.sheets["Contents"]
                            create_content(content, FORMS)
                        except Exception as e:
                            logging.warning("未提供生成目录文件...")

                        for i in DATASET_LIST_excel:
                            try:
                                logging.warning("开始输出数据集{0}".format(i))
                                locals()[str(i)].to_excel(writer, i.upper(), index=False)
                            except Exception as e:
                                logging.warning("数据集{0}未成功输出".format(i))

                        logging.warning("开始调整表格格式...")

                        for key, sheet in writer.sheets.items():
                            if sheet.title != "Contents":
                                logging.warning("开始调整{0}格式...".format(sheet))
                                logging.warning("程序执行成功 - 请在以下路径查看文件: {0}".format(PATH_OUTPUT))
                                set_worksheet_format(sheet)

            # logging.warning("程序执行成功 - 请在以下路径查看文件: {0}".format(PATH_OUTPUT))
            # logging.warning("程序执行结束...")
        # except Exception as e:
        #     logging.error("错误: {0}".format(str(sys.exc_info())))
#
# bt_run = tk.Button(frame,
#                    text="运行",
#                    command=data_handler,
#                    font=LARGE_FONT,
#                    width=20,
#                    relief="raised")
#
# # layout
# frame.grid(row=0, column=0, sticky="WESN")
#
# # 请选择系统
# system_label = Label(frame, text="请选择EDC系统：（必填）", font=LARGE_FONT)
# system_label.grid(row=0, column=0, padx=5, pady=2,sticky="WESN")
# tkk_system.grid(row=0, column=1, padx=2, pady=2, sticky="w")
#
# # 项目名称
# label_project_name = Label(frame, text="请输入项目名称： （必填）", font=LARGE_FONT)
# label_project_name.grid(row=1, column=0, padx=5, pady=2)
# entry_project_name.grid(row=1, column=1, padx=2, pady=2, sticky="w")
#
# # 源数据+目录路径
# bt_open_raw.grid(row=2, column=0, padx=5, pady=2, sticky="w")
# entry_raw.grid(row=2, column=1, padx=2, pady=2, sticky="w")
#
# # 不比较变量
# label_variables = Label(frame, text="请输入所有不需要比较的变量OID，\n并用逗号隔开： （非必填）", font=LARGE_FONT)
# label_variables.grid(row=3, column=0, padx=5, pady=2, sticky="w")
# entry_variables.grid(row=3, column=1, padx=2, pady=2, sticky="w")
#
# label_drop_variables = Label(frame, text="请输入需要删除的变量LABEL，\n并用逗号隔开： （非必填）", font=LARGE_FONT)
# label_drop_variables.grid(row=4, column=0, padx=5, pady=2, sticky="w")
# entry_drop.grid(row=4, column=1, padx=2, pady=2, sticky="w")
#
# bt_run.grid(row=5, column=1, padx=2, pady=20, sticky="w")
#
# if __name__ == '__main__':
#     app.mainloop()

print("********** Done! **********")
