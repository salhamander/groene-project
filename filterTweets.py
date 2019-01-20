import re
import pandas as pd
import itertools
from collections import Counter
from helpers import *

def getTwitterTags(word, hashtags=True, at_mentions=False):
	''' Filters and ranks hashtags from a list of tweets. '''

	# Setup connection
	db = mysql.connector.connect(host='localhost',user='root',passwd='',database='actualiteitenprogrammas')
	cur = db.cursor()
	print('Connected to database')

	li_forbidden_hashtags = ['#nosharia', '#nosparadran', '#nosviesdabord', '#nosmémoires']
		

	word = '%' + word + '%'
	cur.execute('''
		SELECT * FROM actualiteitenprogrammas_tweets
		WHERE text LIKE %s
		''', (word,))

	print('Executing query')
	results = cur.fetchall()
	db.close()
	li_tweets = [tweet[20] for tweet in results]
	li_tags = []
	for index, tweet in enumerate(li_tweets):
		#print(tweet, type(tweet))
		hashtags = re.findall(r'#\w*[a-zA-Z]+\w*', tweet)
		at_mentions = re.findall(r'@\w*[a-zA-Z]+\w*', tweet)
		tags = list(itertools.chain.from_iterable([hashtags, at_mentions]))
		#Filter out forbidden hashtags
		tags = [tag for tag in tags if tag.lower() not in li_forbidden_hashtags]
		li_tags.append(hashtags)

	li_tags = list(itertools.chain.from_iterable(li_tags))
	li_tags = Counter(li_tags)
	print(li_tags.most_common(100))

def filterBioHashtags():
	''' Filters a tcat dataset by most-used
	hashtags and @-mentions. '''


if __name__ == '__main__':
	getTwitterTags('racisme')