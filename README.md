#OSRScrape

Or Osiris Crêpe 

These are the basic python scripts I use(d) to scrape data from the OSRS wiki: http://oldschoolrunescape.wikia.com/wiki/Old_School_RuneScape_Wiki

Main python libraries used: requests, bs4, json</br>
Some openpyxl when I began and decided to play with it, but since I've transferred to json.</br>

The ultimate goal is to create a semantic net of concepts in the OSRS game world. A lot of information can be gained by simply scraping the already fairly structured content of the wiki.</br>

However I would like to branch into extracting relationships and semantics from the wiki articles using NLP. I have a very very very very very rough idea of how to start, but by no means do I understand the state of the art. I've started learning basics with the nltk python library but if anyone has pointers or ideas or contributions please let me know.</br>

I have added the latest json files. They are in a fairly structured format, but they are not yet in JSON-LD. As can be seen in armory_v#.json the natural language article text has been scraped and stitched. An important not is that links have been replaced with tokens (format: 'rsrc####') to assist with cross referencing. This relies on the availability and consistency of the rsrc_token_dict.json .
