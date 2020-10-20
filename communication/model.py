import peewee

proxy = peewee.Proxy()


class communicationModel(peewee.Model):
    class Meta:
        database = proxy


class DevModel(communicationModel):
    id = peewee.AutoField()
    slot = peewee.FixedCharField(max_length=20, index=True, help_text='slot 是设备接口的唯一标识')
    protocol = peewee.FixedCharField(max_length=20, help_text='每种设备必须注册一个 Protocol')
    uri = peewee.CharField(max_length=255, help_text='设备配置')
    description = peewee.CharField(max_length=255, help_text='设备描述')
    enable = peewee.BooleanField(default=True, help_text='启用设备')

    class Meta:
        table_name = 't_dev'


# class VarModel(communicationModel):
#     id = peewee.AutoField()
#     sig_name = peewee.CharField(max_length=128, index=True, help_text='变量名')
#     sig_type = peewee.FixedCharField(max_length=20, help_text='变量类型')
#     val_type = peewee.FixedCharField(max_length=20, help_text='数值类型')
#     slot = peewee.FixedCharField(max_length=20, index=True, help_text='通信接口, 关联 `t_dev.slot`')
#     uri = peewee.CharField(max_length=40, help_text='变量通信参数')
#     # 单位换算
#     eu = peewee.FixedCharField(max_length=20, help_text='engineering unit')
#     # cv = pw.FixedCharField(max_length=2, help_text='C/V')
#     rlo = peewee.FloatField(null=True, help_text='工程量下限')
#     rhi = peewee.FloatField(null=True, help_text='工程量上限')
#     elo = peewee.FloatField(null=True, help_text='信号量下限')
#     ehi = peewee.FloatField(null=True, help_text='信号量上限')
#     channel = peewee.CharField(max_length=255, help_text='通道')
#     termination = peewee.CharField(max_length=255, help_text='端子')
#     description = peewee.CharField(max_length=255, help_text='变量描述')
#     initial = peewee.CharField(max_length=255, help_text='初始值')
#
#     class Meta:
#         table_name = 't_var'


class VarModel(communicationModel):
    id = peewee.AutoField()
    sig_name = peewee.CharField(max_length=128, index=True, help_text='变量名')
    sig_type = peewee.FixedCharField(max_length=20, help_text='变量类型')
    chr = peewee.FixedCharField(max_length=20, help_text='数值类型')
    slot = peewee.FixedCharField(max_length=20, index=True, help_text='通信接口, 关联 `t_dev.slot`')
    # 单位换算
    engineering_unit = peewee.FixedCharField(max_length=20, help_text='engineering unit')
    # cv = pw.FixedCharField(max_length=2, help_text='C/V')
    rlo = peewee.FloatField(null=True, help_text='工程量下限')
    rhi = peewee.FloatField(null=True, help_text='工程量上限')
    elo = peewee.FloatField(null=True, help_text='信号量下限')
    ehi = peewee.FloatField(null=True, help_text='信号量上限')
    channel = peewee.CharField(max_length=255, help_text='通道')
    # termination = peewee.CharField(max_length=255, help_text='端子')
    # description = peewee.CharField(max_length=255, help_text='变量描述')
    initial = peewee.CharField(max_length=255, help_text='初始值')
    reg = peewee.IntegerField(null=True, help_text='功能码及地址')
    block = peewee.IntegerField(null=True)
    offset = peewee.IntegerField(null=True)
    bit = peewee.IntegerField(null=True)

    class Meta:
        table_name = 't_var'


def init_database(database: peewee.Database):
    proxy.initialize(database)
    database.create_tables([DevModel, VarModel], safe=True)
