import requests, bs4, openpyxl as xl
import myScrapingLib as msl

WORKBOOK_NAME = 'ITEMS'
wb = xl.load_workbook(WORKBOOK_NAME+'.xlsx')

TYPE_SCRAPED = 'ITEM'

directorySheet = wb[TYPE_SCRAPED+'_URIs']

countDict = {}
for row in directorySheet.iter_rows():
	for cell in row:
		print('Doing: ' + cell.value)
		soup = msl.getSoup(cell.value)
		infoBox = soup.select('table[class~=infobox]')
		if len(infoBox) > 0:
			infoBox = infoBox[0]
		else:
			continue
		#print(not infoBox is None)

		for th in infoBox.select('th'):
			countDict.setdefault(th.text, 0)
			countDict[th.text] += 1

dictEntriesWritten = 0
ws = wb.create_sheet(TYPE_SCRAPED + '_INFOBOX_ENTRY_COUNT')
for (header, count) in countDict.items():
	dictEntriesWritten += 1
	ws.cell(row=dictEntriesWritten,column=1).value = header
	ws.cell(row=dictEntriesWritten,column=2).value = count

wb.save(WORKBOOK_NAME+'.xlsx')

print(directorySheet)

