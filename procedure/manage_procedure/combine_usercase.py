# -*- coding: UTF-8 -*-
'''
    最用例进行组合，生成新的用例组或者规程
'''

from .models import Usecase, UsecaseGroup, Procedure
import json

def list_all_usecase():
    usecases = Usecase.get_all()
    return usecases

#组合用例组为新的用例组
def usecase_group():
    usecases = list_all_usecase()
    usecaseGroup = UsecaseGroup()
    usecaseGroup.usecase = []
    for usecase in usecases:
        usecaseGroup.usecase.append(usecase.number)
    usecaseGroup.name = "第一个用例组"
    usecaseGroup.usecase = json.dumps(usecaseGroup.usecase)
    #usecaseGroup.create_table()
    usecaseGroup.save()


#组合用例组为新的规程
def make_procedure():
    usecases = list_all_usecase()
    procedure = Procedure()
    procedure.usecase = []
    for usecase in usecases:
        procedure.usecase.append(usecase.number)
    procedure.name = "组合的第二个规程"
    procedure.number = "TP3RPN04"
    procedure.usecase = json.dumps(procedure.usecase)
    procedure.save()


if __name__ =="__main__":
    from utils import core
    core.Client.setDb('C:\\Users\\zhan\\Desktop\\dcs_pro\\p1\\.resources\\dcs.db')

    usecase_group()
    #make_procedure()
