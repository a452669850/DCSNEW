from utils.ClientModels import RunResult


class textRecordModel():

    @classmethod
    def get_runresult(cls):
        """获取数据函数"""
        run_results = RunResult.get_all()
        result_info = []
        IS_STOP_MAP = {
            'True': '否',
            'False': '是'
        }
        if run_results:
            for run_result in run_results:
                result_info.append([run_result.procedure_number,
                                    run_result.usecase_group_name,
                                    run_result.usecase_number,
                                    run_result.run_time.strftime("%Y-%m-%d %H:%M:%S"),
                                    run_result.is_stop,
                                    run_result.run_uuid
                                    ])
        for usecaseInfo in result_info:
            usecaseInfo[4] = IS_STOP_MAP[str(usecaseInfo[4])]
        return result_info

    @classmethod
    def search_data(cls, **kwargs):
        """查询数据函数"""
        type = kwargs.get('type', None)
        is_complete = kwargs.get('is_complete', None)
        number = kwargs.get('number', None)
        name = kwargs.get('name', None)

        result_info = []
        IS_STOP_MAP = {
            'True': '否',
            'False': '是'
        }
        lis = []
        searchResults = RunResult.search_result(type=type, is_complete=is_complete, number=number, name=name)
        if len(searchResults):
            for search in searchResults:
                if search.run_type == 1:
                    result_info.append(['规程',
                                        search.procedure_number,
                                        search.procedure_name,
                                        search.run_time.strftime("%Y-%m-%d %H:%M:%S"),
                                        search.is_stop,
                                        search.run_uuid
                                        ])
                    lis.append(search)
                if search.run_type == 2:
                    result_info.append(
                        [
                            '用例组',
                            search.usecase_group_number,
                            search.usecase_group_name,
                            search.run_time.strftime("%Y-%m-%d %H:%M:%S"),
                            search.is_stop,
                            search.run_uuid
                        ]
                    )
                    lis.append(search)
                if search.run_type == 3:
                    result_info.append(
                        [
                            '用例',
                            search.usecase_group_number,
                            search.usecase_group_name,
                            search.run_time.strftime("%Y-%m-%d %H:%M:%S"),
                            search.is_stop,
                            search.run_uuid
                        ]
                    )
                    lis.append(search)
        for usecaseInfo in result_info:
            usecaseInfo[4] = IS_STOP_MAP[str(usecaseInfo[4])]
        return result_info, lis

    @classmethod
    def deleteView(cls, id):
        """删除行"""
        RunResult.delete_obj(id)
