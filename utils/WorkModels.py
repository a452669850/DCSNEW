# coding=utf-8
from __future__ import unicode_literals

from peewee import *

proxy = Proxy()


# for test
# import os.path
# path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dcs_io.db')
# print('>>>', path)
# database = SqliteDatabase(path)


class BaseModel(Model):
    class Meta:
        database = proxy


AI = 1
AO = 2
DI = 3
DO = 4
PI = 5

IO_CHOICES = (
    (AI, 'AI'),
    (AO, 'AO'),
    (DI, 'DI'),
    (DO, 'DO'),
    (PI, 'PI'),
)

# TODO: 网络设置需要4个项,RPC, S3, FTP, MODBUS, 根据下表构造表单(协议, 显示名, 键, 类型, 默认值)
DEFAULT_CONFIG = (
    ('RPC', '地址', 'RPC_HOST', str, ''),
    ('RPC', '端口', 'RPC_PORT', int, 9000),

    ('S3', '地址', 'S3_HOST', str, ''),
    ('S3', '端口', 'S3_PORT', int, 8888),

    ('FTP', '地址', 'FTP_HOST', str, ''),
    ('FTP', '端口', 'FTP_PORT', int, 22),
    ('FTP', '用户名', 'FTP_USER', str, ''),
    ('FTP', '密码', 'FTP_PASSWORD', str, ''),

    ('MODBUS', '地址', 'MODBUS_HOST', str, ''),
    ('MODBUS', '端口', 'MODBUS_PORT', int, 502),
)

standard_structure = [
    ('force_value_display', '强制值'),  # 强制值
    ('current_value_display', '当前值', float),  # 当前值
    ('point_name', '8000点名', str),  # 变量名
    ('comment', '描述', str),  # 描述
    ('meas_min', '最小值', float),  # 最小值
    ('meas_max', '最大值', float),  # 最大值
    ('meas_unit', '单位Meas.', str),  # 单位
]

table_structure = [
    ('id_code', 'Id-Code', str),
    ('elec_min', 'Electrical Min', float),
    ('elec_max', 'Electrical Max', float),
    ('elec_unit', 'Electrical Unit', str),
    ('io', 'I/O', str),
    ('extens_code', 'Extens.Code', str),
    ('designation', 'Designation', str),
    ('mod_var', '模型变量', str),
    ('sim_var', '接口变量', str),
    ('swi_var', '切换变量', str),
    ('signal_from', 'From', str),
    ('signal_to', 'To', str),
    ('io_type', 'I/O Type', str),
    ('functional_class', 'Functional class', str),
    ('signal_spec', 'Signal Spec.', str),
    ('power_supply', 'Power Supply', str),
    ('level', 'Level', str),
    ('diagram_number', 'Diagram Number', str),
    ('rev_note2', 'Rev. (NOTE2)', str),
    ('remarks', 'Remarks', str),
    ('cabinet_num', '机柜号', str),
    ('cabinet_type', '机箱', str),
    ('slot_num', '槽位', int),
    ('card_type', '卡件型号', str),
    ('channel_num', '通道号', str),
    ('terminal_type', '端子模块型号', str),
    ('terminal_channel', '端子通道号', int),
]

total_structure = standard_structure + table_structure


class NetworkConfig(BaseModel):
    id = AutoField()
    slot = FixedCharField(max_length=20, index=True, help_text='slot 是设备接口的唯一标识')
    protocol = FixedCharField(max_length=20, help_text='每种设备必须注册一个 Protocol')
    uri = CharField(max_length=255, help_text='设备配置')
    description = CharField(max_length=255, help_text='设备描述')
    enable = BooleanField(default=True, help_text='启用设备')


class PointModel(BaseModel):
    id = AutoField()
    sig_name = CharField(max_length=128, index=True, help_text='变量名')
    sig_type = FixedCharField(max_length=20, help_text='变量类型')
    chr = FixedCharField(max_length=20, help_text='数值类型')
    slot = FixedCharField(max_length=20, index=True, help_text='通信接口, 关联 `t_dev.slot`')
    # 单位换算
    engineering_unit = FixedCharField(max_length=20, help_text='engineering unit')
    # cv = pw.FixedCharField(max_length=2, help_text='C/V')
    rlo = FloatField(null=True, help_text='工程量下限')
    rhi = FloatField(null=True, help_text='工程量上限')
    elo = FloatField(null=True, help_text='信号量下限')
    ehi = FloatField(null=True, help_text='信号量上限')
    channel = CharField(max_length=255, help_text='通道')
    # termination = peewee.CharField(max_length=255, help_text='端子')
    # description = peewee.CharField(max_length=255, help_text='变量描述')
    initial = CharField(max_length=255, help_text='初始值')
    reg = IntegerField(null=True, help_text='功能码及地址')
    block = IntegerField(null=True)
    offset = IntegerField(null=True)
    bit = IntegerField(null=True)

    @classmethod
    def all_points(cls, page=None, paginate_by=20):
        query = cls.select()
        if page is not None:
            query = query.paginate(page, paginate_by)
        return query


class PointGroup(BaseModel):
    # 变量组
    group_name = CharField(max_length=255, null=True, verbose_name='Group Name')
    points = ManyToManyField(PointModel)

    @classmethod
    def create_group(cls, group_name, points=None):
        # type: (str, list) -> PointGroup
        """
        create a point group and add points to this group
        """
        lis = []
        with cls._meta.database.atomic():
            query = cls.create(group_name=group_name)
            if points:
                for i in points:
                    lis.append(i)
                    if len(lis) < 100:
                        continue
                    query.points.add(lis)
                    lis.clear()
                query.points.add(lis)
            return query

    @classmethod
    def all_groups(cls, page=None, paginate_by=20):
        query = cls.select().join(cls.points.get_through_model()).distinct()
        if page is not None:
            query = query.paginate(page, paginate_by)
        return query

    @classmethod
    def get_all(cls):
        return cls.select()


class TimeCard(BaseModel):
    id = AutoField()
    sig_name = CharField(max_length=128, index=True, help_text='变量名')
    pid = CharField(null=True, max_length=255, help_text='pid')
    tid = CharField(null=True, max_length=255, help_text='tid')
    edge = IntegerField(null=True)
    status = IntegerField(null=True)
    sequence = CharField(null=True, max_length=255, help_text='sequence')
    s_type = CharField(null=True, max_length=255, help_text='s_type')
    tm_out = IntegerField(null=True)

    @classmethod
    def selectTimer(cls, name):
        lis = []
        query = cls.select().where(cls.pid == name)
        for i in query:
            if i.edge == 0:
                lis.append([i.sig_name, i.tm_out, i.tid, 'DOWN', ''])
            if i.edge == 1:
                lis.append([i.sig_name, i.tm_out, i.tid, 'UP', ''])
        return lis


def init_database(database: Database):
    # 初始化数据库
    proxy.initialize(database)
    database.create_tables([NetworkConfig, PointModel, PointGroup, TimeCard,
                            PointGroup.points.get_through_model()], safe=True)
