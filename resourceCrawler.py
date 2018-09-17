import requests
import bs4
import json
from myScrapingLib import getSoup, getArticle, getCategories, reverseDict, TokenDict
wikiNS = 'http://oldschoolrunescape.wikia.com'
count = 6324

# Our data and token dicts
dataDict = json.load(open('cat_and_link_'+str(count)+'.json','r'))
rsrcTokenDict = TokenDict(dic=json.load(open('rsrc_tokens_dict_'+str(count)+'.json','r')))
catTokenDict = TokenDict(dic=json.load(open('cat_tokens_dict_'+str(count)+'.json','r')))
failures = json.load(open('cat_and_link_failures2.json','r'))
tokenRsrcDict = reverseDict(
						   rsrcTokenDict.myDict,
						   'token'
						   )
tokenCatDict = reverseDict(
						  catTokenDict.myDict,
						  'token'
						  )

# get all webpages we know about
knownResources = [ogrsrc for ogrsrc in rsrcTokenDict.myDict.keys()]

def jsonDump():
	with open('CRcat_and_link_'+str(count)+'.json', 'w') as outfile:
		json.dump(dataDict, outfile)
			
	with open('CRcat_tokens_dict_'+str(count)+'.json', 'w') as outfile:
		json.dump(getattr(catTokenDict,'myDict'), outfile)

	with open('CRrsrc_tokens_dict_'+str(count)+'.json', 'w') as outfile:
		json.dump(getattr(rsrcTokenDict,'myDict'), outfile)

	with open('CRcat_and_link_failures2.json', 'w') as outfile:
		json.dump(list(set(failures)), outfile)

resourceURL = ''
continues = 0
for resourceCR in knownResources:
	try:
		print('Crawling through ' + resourceCR)
		dataEntry = dataDict[rsrcTokenDict.getToken(resourceCR)]
		# entry has resources
		if 'links_to' in dataEntry:
			for resourceToken in dataEntry['links_to']:
				# skip the crawl if full entry already in dictionary
				if resourceToken in dataDict and 'links_to' in dataDict[resourceToken]:
					continues += 1
					print('continues: ' + str(continues))
					continue

				# else write new entry, possibly overwriting previous categories (negligible)
				dataDict[resourceToken] = {}
				resourceName = tokenRsrcDict[resourceToken]
				print('Cat and link: ' + resourceName)

				resourceURL = wikiNS + resourceName
				# same execution as cat_and_link_jsoner
				soup = getSoup(resourceURL)

				dataDict[resourceToken]['categories'] = [catTokenDict.getToken(cat) for cat in getCategories(soup)]

				mainArticle = getArticle(soup)

				links = set(a.attrs['href'] for a in mainArticle.select('a[href]') if 'class' not in a.attrs)
				
				badSubStrings = ['?action=',':']
				for badSubString in badSubStrings:
					links = set(href for href in links if badSubString not in href)

				print('Linked out to ' + str(len(links)))
				dataDict[resourceToken]['links_to'] = [rsrcTokenDict.getToken(link) for link in links]
				
				for link in links:
					linkToken = rsrcTokenDict.getToken(link)
					if linkToken not in dataDict:
						dataDict[linkToken] = {}
						linkCats = set([])
						if link.startswith('/wiki/'):
							linkSoup = getSoup(wikiNS + link)
							print('Getting cats from: ' + link)
							linkCats = getCategories(linkSoup)

							mainArticle = getArticle(linkSoup)

							links = set(a.attrs['href'] for a in mainArticle.select('a[href]') if 'class' not in a.attrs)
							
							badSubStrings = ['?action=',':']
							for badSubString in badSubStrings:
								links = set(href for href in links if badSubString not in href)

							print('Linked out to ' + str(len(links)))
							dataDict[resourceToken]['links_to'] = [rsrcTokenDict.getToken(link) for link in links]
						else:
							linkCats = set(['foreign'])
						
						dataDict[linkToken]['categories'] = [catTokenDict.getToken(cat) for cat in linkCats]

				count += 1

				if count % 500 == 0 or count == 6400:
					jsonDump()
	except KeyboardInterrupt as e:
		jsonDump()
		exit()
	except Exception as e:
		print(e)
		failures.append(resourceURL)

jsonDump()