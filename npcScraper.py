import myScrapingLib as msl
import requests, json, bs4

home_lists = ['/wiki/Category:Items','/wiki/Category:Non-player_characters','/wiki/Category:Bestiary']

testWrite = True

for index, home_list in enumerate(home_lists):
	fileName = home_list.split(':')[-1]
	npcDict = {}
	soup = msl.getSoup(msl.rsns + home_list)
	main_section = soup.find(id='mw-pages')
	print('next section: ' + str(main_section.find('a',text='next 200')))
	main_table   = main_section.find('table')

	while True:
		npc_links = main_table.find_all('a')

		for npc in npc_links:
			
			npc_link = npc.attrs['href']
			if 'Bestiary' in npc_link:
				continue
			print(npc_link)
			npc_token = msl.rt_dict.getToken(npc_link)
			npcDict[npc_token] = {}
			npcDict[npc_token]['drops'] = []
			if index == 0:
				npcDict[npc_token]['type'] = 'monster'
			else:
				npcDict[npc_token]['type'] = 'npc'

			npc_soup = msl.getSoup(msl.rsns + npc_link)
			for dropTable in npc_soup.find_all('table', class_='dtable'):
				# weird quirk - couldn't separate tbody from thead
				entry_list = dropTable.find_all('tr')
				entry_list = entry_list[1:]
				for entry in entry_list:
					# tr td's in this order:
					# 0: thumbnail + link
					# 1: name + link
					# 2: quantity
					# 3: rarity
					# 4: ge market price
					entry_tds = entry.find_all('td')
					entryDict = {}
					item_link = entry_tds[1].find('a',href=True).attrs['href']
					entryDict['item'] = msl.rt_dict.getToken(item_link)
					entryDict['quantity'] = entry_tds[2].text.strip()
					entryDict['rarity'] = entry_tds[3].text.strip()
					npcDict[npc_token]['drops'].append(entryDict)

			
			info_box = msl.osrsInfoBox(npc_soup)
			for key, val in info_box.items():
				npcDict[npc_token][key] = val
			npcDict[npc_token]['article-text'] = msl.osrsAsNL(npc_soup)

		next_section = main_section.find('a', text='next 200')
		if next_section is None:
			print('No next_section, breaking')
			break
		soup = msl.getSoup(msl.rsns + next_section.attrs['href'])
		main_section = soup.find(id='mw-pages')
		main_table   = main_section.find('table')

		print('~'*23)
		print('~'*23)
		print('~'*8 + 'flipping page' + '~'*8)
		print('~'*23)
		print('~'*23)

		if testWrite:
			testWrite = False
			with open('npcs_test_v1.json', 'w') as npcFile:
				json_string = json.dumps(npcDict)
				json_string = msl.removeUnicodes(json_string)
				npcFile.write(json_string)
	

with open(fileName+'_v1.json', 'w') as npcFile:
	json_string = json.dumps(npcDict)
	json_string = msl.removeUnicodes(json_string)
	npcFile.write(json_string)


msl.saveTokenDicts()