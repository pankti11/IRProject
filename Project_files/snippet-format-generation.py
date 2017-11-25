import xlrd

workbook = xlrd.open_workbook('workbooks-query-expansion/query-expansion-bm25.xlsx', on_demand = True)

myfile = open("snippet-format.txt", "a")
for sheet in workbook.sheets():
	total_rows = 10
	#print total_rows
	total_cols = sheet.ncols
	#print total_cols
	# read a row row_slice
	ret_rel_docs = [] # our retreived relevant 100 documents
	for row in range(total_rows):
		cells = sheet.row_slice(rowx=row,start_colx=0,end_colx=total_cols)

		myfile.write(cells[0].value + " " + cells[2].value + "\n")