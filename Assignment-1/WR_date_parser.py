###############################################################################################
#
# 	FILE:
# 		WR_date_parser.py
# 	AUTHOR:
# 		Warith Rahman
# 	DESCRIPTION:
# 		This program opens a text file and splits it into paragraphs according to <p> tags,
#		uses tokenizer to split into sentences, and extracts dates from each sentences.
#		For each sentence a tuple is outputted: the first element is the sentence, and 
#		the second is a list of datetime objects found in said sentence.
# 	DEPENDENCIES:
# 		Created with Python 3.10.11
# 		Libraries used: re, datetime, isoweek, nltk.data
#
###############################################################################################

import re # regex module
from datetime import date, datetime, timedelta # for relative times
from isoweek import Week # https://pypi.org/project/isoweek/
import nltk.data
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') # loads english.pickle

################################################## Lists for storing the months ##################################################
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
months_short = ["Jan.", "Feb.", "Mar.", "Apr.", "May.", "Jun.", "Jul.", "Aug.", "Sep.", "Oct.", "Nov.", "Dec."]
################################################## Lists for storing the months ##################################################

F = open("text_web.txt", "r") # input file

initial = ''.join(map(str, F.readlines())) # combines all lines into one long string
paragraphs = initial.split(" <p> ") # split thing into paragraphs

MASTER_LIST = [] # stores ALL the dates

for p in paragraphs:
	# so apparently page citations are listed as "(pg . xy)"
	p = p.replace("pg . ", "pg.")
	sentences = tokenizer.tokenize(p) # forms sentences

	for i in range(len(sentences)):
		# upd: since we're using NLTK we don't have to worry about weird sentence splitting losing punctuation

		# now for the hard part: extracting dates ._.
		# list of options:
			# YYYY-MM-DD
			# MM/DD/YYYY
			# MM/DD/YY
			# BB DD, YYYY (July 04 or July 4)
			# bb DD, YYYY (Jul  04 or Jul  4)
			# today, yesterday, tomorrow
			# this/next/last weekday
				# last + next refer to ISO weeks 
				# this refers to the 7-day span beginning from this day
		# also note that it can just exclude the year... so also catch things like "July 04"

		cur = sentences[i]
		date_list = []
		for DATE in re.findall(r"\d{4}-\d{2}-\d{2}", cur): # YYYY-MM-DD
			obj = date(int(DATE[:4]), int(DATE[5:7]), int(DATE[8:]))
			date_list.append(obj)
		for DATE in re.findall(r"\d{2}/\d{2}/\d{4}", cur): # MM/DD/YYYY
			obj = date(int(DATE[6:]), int(DATE[:2]), int(DATE[3:5]))
			date_list.append(obj)
		# [slight problem: it can catch both "08/23/2011" and "08/23/20"]
		tmp_list = re.findall(r"\d{2}/\d{2}/\d{2}", cur) # MM/DD/YY
		for DATE in tmp_list:
			b = False
			for x in date_list:
				b |= (DATE in x)
			if not b:
				obj = date(int(DATE[6:]), int(DATE[:2]), int(DATE[3:5]))
				date_list.append(obj)	


		todays_date = datetime.now().date()
		for DATE in re.findall(r"(?i)today|yesterday|tomorrow", cur): # (?i) for case-insensitive
			if DATE.lower() == "today":
				date_list.append(todays_date)
			elif DATE.lower() == "yesterday":
				date_list.append(todays_date - timedelta(days=1))
			else:
				date_list.append(todays_date + timedelta(days=1))


		tuples = re.findall(r"(?i)(last|this|next)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", cur)
		for x in tuples:
			# problem with this one is that this returns a list of tuples instead of single strings
			if x[0] == 'this':
				# i think this is the easiest case
				todays_day = todays_date.weekday()
				goal = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(x[1])
				diff = (goal - todays_day + 7) % 7 # in case the day is 'before' in ISO terms
				date_list.append(todays_date + timedelta(days=diff))
			else:
				todays_week = Week.thisweek() # current ISO week
				new_week = todays_week + (-1 if x[0] == 'last' else +1) # new ISO week
				func = "new_week." + x[1].lower() + "()"
				date_list.append(eval(func))


		# in both of the next two cases, one string in the tuple will be null, pick the one that isn't
		# time for the BB DD, YYYY case
		for i in range(12):
			M = months[i]
			early_tmp_list = re.findall(r"(" + M + r" \d{1,2}(st|nd|rd|th) ,? \d{4})|(" + M + r" \d{1,2}(st|nd|rd|th))", cur)
			early_tmp_list = [x[0] or x[1] for x in early_tmp_list]
			for DATE in early_tmp_list:
				found = False
				for x in re.findall(r"(" + M + r" \d{4})", cur):
					found |= (DATE in x)
				if not found and DATE != '':
					obj = date(int(DATE[-4:]), i+1, int(DATE[len(M)+1 : len(DATE)-9]))
					date_list.append(obj)
			# ok so another problem is that it thinks dates like "February 2010" are dates like "February 20"...
			tmp_list = re.findall(r"(" + M + r" \d{1,2} ,? \d{4})|(" + M + r" \d{1,2})", cur)
			for DATE in [x[0] or x[1] for x in tmp_list]:
				found = False
				for x in re.findall(r"(" + M + r" \d{4})", cur):
					found |= (DATE in x)
				for x in early_tmp_list:
					found |= (DATE in x)
				if not found and DATE != '':
					dd, yy = 0, 0 # initialization
					if len(DATE) > len(M) + 3:
						dd, yy = int(DATE[len(M)+1 : len(DATE)-7]), int(DATE[-4:])
					else:
						dd, yy = int(DATE[len(M)+1:]), todays_date.year
					obj = date(yy, i+1, dd)
					date_list.append(obj)

		# and the bb DD, YYYY case
		for i in range(12):
			M = months_short[i]
			# ok so another problem is that it thinks dates like "Feb. 2010" are dates like "February 20"...
			tmp_list = re.findall(r"(" + M + r" \d{1,2} ,? \d{4})|(" + M + r" \d{1,2})", cur)
			for DATE in [x[0] or x[1] for x in tmp_list]:
				found = False
				for x in re.findall(r"(" + M + r" \d{4})", cur):
					found |= (DATE in x)
				if not found and DATE != '' and M in DATE:
					dd, yy = 0, 0 # initialization
					if len(DATE) > 7:
						dd, yy = int(DATE[5 : len(DATE)-7]), int(DATE[-4:])
					else:
						dd, yy = int(DATE[5:]), todays_date.year
					obj = date(yy, i+1, dd)
					date_list.append(obj)
		
		date_list = list(set(date_list)) # remove any possible duplicates
		for i in range(len(date_list)):
			date_list[i] = date_list[i].strftime("%Y-%m-%d") # reformat dates
		if len(date_list) != 0:
			print((cur, date_list))
			MASTER_LIST += date_list

print("Total number of dates:", len(MASTER_LIST)) # total number of extracted dates

F.close() # close the file reader