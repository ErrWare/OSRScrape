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

