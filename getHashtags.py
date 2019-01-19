def getHashTags(li_tweets):
	''' Filters and ranks hashtags from a list of tweets. '''

	li_hashtags = []
	for index, tweet in enumerate(li_tweets):
		print(tweet, type(tweet))
		hashtags = re.findall(r'#\w*[a-zA-Z]+\w*', tweet)
		li_hashtags.append(hashtags)
	
	print(li_hashtags)