import xlwings as xw
wb = xw.Book('test.xlsx')
sht = wb.sheets['Sheet2']

print(sht.range('A1').value)
sht.range('A2').value = 'aaa'
