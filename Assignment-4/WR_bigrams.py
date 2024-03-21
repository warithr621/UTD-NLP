#######################################################################################################
#
# 	FILE:
# 		WR_bigrams.py
# 	AUTHOR:
# 		Warith Rahman
# 	DESCRIPTION:
# 		This program ideally takes the HTML of a Wikipedia article (in this case that of K-pop group 
#		TWICE), strips out any HTML tags like <p>, forms bigrams (consecutive word/punctuation pairs
#		like "The potato" and "potato grew"), and returns the top 10 most common bigrams.
# 	DEPENDENCIES:
# 		Created with Python 3.10.11
# 		Libraries used: re, nltk, bs4->BeautifulSoup, requests, time (execution time analysis)
#		To run without time, comment out lines 24 + 28 + 69 + 72 + 88
#
#######################################################################################################

import re # regex module
import nltk.data
from nltk.tokenize import word_tokenize
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') # loads english.pickle
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

word_list = []
start_found = False # since some of the earlier sentences are weird
for s in sentences:
	if "BTS" in s:
		# this is the first sentence that starts all the references
		# which completely messes up the frequencies
		break
	s = re.sub(r'\[\d+?\]', '', s).strip()
	# there's also some weird "sentences" at the start we want to skip over
	if not start_found:
		if s[:9] == "The group":
			start_found = True
		else:
			continue
	out.write(s + "\n\n")
	tmp = word_tokenize(s)
	word_list += tmp
bigrams = [b for b in nltk.bigrams(word_list)] # create bigram tuples
bigram_freq = dict()
for b in bigrams:
	if b in bigram_freq.keys():
		bigram_freq[b] += 1
	else:
		bigram_freq[b] = 1
bigram_freq = sorted(bigram_freq.items(), key = lambda x:x[1], reverse = True) # sort dictionary by values (frequency)

print(f"Length of the word list: {len(word_list)}") # 9402
print("Below are the top 10 most common bigrams on the TWICE wiki article:\n")
for tup in bigram_freq[:10]:
	print(f"The bigram {tup[0]} appears {tup[1]} times")
out.close()
print(f"The assignment code took {time.time() - start:.3f} seconds to run\n\n")

## Bonus out of curiosity: find top 10 most common *words* instead of *bigrams*
start = time.time()
word_freq = dict()
for w in word_list:
	punc = [(1 if x in "~`!@#$%^&*()-_=+{}[]|\\:\";\'<>,.?/" else 0) for x in w]
	# basically if the sum of all numbers in punc is non-zero
	# that means at least one character in 'w' is a punctuation character
	if sum(punc) != 0:
		continue # remove any "words" with punctuation
	if w in word_freq.keys():
		word_freq[w] += 1
	else:
		word_freq[w] = 1
word_freq = sorted(word_freq.items(), key = lambda x:x[1], reverse = True) # sort dictionary by values (frequency)
print("Below are the top 10 most common words on the TWICE wiki article:\n")
for tup in word_freq[:10]:
	print(f"The word {tup[0]} appears {tup[1]} times")
print(f"The bonus code took {time.time() - start:.3f} seconds to run")
