# -*- coding: UTF-8 -*-
"""
    parse procedure_file
"""
import os,xlrd,json,types,re
from test.log_info import DCSLog, DCSLogType
from utils import core
from collections import Counter


# Formula_Regular = r'^([\w]+)=([-+]?[0-9]+\.[0-9]+[eE][-+]?[0-9]+)|^([\w]+)=([-+]?[0-9]+\.[0-9]+)|^([\w]+)=([-+]?[0-9]+)'
Formula_Regular = r'^([\w]+)=([\+\-]?[\d]+([\.][\d]*)?([Ee][+-]?[\d]+)?)'

def list_procedure():
    rootdir = ur"E:\pycharmWork\zhong\procedure_file"
    list_p = []
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:  # 输出文件信息
            list_p.append(os.path.join(parent, filename))
    return list_p


def select_p():
    list_p = list_procedure()
    if os.path.exists(list_p[0]):
        parse_procedure(list_p[0])
    else:
        print "解析的规程不存在"


def open_excel(pstr):
    try:
        procedure = xlrd.open_workbook(pstr)
        return procedure
    except Exception, e:
        print str(e)


from models import Procedure, Usecase


def parse_procedure(pstr):
    global all_formula_val  # 全局变量用来保存规程的变量名
    all_formula_val = []
    data = open_excel(pstr)
    excel = data.sheets()[0]
    procedure = Procedure()
    procedure.name = excel.row_values(0)[1]
    procedure.number = excel.row_values(0)[3]
    procedure.usecase = []
    check_excel = check_excel_line(excel)
    if check_excel:
        for check_log in check_excel:
            dcs_log_info(check_log, DCSLogType.ERROR)
    else:
        dcs_log_info(u'正在导入规程:' + procedure.name + u'规程编号为:' +
                     procedure.number, DCSLogType.DEFAULT)
        usecase_save = parse_usecase(excel, procedure)
        procedure.usecase = json.dumps(procedure.usecase)
        if usecase_save:
            procedure.save_obj()
            dcs_log_info(u'规程导入成功', DCSLogType.RIGHT)
            core.Client.StatusBar.clear()


def parse_usecase(excel, procedure):
    usercase_pass = True
    for rownum in range(1, excel.nrows):
        row = excel.row_values(rownum)
        if row[0] == u"测试用例":
            usecase = Usecase()
            usecase.name = row[1]
            usecase.number = row[3]
            procedure.usecase.append(usecase.number)
            usecase.IC = row[8]
            usecase.description = row[5]
            usecase.operation = json.dumps(parse_operation(excel, rownum))
            # TODO 检查 all_formula_val 变量是否存在于点表
            if usecase.operation != "false":
                usecase.save_obj()
            else:
                usercase_pass = False
    return usercase_pass


def parse_operation(excel, rownum):
    oper = []
    k = 0
    subrownum = rownum + 3
    total_lines = excel.nrows
    while subrownum < excel.nrows:
        subrow = excel.row_values(subrownum)
        if subrow[0] == ur"测试用例":
            break
        elif type(subrow[0]) != types.FloatType:
            oper.append([subrow[0]])
            subrownum += 1
            j = 1
            k += 1
        elif ur"设置" in subrow[1]:
            write_formula = parse_write(subrow[1])
            if not write_formula:
                dcs_log_info(u'规程第' + str(subrownum + 1) + u'行公式解析错误\n' + subrow[1], DCSLogType.ERROR)
                return False
            oper[k - 1].append(["WRITE", {"sort": str(int(subrow[0])), "name": subrow[1], "remark": subrow[8],
                                          "startdelay": parse_startdelay(subrow[1]),
                                          "delay": parse_delay(subrow[1]),
                                          "location": subrow[2], "formula": write_formula}])
            j = j + 1
            subrownum += 1
        elif ur"检查" in subrow[1]:
            first_read = True
            while subrownum < excel.nrows:
                rsubrow = excel.row_values(subrownum)
                if ur'检查' not in rsubrow[1]:
                    break
                if first_read:
                    read_formula = parse_read(rsubrow[3])
                    if not read_formula:
                        dcs_log_info(u'规程第' + str(subrownum + 1) + u'行公式解析错误\n' +
                                     rsubrow[1] + u"\n预期:" + rsubrow[3], DCSLogType.ERROR)
                        return False
                    oper[k - 1].append(
                        ["READ", {"sort": str(int(rsubrow[0])), "name": rsubrow[1], "remark": rsubrow[8],
                                  "delay": parse_delay(rsubrow[1]), "except": rsubrow[3],
                                  "location": rsubrow[2], "formula": read_formula}
                         ])
                    first_read = False
                elif not first_read:
                    read_formula = parse_read(rsubrow[3])
                    if not read_formula:
                        dcs_log_info(u'规程第' + str(subrownum + 1) + u'行公式解析错误\n' +
                                     rsubrow[1] + u"\n预期:" + rsubrow[3], DCSLogType.ERROR)
                        return False
                    oper[k - 1][j].append({"sort": str(int(rsubrow[0])), "name": rsubrow[1], "remark": rsubrow[8],
                                           "delay": parse_delay(rsubrow[1]), "except": rsubrow[3],
                                           "location": rsubrow[2], "formula": read_formula})
                subrownum += 1
            j = j + 1
        elif ur"初始化" in subrow[1]:
            oper[k - 1].append(["INIT", {"sort": str(int(subrow[0])), "name": subrow[1], "remark": subrow[8],
                                         "location": subrow[2], "except": subrow[3]}
                                ])
            j = j + 1
            subrownum += 1
        else:  # 以上几种都不存在的时候返回False
            dcs_log_info(u'规程第' + str(subrownum + 1) + u'暂不支持该操作', DCSLogType.ERROR)
            return False
        complete_progress = 100 * float(subrownum) / float(total_lines) if total_lines else 0
        # dcs_log_info(complete_progress, DCSLogType.DEFAULT)
        core.Client.StatusBar.updateProcess(int(complete_progress))

    return oper


