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
for item in os.listdir():
	file = open(item,'rb')
	soup = bs4.BeautifulSoup(file,features='html5lib')
	

	
for row in illegitimateRowNums:
	cell = ws.cell(row=row,column=1)
	print('Not an item: ' + cell.value)
	cell.value = ''

os.chdir(originalDir)
wb.save(WORKBOOK_NAME+'.xlsx')