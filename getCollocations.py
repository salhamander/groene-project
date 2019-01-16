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
from helpers import getPolitiekTokens, getKrantTokens, getStem
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

def calculateColocation(inputtokens, windowsize, nsize, querystring, fullcomment=False, min_frequency=1, max_output=100, matchword=''):
	''' Generates a tuple of word collocations (bigrams or trigrams).
	params: to be described :') '''

	tokens = []

	if isinstance(querystring, str):
		for spreekbeurt in inputtokens:
			if querystring in spreekbeurt:
				tokens.append(spreekbeurt)
	elif isinstance(querystring, list):
		for spreekbeurt in inputtokens:
			if any(i in querystring for i in spreekbeurt):
				tokens.append(spreekbeurt)
	tokens = list(itertools.chain.from_iterable(tokens))
	#print(tokens[:10])

	if matchword == '':
		# if isinstance(querystring, str):
		# 	matchword = [querystring]
		# else:
		matchword = querystring
	if nsize == 1:
		finder = BigramCollocationFinder.from_words(tokens, window_size=windowsize)
		#filter on bigrams that only contain the query string
		if fullcomment == False:
			word_filter = lambda w1, w2: matchword not in (w1, w2)
			finder.apply_ngram_filter(word_filter)
	#generate trigrams
	if nsize == 2:
		finder = TrigramCollocationFinder.from_words(tokens, window_size=windowsize)
		#filter on trigrams that only contain the query string
		if fullcomment == False:
			word_filter = lambda w1, w2, w3: matchword not in (w1, w2)
			finder.apply_ngram_filter(word_filter)

			finder.apply_freq_filter(min_frequency)

	colocations = sorted(finder.ngram_fd.items(), key=operator.itemgetter(1), reverse=True)[0:max_output]
	#print(colocations[:10])
	return colocations

def createColocationDf(input_collocations):
	''' Converts tuple collocation data to a simple Pandas DataFrame
	Doesn't work with trigrams yet '''

	df = pd.DataFrame()
	df['first_word'] = [tpl[0][0] for tpl in inputcolocations]
	df['second_word'] = [tpl[0][1] for tpl in inputcolocations]
	df['frequency'] = [tpl[1] for tpl in inputcolocations]

	print(df)
	return(df)

def createRankfFlowDf(input_collocations, input_word, li_headers):
	''' Converts a list of collocation data to a RankFlow compatible
	Pandas DataFrame. Requires a list of collocation tuples, an `input_word`
	which will be used to filter the results, and a list of headers
	to use in the DataFrame. '''

	print('Making a RankFlow capable DataFrame of collocation data.')

	di_stems = p.load(open('data/di_stems.p', 'rb'))
	di_all_data = OrderedDict()


	print('Collecting data')
	# Loop through total list of list of collocation tuples
	for i, li_tpl in enumerate(input_collocations):
		li_words = []
		li_freqs = []
		# Loop through single list of collocation tuples
		for tpl in li_tpl:
			# Add one of the two bigram collocations
			# depending on whether it contains the `input_word`
			if tpl[0][0] != input_word:
				li_words.append(di_stems[tpl[0][0]][0])
			else:
				li_words.append(di_stems[tpl[0][1]][0])

			li_freqs.append(tpl[1])
			di_all_data[li_headers[i]] = li_words
			di_all_data['frequency_' + str(li_headers[i])] = li_freqs

	#print(di_all_data)
	print('Compiling DataFrame')
	df = pd.DataFrame(di_all_data)
	print(df.head())
	return df

def getHandelingenCollocations():
	tokens = p.load(open('data/politiek/handelingen/tokens/tokens_handelingen_20072010.p', 'rb'))
	tokens = list(itertools.chain.from_iterable(tokens))
	colocations = calculateColocation(tokens, 10, 2, 'islam', fullcomment=False, frequencyfilter=10, max_output=10)

	print('Generating RankFlow-capable csv of colocations')
	rankflow_df = createColocationDf(colocations)
	rankflow_df.to_csv('colocations/islam-colocations-.csv')

	print('Writing restults to textfile')
	write_handle = open('data/politiek/handelingen/islam-colocations-.txt',"w")
	write_handle.write(str(str_colocations))
	write_handle.close()

def getHashTags(li_tweets):
	''' Filters and ranks hashtags from a list of tweets. '''

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


if __name__ == '__main__':

	#di_stems = p.load(open('data/di_stems.p', 'rb'))
	#print(sorted(di_stems.keys()))
	#print(di_stems['multiculturele'])
	#quit()

	li_years = [[1995,1996,1997,1998,1999],[2000,2001,2002,2003,2004],[2005,2006,2007,2008,2009],[2010,2011,2012,2013,2014],[2015,2016,2017,2018]]

	#li_years = [[1999],[2000],[2001]]
	print('Loading tokens')

	querystring = getStem('allochton')

	li_collocations = []
	for years in li_years:
		li_tokens = getPolitiekTokens(years, contains_word=querystring)
		collocations = calculateColocation(li_tokens, 3, 1, querystring, min_frequency=10)
		li_collocations.append(collocations)

	df = createRankfFlowDf(li_collocations, querystring, li_headers=[', '.join(str(x) for x in colnames) for colnames in li_years])
	df.to_csv('data/bigrams/bigrams-' + querystring + '.csv')