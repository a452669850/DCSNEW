import json
import os

from utils.AcountModels import *
from utils.ClientModels import *
from utils.WorkModels import *
from utils.core import MainWindowConfig
from utils.iomapping import IOMapping


def initDatabase(dbPath):
    # 创建数据库
    lis = [
        '新建工程', '打开工程', '保存工程',
        '导入工程', '用例组管理', '配置',
        '自动执行', '单步执行', '暂停/继续',
        '退出', '终止规程列表', '变量组管理',
        '测试记录', '日志', '账户管理'
    ]
    row = 1

    db = SqliteDatabase(dbPath)
    database_proxy.initialize(db)
    modelsArr = [
        User, Group, UserGroup, Operation, GroupOperatePermission, LoopRunResult, Phrase,
        Procedure, UsecaseGroup, Usecase, RunResult, InitProcedure, StatisticalReport, Classification
        , Script
    ]

    db.connect()
    db.create_tables(modelsArr, safe=True)
    if not User.get_user_by_username('admin'):
        User.create_user('admin', 'admin')
    for i in lis:
        Operation.create_operation(row, name=i)
        row += 1


def createConfig(projectPath, projectName):
    # 创建文件夹以及配置文件
    os.mkdir(os.path.join(projectPath, '.resources'))
    os.mkdir(os.path.join(projectPath, '.userdata'))
    os.mkdir(os.path.join(projectPath, '规程文档'))
    os.mkdir(os.path.join(projectPath, 'log'))
    projectDict = {'project_name': projectName}
    with open(os.path.join(projectPath, 'projectDate.json'), 'w', encoding='utf-8') as f:
        json.dump(projectDict, f)


def connectDb(projectPath):
    # 链接数据库
    if projectPath:
        iomapping = IOMapping(projectPath, 2)
        MainWindowConfig.setIOMapping(iomapping)
        dbPath = os.path.join(projectPath, '.resources', 'dcs.db')
        db = SqliteDatabase(dbPath)
        database_proxy.initialize(db)
        db.connect()
        return dbPath


def judgeProjectPath(projectPath):
    # 判断工程路径是否有效
    if projectPath:
        if os.path.exists(projectPath):
            if {'.resources', '.userdata', '规程文档'} < set(os.listdir(projectPath)):
                return True
            else:
                False
        else:
            return False
    else:
        return False
