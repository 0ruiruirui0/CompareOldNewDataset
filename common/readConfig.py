# coding=utf-8
__author__ = "ruijing.li"

import os
import json
from configparser import ConfigParser

class MyConfig:
    def __init__(self,path:str):
        config = ConfigParser()
        config_file_path = path
        config.read(config_file_path)
        self.project_system = config.get("project", "system")
        self.project_name = config.get("project", "name")
        self.func_keepDeleted = eval(config.get("func", "keepDeleted").lower().capitalize())
        self.func_markChangedInColour  = eval(config.get("func", "markChangedInColour").lower().capitalize())
        self.compare_notCompareOID = json.loads(config.get("compare", "notCompareOID"))
        self.sort_fieldsOID = json.loads(config.get("sort", "fieldsOID"))
        self.sort_order = eval(config.get("sort", "IsAscendingOrder").lower().capitalize())
        self.sort_dateFields = json.loads(config.get("sort", "dateFields"))
        self.sort_dateFormat = config.get("sort", "dateFormat")
        self.delete_fieldsLabel = json.loads(config.get("delete", "fieldsLabel"))
        self.content_formOID = json.loads(config.get("content", "formOID"))
        self.content_formName = json.loads(config.get("content", "formName"))
