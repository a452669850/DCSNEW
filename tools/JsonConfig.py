from utils.core import jsonPath
import json
import os

jsonPath = jsonPath

def writeJson(projectPath):
    # 将即将关闭的工程信息写入json中
    print(jsonPath)
    if os.path.exists(jsonPath):
        with open(jsonPath, 'r', encoding='utf-8') as f1:
            loadDict = json.load(f1)
            projectList = loadDict['last_project_list']
            if projectList == []:
                loadDict['last_project_list'] = [projectPath]
            else:
                newList = projectList
                newList.append(projectPath)
                loadDict['last_project_list'] = list(set(newList))
            loadDict['last_project'] = projectPath

        with open(jsonPath, 'w', encoding='utf-8') as f2:
            json.dump(loadDict, f2)
    else:
        loadDict = {}
        loadDict['last_project_list'] = [projectPath]
        loadDict['user_name'] = 'admin'
        loadDict['last_project'] = [projectPath]
        with open(jsonPath, 'w', encoding='utf-8') as f2:
            json.dump(loadDict, f2)

def rewriteJson(value):
    # 记录即将关闭工程信息
    if os.path.exists(jsonPath):
        with open(jsonPath, 'r', encoding='utf-8') as f1:
            loadDict = json.load(f1)
            loadDict['admin'] = value
        with open(jsonPath, 'w', encoding='utf-8') as f2:
            json.dump(loadDict, f2)
    else:
        newDict = {'admin' : value}
        with open(jsonPath, 'w', encoding='utf-8') as f3:
            newDict['last_project_list'] = []
            json.dump(newDict, f3)

def getProjectPath():
    # 获取最后一次打开的工程
	if os.path.exists(jsonPath):
		with open(jsonPath, 'r', encoding='utf-8') as f:
			loadDict = json.load(f)
			return loadDict['last_project']
	else:
		return None

def getProjectList():
    # 获取最近打开的工程列表
    if os.path.exists(jsonPath):
        with open(jsonPath, 'r', encoding='utf-8') as f:
            loadDict = json.load(f)
            return [x for x in loadDict['last_project_list']  if x]
    else:
        return []

def getProjectName(projectPath):
    # 根据工程路径获取工程名
	if projectPath:
		if os.path.exists(projectPath):
			with open(os.path.join(projectPath, 'projectDate.json'), 'r', encoding='utf-8') as f:
				loadDict = json.load(f)
				return loadDict['project_name']
		else:
			return None
	else:
		return None

def getLastUser():
    # 获取最后一次打开的工程用户名
    print(jsonPath)
    if os.path.exists(jsonPath):
        with open(jsonPath, 'r', encoding='utf-8') as f:
            loadDict = json.load(f)
            return loadDict['user_name']
    else:
        return None