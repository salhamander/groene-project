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
from collections import OrderedDict, Counter
from nltk.collocations import *
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from createHisto import createHorizontalHisto
from helpers import getPolitiekTokens, getKrantTokens, getFbTokens, getStem, rankVergaderingen, getFbDf

def calculateColocation(inputtokens, windowsize, nsize, querystring, full_comment=False, min_frequency=1, max_output=100, forbidden_words=False):
	''' Generates a tuple of word collocations (bigrams or trigrams).
	params: to be described :') '''
	
	tokens = []
	
	if isinstance(querystring, str):
		querystring = [querystring]
		print(querystring)

	if isinstance(inputtokens[0], list):
		tokens = list(itertools.chain.from_iterable(inputtokens))
	else:
		tokens = inputtokens

	if nsize == 1:
		finder = BigramCollocationFinder.from_words(tokens, window_size=windowsize)

		# Filter out combinations not containing the query string
		if full_comment == False:
			word_filter = lambda w1, w2: not any(string in (w1, w2) for string in querystring) or any(string in (w1, w2) for string in forbidden_words)
			#any([word for word in querystring] not in (w1, w2))
			finder.apply_ngram_filter(word_filter)
		
		# Filter out forbidden words
		if forbidden_words != False:
			forbidden_words_filter = word_filter = lambda w1, w2: any(string in (w1, w2) for string in forbidden_words)
			finder.apply_ngram_filter(word_filter)

		finder.apply_freq_filter(min_frequency)
	#generate trigrams
	if nsize == 2:
		finder = TrigramCollocationFinder.from_words(tokens, window_size=windowsize)

		# Filter out combinations not containing the query string
		if full_comment == False:
			word_filter = lambda w1, w2, w3: not any(string in (w1, w2, w3) for string in querystring)
			finder.apply_ngram_filter(word_filter)
		
		# Filter out forbidden words
		if forbidden_words != False:
			forbidden_words_filter = word_filter = lambda w1, w2, w3: any(string in (w1, w2, w3) for string in forbidden_words)
			finder.apply_ngram_filter(word_filter)

		finder.apply_freq_filter(min_frequency)

	colocations = sorted(finder.ngram_fd.items(), key=operator.itemgetter(1), reverse=True)[0:max_output]
	return colocations

def createColocationDf(input_collocations):
	''' Converts tuple collocation data to a simple Pandas DataFrame
	Doesn't work with trigrams yet '''

	df = pd.DataFrame()
	df['first_word'] = [tpl[0][0] for tpl in inputcolocations]
	df['second_word'] = [tpl[0][1] for tpl in inputcolocations]
	df['frequency'] = [tpl[1] for tpl in inputcolocations]

	#print(df)
	return(df)

def createRankfFlowDf(input_collocations, input_word, ngram_size, li_headers, filter_words=True):
	''' Converts a list of collocation data to a RankFlow compatible
	Pandas DataFrame. Requires a list of collocation tuples, an `input_word`
	which will be used to filter the results, and a list of headers
	to use in the DataFrame. '''

	print('Making a RankFlow capable DataFrame of collocation data.')

	di_stems = p.load(open('data/di_stems.p', 'rb'))
	di_all_data = OrderedDict()

	forbidden_words = ['reserved']

	print('Collecting data')
	# Loop through total list of list of collocation tuples
	for i, li_tpl in enumerate(input_collocations):
		li_words = []
		li_freqs = []
		# Loop through single list of collocation tuples

		for tpl in li_tpl:
			if ngram_size == 1:
				# Print the full bigrams or just the ones that are not the input words
				if filter_words:
					# Add one of the two bigram collocations
					# depending on whether it contains the `input_word`
					if tpl[0][0] not in forbidden_words and tpl[0][1] not in forbidden_words:
						if tpl[0][0] != input_word:
							if tpl[0][0] in di_stems:
								li_words.append(di_stems[tpl[0][0]][0])
							else:
								li_words.append(tpl[0][0])
						else:
							if tpl[0][1] in di_stems:
								li_words.append(di_stems[tpl[0][1]][0])
							else:
								li_words.append(tpl[0][1])
				else:
					li_words.append(str(di_stems[tpl[0][0]][0]) + ', ' + str((di_stems[tpl[0][1]][0])))

			elif ngram_size == 2:
				li_words.append(' '.join(tpl[0]))
			else:
				print('Incorrect ngram_size, try again.', ngram_size)
				quit()
			
			# Add the frequencies of the collocations
			li_freqs.append(tpl[1])
			
		di_all_data[li_headers[i]] = li_words
		di_all_data['frequency_' + str(li_headers[i])] = li_freqs

	#print(di_all_data)
	print('Compiling DataFrame')
	# Give the results the same length (fill up empty space with NaNs)
	df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in di_all_data.items() ]))
	print(df.head())
	return df

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

