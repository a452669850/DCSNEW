# -*- coding: UTF-8 -*-

import types, re,json
from parse_procedure import open_excel
from models import InitProcedure

Formula_Regular = r'^([\w]+)=([\+\-]?[\d]+([\.][\d]*)?([Ee][+-]?[\d]+)?)'
init_operation = []


def prase_init_procedure(pstr):
    data = open_excel(pstr)
    excel = data.sheets()[0]
    if excel.row_values(0)[0] != u"规程名称":
        return False
    if excel.row_values(4)[0] != u"源量程IP通道初始化":
        return False
    initProcedure = InitProcedure()
    initProcedure.name = excel.row_values(0)[1]
    initProcedure.number = excel.row_values(0)[3]
    initProcedure.IC = excel.row_values(1)[8]
    for i in range(5, excel.nrows):
        if type(excel.row_values(i)[0]) == types.FloatType:
            parse_formula(excel.row_values(i)[1], excel.row_values(i)[2])
    initProcedure.operation = json.dumps(init_operation)
    try:
        InitProcedure.get(InitProcedure.number == initProcedure.number).delete_instance()
    except:
        pass
    initProcedure.save()
    return True

def parse_formula(pstring, location):
    for line in pstring.replace(" ", "").split("\n"):
        match_result = re.match(Formula_Regular, line)
        if match_result:
            init_operation.append([match_result.group(), location])

