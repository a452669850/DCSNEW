# -*- coding: UTF-8 -*-

from peewee import *
from utils import core

database_proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = core.Client.database_proxy

    @classmethod
    def update_obj(cls, obj):
        obj.save()

    @classmethod
    def delete_obj(cls, id):
        cls.get(cls.id == id).delete_instance()

    @classmethod
    def get_all(cls):
        return cls.select()

    @classmethod
    def get_by_id(cls, id):
        return cls.get(cls.id == id)


# 规程类模型
class Procedure(BaseModel):
    name = CharField()
    number = CharField(unique=True)
    usecase = CharField()

    # 保存规程，如果已经存在，删除之后再保存
    def save_obj(self):
        delete_p = None
        try:
            delete_p = Procedure.get(Procedure.number == self.number)
        except:
            DataError
        if delete_p:
            import json
            save_usecase_list = json.loads(self.usecase)
            dele_usecase_list = json.loads(delete_p.usecase)
            for item in dele_usecase_list:
                if item not in save_usecase_list:
                    save_usecase_list.append(item)
            delete_p.delete_instance()
            self.usecase = json.dumps(sorted(save_usecase_list))
        self.save()


# 用例集合类模型
class Usecase(BaseModel):
    name = CharField()
    number = CharField(unique=True)
    IC = CharField(null=True)
    operation = TextField()
    description = CharField(null=True)

    def save_obj(self):
        try:
            delete_u = Usecase.get(Usecase.number == self.number)
            delete_u.delete_instance()
        except:
            DataError
        self.save()


# 用例组 类模型
class UsecaseGroup(BaseModel):
    name = CharField(unique=True)
    usecase = CharField()


# 运行时信息
class RunResult(BaseModel):
    run_uuid = CharField()
    procedure_number = CharField(null=True)
    run_type = IntegerField()
    procedure_name = CharField(null=True)
    usecase_group_name = CharField(null=True)
    usecase_number = CharField()
    run_usecase_index = IntegerField(null=True)
    operation_section = IntegerField()
    section_sort = IntegerField()
    run_text = CharField()
    run_time = DateTimeField()
    run_result = BooleanField()
    is_stop = BooleanField()
    run_big_sort = IntegerField()

    def itemData(self):
        obj = None
        if self.procedure_number:
            try:
                obj = Procedure.get(Procedure.number == self.procedure_number)
            except:
                pass
        elif self.usecase_group_name:
            try:
                obj = UsecaseGroup.get(UsecaseGroup.name == self.usecase_group_name)
            except:
                pass
        if obj:
            from test.ui_data import FileObj
            return FileObj(obj)
        else:
            return None

    @classmethod
    def get_all(cls):
        return cls.select().group_by(RunResult.run_uuid).order_by(-cls.run_time)

    @classmethod
    def delete_obj(cls, uuid):
        query = cls.delete().where(cls.run_uuid == uuid)
        query.execute()

    @classmethod
    def delete_stop_result(cls, uuid):
        query = cls.update(is_stop=False).where(cls.run_uuid == uuid)
        query.execute()

    @classmethod
    def search_result(cls, **kwargs):
        """
        @param kwargs: type = 0,1,2,目前只查询规程和用例组
                        is_complete = 0,1,2
                        number = None,"number"
                        name = None, "name"
        @return:
            run_result query_result
        """
        is_complete_map = {1: False, 2: True}
        type = kwargs.get('type', None)
        is_complete = kwargs.get('is_complete', None)
        number = kwargs.get('number', None)
        name = kwargs.get('name', None)
        if type != 0:
            if is_complete != 0:
                return cls.select().where((RunResult.run_type == type) &
                                          (RunResult.is_stop == is_complete_map.get(is_complete)) &
                                          (RunResult.usecase_group_name.contains(name) |
                                           RunResult.procedure_name.contains(name)) &
                                          (RunResult.procedure_number.contains(number) |
                                           RunResult.usecase_number.contains(number))
                                          ).group_by(RunResult.run_uuid).order_by(cls.run_time)
            else:
                return cls.select().where((RunResult.run_type == type) &
                                          (RunResult.usecase_group_name.contains(name) |
                                           RunResult.procedure_name.contains(name)) &
                                          (RunResult.procedure_number.contains(number) |
                                           RunResult.usecase_number.contains(number))
                                          ).group_by(RunResult.run_uuid).order_by(cls.run_time)
        else:
            if is_complete != 0:
                return cls.select().where(
                    (RunResult.is_stop == is_complete_map.get(is_complete)) &
                    (RunResult.usecase_group_name.contains(name) |
                     RunResult.procedure_name.contains(name)) &
                    (RunResult.procedure_number.contains(number) |
                     RunResult.usecase_number.contains(number))
                ).group_by(RunResult.run_uuid).order_by(cls.run_time)
            else:
                return cls.select().where(
                    (RunResult.usecase_group_name.contains(name) |
                     RunResult.procedure_name.contains(name)) &
                    (RunResult.procedure_number.contains(number) |
                     RunResult.usecase_number.contains(number))
                ).group_by(RunResult.run_uuid).order_by(cls.run_time)

    @classmethod
    def get_finshed_result(cls, result_type):
        """
            获取测试结果列表，测试结果都是测试完成的
        @return:测试结果列表
        """
        if result_type == "procedure":
            return cls.select().where((RunResult.procedure_number != "") &
                                      (RunResult.is_stop == False)).group_by(RunResult.run_uuid).order_by(-cls.run_time)
        elif result_type == "usecasegroup":
            return cls.select().where((RunResult.usecasegroup != "") &
                                      (RunResult.is_stop == False)).group_by(RunResult.run_uuid).order_by(-cls.run_time)
        elif result_type == "usecase":
            return cls.select().where((RunResult.usecasegroup == "") & (RunResult.is_stop == False) &
                                      (RunResult.procedure_number == "")).group_by(RunResult.run_uuid).order_by(
                -cls.run_time)
        else:
            return cls.select().where(RunResult.is_stop == False).group_by(RunResult.run_uuid).order_by(-cls.run_time)

    @classmethod
    def get_stopped_result(cls, result_type):
        """
        获取终止列表，测试都是暂停之后的结果
        @return:终止测试列表
        """
        if result_type == "procedure":
            return cls.select().where((RunResult.procedure_number != "") &
                                      (RunResult.is_stop == True)).group_by(RunResult.run_uuid).order_by(-cls.run_time)
        elif result_type == "usecasegroup":
            return cls.select().where((RunResult.usecasegroup != "") &
                                      (RunResult.is_stop == True)).group_by(RunResult.run_uuid).order_by(-cls.run_time)
        elif result_type == "usecase":
            return cls.select().where((RunResult.usecasegroup == "") & (RunResult.is_stop == True) &
                                      (RunResult.procedure_number == "")).group_by(RunResult.run_uuid).order_by(
                -cls.run_time)
        else:
            return cls.select().where(RunResult.is_stop == True).group_by(RunResult.run_uuid).order_by(-cls.run_time)


