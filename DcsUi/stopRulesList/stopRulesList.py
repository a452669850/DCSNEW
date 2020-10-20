from utils.ClientModels import *


class rulesListModel():

    @classmethod
    def get_runresult(self):
        """获取终止规程的所有规程信息"""
        run_results = RunResult.get_stopped_result('all')
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
                                    run_result.run_uuid,
                                    run_result.id,
                                    ])
        for usecaseInfo in result_info:
            usecaseInfo[4] = IS_STOP_MAP[str(usecaseInfo[4])]
        return result_info

    @classmethod
    def search_data(cls, **kwargs):
        """查找终止规程"""
        type = kwargs.get('type', None)
        is_complete = kwargs.get('is_complete', 2)
        number = kwargs.get('number', None)
        name = kwargs.get('name', None)

        result_info = []
        IS_STOP_MAP = {
            'True': '是',
            'False': '否'
        }
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
        for usecaseInfo in result_info:
            usecaseInfo[4] = IS_STOP_MAP[str(usecaseInfo[4])]
        return result_info
