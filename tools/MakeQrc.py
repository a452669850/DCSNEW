import os

fileType = 'png' # 通过修改fileType来控制脚本将静态文件夹中所有指定类型文件转换为编译文件

with open('{}Qrc.qrc'.format(fileType), 'w') as f:
	f.write(
		'''<RCC>
    <qresource prefix="/static">

    ''')

	for root, dirs, files in os.walk('..\\static'):
		for file in files:
			if file.split('.')[-1] == fileType:
				print(file)
				f.write('		<file alias="{}">{}</file>\r\n'.format(file, os.path.join(root,file)))

	f.write('''
	</qresource>
</RCC>
		''')


cmd = 'pyrcc5 -o {}.py {}Qrc.qrc'.format(fileType,fileType) # 结果生产py文件如：png.py
os.system(cmd)