class InitProcedure(BaseModel):
    name = CharField()
    number = CharField(unique=True)
    IC = CharField()
    operation = TextField()


class StatisticalReport(BaseModel):
    result_uuid = CharField()

    # procedure 1
    # usecasegroup 2
    # usecase 3
    report_type = SmallIntegerField()
    name_or_number = CharField()
    start_time = DateTimeField()
    end_time = DateTimeField()
    pass_rate = CharField()
    operator = CharField()

    @classmethod
    def search(cls, **kwargs):
        report_type = kwargs.get("report_type", None)
        name_or_number = kwargs.get('name_or_number', None)
        if report_type == 0:
            report_type = None
        if report_type and (not name_or_number):
            return cls.select().where(StatisticalReport.report_type == report_type)
        elif (not report_type) and name_or_number:
            return cls.select().where(StatisticalReport.name_or_number.contains(name_or_number))
        elif report_type and name_or_number:
            return cls.select().where((StatisticalReport.report_type == report_type) & (
                StatisticalReport.name_or_number.contains(name_or_number)))
        else:
            return cls.select()


class LoopRunResult(BaseModel):
    run_uuid = CharField()
    procedure_number = CharField(null=True)
    run_type = IntegerField()
    procedure_name = CharField(null=True)
    usecase_group_name = CharField(null=True)
    usecase_number = CharField()
    run_usecase_index = IntegerField(null=True)
    operation_section = IntegerField()
    section_sort = IntegerField()
    run_text = CharField()
    run_time = DateTimeField()
    run_result = BooleanField()
    is_stop = BooleanField()
    run_big_sort = IntegerField()

# 测试报告对应的原始规程的信息
# class ResultInitInfo(BaseModel):
#     run_uuid = CharField()
