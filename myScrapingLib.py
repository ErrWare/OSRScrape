import requests, bs4

def getSoup(url):
	res = requests.get(url)
	try:
		res.raise_for_status()
		return bs4.BeautifulSoup(res.content,features='html5lib')
	except Exception as exc:
		print('Problem requesting ' + url)
	return None

# Dictionary translates keys to tokens, tracks lookups of each key
class TokenDict:
	'Class doc string accessible via classname.__doc__ (dunders make bold)'
	
	# need to copy dic - on default dic is shared between objects
	# I think the default value is interpreted once and saved as a
	# reference to the initial empty dict
	def __init__(self, dic={}):
		self.myDict = dic.copy()

	def getToken(self, key):
		token = str(-1)
		if key in self.myDict:
			token = self.myDict[key]['token']
			self.myDict[key]['accesses'] += 1
		else:
			token = len(self.myDict)
			self.myDict[key] = {}
			self.myDict[key]['token'] = token
			self.myDict[key]['accesses'] = 1
		return str(token)

# has overloaded functionality for getting article from url, might be too much
def getArticle(soup):
	if type(soup) == type(''):
		soup = getSoup(soup)
	# consider copying mainArticle to leave soup unaltered
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

	return mainArticle

# returns a dictionary where the keys are the identifying values in another dict, and the vals are the keys
def reverseDict(dic, key_att):
	retDic = {}
	for key, val in dic.items():
		retDic[str(val[key_att])] = key

	return retDic

# gets the categories of some osrs wiki page
def getCategories(soup):
	categories = soup.find('ul',class_='categories')
	if categories is None:
		print('No cats')
		return set([])
	else:
		categories = [a.attrs['href'] for a in categories.select('a')]
		return set(categories)