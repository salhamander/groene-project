import sqlite3
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import nltk
import re
import operator
import pickle as p
import itertools
import mysql.connector
from datetime import datetime, timedelta
from collections import OrderedDict
from nltk.collocations import *
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

#HEADERS: num, subnum, thread_num, op, timestamp, timestamp_expired, preview_orig,
# preview_w, preview_h, media_filename, media_w, media_h, media_size,
# media_hash, media_orig, spoiler, deleted, capcode, email, name, trip,
# title, comment, sticky, locked, poster_hash, poster_country, exif

# test db: 4plebs_pol_test_database
# test table: poldatabase
# full db: 4plebs_pol_18_03_2018
# full table: poldatabase_18_03_2018

def calculateColocation(inputtokens, windowsize, nsize, querystring, fullcomment, frequencyfilter, outputlimit, matchword=''):
	#guide here http://www.nltk.org/howto/collocations.html
	#generate bigrams
	print(inputtokens[:10])
	if matchword == '':
		matchword = querystring
	if nsize == 1:
		finder = BigramCollocationFinder.from_words(inputtokens, window_size=windowsize)
		#filter on bigrams that only contain the query string
		if fullcomment == False:
			word_filter = lambda w1, w2: matchword not in (w1, w2)
			finder.apply_ngram_filter(word_filter)
	#generate trigrams
	if nsize == 2:
		finder = TrigramCollocationFinder.from_words(inputtokens, window_size=windowsize)
		#filter on trigrams that only contain the query string
		if fullcomment == False:
			word_filter = lambda w1, w2, w3: matchword not in (w1, w2, w3)
			finder.apply_ngram_filter(word_filter)

			finder.apply_freq_filter(frequencyfilter)

	colocations = sorted(finder.ngram_fd.items(), key=operator.itemgetter(1), reverse=True)[0:outputlimit]
	print(colocations[:10])
	return colocations

def createColocationCsv(inputcolocations):
	
	columns = []
	df = pd.DataFrame()

	for key, values in inputcolocations.items():
		li_colocations = []
		li_mentions = []
		mentions = 0
		columns.append(key)
		columns.append('mentions')

		for colocation_tuple in values:
			str_colocations = ''
			#loop through tuple with colocation words and frequency (at the end)
			for index, tuple_value in enumerate(colocation_tuple):
				
				if type(tuple_value) is tuple:
					for string in tuple_value:
						str_colocations = str_colocations + ' ' + string
				else:
					mentions = tuple_value

			li_colocations.append(str_colocations)
			li_mentions.append(mentions)

		tmp_df = pd.DataFrame()
		tmp_df[key] = li_colocations
		tmp_df['mentions'] = li_mentions
		df = pd.concat([df, tmp_df], axis=1)
		
	print(df)
	return(df)

def getHandelingenCollocations():
	tokens = p.load(open('data/politiek/handelingen/tokens/tokens_handelingen_20072010.p', 'rb'))
	tokens = list(itertools.chain.from_iterable(tokens))
	colocations = calculateColocation(tokens, 10, 2, 'islam', fullcomment=False, frequencyfilter=10, outputlimit=10)

	print('Generating RankFlow-capable csv of colocations')
	rankflow_df = createColocationCsv(colocations)
	rankflow_df.to_csv('colocations/islam-colocations-.csv')

	print('Writing restults to textfile')
	write_handle = open('data/politiek/handelingen/islam-colocations-.txt',"w")
	write_handle.write(str(str_colocations))
	write_handle.close()

def getHashTags(li_tweets):
	'''
	Filters and ranks hashtags from a list of tweets
	'''

	li_hashtags = []
	for index, tweet in enumerate(li_tweets):
		print(tweet, type(tweet))
		hashtags = re.findall(r'#\w*[a-zA-Z]+\w*', tweet)
		li_hashtags.append(hashtags)
	
	print(li_hashtags)

def getTweetCollocations(word):

	db = mysql.connector.connect(
	  host='localhost',
	  user='root',
	  passwd='',
	  database='actualiteitenprogrammas'
	)

	print(db)

	cur = db.cursor()

	# Use all the SQL you like
	cur.execute("""
		SELECT * FROM actualiteitenprogrammas_tweets
		WHERE text LIKE %s
		AND lower(text) NOT LIKE '%nosharia%'
		""", ("%" + word + "%",))

	# Print all the first cell of all the rows
	results = cur.fetchall()

	db.close()

	# Dump the results
	p.dump(results, open('data/social_media/twitter/tweets_actprogrammas_' + word + '.p', 'wb'))

	tweets = [tweet[20] for tweet in results]
	getHashTags(tweets)

getTweetCollocations('islam')