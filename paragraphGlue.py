import bs4, os

originalDir = os.getcwd()
os.chdir(os.path.join('saved_soup','items'))

soupFileNames = os.listdir()

longP = ''
for soupFileName in soupFileNames:
	print('Now on: ' + str(soupFileName))
	file = open(soupFileName, 'rb')
	soup = bs4.BeautifulSoup(file, features='html5lib')
	paragraphs = soup.select('p')
	for p in paragraphs:
		pstring = str(p)
		length = len(pstring)
		#filter out undesirable paragraphs
		if length > 20 and length < 1000 and len(p.select('img')) == 0:
			longP = longP + pstring
	file.close()

	print('New length: ' + str(len(longP)))
	
os.chdir(originalDir)

file = open('LongItemPar.txt','wb')
file.write(longP.encode())
file.close()
