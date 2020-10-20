# coding=utf-8
from time import time, sleep, strftime
import re
from utils import core
import random, json
from procedure.manage_procedure.models import InitProcedure

# init操作函数
def init_operation(runconfig, section_big_sort):
    runconfig.run_text, runconfig.run_sort, runconfig.run_result = "pass", section_big_sort[1]["sort"], True
    tmp_number = u'%s-%s-%s-%s' % (
        runconfig.run_usecase_number, runconfig.run_operation_section, runconfig.run_big_sort_index, runconfig.run_sort)
    if not runconfig.continue_run:
        initProcedure = InitProcedure.get(InitProcedure.id == 1)
        for init_formula in json.loads(initProcedure.operation):
            set_var = init_formula[0].split("=")[0]
            set_value = init_formula[0].split("=")[1]
            set_location = init_formula[1]
            # TODO core.Client.IoController.set_value @shurk
            # io_controller.set_var(set_var, set_value, address=set_location)
        core.Client.CurrentProcedureEditor.SetOperationsNumberValue(
            tmp_number, runconfig.run_text, runconfig.run_result)
        if runconfig.is_loop_run:
            if not runconfig.run_result:
                runconfig.save_loop_result()
        else:
            runconfig.save_run_result()
    runconfig.continue_run = False
    return runconfig.run_result


# write操作函数
# 如果包含startdelay，则再当前的self.start_delay_dict里面添加一个delay的时间{"startdelay1":time()}
def write_operation(runconfig, section_big_sort):
    if section_big_sort[1]["startdelay"] != "":
        runconfig.start_delay_dict[section_big_sort[1]["startdelay"]] = time()
    if section_big_sort[1]["delay"] != "":
        check_time = section_big_sort[1]["delay"].split(",")
        # 如果当前操作的delay时间大于上一步的操作时间
        while (time() - runconfig.start_delay_dict[check_time[0]]) < float(check_time[1]):
            read_loop(runconfig)
            sleep(runconfig.sleep_time)
            # 调用远程的设置值操作
    runconfig.run_text = section_big_sort[1]["formula"].replace(",", "\n")
    runconfig.run_sort = section_big_sort[1]["sort"]
    if not runconfig.continue_run:
        runconfig.run_result = remote_set(runconfig, section_big_sort[1]["location"])
    sleep(runconfig.sleep_time)
    tmp_number = u'%s-%s-%s-%s' % (
        runconfig.run_usecase_number, runconfig.run_operation_section, runconfig.run_big_sort_index, runconfig.run_sort)
    if not runconfig.continue_run:
        core.Client.CurrentProcedureEditor.SetOperationsNumberValue(
            tmp_number, runconfig.run_text, runconfig.run_result)
        if runconfig.is_loop_run:
            if not runconfig.run_result:
                runconfig.save_loop_result()
        else:
            runconfig.save_run_result()
    runconfig.continue_run = False
    return runconfig.run_result


# 调用远程的设置方法
def remote_set(runconfig, location):
    for item in runconfig.run_text.split(","):
        set_var = item.split("=")[0]
        set_value = item.split("=")[1]
        # TODO core.Client.IoController.set_value @shurk
        # if not self.io_controller.set_var(set_var, set_value, address=location):
        #     return False
    return random.choice([True, False])


# read操作函数，需要开始时间和read操作集合
def read_operation(runconfig, section_big_sort):
    global READ_RESULT
    READ_RESULT = {}
    start_read = time()  # read循环操作的时间
    for k in range(1, len(section_big_sort)):
        if section_big_sort[k]["delay"] != "":
            try:
                start_read = runconfig.start_delay_dict[section_big_sort[k]["delay"].split(",")[0]]
            except:
                start_read = time()
            break
    delay_time_list = []
    for j in range(1, len(section_big_sort)):
        delay_time_list.append(int(get_delay_time(section_big_sort[j])))
    max_delay_time = max(delay_time_list)
    # 循环检查read参数
    while (time() - start_read) <= (max_delay_time + runconfig.run_interval):
        runconfig.current_loop_list = get_loop_section(section_big_sort, start_read)
        # 调用loop操作
        read_loop(runconfig)
        sleep(runconfig.sleep_time)
    runconfig.continue_run = False
    for item in READ_RESULT.values():
        if not item:
            return False
    return True

