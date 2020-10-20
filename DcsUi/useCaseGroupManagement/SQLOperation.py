from utils.ClientModels import *


class sqlOperation:

    @classmethod
    def selectusecasegroup(cls):
        # 查询所有用例组
        lis = []
        gops = UsecaseGroup.select()
        for gop in gops:
            lis.append([gop.usecase_group_number, gop.name, gop.usecase])
        return lis

    @classmethod
    def selectProcedures(cls):
        # 查询规程
        lis = []
        gops = Procedure.select()
        for gop in gops:
            lis.append([gop.number, gop.name, gop.usecase])
        return lis

    @classmethod
    def selectUsecase(cls, name):
        # 通过用例组名称查询用例组
        gops = UsecaseGroup.select().where(UsecaseGroup.name == name)
        for gop in gops:
            return eval(gop.usecase)

    @classmethod
    def selectProceduresID(cls, number):
        # 根据规程编码查询对应规程id
        gops = Procedure.select().where(Procedure.number == number)
        for gop in gops:
            return gop.id

    @classmethod
    def deleteProcedures(cls, number):
        # 删除规程
        Procedure.delete_obj(cls.selectProceduresID(number))

    @classmethod
    def selectUsecaseNum(cls, number):
        """通过用例编号查找"""
        gops = Usecase.select().where(Usecase.number == number)
        for gop in gops:
            return gop.id

    @classmethod
    def deleteUsecase(cls, number):
        """删除"""
        Usecase.delete_obj(cls.selectUsecaseNum(number))

    @classmethod
    def searchUsecaseGroup(cls, text):
        """模糊查询用例组"""
        lis = []
        usecasegroups = UsecaseGroup.select().where(
            (UsecaseGroup.name.contains(text)) |
            (UsecaseGroup.usecase_group_number.contains(text))
        )
        if len(usecasegroups):
            for usecasegroup in usecasegroups:
                lis.append([usecasegroup.usecase_group_number, usecasegroup.name, usecasegroup.usecase])
        return lis

    @classmethod
    def searchProcedures(cls, text):
        """模糊查询规程"""
        lis = []
        procedures = Procedure.select().where(
            (Procedure.name.contains(text)) |
            (Procedure.number.contains(text))
        )
        if len(procedures):
            for procedure in procedures:
                lis.append([procedure.number, procedure.name, procedure.usecase])
        return lis
