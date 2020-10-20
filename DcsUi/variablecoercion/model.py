from random import random

from utils.WorkModels import PointModel, PointGroup

standard_structure = [
    ('force_value', '强制值', float),  # 强制值
    ('current_value', '当前值', float),  # 当前值
    ('sig_name', '变量名', str),  # 变量名
    ('sig_type', '变量类型', float),  # 变量类型
    ('slot', '变量标识', float),  # 变量标识
    ('channel', '通道号', str),  # 单位
]

table_structure = [
    ('chr', '数值类型', str),
    ('engineering_unit', 'engineering_unit', float),
    ('rlo', '工程量下限', str),
    ('rhi', '工程量上限', str),
    ('elo', '信号量下限', str),
    ('ehi', '信号量上限', str),
    ('initial', '初始值', str),
    ('reg', '功能码及地址', str),
    ('block', 'block', str),
    ('offset', 'offset', str),
    ('bit', 'bit', str),
]

total_structure = standard_structure + table_structure

data = []

current_value_date = {}


class variableGroupModel:

    @classmethod
    def currentDict(cls):
        row = 0
        currents = PointModel.all_points()
        for current in currents:
            current_value_date[row] = random()
            row += 1
        return current_value_date

    @classmethod
    def searchDate(cls, **kwargs):
        from utils.core import MainWindowConfig
        dic = []
        point = PointModel.all_points().dicts()
        column1 = kwargs.get('column1', '')
        column2 = kwargs.get('column2', '')
        value1 = kwargs.get('value1', '')
        value2 = kwargs.get('value2', '')
        relation = kwargs.get('relation', 'And')

        if column1 != '':
            for j in total_structure:
                if column1 == j[1]:
                    column1 = j[0]
        if column2 != '':
            for z in total_structure:
                if column2 == z[1]:
                    column2 = z[0]

        for date in point:
            if column1 != '' and column2 != '':
                if relation == 'And':
                    if value1 in str(date[column1]) and value2 in str(date[column2]):
                        date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                        date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                        dic.append(date)
                else:
                    if value1 in str(date[column1]) or value2 in str(date[column2]):
                        date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                        date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                        dic.append(date)
            elif column1 == '' and column2 != '':
                if value2 in str(date[column2]):
                    date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                    date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                    dic.append(date)
            elif column2 == '' and column1 != '':
                if value1 in str(date[column1]):
                    date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                    date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                    dic.append(date)
            else:
                date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                dic.append(date)
        return dic

    @classmethod
    def mandatorysearchDate(cls, **kwargs):
        from utils.core import MainWindowConfig
        dic = []
        point = PointModel.all_points().dicts()
        column1 = kwargs.get('column1', '')
        column2 = kwargs.get('column2', '')
        value1 = kwargs.get('value1', '')
        value2 = kwargs.get('value2', '')
        relation = kwargs.get('relation', 'And')

        if column1 != '':
            for j in total_structure:
                if column1 == j[1]:
                    column1 = j[0]
        if column2 != '':
            for z in total_structure:
                if column2 == z[1]:
                    column2 = z[0]

        for date in point:
            if MainWindowConfig.IOMapping.force_value[date['sig_name']] != None:
                if column1 != '' and column2 != '':
                    if relation == 'And':
                        if value1 in str(date[column1]) and value2 in str(date[column2]):
                            date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                            date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                            dic.append(date)
                    else:
                        if value1 in str(date[column1]) or value2 in str(date[column2]):
                            date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                            date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                            dic.append(date)
                elif column1 == '' and column2 != '':
                    if value2 in str(date[column2]):
                        date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                        date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                        dic.append(date)
                elif column2 == '' and column1 != '':
                    if value1 in str(date[column1]):
                        date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                        date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                        dic.append(date)
                else:
                    date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                    date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                    dic.append(date)
        return dic

    @classmethod
    def selectGroupData(cls, **kwargs):
        from utils.core import MainWindowConfig
        dic = []
        name = kwargs.get('name', '')
        column1 = kwargs.get('column1', '')
        column2 = kwargs.get('column2', '')
        value1 = kwargs.get('value1', '')
        value2 = kwargs.get('value2', '')
        relation = kwargs.get('relation', 'And')

        if column1 != '':
            for j in total_structure:
                if column1 == j[1]:
                    column1 = j[0]
        if column2 != '':
            for z in total_structure:
                if column2 == z[1]:
                    column2 = z[0]
        points = PointGroup.get(PointGroup.group_name == name)

        for date in points.points.dicts():
            if column1 != '' and column2 != '':
                if relation == 'And':
                    if value1 in str(date[column1]) and value2 in str(date[column2]):
                        date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                        date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                        dic.append(date)
                else:
                    if value1 in str(date[column1]) or value2 in str(date[column2]):
                        date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                        date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                        dic.append(date)
            elif column1 == '' and column2 != '':
                if value2 in str(date[column2]):
                    date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                    date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                    dic.append(date)
            elif column2 == '' and column1 != '':
                if value1 in str(date[column1]):
                    date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                    date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                    dic.append(date)
            else:
                date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                dic.append(date)
        return dic

    @classmethod
    def mandatorySelectGroupData(cls, **kwargs):
        from utils.core import MainWindowConfig
        dic = []
        name = kwargs.get('name', '')
        column1 = kwargs.get('column1', '')
        column2 = kwargs.get('column2', '')
        value1 = kwargs.get('value1', '')
        value2 = kwargs.get('value2', '')
        relation = kwargs.get('relation', 'And')
        points = PointGroup.get(PointGroup.group_name == name)

        if column1 != '':
            for j in total_structure:
                if column1 == j[1]:
                    column1 = j[0]
        if column2 != '':
            for z in total_structure:
                if column2 == z[1]:
                    column2 = z[0]

        for date in points.points.dicts():
            if MainWindowConfig.IOMapping.force_value[date['sig_name']] != None:
                if column1 != '' and column2 != '':
                    if relation == 'And':
                        if value1 in str(date[column1]) and value2 in str(date[column2]):
                            date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                            date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                            dic.append(date)
                    else:
                        if value1 in str(date[column1]) or value2 in str(date[column2]):
                            date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                            date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                            dic.append(date)
                elif column1 == '' and column2 != '':
                    if value2 in str(date[column2]):
                        date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                        date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                        dic.append(date)
                elif column2 == '' and column1 != '':
                    if value1 in str(date[column1]):
                        date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                        date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                        dic.append(date)
                else:
                    date['force_value'] = MainWindowConfig.IOMapping.force_value[date['sig_name']]
                    date['current_value'] = MainWindowConfig.IOMapping.current_value[date['sig_name']]
                    dic.append(date)
            return dic

    @classmethod
    def searchEdi(cls, text):
        lis = []
        point = PointModel.all_points()
        for data in point:
            if text in data.point_name:
                lis.append({'name': data.point_name, 'data': data})
        return lis

    @classmethod
    def addGroupData(cls, name, point):
        points = PointGroup.get(PointGroup.group_name == name).points
        points.add(point)

    @classmethod
    def deleteGroupData(cls, name, point):
        points = PointGroup.get(PointGroup.group_name == name).points
        points.remove(point)

    @classmethod
    def createGroup(cls, name, points):
        try:
            PointGroup.get(PointGroup.group_name == name)
            return False
        except Exception as e:
            PointGroup.create_group(name, points)
            return True

    @classmethod
    def getGroupData(cls, name):
        lis = []
        points = PointGroup.get(PointGroup.group_name == name).points
        for i in points:
            lis.append(i)
        return lis

    @classmethod
    def updataGroup(cls, name, points):
        lis = []
        group = PointGroup.get(PointGroup.group_name == name)
        group.points.clear()
        for i in points:
            lis.append(i)
            if len(lis) < 100:
                continue
            group.points.add(lis)
            lis.clear()
        group.points.add(lis)


def current_value(var) -> [float, int, list]:
    return random()
