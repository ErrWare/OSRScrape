import requests, os, bs4, openpyxl as xl
from myScrapingLib import getSoup

# scrapes item soup from xl list of all items
# also removes 'items' w/o infobox

wikiNS = 'http://oldschoolrunescape.wikia.com'

WORKBOOK_NAME = 'ITEMS'
wb = xl.load_workbook(WORKBOOK_NAME+'.xlsx')

SHEET_NAME = 'ITEM_URIs'
ws = wb[SHEET_NAME]

SLASH_REPLACEMENT = '$$'


originalDir = os.getcwd()
os.chdir(os.path.join('saved_soup','items'))
illegitimateRowNums = []
for i in range(1692,ws.max_row + 1):
	print('Now on row: ' + str(i))
	uri = str(ws.cell(row = i, column=1).value)
	res = requests.get(uri)
	res.raise_for_status()
	soup = bs4.BeautifulSoup(res.text)

	isLegitPage = not len(soup.select('table[class~=infobox]')) == 0

	if isLegitPage:
		itemName = uri.replace(wikiNS,'')
		itemName = itemName.replace(r'/wiki/','')
		itemName = itemName.replace(r'/',SLASH_REPLACEMENT)
		soupFile = open(itemName+'.html', 'wb')
		article = soup.find(id='WikiaMainContent')
		for chunk in res.iter_content(100000):
			soupFile.write(chunk)
		soupFile.close()
	else:
		illegitimateRowNums.append(i)

	
for row in illegitimateRowNums:
	cell = ws.cell(row=row,column=1)
	print('Not an item: ' + cell.value)
	cell.value = ''

os.chdir(originalDir)
wb.save(WORKBOOK_NAME+'.xlsx')