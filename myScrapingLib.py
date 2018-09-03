import requests, bs4

def getSoup(url):
	res = requests.get(url)
	try:
		res.raise_for_status()
		return bs4.BeautifulSoup(res.content,features='html5lib')
	except Exception as exc:
		print('Problem requesting ' + url)
	return null
