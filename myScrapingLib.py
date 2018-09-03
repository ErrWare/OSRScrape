import requests, bs4

def getSoup(url):
	res = requests.get(url)
	try:
		res.raise_for_status()
		return bs4.BeautifulSoup(res.content,features='html5lib')
	except Exception as exc:
		print('Problem requesting ' + url)
	return None

class TokenDict:
	'Class doc string accessible via classname.__doc__'
	
	def __init__(self):
		self.myDict = {}

	def getToken(self, key):
		token = -1
		if key in self.myDict:
			token = self.myDict[key]['token']
			self.myDict[key]['accesses'] += 1
		else:
			token = len(self.myDict)
			self.myDict[key] = {}
			self.myDict[key]['token'] = token
			self.myDict[key]['accesses'] = 1
		return token