def getPolitiekCollocations(querystring='', li_years='all', ngram_size=1, window_size=3, full_comment=False, forbidden_words=False):
	''' Executes the collocation scripts for politiek data. '''

	li_tokens = getPolitiekTokens(contains_word=querystring, years=li_years)
	print(li_tokens[0])

	# Get the collocations per year
	li_collocations = []

	for tokens in li_tokens:
		collocations = calculateColocation(tokens, window_size, ngram_size, querystring, min_frequency=1, full_comment=full_comment, forbidden_words=forbidden_words)
		li_collocations.append(collocations)
		print(collocations[:5])

	if ngram_size == 1:
		ngram_label = 'bigrams-'
	elif ngram_size == 2:
		ngram_label = 'trigrams-'

	if isinstance(li_years[0], list):
		columns = [', '.join(str(x) for x in colnames) for colnames in li_years]
	else:
		columns = [str(year) for year in li_years]
	
	if isinstance(querystring, list):
		querystring = 'OR'.join(querystring)

	df = createRankfFlowDf(li_collocations, querystring, ngram_size, li_headers=columns, filter_words= not full_comment)
	df.to_csv('data/ngrams/politiek-' + ngram_label + querystring + '.csv')

	# Print out the vergaderingen that mentioned the querystring the most for reference
	print('Getting vergaderingen mentioning "' + str(querystring) + '" the most.')
	rank_vergaderingen = rankVergaderingen(querystring)
	print(rank_vergaderingen)
	txtfile_full = open('data/politiek/vergaderingen_by_query/vergaderingen_' + 'OR'.join(querystring) + '.txt', 'w')
	txtfile_full.write('%s' % rank_vergaderingen)

def getKrantCollocations(file, querystring, li_years, ngram_size=1, window_size=3, filter_krant=False, forbidden_words=False):
	''' Executes the collocation scripts for newspapers '''
	li_collocations = []
	li_tokens = getKrantTokens('data/media/kranten/' + file, filter_krant=filter_krant, years=li_years)
	
	# Filter out some unecessary newspaper data
	if isinstance(forbidden_words, list):
		forbidden_words.append('reserved')
	else:
		forbidden_words = ['reserved']

	for tokens in li_tokens:
		collocations = calculateColocation(tokens, window_size, ngram_size,  querystring, min_frequency=1, forbidden_words=forbidden_words)
		li_collocations.append(collocations)
		print(collocations[:5])

	# Set file name
	if ngram_size == 1:
		ngram_label = 'bigrams-'
	elif ngram_size == 2:
		ngram_label = 'trigrams-'
	if filter_krant == False:
		krant = ''
	else:
		krant = '-' + krant

	columns = [', '.join(str(x) for x in colnames) for colnames in li_years if isinstance(colnames, list)] + [str(year) for year in li_years if isinstance(year, int)]

	df = createRankfFlowDf(li_collocations, querystring, ngram_size, li_headers=columns)
	
	if isinstance(querystring, list):
		querystring = 'OR'.join(querystring)

	df.to_csv('data/ngrams/kranten-' + ngram_label + querystring + '-' + str(window_size) + '.csv')

def getFbCollocations(querystring='', li_years='all', ngram_size=1, window_size=3, full_comment=False, forbidden_words=False):
	''' Executes the collocation scripts for fb files '''

	# Fetch relevant data from the sqlite database
	li_tokens = getFbTokens(contains_word=querystring)
	
	# Wrap the tokens in a list if it's a single list
	if isinstance(li_tokens[0], str):
		print(len(li_tokens))
		li_tokens = [li_tokens]

	# Get the collocations per year
	li_collocations = []
	for tokens in li_tokens:
		collocations = calculateColocation(tokens, window_size, ngram_size, querystring, min_frequency=1, full_comment=full_comment, forbidden_words=forbidden_words)
		li_collocations.append(collocations)
		print(collocations[:5])

	if isinstance(li_years[0], list):
		columns = [', '.join(str(x) for x in colnames) for colnames in li_years]
	else:
		columns = [str(year) for year in li_years]

	if ngram_size == 1:
		ngram_label = 'bigrams-'
	elif ngram_size == 2:
		ngram_label = 'trigrams-'

	if isinstance(querystring, list):
		querystring = 'OR'.join(querystring)

	df = createRankfFlowDf(li_collocations, querystring, ngram_size, li_headers=columns, filter_words = not full_comment)
	df.to_csv('data/ngrams/facebook-' + ngram_label + querystring + '.csv')

	# Make a bar chart with the frequencies of the trigrams
	createHorizontalHisto((df[df.columns[0]].tolist())[:10], (df[df.columns[1]].tolist())[:10], histo_title='Veelvoorkomende woordcominaties met "' + querystring + '"\nop Facebook pagina\'s van actualiteitenprogramma\'s', file_name= 'facebook-' + ngram_label + querystring)

if __name__ == '__main__':

	li_years = [[1995,1996,1997],[1998,1999,2000],[2001,2002,2003],[2004,2005,2006],[2007,2008,2009],[2010,2011,2012],[2013,2014,2015],[2016,2017,2018]]
	#li_years = [[1999],[2000],[2001]]
	#li_years = [2011,2012,2013,2014,2015,2016,2017,2018]

	querystring = getStem('racism')
	#getPolitiekCollocations(querystring=querystring, li_years=li_years, full_comment=False, ngram_size=2)
	#getKrantCollocations('all-multicultureel-multiculturele-multiculturalisme-withtokens-deduplicated.csv', ngram_size=2, querystring=querystring, li_years=li_years, forbidden_words=['institut','forum'])

	getFbCollocations(querystring=querystring, ngram_size=2)