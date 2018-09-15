# For all items:
#	record categories
#	record out links as resources
# For all categories:
#	store as token in cat_tokens_dict_COUNT.json
#	track reference count
# For all resources:
#	store as token in rsrc_tokens_dict_COUNT.json
#	track reference count



import requests, bs4, json
from myScrapingLib import getSoup, TokenDict
import openpyxl as xl

# Our data and token dicts
# For each item and resource: keep track of categories
# For each item: keep track of linked resources
dataDict = {}
# tokenizes resources and tracks accesses
rsrcTokenDict = TokenDict()
# tokenizes categories and tracks accesses
catTokenDict = TokenDict()

# urls for which normal execution failed
failures = []

# gets the categories of some osrs wiki page
def getCategories(soup):
	categories = soup.find('ul',class_='categories')
	if categories is None:
		print('No cats')
		return set([])
	else:
		categories = [a.attrs['href'] for a in categories.select('a')]
		return set(categories)

# Amount items counted
count = 0

# Save data to json
def jsonDump():
	with open('cat_and_link_'+str(count)+'.json', 'w') as outfile:
		json.dump(dataDict, outfile)
			
	with open('cat_tokens_dict_'+str(count)+'.json', 'w') as outfile:
		json.dump(getattr(catTokenDict,'myDict'), outfile)

	with open('rsrc_tokens_dict_'+str(count)+'.json', 'w') as outfile:
		json.dump(getattr(rsrcTokenDict,'myDict'), outfile)

	with open('cat_and_link_failures.json', 'w') as outfile:
		json.dump(failures, outfile)


wikiNS = 'http://oldschoolrunescape.wikia.com'
WORKBOOK_NAME = 'ITEMS'
wb = xl.load_workbook(WORKBOOK_NAME+'.xlsx')

TYPE_SCRAPED = 'ITEM'

directorySheet = wb[TYPE_SCRAPED+'_URIs']

#Because some items are giving me trouble
#ITEMS_TO_SKIP = ['/wiki/Snakeskin']

#for each item
for row in directorySheet.iter_rows():
	for cell in row:
		try:
			print('Doing: ' + cell.value)
			resourceName = cell.value.replace(wikiNS,'')
			print(resourceName)
			# Tokenize subject resource
			resourceToken = rsrcTokenDict.getToken(resourceName)
			# give it an entry in our dataDict
				# in some cases over-writes previous entry - negligible
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
			if triviaSpan is not None:
				for ul in triviaSpan.parent.find_next_siblings('ul'):
					ul.decompose()

			# Only articles relevant to text are those without a class attribute
			# class attribute denotes an image, we can do away with that.
			links = set(a.attrs['href'] for a in mainArticle.select('a[href]') if 'class' not in a.attrs)
			
			# these substrings are found in hrefs we are uninterested in
			badSubStrings = ['?action=','Exchange:','Update:','Poll:']
			for badSubString in badSubStrings:
				links = set(href for href in links if badSubString not in href)

			#add links_to set
			dataDict[resourceToken]['links_to'] = [rsrcTokenDict.getToken(link) for link in links]
			
			#for each link of interest
			for link in links:
				linkToken = rsrcTokenDict.getToken(link)
				# track categories of resource if not yet tracked
				# otherwise we won't be able to categorize non-item resources
				if linkToken not in dataDict:
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
			if count % 500 == 0 or count == 10:
				jsonDump()
		
		except:
			failures.append(cell.value)

jsonDump()


		


	#if links to wiki page
		#add entry to dict
		#make set of the categories
	#else
		#add entry to dict
		#make set with category: foreign
	#add link to linksTo set
