# -*- coding: utf-8 -*-

import json
import os
import tempfile
import pathlib

from utils.ClientModels import Phrase

APPNAME = 'dcsIde'

dataDir = os.path.join(os.getenv('APPDATA'), APPNAME)

if not os.path.exists(dataDir):
    os.makedirs(dataDir)

logFile = open(os.path.join(dataDir, "dcsIde.log"), 'w')

tempDir = os.path.join(tempfile.gettempdir(), 'dcsIde')

from peewee import Proxy

# NOTE: Magic... You must explicit import these package,
# or PyInstaller will not found them
# import ConfigParser  # NoQA
# from passlib.handlers import pbkdf2  # NoQA
# from pyexcel_xls import xls  # NoQA
jsonPath = os.path.join(pathlib.Path('~').expanduser().absolute().as_posix(), 'dcslde.json') # json文件路径

from DcsUi.variablecoercion.model import total_structure


class MainWindowConfig(object):
    projectName = None
    header = total_structure
    ContinueRunFalse = False
    RunInterval = 500
    IOMapping = None
    DIC = {
        1: ['新建工程', '打开工程', '保存工程'],
        2: ['导入工程', '用例组管理', '配置'],
        3: ['自动执行', '单步执行', '暂停/继续', '退出', '变量组管理'],
        4: ['终止规程列表', '测试记录', '日志'],
        5: ['账户管理']
    }

    @classmethod
    def setIOMapping(cls, iomapping):
        cls.IOMapping = iomapping


class Client(object):
    """
    LOG: Project.AddLog: test.log_info_DCSLog
    """
    Cwd = None
    App = None
    MainFrame = None
    Project = None
    TabMgr = None
    ToolMgr = None
    WinMgr = None
    TrendMgr = None

    TrendAxe = None
    TrendAxeData = []
    TrendAxeLine = ['A', 'B', 'C']
    TrendAxeLineObj = []
    TrendFigureCanvas = None

    StatusBar = None

    User = None
    db = None

    CurrentProcedureEditor = None
    CurrentProcedure = None
    ContinueRunProcedure = False
    CurrentRun = None
    RunInterval = None
    IOMapping = None
    ContinueRunFalse = False

    RunDirty = False

    ThemeBackgroundColor = '#A5C3DC'

    PermissionKeyOrObj = None

    database_proxy = Proxy()

    @classmethod
    def setIOMapping(cls, iomapping):
        cls.IOMapping = iomapping

    @classmethod
    def setCurrentProcedureEditor(cls, editor):
        # .SetOperationsNumberValue
        #  number: 标识
        #  real_result：实际结果
        #  result_check：是否一致
        if not editor:
            cls.CurrentProcedureEditor = None
            cls.CurrentProcedure = None
        else:
            cls.CurrentProcedureEditor = editor
            cls.CurrentProcedure = editor.itemData

    @classmethod
    def setCurrentRun(cls, currentRun):
        cls.CurrentRun = currentRun

    @classmethod
    def setPermissionKeyOrObj(cls, permissionKeyOrObj):
        cls.PermissionKeyOrObj = permissionKeyOrObj

    @classmethod
    def setUser(cls, user):
        cls.User = user
        return cls.User

    @classmethod
    def clear(cls):
        cls.setUser(user=None)

    @classmethod
    def setCwd(cls, Cwd):
        cls.Cwd = Cwd

    @classmethod
    def setApp(cls, App):
        cls.App = App

    @classmethod
    def setFrame(cls, main_frame):
        cls.MainFrame = main_frame

    @classmethod
    def setProject(cls, Project):
        cls.Project = Project
        cls.setDb(Project.DbPath)

    @classmethod
    def setDb(cls, DbPath):
        from peewee import SqliteDatabase
        cls.db = SqliteDatabase(DbPath)
        cls.database_proxy.initialize(cls.db)

        from .db import initDatabase
        initDatabase(cls.db)

    @classmethod
    def setTabMgr(cls, TabMgr):
        cls.TabMgr = TabMgr

    @classmethod
    def setToolMgr(cls, ToolMgr):
        cls.ToolMgr = ToolMgr

    @classmethod
    def setWinMgr(cls, WinMgr):
        cls.WinMgr = WinMgr

    @classmethod
    def setTrendMgr(cls, TrendMgr):
        cls.TrendMgr = TrendMgr

    @classmethod
    def setStatusBar(cls, statusBar):
        cls.StatusBar = statusBar

    @classmethod
    def getMenuBarList(cls):
        cwd = cls.Cwd
        try:
            path = os.path.join(cwd, 'static', 'data', 'operation.json')
            f = open(path, 'r')
            menuBarData = json.loads(f.read())
            f.close()
        except Exception as e:
            # print e.message
            menuBarData = []
        return menuBarData


def DataDir():
    return dataDir


def TempDir():
    return tempDir


def Log(*text):
    text = " ".join([str(t) for t in text])
    try:
        print(text)
        if not text.endswith("\n"):
            text += "\n"
        logFile.write(text)
        logFile.flush()
    except:
        pass


def IsProject(dirPath):
    return os.path.isfile(os.path.join(dirPath, 'project.data.yaml'))


def IsNewProjectPath(dirPath):
    return False if os.listdir(dirPath) else True


def getVarForceColsStruct():
    from .WorkModels import table_structure
    return [i for i in table_structure[1:]]


import time, datetime


def calTime(date1, date2):
    date1 = time.strptime(date1, "%Y-%m-%d %H:%M:%S")
    date2 = time.strptime(date2, "%Y-%m-%d %H:%M:%S")
    date1 = datetime.datetime(date1[0], date1[1], date1[2], date1[3], date1[4], date1[5])
    date2 = datetime.datetime(date2[0], date2[1], date2[2], date2[3], date2[4], date2[5])
    return date2 - date1