# 循环操作
def read_loop(runconfig):
    """
    遍历循环列表中的检查操作["location,formula1,formula2",""]这种格式
    @return:
    """
    for item in runconfig.current_loop_list:
        check_formula = item["formula"].split(",")
        location = check_formula[0]
        runconfig.run_sort = item["sort"]
        # 对一个检查中的多个公式进行循环设置
        if not runconfig.continue_run:
            remote_read(runconfig, check_formula, location)
            if runconfig.is_loop_run:
                if not runconfig.run_result:
                    runconfig.save_loop_result()
            else:
                runconfig.save_run_result()


# 调用远程的取值方法
def remote_read(runconfig, check_formula, location):
    runconfig.run_text = ""
    for i in range(1, len(check_formula)):
        var_name = check_formula[i].split("=")[0]
        expected_values = float(check_formula[i].split("=")[1])
        # TODO core.Client.IoController.set_value @shurk
        # tuple_result = runconfig.io_controller.check_var(var_name, expected_values, address=location)

        tuple_result = (random.choice([True, False]), "aa")
        runconfig.run_text += var_name + "=" + str(tuple_result[1]) + "\n"
        runconfig.run_result = tuple_result[0]
        global READ_RESULT
        READ_RESULT[runconfig.run_sort] = runconfig.run_result
        tmp_number = u'%s-%s-%s-%s' % (
            runconfig.run_usecase_number, runconfig.run_operation_section, runconfig.run_big_sort_index,
            runconfig.run_sort)
        core.Client.CurrentProcedureEditor.SetOperationsNumberValue(
            tmp_number, runconfig.run_text, runconfig.run_result)


# 获取循环数组
def get_loop_section(section, start_time):
    loop_section = []
    v_loop_section = []
    # 先组合为一个循环执行的数组,从索引1开始，第0个是read标识
    for i in range(1, len(section)):
        if (time() - start_time) > int(get_delay_time(section[i])):
            loop_section.append(section[i])
    # 将delay和前面有重复的操作，延时改为-1
    for j in range(0, len(loop_section)):
        if int(get_delay_time(loop_section[j])) > 0:
            for k in range(0, j):
                # 比较检查的公式位置和变量是否相同，如果相同则将delay_time设为-1
                if compare_formula(loop_section[k]["formula"], loop_section[j]["formula"]):
                    loop_section[k]["delay"] = "-1"
    # 去掉delay_time 小于0的操作
    for m in range(0, len(loop_section)):
        if int(get_delay_time(loop_section[m])) >= 0:
            v_loop_section.append(loop_section[m])
    return v_loop_section


# 比较befor_formula是否包含在after_formula中
def compare_formula(befor_formula, after_formula):
    tmp_formual = after_formula.split(",")
    compare_list = []
    compare_list.append(tmp_formual[0])
    for i in range(1, len(tmp_formual)):
        compare_list.append(tmp_formual[i].split("=")[0])
    # 若有一个公式不包含在after_formula中，则返回False
    for item in befor_formula.split(","):

        if re.match(r'([0-9a-zA-Z\_]+)', item).group() not in compare_list:
            return False
    return True


# 返回当前操作中delay的时间
def get_delay_time(section_big_sort):
    if section_big_sort["delay"] != "" and "," not in section_big_sort["delay"]:
        return int(section_big_sort["delay"])
    elif section_big_sort["delay"] != "":
        return section_big_sort["delay"].split(",")[1]
    else:
        return 0
