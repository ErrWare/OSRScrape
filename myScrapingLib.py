import requests, bs4
import os
import inspect
import json
import re

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
		self.token_dict = dic.copy()

	def getToken(self, key):
		token = str(-1)
		if key in self.token_dict:
			token = self.token_dict[key]['token']
			self.token_dict[key]['accesses'] += 1
		else:
			token = len(self.token_dict)
			self.token_dict[key] = {}
			self.token_dict[key]['token'] = token
			self.token_dict[key]['accesses'] = 1
		return str(token)

	def __len__(self):
		return len(self.token_dict)

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

def categorizeDict(dic, cat_att):
	retDic = {}
	for key, val in dic.items():
		retDic[tuple(val[cat_att])] = key
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


# Load token dicts
ASSETS_FOLDER_NAME = 'assets'
MSL_ASSETS_FOLDER_NAME = 'mslAssets'
MY_DIR_NAME = os.path.dirname(inspect.stack()[0][1])
msl_assets_folder = os.path.join(MY_DIR_NAME,ASSETS_FOLDER_NAME,MSL_ASSETS_FOLDER_NAME)
if os.path.isdir(msl_assets_folder):
	files = os.listdir(msl_assets_folder)
	rt_dicts = [f for f in files if f.startswith('rsrc_tokens_dict')]
	ct_dicts = [f for f in files if f.startswith('cat_tokens_dict')]
	
	if len(rt_dicts) > 0:
		rt_dict = rt_dicts[0]
		for candidate_dict in rt_dicts[1:]:
			if os.path.getsize( os.path.join(msl_assets_folder, rt_dict) ) < \
			   os.path.getsize( os.path.join(msl_assets_folder,candidate_dict) ):
				rt_dict = candidate_dict
		rt_dict = json.load(open(os.path.join(msl_assets_folder,rt_dict)))
		rt_dict = TokenDict(rt_dict)
	else:
		print('myScrapingLib:\tFailed to locate resource token dicts')

	if len(ct_dicts) > 0:
		ct_dict = ct_dicts[0]
		for candidate_dict in ct_dicts[1:]:
			if os.path.getsize( os.path.join(msl_assets_folder, ct_dict) ) < \
			   os.path.getsize( os.path.join(msl_assets_folder,candidate_dict) ):
				ct_dict = candidate_dict
		ct_dict = json.load(open(os.path.join(msl_assets_folder,ct_dict)))
		ct_dict = TokenDict(ct_dict)
	else:
		print('myScrapingLib:\tFailed to locate resource token dicts')
else:
	print('myScrapingLib:\tfailed to locate assets\\mslAssets\\ folder')

def saveTokenDicts():
	with open(os.path.join(msl_assets_folder,'cat_tokens_dict_'+str(len(ct_dict))+'_CR.json'),'w') as f:
		f.write(json.dumps(ct_dict.token_dict))
	with open(os.path.join(msl_assets_folder,'rsrc_tokens_dict_'+str(len(rt_dict))+'_CR.json'),'w') as f:
		f.write(json.dumps(rt_dict.token_dict))
	print('TokenDicts updated')
	


def disqualified(p):
	if p.parent.name == 'figcaption':
		return True
	if 'class' in p.parent.attrs and 'navbox-list' in p.parent.attrs['class']:
		return True
	if 'class' in p.attrs and p.attrs and 'caption' in p.attrs['class']:
		return True
	# hopefully this is better than checking length
	if p.text.startswith('<'):
		return True
	# if len(p.text) > 600:
	# 	return True
	
	return False

def tokenizeLinks(tag):
	for a in tag.find_all('a'):
		if 'href' in a.attrs:
			a.replace_with('rsrc'+rt_dict.getToken(a.attrs['href']))
		else:
			print('link w/o href in tag: ' + a.text)
			a.replace_with(a.text)

# replaces article links with resource ids like rsrcTOKEN
def osrsAsNL(urlORsoup):
	try:
		if type(urlORsoup) == type(''):
			soup = getSoup(urlORsoup)
		else:
			soup = urlORsoup
	
		article = soup.find()
		pars = article.findAll('p')
		pars = [p for p in pars if not disqualified(p)]

		natural_par = ''
		for p in pars:
			tokenizeLinks(p)
		
		natural_par = ' '.join([p.text.strip() for p in pars])

		# find trivia
		trivia = soup.find(id='Trivia')
		if trivia is not None:
			trivia = trivia.parent.find_next_sibling('ul').find_all('li')
			for trivia_item in trivia:
				tokenizeLinks(trivia_item)
		
			trivia_text = ' '.join([t.text.strip() for t in trivia])
			natural_par = natural_par + ' ' + trivia_text
		
		#clean it up
		natural_par.replace(u'\xa0', u' ')
		return natural_par
	except Exception as e:
		print('Failure converting url to natural language')
		print(e)
		return 'ERROR: exception harvesting NL'

def osrsInfoBox(urlORsoup):
	try:
		if type(urlORsoup) == type(''):
			soup = getSoup(urlORsoup)
		else:
			soup = urlORsoup

		info_box = soup.find('table', class_='infobox')

		box_dict = {}
		if info_box is not None:
			box_dict['info-caption'] = info_box.find('caption').text.strip()

			info_rows = info_box.find_all('tr')

			for row in info_rows:
				th = row.find('th')
				if th is None:
					continue
				tds = row.find_all('td')
				href = th.find('a', href=True)
				if href is None:
					href = ''
				else:
					href = href.attrs['href'].replace('/wiki/','').lower()
				# Simple case - 1 cell desc, 1 cell value
				if len(tds) == 1:
					if href == 'Prices#Grand_Exchange_Guide_Price':
						continue
					box_dict[th.text.strip()] = tds[0].text.strip()
				else:
						
					if href in ['examine', 'attack_style'] :
						box_dict[href] = th.parent.find_next_sibling('tr').text.strip()
					elif href == 'slayer_master':
						box_dict['assigned_by'] = [rt_dict.getToken(a.attrs['href'])	\
												for a in th.parent.find_next_sibling('tr').find_all('a',href=True)]
					elif href in ['combat', 'attack', 'defence']:
						stat_headers = th.parent.find_next_siblings('tr')[0].find_all('th')
						stat_titles = [a.attrs['href'].lower for a in stat_headers.find_all('a',href=True)]
						stat_tds   = th.parent.find_next_siblings('tr')[1].find_all('td')
						stats = [td.text.strip() for td in stat_tds]
						for title, stat in zip(stat_titles, stats):
							box_dict[href+'_'+title] = stat
					elif href == 'monster_attack_speed':
						# attack speed displayed as a gif image... bs4 doesn't find <img> tag
						asre = re.compile('Monster_attack_speed_([0-9]+)')
						mo = asre.search(th.parent.find_next_sibling('tr').text)
						box_dict['attack_speed'] = mo.group(1)
					
					else:
						print('INFOBOX:\tUnparsed row header:\t'+th.text.strip())
		return box_dict

	except Exception as e:
		print('Failure converting url to natural language')
		print(e)
	
	return {}
	

def demoPars(url):
	soup = msl.getSoup(url)
	article = soup.find(id='mw-content-text')
	pars = article.findAll('p')
	for index, p in enumerate(pars):
		if p.parent.name != 'figcaption':
			print(str(index)+':\t'+p.text[:30])
	return pars

def demo(url, **kwargs):
	soup = msl.getSoup(url)
	article = soup.find(id='mw-content-text')
	tags = article.findAll(**kwargs)
	for index, t in enumerate(tags):
		print(str(index)+':\t'+t.text[:30])
	return tags