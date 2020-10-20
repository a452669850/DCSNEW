from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import os
import collections
from static.Png import *
from utils.AcountModels import getPermission


class ToolBarSetting():
    def __init__(self, MainWindow):
        # MainWindow为工作栏所在窗口类
        super().__init__()
        if MainWindow.__class__.__name__ == 'MainWindow':
            self.actions = getPermission(MainWindow.user) # 如果是主窗口中的工具栏则根据用户名获取用户权限
            # print(permission)
            # if permission:
            #     self.actions = []
            #     [[self.actions.append(y) for y in eval(x)] for x in permission]
            
            # else:
            #     self.actions = None
        self.initSetting(MainWindow)
    def initSetting(self, MainWindow):
        # 为主窗口添加工具栏函数
        self.toolImgPath = ':/static/'
        if MainWindow.__class__.__name__ == 'MainWindow':
            # 创建菜单栏并添加菜单
            MainWindow.menubar = MainWindow.menuBar()  # 创建一个菜单栏实例menuber
            # MainWindow.viewMenu = MainWindow.menubar.addMenu('&视图')  # 添加菜单file
            MainWindow.projectMenu = MainWindow.menubar.addMenu('&工程')
            MainWindow.procedureTestingMenu = MainWindow.menubar.addMenu('&规程测试')
            MainWindow.performanceTestingMenu = MainWindow.menubar.addMenu('&规程管理')
            MainWindow.varForceMenu = MainWindow.menubar.addMenu('&变量强制')
            MainWindow.recordMenu = MainWindow.menubar.addMenu('&记录')
            # 为每个菜单添加对应关系方便添加子选项
            self.menuBarDict = {
                # '视图': MainWindow.viewMenu,
                '工程': MainWindow.projectMenu,
                '规程测试': MainWindow.procedureTestingMenu,
                '规程管理': MainWindow.performanceTestingMenu,
                '变量强制': MainWindow.varForceMenu,
                '记录': MainWindow.recordMenu
            }
            # 设置工具栏图标存储路径
            ''' 创建工具栏对应有序字典 按钮名 ： [(0: 不显示, 1: 在菜单栏和工具栏同时显示
            2: 只在工具栏显示), 所属菜单, 按钮文字提示, 按钮对应图标]'''
            self.toolBarDict = collections.OrderedDict() # 有序字典方便操作工具栏按钮的顺序
            # self.toolBarDict['viewDefault'] = [1, '视图', '恢复默认', 'view_default.png']
            self.toolBarDict['projectCreate'] = [1, '工程', '新建工程', 'project_new.png']
            self.toolBarDict['projectOpen'] = [1, '工程', '打开工程', 'project_open.png']
            self.toolBarDict['projectSave'] = [1, '工程', '保存工程', 'project_save.png']
            self.toolBarDict['proceduresImport'] = [1, '规程管理', '导入规程', 'procedures_import.png']
            self.toolBarDict['varforceUpdateGroup'] = [1, '规程管理', '用例组管理', 'varforce_update_group.png']
            # self.toolBarDict['proceduresDelete'] = [1, '工程', '删除规程', 'procedures_delete.png']
            self.toolBarDict['proceduresSettings'] = [1, '工程', '配置', 'procedures_settings.png']
            self.toolBarDict['procedureAutoRun'] = [1, '规程测试', '自动执行', 'procedure_run.png']
            self.toolBarDict['procedureDebug'] = [1, '规程测试', '单步执行', 'procedure_debug.png']
            self.toolBarDict['procedurePause'] = [1, '规程测试', '暂停/继续', 'procedure_pause.png']
            self.toolBarDict['procedureQuit'] = [1, '规程测试', '退出', 'procedure_quit.png']
            self.toolBarDict['procedureListPause'] = [1, '规程测试', '终止规程列表', 'procedure_pause_list.png']
            self.toolBarDict['logRunResult'] = [1, '记录', '测试记录', 'log_run_result.png']
            self.toolBarDict['logOperate'] = [1, '记录', '日志', 'log_operate.png']
            # self.toolBarDict['help'] = [2, '帮助', 'help.png']
            self.toolBarDict['variableSettings'] = [1, '变量强制', '变量组管理', 'variable_settings.png']
            self.toolBarDict['accountManagement'] = [2, '账户管理', 'account_management.png']
            self.toolBarDict['pharseManagement'] = [2, '短语库管理', 'init_procedures_import.png']
            self.toolBarDict['labelManagement'] = [2, '分类管理', 'statistical_report.png']
            self.toolBarDict['realTrend'] = [1,'记录', '实时趋势', 'procedures_export.png']
            self.toolBarDict['historyTrend'] = [1,'记录', '历史趋势', 'property_settings.png']
            # self.toolBarDict['communication'] = [2, '通讯', 'variable_settings_icon2.png']
            self.CreateToolBar(MainWindow)
        elif MainWindow.__class__.__name__ == 'VariableSettingsUi':
            # 创建菜单栏并添加菜单
            MainWindow.menubar = MainWindow.menuBar()  # 创建一个菜单栏实例menuber
            MainWindow.cancelMenu = MainWindow.menubar.addMenu('&取消强制')  # 添加菜单file
            # 为每个菜单添加对应关系方便添加子选项
            self.menuBarDict = {
                '取消强制': MainWindow.cancelMenu,
            }
            self.toolBarDict = collections.OrderedDict()
            # self.toolBarDict['varforceSetcol'] = [2, '显示列', 'var_force_set_col.png']
            # self.toolBarDict['varforceCancelCurrentroup'] = [1, '取消强制', '取消当前组强制', 'var_force_cancel_current_group.png']
            # self.toolBarDict['varforceCancelAllforceGroup'] = [1, '取消强制', '取消所有强制', 'var_force_cancel_all_group.png']
            self.toolBarDict['varforceFind'] = [2, '搜索', 'var_force_find.png']
            self.toolBarDict['varforceEdiTuple'] = [2, '编辑组', 'var_force_find_double_tuple.png']
            self.toolBarDict['varforceNewGroup'] = [2, '保存新组', 'varforce_new_group.png']
            self.toolBarDict['varforceAllForceGroup'] = [2, '所有强制列表', 'varforce_all_force_group.png']
            self.CreateToolBar(MainWindow)
    def CreateToolBar(self, MainWindow):
        MainWindow.toolBar = MainWindow.addToolBar('工具栏')  # 创建一个工具栏实例
        MainWindow.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 文字图片垂直排列
        # MainWindow.toolBar = MainWindow.addToolBar('工具栏')
        for key, value in self.toolBarDict.items():
            if value[0] == 1:
                # 创建一个事件和一个特定图标和一个退出的标签
                if key in ['proceduresImport', 'procedureAutoRun', 'procedureListPause', 'variableSettings', 'realTrend']:
                    MainWindow.toolBar = MainWindow.addToolBar('工具栏') 
                    MainWindow.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                if MainWindow.__class__.__name__ == 'MainWindow':
                    if self.actions and MainWindow.user != 'admin':
                        if value[2] not in self.actions: # 判断按钮是否在用户权限当中
                            continue
                Action = locals()['MainWindow.{}Action'.format(str(key))] = QAction(
                    QIcon(os.path.join(self.toolImgPath, value[-1])), value[-2], MainWindow)
                # Action.setShortcut('Ctrl+Q')    # 设置事件的快捷方式
                Action.setStatusTip(value[-2])  # 设置事件的状态提示
                Action.triggered.connect(getattr(MainWindow, '{}Clicked'.format(key)))  # 事件的触发
                self.menuBarDict[value[1]].addAction(Action)  # 菜单添加事件
                MainWindow.toolBar.addAction(Action)  # 绑定触发事件
            elif value[0] == 2:
                if MainWindow.__class__.__name__ == 'MainWindow':
                    if self.actions and MainWindow.user != 'admin':
                        if value[1] not in self.actions:
                            continue
                Action = locals()['MainWindow.{}Action'.format(str(key))] = QAction(
                    QIcon(os.path.join(self.toolImgPath, value[-1])), value[-2], MainWindow)
                Action.setStatusTip(value[-2])
                Action.triggered.connect(getattr(MainWindow, '{}Clicked'.format(key)))
                MainWindow.toolBar.addAction(Action)
        MainWindow.toolBar.setIconSize(QSize(50, 50))
        # MainWindow.toolBar.insertSeparator(MainWindow.projectCreateAction)
    

