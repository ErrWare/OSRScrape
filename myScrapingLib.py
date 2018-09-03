import requests, bs4

def getSoup(url):
	res = requests.get(url)
	try:
		res.raise_for_status()
		return bs4.BeautifulSoup(res.content,features='html5lib')
	except Exception as exc:
		print('Problem requesting ' + url)
	return null

class TokenDict:
	'Class doc string accessible via classname.__doc__'
	myDict = {}
	
	def __init__(self):
		myDict = {}

	def getToken(key):
		token = -1
		if key in myDict:
			token = myDict[key]['token']
			myDict[key]['accesses'] += 1
		else:
			token = len(myDict)
			myDict[key] = {}
			myDict[key]['token'] = token
			myDict[key]['accesses'] += 1
		return token

