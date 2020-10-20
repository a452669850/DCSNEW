from utils.WorkModels import NetworkConfig, PointGroup, PointModel


class getListData:

    @classmethod
    def getNtworkConfigData(cls):
        """用来查询配置"""
        lis = []
        configs = NetworkConfig.select().distinct()
        row = 1
        for i in configs:
            lis.append([row, i.name, i.desc, i.ip, str(i.port)])
            row += 1
        return lis

    # @classmethod
    # def create_group(cls):
    #     lis1 = []
    #     lis2 = []
    #     s = set()
    #     dev = NetworkConfig.select()
    #     for j in dev:
    #         s.add(j.protocol)
    #     for i in dev:
    #         if i.protocol == list(s)[0]:
    #             lis1.append(i)
    #         if i.protocol == list(s)[1]:
    #             lis2.append(i)
    #     var_list1 = PointModel.filter(PointModel.slot.in_([x.slot for x in lis1])).order_by(PointModel.id)
    #     var_list2 = PointModel.filter(PointModel.slot.in_([x.slot for x in lis2])).order_by(PointModel.id)
    #     PointGroup.create_group(group_name=list(s)[0], points=var_list1)
    #     PointGroup.create_group(group_name=list(s)[1], points=var_list2)

    @classmethod
    def create_group(cls, name):
        """创建组"""
        points = PointModel.all_points()
        PointGroup.create_group(group_name=name, points=points)

    @classmethod
    def search_NetworkConfig(cls, text):
        """查询网络配置"""
        lis = []
        configs = NetworkConfig.select().where(
            (NetworkConfig.slot.contains(text)) |
            (NetworkConfig.description.contains(text))
        )
        if len(configs):
            for config in configs:
                lis.append([config.id, config.slot, config.description, config.uri])
        return lis
