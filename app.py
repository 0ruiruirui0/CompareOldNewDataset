# -*- coding: utf-8 -*-
__author__ = "ruijing.li"

from datetime import datetime
import pandas
import tkinter as tk
import logging
import os
import sys
from functools import partial
from common.func import select_file
from tkinter import messagebox
from common.func import create_content
from common.func import read_content,read_content_excel,read_visitorder_excel
from common.func import set_worksheet_format
from common.func import highlight_cells, highlight_rows
from common.func import get_dataset_list, get_dataset_list_excel
from common.func import get_label_list_fromALS
from system.RAVE import Rave
from system.RAVE_LAB import Rave_lab
from system.RAVE_Classic import Rave_C
from system.RAVE_Classic_LAB import Rave_C_lab
from system.OC import OC
from system.Taimei import taimei
from system.ClinFlash import ClinFlash
from system.Bioknow import Bioknow
from system.CIMS import cims
from system.CIMS_odm import cims_odm
from common.func import filter_variables
from common.readConfig import MyConfig
from tkinter import ttk
from tkinter import Label

LARGE_FONT = ("Arial", 12)
LARGE_FONT_ENTRY = ("Arial", 10)

logger = logging.getLogger()
logger.setLevel(logging.WARNING)

# 设置屏幕打印的格式
sh = logging.StreamHandler()
# sh.setFormatter()
logger.addHandler(sh)

app = tk.Tk()
app.title("Medical Review Listing Report Generator")
app.geometry("1060x200")

frame = tk.Frame(app, width=300, height=300)

str_outputflag = tk.StringVar(frame)
str_raw = tk.StringVar(frame)
str_old_file = tk.StringVar(frame)
str_new_file = tk.StringVar(frame)

entry_raw = tk.Entry(frame, textvariable=str_raw, width=100, font=LARGE_FONT_ENTRY)
entry_old_file = tk.Entry(frame, textvariable=str_old_file, width=100, font=LARGE_FONT_ENTRY)
entry_new_file = tk.Entry(frame, textvariable=str_new_file, width=100, font=LARGE_FONT_ENTRY)

tkk_outputflag = ttk.Combobox(frame)
tkk_outputflag['values'] = ["OldData->NewData","批注"]
tkk_outputflag['state'] = 'readonly'

bt_open_raw = tk.Button(frame,
                        text="请选择配置文件所在的文件夹路径：",
                        command=partial(select_file, str_raw),
                        font=LARGE_FONT,
                        width=28,
                        relief="raised")

bt_open_old = tk.Button(frame,
                        text="选择上一次的源数据：",
                        command=partial(select_file, str_old_file),
                        font=LARGE_FONT,
                        width=28,
                        relief="raised")

bt_open_new = tk.Button(frame,
                        text="选择本次的源数据：",
                        command=partial(select_file, str_new_file),
                        font=LARGE_FONT,
                        width=28,
                        relief="raised")


 # TODO: 打包时，请使用注释部分，以限定服务器使用路径。
# CUR_DIR = os.path.abspath(os.curdir)
# SUB_DIR = r"\Library\Data_Management\5. Database Design\22 Tools\Python Tool"
# if not SUB_DIR in CUR_DIR:
#     messagebox.showerror("错误：", "请在原始路径使用该工具，不要移动到其他路径使用。")
#     raise ValueError("错误：", "请在原始路径使用该工具，不要移动到其他路径使用。")

# if __name__ == '__main__':

