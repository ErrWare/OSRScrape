import re, bs4
pRegex = re.compile('<p.*>')
supRegex = re.compile('<sup.*>')


f = open('LongItemPar.txt','rb')
string = f.read(9999999)
string = string.decode()
print(len(string))
tokensToRemove = ['<p>','</p>','<b>','</b>','•','<i>','</i>']
for token in tokensToRemove:
	string = string.replace(token,'')

reToRemove = [re.compile('<p.*>'),re.compile('<sup.*>')]
				#re.compile('class=".*"'),re.compile('title=".*"')]
for rx in reToRemove:
	string = re.sub(rx,'',string)

#The ? denote non-greedy re
'''
resourceRe = re.compile('<a.*?>.*?</a>')
string = re.sub(resourceRe, '<resource>', string)
'''

soup = bs4.BeautifulSoup(string,features='html5lib')
for link in soup.select('a'):
	resourceLink = link.attrs['href']
	link.replace_with(resourceLink)

string = soup.text
print(len(string))
f.close()
f = open('nlpItemPar.txt','wb')
f.write(string.encode())
f.close()