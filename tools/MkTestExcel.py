from openpyxl import Workbook
wb = Workbook()    #创建文件对象

# grab the active worksheet
ws = wb.active     #获取第一个sheet

# Data can be assigned directly to cells


# Rows can also be appended
for x in range(100000):
	ws.append([x, x + 1, x + 2, x + 3, x + 4, x + 5, x + 6 ])    #写入多个单元格
	print(x, '写入成功', '{}%'.format(x / 100000 * 100))


# Save the file
wb.save("test.xlsx")