def data_handler():
    global visit_order
    outputflag = tkk_outputflag.get()
    path_input_old = '{0}\\'.format(str_old_file.get())
    path_input_new = '{0}\\'.format(str_new_file.get())
    path_input_config = '{0}\\{1}'.format(str_raw.get(), "MyConfig.ini")
    path_input_e_spec = '{0}\\{1}'.format(str_raw.get(), "eCRF_specification.xlsx")
    path_output = '{0}\\Output\\{1}\\'.format(str_raw.get(), datetime.now().strftime("%Y-%m-%d"))
    my_config = MyConfig(path_input_config)
    if not os.path.exists(path_output):
        os.makedirs(path_output)

    path_input_not_compare_variables = my_config.compare_notCompareOID
    path_input_drop_variables = my_config.delete_fieldsLabel
    project_name = my_config.project_name
    system = my_config.project_system
    sort_fields = my_config.sort_fieldsOID
    sort_date_fields = my_config.sort_dateFields
    sort_date_format = my_config.sort_dateFormat
    keep_delete_data = my_config.func_keepDeleted
    keep_colour = my_config.func_markChangedInColour

    if system == '':
        messagebox.showerror("错误:", "请输入选择EDC系统")
    elif project_name == "":
        messagebox.showerror("错误:", "请输入项目名称")
    elif len(path_input_old) == 0 or len(path_input_new) == 0:
        messagebox.showerror("错误:", "请确认是否正确提供OLD+NEW两个数据集")
    elif keep_delete_data == '':
        messagebox.showerror("错误:", "请选择是否需要保留删除数据")
    elif keep_colour == '':
        messagebox.showerror("错误:", "请选择是否需要保留对数据标色")
    else:
        try:
            # path_input_old = path_input_old + "\\"
            # path_input_new = path_input_new + "\\"
            path_input_content = '{0}\\{1}'.format(str_raw.get(), "Content.xlsx")

            dataset_name = os.listdir(path_input_new)
            dataset_list = get_dataset_list(dataset_name)
            dataset_list_excel = get_dataset_list_excel(dataset_name)

            logging.warning("当前数据集路径: {0}".format(str_raw.get()))
            logging.warning("已选系统: {0}".format(system))
            logging.warning("比较项目名称: {0}".format(project_name))
            logging.warning("不参与比较的变量: {0}".format(path_input_not_compare_variables))
            logging.warning("是否保留已删除/Inactived的数据: {0}".format(keep_delete_data))
            logging.warning("是否需要对输出标记颜色: {0}".format(keep_colour))
            logging.warning("当前排序变量: {0}".format(sort_fields))
            logging.warning("当前排序日期型变量: {0}".format(sort_date_fields))
            logging.warning("当前排序日期型格式: {0}".format(sort_date_format))
            order = "升序" if MyConfig(path_input_config).sort_order == "True" else "降序"
            logging.warning("当前排序顺序: {0}".format(order))
            logging.warning("————————————————————————————————————————————————————")
            logging.warning("————————————————————————————————————————————————————")


            if os.path.exists(path_input_content):
                visit_order = read_visitorder_excel(path_input_content)
                logging.warning("已提供content文件...")
            else:
                visit_order = None
                logging.warning("未提供content文件...")


            if system.upper() == "TAIMEI":
                for i in dataset_list:
                    try:
                        logging.warning("开始比较数据集{0}".format(i))

                        locals()[str(i)] = taimei(path_input_old, path_input_new, i,
                                              path_input_not_compare_variables, keep_delete_data, keep_colour,
                                              my_config,visit_order).data
                        filtered_drop_variables = filter_variables(path_input_drop_variables, locals()[str(i)])
                        locals()[str(i)] = locals()[str(i)].drop(columns=filtered_drop_variables)
                        # col_name = locals()[str(i)].columns.tolist()
                        # col_name.insert(0, col_name.pop(col_name.index('Flag')))
                        # locals()[str(i)] = locals()[str(i)][col_name]
                        locals()[str(i)] = locals()[str(i)].style.apply(highlight_rows, axis=1).applymap(
                            highlight_cells)
                    except Exception as e:
                        raise e
            elif system.upper() == "OC/RDC":
                for i in dataset_list:
                    try:
                        logging.warning("————————————————————————————————————————————————————")
                        logging.warning("开始比较数据集{0}".format(i))
                        locals()[str(i)] = OC(path_input_old, path_input_new, i, path_input_not_compare_variables,
                                              keep_delete_data, keep_colour, my_config).data
                        filtered_drop_variables = filter_variables(path_input_drop_variables, locals()[str(i)])
                        locals()[str(i)] = locals()[str(i)].drop(columns=filtered_drop_variables)
                        locals()[str(i)] = locals()[str(i)].style.apply(highlight_rows, axis=1).applymap(
                            highlight_cells)
                    except Exception as e:
                        raise e

            elif system.upper() == "CIMS":
                for i in dataset_list:
                    try:
                        logging.warning("————————————————————————————————————————————————————")
                        logging.warning("开始比较数据集{0}".format(i))
                        if i == "crf_form" or i == "raw_codelist" :
                            continue
                        elif i == "ecrf_comment":
                            locals()[str(i)] = locals()[str(i)] = cims_odm(path_input_old, path_input_new, i, path_input_not_compare_variables,
                                                    keep_delete_data, keep_colour, my_config,visit_order).data
                            filtered_drop_variables = filter_variables(path_input_drop_variables, locals()[str(i)])
                            locals()[str(i)] = locals()[str(i)].drop(columns=filtered_drop_variables)
                        else:
                            locals()[str(i)] = cims(path_input_old, path_input_new, i, path_input_not_compare_variables,
                                                    keep_delete_data, keep_colour, my_config,visit_order).data
                            filtered_drop_variables = filter_variables(path_input_drop_variables, locals()[str(i)])
                            locals()[str(i)] = locals()[str(i)].drop(columns=filtered_drop_variables)
                        locals()[str(i)] = locals()[str(i)].style.apply(highlight_rows, axis=1).applymap(
                            highlight_cells)
                    except Exception as e:
                        raise e

            elif system.upper() == "CLINFLASH":
                for i in dataset_list:
                    try:
                        logging.warning("————————————————————————————————————————————————————")
                        logging.warning("开始比较数据集{0}".format(i))
                        locals()[str(i)] = ClinFlash(path_input_old, path_input_new, i,
                                                     path_input_not_compare_variables, keep_delete_data, keep_colour,
                                                     my_config,visit_order).data
                        filtered_drop_variables = filter_variables(path_input_drop_variables, locals()[str(i)])
                        locals()[str(i)] = locals()[str(i)].drop(columns=filtered_drop_variables)
                        locals()[str(i)] = locals()[str(i)].style.apply(highlight_rows, axis=1).applymap(
                            highlight_cells)
                    except Exception as e:
                        raise e

            elif system.upper() == "RAVE":
                for i in dataset_list:
                    try:
                        logging.warning("————————————————————————————————————————————————————")
                        logging.warning("开始比较数据集{0}".format(i))
                        if i == "lab":
                            locals()[str(i)] = Rave_lab(path_input_old, path_input_new, i,
                                                        path_input_not_compare_variables, keep_delete_data, keep_colour,
                                                        my_config).data
                            filtered_drop_variables = filter_variables(path_input_drop_variables, locals()[str(i)])
                            locals()[str(i)] = locals()[str(i)].drop(columns=filtered_drop_variables)
                        else:
                            locals()[str(i)] = Rave(path_input_old, path_input_new, i,
                                                    path_input_not_compare_variables, keep_delete_data, keep_colour,
                                                    my_config).data
                            filtered_drop_variables = filter_variables(path_input_drop_variables, locals()[str(i)])
                            locals()[str(i)] = locals()[str(i)].drop(columns=filtered_drop_variables)
                        locals()[str(i)] = locals()[str(i)].style.apply(highlight_rows, axis=1).applymap(
                            highlight_cells)
                    except Exception as e:
                        raise e

            elif system.upper() == "RAVE_Classic":
                for i in dataset_list:
                    try:
                        logging.warning("————————————————————————————————————————————————————")
                        logging.warning("开始比较数据集{0}".format(i))
                        if i == "lab":
                            locals()[str(i)] = Rave_C_lab(path_input_old, path_input_new, i,
                                                        path_input_not_compare_variables, keep_delete_data, keep_colour,
                                                        my_config).data
                            filtered_drop_variables = filter_variables(path_input_drop_variables, locals()[str(i)])
                            locals()[str(i)] = locals()[str(i)].drop(columns=filtered_drop_variables)
                        else:
                            locals()[str(i)] = Rave_C(path_input_old, path_input_new, i,
                                                    path_input_not_compare_variables, keep_delete_data, keep_colour,
                                                    my_config).data
                            filtered_drop_variables = filter_variables(path_input_drop_variables, locals()[str(i)])
                            locals()[str(i)] = locals()[str(i)].drop(columns=filtered_drop_variables)
                        locals()[str(i)] = locals()[str(i)].style.apply(highlight_rows, axis=1).applymap(
                            highlight_cells)
                    except Exception as e:
                        raise e

            elif system.upper() == "BIOKNOW":
                try:
                    label_dict = get_label_list_fromALS(path_input_e_spec)
                    for i in dataset_list_excel:
                        try:
                            logging.warning("————————————————————————————————————————————————————")
                            logging.warning("开始比较数据集{0}".format(i))
                            locals()[str(i)] = Bioknow(path_input_old, path_input_new, label_dict, i,
                                                       path_input_not_compare_variables, keep_delete_data, keep_colour,
                                                       my_config,visit_order).data
                            filtered_drop_variables = filter_variables(path_input_drop_variables, locals()[str(i)])
                            locals()[str(i)] = locals()[str(i)].drop(columns=filtered_drop_variables)
                            locals()[str(i)] = locals()[str(i)].style.apply(highlight_rows, axis=1).applymap(
                                highlight_cells)
                        except Exception as e:
                            raise e

                except Exception as e:
                    logging.warning("未提供ALS文件...")

            # 输出
            file = f"{project_name}_Medical Review Listing_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

            with pandas.ExcelWriter("{0}\\{1}".format(path_output, file),
                                    datetime_format="yyyy/mm/dd hh:mm:ss",
                                    date_format="yyyy/mm/dd",
                                    ) as writer:
                logging.warning("————————————————————————————————————————————————————")
                logging.warning("开始输出...")
                # 有目录文件就生成目录，没有就跳过
                try:
                    if os.path.exists(path_input_content):
                        forms = read_content_excel(path_input_content)
                    else:
                        forms = read_content(path_input_config)
                    pandas.DataFrame().to_excel(writer, "Contents", index=False)
                    logging.warning("正在生成目录...")
                    content = writer.sheets["Contents"]
                    create_content(content, forms)
                except Exception as e:
                    logging.warning("未正确提供生成目录信息...")

                for i in dataset_list:
                    try:
                        logging.warning("开始输出数据集{0}".format(i))
                        locals()[str(i)].to_excel(writer, i.upper(), index=False)
                    except Exception as e:
                        logging.warning("数据集{0}未成功输出。Error：{1}".format(i, e))

                for i in dataset_list_excel:
                    try:
                        logging.warning("开始输出数据集{0}".format(i))
                        locals()[str(i)].to_excel(writer, i.upper(), index=False)
                    except Exception as e:
                        logging.warning("数据集{0}未成功输出。Error：{1}".format(i, e))

                logging.warning("开始调整表格格式...")

                for key, sheet in writer.sheets.items():
                    if sheet.title != "Contents":
                        logging.warning("开始调整{0}格式...".format(sheet))
                        set_worksheet_format(sheet,outputflag)

            logging.warning("程序执行成功 - 请在以下路径查看文件: {0}".format(path_output))
            logging.warning("程序执行结束...")
        except Exception as e:
            logging.error("错误: {0}".format(str(sys.exc_info())))


bt_run = tk.Button(frame,
                   text="运行",
                   command=data_handler,
                   font=LARGE_FONT,
                   width=20,
                   relief="raised")

# layout
frame.grid(row=0, column=0, sticky="WESN")

# 源数据+目录路径
system_label = Label(frame, text="请选择对比数据输出方式", font=LARGE_FONT)
system_label.grid(row=1, column=0, padx=5, pady=2, sticky="WESN")
tkk_outputflag.grid(row=1, column=1, padx=2, pady=2, sticky="w")
bt_open_raw.grid(row=4, column=0, padx=5, pady=2, sticky="w")
bt_open_old.grid(row=2, column=0, padx=5, pady=2, sticky="w")
bt_open_new.grid(row=3, column=0, padx=5, pady=2, sticky="w")

entry_raw.grid(row=4, column=1, padx=2, pady=2, sticky="w")
entry_old_file.grid(row=2, column=1, padx=2, pady=2, sticky="w")
entry_new_file.grid(row=3, column=1, padx=2, pady=2, sticky="w")

bt_run.grid(row=7, column=1, padx=2, pady=20, sticky="w")

if __name__ == '__main__':
    app.mainloop()

print("********** Done! **********")
