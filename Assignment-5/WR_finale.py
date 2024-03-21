#######################################################################################################
#
# 	FILE:
# 		WR_finale.py
# 	AUTHOR:
# 		Warith Rahman
# 	DESCRIPTION:
# 		This program ideally takes the HTML of a Wikipedia article (in this case that of K-pop group 
#		TWICE), strips out any HTML tags like <p>, and does stuff after that idk
# 	DEPENDENCIES:
# 		Created with Python 3.10.11
# 		Libraries used: re, nltk, bs4->BeautifulSoup, requests, time (execution time analysis)
#		To run without time, comment out the lines that use time
#
#######################################################################################################

import re # regex module
import nltk.data
from nltk.tokenize import word_tokenize
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') # loads english.pickle
from nltk.corpus import wordnet as wn # for synset and part of speech identification
from bs4 import BeautifulSoup
import requests
import time

out = open('debug.txt', 'w') # debugging purposes

start = time.time()

url = "https://en.wikipedia.org/wiki/Twice"
raw_html = str(requests.get(url).text) # use requests module to get HTML info
raw_html = re.sub('>', '> ', raw_html) # space out the tags
obj = BeautifulSoup(raw_html, "html.parser") # i like soup

txt = str(obj.text).replace('\n', '')
sentences = tokenizer.tokenize(txt)

fixed = []
word_list = []
start_found = False # since some of the earlier sentences are weird
for s in sentences:
	if "BTS" in s:
		# this is the first sentence that starts all the references
		# which completely messes up the frequencies
		break
	s = re.sub(r'\[\d+?\]', '', s).strip() # remove any hyperlink numbers
	s = re.sub(r'\s{2,}|\t', ' ', s) # remove duplicate whitespaces
	# there's also some weird "sentences" at the start we want to skip over
	if not start_found:
		if s[:9] == "The group":
			start_found = True
		else:
			continue
	out.write(s + "\n\n")
	fixed.append(s)
sentences = fixed



out.close()