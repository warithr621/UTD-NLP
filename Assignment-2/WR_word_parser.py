#######################################################################################################
#
# 	FILE:
# 		WR_word_parser.py
# 	AUTHOR:
# 		Warith Rahman
# 	DESCRIPTION:
# 		This program first processes a text file and removes any possible HTML tags (such as <p>),
#		then splits the data on both newlines and by sentences. For each sentence, the program 
#		identifies all words in the sentence and returns a list of tuples in the form ('word', 'POS').
#		It then takes the first noun and prints a list of all synsets for such noun.
# 	DEPENDENCIES:
# 		Created with Python 3.10.11
# 		Libraries used: re, nltk, time (used for execution time analysis)
#		To run without `time`, comment out lines 24 + 43 + 82-83
#
#######################################################################################################

import re # regex module
import nltk.data
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') # loads english.pickle
from nltk.corpus import wordnet as wn # for synset and part of speech identification
# nltk.download('averaged_perceptron_tagger') # necessary line for POS parsing
import time # just to check execution time

def remove_at(s):
	# since for some reason a bunch of sentences have the '@' character
	# just make a method to remove all of them without destroying the entire string
	tmp = nltk.word_tokenize(s)
	tmp = [w for w in tmp if '@' not in w]
	return ' '.join(map(str, tmp))

fr = open('text_web.txt', 'r', encoding='utf-8') # fr = file reader
file_input = ''.join(map(str, fr.readlines())) # stores all input in a single long string
fw = open('output.txt', 'w', encoding='utf-8') # fw = file writer

file_input = re.sub('<.*?>', '', file_input) # replaces all HTML tags with blank characters
file_input = file_input.replace('\n', '') # take out any newlines

file_input = tokenizer.tokenize(file_input) # uses tokenizer to split into sentences
print("# of sentences found:", len(file_input)) # 63430 sentences found

start = time.time()
for sentence in file_input:
	sentence = remove_at(sentence) # refer to declaration on line 24
	word_list = nltk.word_tokenize(sentence)
	word_list = [w for w in word_list if '@' not in w] # dumb @ signs... ._.
	tagged = nltk.pos_tag(word_list) # splits into words and calls pos_tag()
	tuple_list = [(word, POS) for word, POS in tagged] # forms the tuples
	noun_list = []
	for T in tuple_list:
		if 'NN' in T[1]:
			# this word is a noun!
			noun_list.append(T[0])
	if len(noun_list) == 0: continue # not sure why this would happen, but in case
	noun, synsets = noun_list[0], wn.synsets(noun_list[0])

	################### just store the output in a single string lol ###################
	output = f"{'~'*40}\n{sentence}\n{str(tuple_list)}\n{noun} {str(synsets)}\n"
	################### just store the output in a single string lol ###################

	# darn I thought I was done, time to do 3.4
	for syn in synsets:
		defin = syn.definition()[:30] # truncate definition
		output += f"{str(syn)}: {defin}...\n"
		if syn.pos() != 'n': continue # nouns can have non-noun synsets
		for N in noun_list[1:]: # exclude the first noun obviously
			lch = syn # will store the lowest common hypernym among
			         # all synsets of `N` and syn
			found = False
			for tmp in wn.synsets(N):
				if tmp.pos() != 'n': continue # again, nouns can have non-noun synsets
				lch = lch.lowest_common_hypernyms(tmp)[0]
				# remember that l_c_h() returns a list
				found = True # say that we actually found a noun
			if found:
				output += f"\tLCH between {syn} and '{N}' is {lch}: {lch.definition()[:30]}...\n"

	print(output, flush=True) # prints output
	fw.write(output) # writes output to file

exec_time = time.time() - start
print(f"Program took a total of {exec_time:.3f} seconds, for an average of {(exec_time / len(file_input)):.5e} seconds per sentence.")

## close open() ##
fr.close()
fw.close()
## close open() ##