# 解析设置值的公式，匹配顺序是科学计数法-》小数-》整数
def parse_write(name):
    formula = []
    for subline in name.replace(" ", "").split("\n"):
        if subline != "" and "DELAY" not in subline:
            match_result = re.match(Formula_Regular, subline)
            if match_result:
                formula.append(match_result.group())
                # 保存全部的变量名 供后续检查变量是否存在
                all_formula_val.append(match_result.group().split("=")[0])
    # 如果设置公式匹配数为0 ，返回fasle
    if len(formula) == 0:
        return False
    return ",".join(formula)


# 解析检查值的公式,匹配顺序是科学计数发 -》小数-》整数
def parse_read(name):
    assert_line = name.split("\n")
    formula = []
    if len(assert_line) > 0:
        formula.append(re.match(r'^\w+', assert_line[0]).group())
        for i in range(1, len(assert_line)):
            match_result = re.match(Formula_Regular, assert_line[i])
            if match_result:
                formula.append(match_result.group())
                # 保存全部的变量名 供后续检查变量是否存在
                all_formula_val.append(match_result.group().split("=")[0])
    if len(formula) < 2:  # 预期结果的公式匹配错误
        return False
    else:
        return ",".join(formula)


# 解析公式中的delaytime,比如DELAY4=4s 则返回 "DELAY4,4"
def parse_delay(name):
    line = name.split("\n")
    delay_time = ""
    for subline in line:
        if "DELAY" in subline:
            if re.match(r'^(DELAY\d+)', subline):
                delay_time = ["START" + subline.split("=")[0], re.match(r'\d+', subline.split("=")[1]).group()]
    return ",".join(delay_time)


# 解析公式中的startdelay,比如是STARTDELAY4=0 ,则返回STARTDELAY4
def parse_startdelay(name):
    line = name.split("\n")
    startdelay = ""
    for subline in line:
        if "STARTDELAY" in subline:
            startdelay = subline.split("=")[0].replace(" ", "")
    return startdelay


def dcs_log_info(infomation, dcs_log_type):
    log = DCSLog(infomation, dcs_log_type)
    core.Client.Project.AddLog(log)


def check_excel_line(excel):
    excel_error = []
    if (excel.row_values(0)[0] != u'规程名称') or (excel.row_values(0)[2] != u'规程编号'):
        excel_error.append(u"不是规程文件")
        return excel_error
    for i in range(0, excel.nrows):
        if (not excel.row_values(i)[0]) and (not excel.row_values(i)[1]):
            excel_error.append(u'表格第' + str(i + 1) + u"行,规程可能有空行")
        if type(excel.row_values(i)[0]) == types.FloatType:
            if ur"检查" in excel.row_values(i)[1]:
                if not parse_read(excel.row_values(i)[3]):
                    excel_error.append(u'表格第' + str(i + 1) + u"行,公式错误")
            elif ur"设置" in excel.row_values(i)[1]:
                if not parse_write(excel.row_values(i)[1]):
                    excel_error.append(u'表格第' + str(i + 1) + u"行,公式错误")
            elif ur"初始化" in excel.row_values(i)[1]:
                pass
            else:
                excel_error.append(u'表格第' + str(i + 1) + u"行,无法解析该语义")

    # col_num = [int(i) for i in excel.col_values(0)[5:] if type(i)==float]
    # for k,v in Counter(col_num).iteritems():
    #     if v >1:
    #         excel_error.append(u'表格第' + str(k+5) + u'行，操作编号有重复')
    return excel_error
