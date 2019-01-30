import re
import pandas as pd
import itertools
from datetime import date, datetime, timedelta
from collections import Counter, OrderedDict
from helpers import *

def getTwitterText(word, table, hashtags=True, at_mentions=False, date='', topn=25):
	''' Filters and ranks hashtags from a list of tweets. '''
	db = mysql.connector.connect(host='localhost', user='root', passwd='', database='tweet_collections')
	cur = db.cursor()
	print('Connected to database')
	word = '%' + word + '%'
	sql_query = 'SELECT * FROM ' + table + ' WHERE lower(text) LIKE "' + word + '"'

	if date != '':
		#time = '"%' + month + '"'
		if len(date) == 4:
			sql_query = sql_query + ' AND YEAR(created_at) = ' + date
		else:
			month = date[-2:]
			year = date[:-3]
			sql_query = sql_query + ' AND MONTH(created_at) = ' + month + ' AND YEAR(created_at) = ' + year
	#print(sql_query)
	cur.execute(sql_query)
	results = cur.fetchall()

def getTwitterTags(word, table, hashtags=True, at_mentions=False, date='', topn=25, forbidden_tags=[]):
	''' Filters and ranks hashtags from a list of tweets. '''

	# Setup connection
	db = mysql.connector.connect(host='localhost', user='root', passwd='', database='tweet_collections')
	cur = db.cursor()
	print('Connected to database')

	forbidden_tags.append(['#nosharia', '#nosparadran', '#nosviesdabord', '#nosmémoires'])

	# Fetch data from the db
	print('Executing query')
	sql_query = 'SHOW columns FROM ' + table
	cur.execute(sql_query)
	columns = [column[0] for column in cur.fetchall()]

	word = '%' + word + '%'
	sql_query = 'SELECT * FROM ' + table + ' WHERE lower(text) LIKE "' + word + '"'

	if date != '':
		if len(date) == 4:
			sql_query = sql_query + ' AND YEAR(created_at) = ' + date
		else:
			month = date[-2:]
			year = date[:-3]
			sql_query = sql_query + ' AND MONTH(created_at) = ' + month + ' AND YEAR(created_at) = ' + year + ' LIMIT 10'
	
	print(sql_query)
	cur.execute(sql_query)
	results = cur.fetchall()
	db.close()
	df = pd.DataFrame(results, columns=columns)

	# Extract hashtags from the tweets
	li_tweets = [tweet['text'] for i, tweet in df.iterrows()]
	li_tags = []
	
	for index, tweet in enumerate(li_tweets):
		#print(tweet, type(tweet))
		hashtags = re.findall(r'#\w*[a-zA-Z]+\w*', tweet)
		at_mentions = re.findall(r'\@\w*[a-zA-Z]+\w*', tweet)
		tags = list(itertools.chain.from_iterable([hashtags, at_mentions]))
		#Filter out forbidden hashtags
		tags = [tag for tag in tags if tag not in forbidden_tags]
		li_tags.append(hashtags)

	li_tags = list(itertools.chain.from_iterable(li_tags))
	li_tags = Counter(li_tags)
	print(li_tags.most_common(topn))
	return li_tags.most_common(topn)

def filterBioHashtags():
	''' Filters a tcat dataset by most-used
	hashtags and @-mentions. '''

	# to write...

def createRankFlowDf(di_values):
	''' Creates a rankflow-compatible df based on the
	tweet data. '''
	di_formatted = OrderedDict()

	for key, values in di_values.items():
		di_formatted[key] = [tpl[0] for tpl in values]
		di_formatted['frequency_' + key] = [tpl[1] for tpl in values]

	df = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in di_formatted.items()]))
	return(df)

def createStreamgraphDf(df, li_headers, limit=10):
	''' Converts a Rankflow DataFrame to RAWGraphs
	streamgraphs-compatible	pandas DataFrame. ''' 

	print('Making a RAWGraphs compatible csv...')

	li_words = []
	li_values = []
	li_dates = []

	# Make lists of the words and their frequencies
	for i, column in enumerate(df.columns):
		if 'frequency_' in column:
			for n in range(limit):
				li_values.append(df.iloc[n][column])
		elif '20' in column or '19' in column:
			for n in range(limit):
				li_words.append(df.iloc[n][column])
	
	print(li_values, li_words)

	# Make a list with dates
	for header in li_headers:
		for n in range(limit):
			print(header, n)
			li_dates.append(header[:4])

	# Write the lists as columns to a DataFrame
	di_df = {'word': li_words, 'values': li_values, 'dates': li_dates}
	df = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in di_df.items()]))
	return df

if __name__ == '__main__':

	di_tags = OrderedDict()
	forbidden_tags=['#dwdd','#lagerhuis', '#jinek','#nieuwsuur']
	for year in getDateRange('2014', '2018', time_format='years'):
		print(year)
		li_tags = getTwitterTags('sylvana', 'actualiteitenprogrammas_tweets', date=year, topn=25, forbidden_tags=forbidden_tags)
		di_tags[year] = li_tags
	df = createRankFlowDf(di_tags)
	columns = [year for year in getDateRange('2014', '2018', time_format='year')]
	df_stream = createStreamgraphDf(df, columns)
	df_stream.to_csv('hashtags_sylvana.csv')
	#getTwitterTags('racisme', 'actualiteitenprogrammas_tweets')