import requests, bs4, json
from myScrapingLib import getSoup
import openpyxl as xl
def getCategories(soup):
	categories = soup.find('ul',class_='categories')
	if categories is None:
		print('No cats')
		return set([])
	else:
		categories = [a.attrs['href'] for a in categories.select('a')]
		return set(categories)

catTokenDict = {}
def getToken(category):
	if not category in catTokenDict:
		catTokenDict[category] = len(catTokenDict)
	return catTokenDict[category]

count = 0
def jsonDump():
	with open('cat_and_link_'+str(count)+'.json', 'w') as outfile:
		json.dump(dataDict, outfile)
			
	with open('cat_tokens_'+str(count)+'.json', 'w') as outfile:
		json.dump(catTokenDict, outfile)

wikiNS = 'http://oldschoolrunescape.wikia.com'
WORKBOOK_NAME = 'ITEMS'
wb = xl.load_workbook(WORKBOOK_NAME+'.xlsx')

TYPE_SCRAPED = 'ITEM'

directorySheet = wb[TYPE_SCRAPED+'_URIs']

dataDict = {}


#for each item
for row in directorySheet.iter_rows():
	for cell in row:
		print('Doing: ' + cell.value)
		resourceName = cell.value.replace(wikiNS,'')
		dataDict[resourceName] = {}
		soup = getSoup(cell.value)
		#add categories set
		dataDict[resourceName]['categories'] = list(getCategories(soup))

		mainArticle = soup.find(id='mw-content-text')
		# Don't want these bad boys. Not really relevant to main article
		badTables = mainArticle.find_all('table',class_='navbox')
		for badTable in badTables:
			badTable.decompose()
		# To destroy: div.messagebox
		# To destroy: span#trivia - destroy all ul siblings below it
		# To destroy: href w/ ?action=
		# To destroy: href w/ Exchange:
		# To destroy: href w/ Update:
		# To destroy: href w/ Poll:


		# Only articles relevant to text are those without a class attribute
		# class attribute denotes an image, we can do away with that.
		links = set(a.attrs['href'] for a in mainArticle.select('a[href]') if not 'class' in a.attrs)
		#add links_to set
		dataDict[resourceName]['links_to'] = list(links)
		#for each link in div#mw-content-text but not in table class~=navbox
		for link in links:
			if not link in dataDict:
				dataDict[link] = {}
				#if not yet in dataDict
				linkCats = set([])
				if link.startswith('/wiki/'):
					linkSoup = getSoup(wikiNS + link)
					print('Getting cats from: ' + link)
					linkCats = getCategories(linkSoup)
				else:
					linkCats = set(['foreign'])
				dataDict[link]['categories'] = list(getToken(cat) for cat in linkCats)

		print('Linked out to ' + str(len(links)) + ' resources')
		count = count + 1
		if count % 150 == 0:
			jsonDump()


		


	#if links to wiki page
		#add entry to dict
		#make set of the categories
	#else
		#add entry to dict
		#make set with category: foreign
	#add link to linksTo set
