#######################################################################################################
#
# 	FILE:
# 		WR_site_parser.py
# 	AUTHOR:
# 		Warith Rahman
# 	DESCRIPTION:
# 		This program first extracts HTML from a website and removes any possible HTML tags (such as <p>),
#		then splits the data on both newlines and by sentences. For each sentence, the program 
#		identifies all words in the sentence and returns a list of tuples containing the word, its part of
#		speech, and its stem according to the PorterStemmer
# 	DEPENDENCIES:
# 		Created with Python 3.10.11
# 		Libraries used: re, nltk, bs4->BeautifulSoup, requests, time (used for execution time analysis)
#		To run without `time`, comment out lines 22 + 35 + 49-50
#
#######################################################################################################

import re # regex module
import nltk.data
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') # loads english.pickle
import time # just to check execution time
from bs4 import BeautifulSoup
import requests

url = "https://www.ktvu.com/news/wildlife-experts-seek-to-capture-surfing-santa-cruz-sea-otter-deemed-public-safety-risk"
raw_html = str(requests.get(url).text) # use requests module to get HTML info
re.sub('>', '> ', raw_html) # space out the tags
obj = BeautifulSoup(raw_html, "html.parser") # i like soup

txt = str(obj.text).replace('\n', '')
sentences = tokenizer.tokenize(txt)
print("# of sentences found:", len(sentences)) # 40 sentences found

start = time.time()
porter = nltk.PorterStemmer() # used for finding stems of words
for sentence in sentences:
	word_list = nltk.word_tokenize(re.sub(' +', ' ', sentence)) # remove extraneous spaces
	tagged = nltk.pos_tag(word_list) # splits into words and calls pos_tag()
	tuple_list = [(word, POS, porter.stem(word)) for word, POS in tagged] # forms the tuples

	###################### just store the output in a single string lol ######################
	output = f"{'~'*40}\n{sentence}\n{str(tuple_list)}\n"
	###################### just store the output in a single string lol ######################
	# note I copied this idea from Assignment 2, significantly less necessary now but oh well

	print(output, flush=True) # prints output

exec_time = time.time() - start
print(f"Program took a total of {exec_time:.3f} seconds, for an average of {(exec_time / len(sentences)):.3e} seconds per sentence.")