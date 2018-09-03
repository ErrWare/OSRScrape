import requests, bs4, openpyxl as xl
import myScrapingLib as msl

# scrapes item uris from list of all items

wikiNS = 'http://oldschoolrunescape.wikia.com'
initPage = '/wiki/Category:Items'

itemsAdded = 0

WORKBOOK_NAME = 'ITEMS'
wb = xl.Workbook()
# remove first sheet
wb.remove(wb.worksheets[0])

SHEET_NAME = 'ITEM_URIs'
ws = wb.create_sheet(SHEET_NAME)

soup = msl.getSoup(wikiNS + initPage)

while True:
	pageDiv = soup.find(id='mw-pages')

	print(len(pageDiv.select('a')))
	links = pageDiv.select('a')
	itemPages = [link.attrs['href'] for link in links if not link.attrs['href'].startswith('/wiki/Category:Items')]
	print(len(itemPages))
	for itemPage in itemPages:
		itemsAdded += 1
		ws.cell(row=itemsAdded, column=1).value = wikiNS+itemPage

	nextLink = next((tag for tag in links if '?pagefrom=' in tag.attrs['href']),None)
	if(nextLink is None):
		break
	soup = msl.getSoup(wikiNS + nextLink.attrs['href'])


wb.save(WORKBOOK_NAME+'.xlsx')