import time

import pandas as pd
from influxdb import InfluxDBClient


def select_library():
    """连接数据库"""
    client = InfluxDBClient('localhost', 8086, 'root', 'admin', '123456')
    return client.get_list_database()


def save(name):
    """创建存储的库"""
    client = InfluxDBClient('localhost', 8086, 'root', 'admin', '123456')

    client.create_database(name)

    client.create_retention_policy('history', '30d', 1, database=name, default=True)


def add_to_history(time, name, value, str, Libraryname):
    """Libraryname代表插入数据库的库名
       time代表插入的时间
       name代表点名
       value代表插入的值
       str是时间戳
    """
    client = InfluxDBClient('localhost', 8086, 'root', 'admin', '123456')

    points = [
        {
            'measurement': name,
            'time': time,
            'fields': {
                'value': value,
                'year': time[0:4],
                'month': time[0:7],
                'day': time[0:10],
                'hour': time[0:13],
                'minute': time[0:16],
                'second': time[0:19],
                'timestamp': str
            }
        }
    ]
    client.write_points(points, database=Libraryname)


def select_history(name, str, Libraryname):
    """Libraryname代表插入数据库的库名
        name代表点名
        str表示模式
        """
    client = InfluxDBClient('localhost', 8086, 'root', 'admin', '123456')

    result = client.query('select * from %s;' % name, database=Libraryname)
    temp = pd.DataFrame(result.get_points())
    if str == '年':
        grouped = temp['value'].groupby(temp['year'])
        for i in grouped:
            yield (i[0], i[1].mean())
    elif str == '月':
        grouped = temp['value'].groupby(temp['month'])
        for i in grouped:
            yield (i[0], i[1].mean())
    elif str == '日':
        grouped = temp['value'].groupby(temp['day'])
        for i in grouped:
            yield (i[0], i[1].mean())
    elif str == '时':
        grouped = temp['value'].groupby(temp['hour'])
        for i in grouped:
            yield (i[0], i[1].mean())
    elif str == '分':
        grouped = temp['value'].groupby(temp['minute'])
        for i in grouped:
            yield (i[0], i[1].mean())
    elif str == '秒':
        grouped = temp['value'].groupby(temp['second'])
        for i in grouped:
            yield (i[0], i[1].mean())
    else:
        grouped = temp['value'].groupby(temp['timestamp'])
        for i in grouped:
            yield (i[0], i[1].mean())
