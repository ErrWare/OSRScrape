# Scrape all equipment to new json dict
# Outputs armory_v#.json

import bs4
import requests
import myScrapingLib as msl
from myScrapingLib import getSoup
import json

def headCellName(headCell):
	colRep = headCell.find('a')
	if(colRep is None):
		return headCell.text.strip()
	else:
		return colRep.attrs['title']

def entryCellVal(entryCell):
	cellLink = entryCell.find('a')
	if(cellLink is None):
		return entryCell.text
	else:
		return cellLink.attrs['title']

wikiNS = 'http://oldschoolrunescape.wikia.com'
tableIndex = '/wiki/Category:Slot_tables'

tableIndexSoup = getSoup(wikiNS+tableIndex)

titledLinks = tableIndexSoup.select('a[title]')
slotTableLinks = [link for link in titledLinks if link.attrs['title'].endswith('slot table')]

tableDict = {}
for link in slotTableLinks:
	attrs = link.attrs	
	title = attrs['title']
	href = attrs['href']
	slotType = title.split(' ')[0]
	slotTableLink =  wikiNS + href
	tableDict[slotType] = slotTableLink
	#print('Slot: ' + slotType)
	#print('full link: ' + slotTableLink)
	
# Made into dict to remove dupes
print('From		dict of table page uris')
print('Making	dict of table heads and body elems')

equipmentDict = {}
i = 0
print(tableDict.keys())
for (tableType,value) in tableDict.items():
	print(tableType + ' : ' + value)
	tablePage = getSoup(value)
	tableInPage = tablePage.select('table[class~=wikitable]')[0]
	body = tableInPage.find('tbody')

	
	
	# assume header is first row in tbody with no 'td'
	head = body.find(lambda tag: len(tag.find_all('td')) == 0)
	headColumns = head.find_all('th')
	num_columns = len(headColumns)
	
	column_names = ['name']		# First th unlike rest
	for th in headColumns:
		try:
			column_names.append(th.find('a').attrs['title'])
		except:
			pass
	

	# assume entries are rows in tbody with all 'td'
	# size of each entry must match size of header
	tableEntries = body.find_all(lambda tag: len(tag.find_all('td'))==num_columns)
	print(len(tableEntries))

	for entry in tableEntries:
		entryCells = entry.find_all('td')
		#assume first entry cell has link out
		print(entryCells[0].find('a').attrs['href'])
		entry_resource = entryCells[0].find('a').attrs['href']
		resourceToken = msl.rt_dict.getToken(entry_resource)
		equipmentDict[resourceToken] = {}
		equipmentDict[resourceToken]['type'] = tableType	# key corresponding to equipment table type

		for index, cell in enumerate(entryCells):
			equipmentDict[resourceToken][column_names[index]] \
				= cell.text.strip()
		equipmentSoup = msl.getSoup(wikiNS+entry_resource)
		info_box = msl.osrsInfoBox(equipmentSoup)
		for key, val in info_box.items():
			equipmentDict[resourceToken][key] = val
		equipmentDict[resourceToken]['article-text'] = msl.osrsAsNL(equipmentSoup)

		i += 1
		if i == 10:
			with open('armory_10_v2.json','w') as armory_file:
				armory_file.write(json.dumps(equipmentDict))

with open('armory_v2.json','w') as armory_file:
	json_string = json.dumps(equipmentDict)
	white_space_markers = ['\\u00a0', '\\n', '\\u2022']
	for wsm in white_space_markers:
		json_string = json_string.replace(wsm, ' ')
	
	armory_file.write(json_string)

msl.saveTokenDicts()