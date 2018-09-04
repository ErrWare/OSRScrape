import requests, bs4, json
from myScrapingLib import getSoup, TokenDict
import openpyxl as xl

#for when cat_and_link fails....

CONT_ROW = 5000

# Our data and token dicts
dataDict = json.load(open('cat_and_link_'+str(CONT_ROW)+'.json','r'))
rsrcTokenDict = TokenDict(dic=json.load(open('rsrc_tokens_dict_'+str(CONT_ROW)+'.json','r')))
catTokenDict = TokenDict(dic=json.load(open('cat_tokens_dict_'+str(CONT_ROW)+'.json','r')))

def getCategories(soup):
	categories = soup.find('ul',class_='categories')
	if categories is None:
		print('No cats')
		return set([])
	else:
		categories = [a.attrs['href'] for a in categories.select('a')]
		return set(categories)

'''
catTokenDict = {}
def getToken(category):
	if not category in catTokenDict:
		catTokenDict[category] = len(catTokenDict)
	return catTokenDict[category]
'''
count = CONT_ROW
def jsonDump():
	with open('cat_and_link_'+str(count)+'.json', 'w') as outfile:
		json.dump(dataDict, outfile)
			
	with open('cat_tokens_dict_'+str(count)+'.json', 'w') as outfile:
		json.dump(getattr(catTokenDict,'myDict'), outfile)

	with open('rsrc_tokens_dict_'+str(count)+'.json', 'w') as outfile:
		json.dump(getattr(rsrcTokenDict,'myDict'), outfile)


wikiNS = 'http://oldschoolrunescape.wikia.com'
WORKBOOK_NAME = 'ITEMS'
wb = xl.load_workbook(WORKBOOK_NAME+'.xlsx')

TYPE_SCRAPED = 'ITEM'

directorySheet = wb[TYPE_SCRAPED+'_URIs']

#Because some items are giving me trouble
ITEMS_TO_SKIP = ['/wiki/Snakeskin']

#for each item
for row in directorySheet.iter_rows(min_row=CONT_ROW+1):
	for cell in row:
		print('Doing: ' + cell.value)
		resourceName = cell.value.replace(wikiNS,'')
		print(resourceName)
		if resourceName in ITEMS_TO_SKIP:
			continue
		resourceToken = rsrcTokenDict.getToken(resourceName)
		dataDict[resourceToken] = {}
		soup = getSoup(cell.value)
		#add categories set
		dataDict[resourceToken]['categories'] = [catTokenDict.getToken(cat) for cat in getCategories(soup)]

		mainArticle = soup.find(id='mw-content-text')
		# Don't want these bad boys. Not really relevant to main article
		badTables = mainArticle.find_all('table',class_='navbox')
		for badTable in badTables:
			badTable.decompose()
		# To destroy: div.messagebox
		messageBoxes = mainArticle.select('div.messagebox')
		for messageBox in messageBoxes:
			messageBox.decompose()
		# To destroy: span#trivia - destroy all ul below it
		triviaSpan = mainArticle.find(id='Trivia')
		if not triviaSpan is None:
			for ul in triviaSpan.parent.find_next_siblings('ul'):
				ul.decompose()

		# Only articles relevant to text are those without a class attribute
		# class attribute denotes an image, we can do away with that.
		links = set(a.attrs['href'] for a in mainArticle.select('a[href]') if not 'class' in a.attrs)
		
		badSubStrings = ['?action=','Exchange:','Update:','Poll:']
		for badSubString in badSubStrings:
			links = set(href for href in links if not badSubString in href)

		#add links_to set
		dataDict[resourceToken]['links_to'] = [rsrcTokenDict.getToken(link) for link in links]
		#for each link in div#mw-content-text but not in table class~=navbox
		for link in links:
			linkToken = rsrcTokenDict.getToken(link)
			if not linkToken in dataDict:
				dataDict[linkToken] = {}
				#if not yet in dataDict
				linkCats = set([])
				if link.startswith('/wiki/'):
					linkSoup = getSoup(wikiNS + link)
					print('Getting cats from: ' + link)
					linkCats = getCategories(linkSoup)
				else:
					linkCats = set(['foreign'])
				dataDict[linkToken]['categories'] = [catTokenDict.getToken(cat) for cat in linkCats]

		print('Linked out to ' + str(len(links)) + ' resources')
		count = count + 1
		if count % 50 == 0 or count == 10:
			jsonDump()

jsonDump()


		


	#if links to wiki page
		#add entry to dict
		#make set of the categories
	#else
		#add entry to dict
		#make set with category: foreign
	#add link to linksTo set
