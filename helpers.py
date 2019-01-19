import pickle as p
import pandas as pd
import itertools
import ast
import sqlite3
from collections import Counter

# Helper functions for the rest of the code

def getPolitiekTokens(years='all', contains_word=''):
	''' Returns a list of Tweede Kamer tokens.
	Accepts multiple ways of filtering on year: single int, 
	list of ints, list of list ints.
	Provide a word in `contains_word` to only get
	spreekbeurten that contain that string. '''

	li_tokens = []

	# Convert the querystring to a list of one element if it is a string
	if isinstance(contains_word, str):
		contains_word = [contains_word]

	if years == 'all':
		for i in range(23):
			year = 1995 + i
			tokens = p.load(open('data/politiek/handelingen/tokens/tokens_handelingen_' + str(year) + str(year + 1) + '.p', 'rb'))
			if contains_word != '':
				for spreekbeurt in tokens:
					if set(contains_word).issubset(spreekbeurt):
						#print(spreekbeurt, contains_word)
						tokens.append(spreekbeurt)
				#li_tokens = [spreekbeurt for spreekbeurt in li_tokens if set(contains_word).issubset(spreekbeurt)]
	
	# Simply return the tokens of one year if `years` is a single int
	elif isinstance(years, int):
		tokens = p.load(open('data/politiek/handelingen/tokens/tokens_handelingen_' + str(years) + str(years + 1) + '.p', 'rb'))
		# Filter on word if nessecary
		if contains_word != '':
			for spreekbeurt in tokens:
				if set(contains_word).issubset(spreekbeurt):
					#print(spreekbeurt, contains_word)
					tokens.append(spreekbeurt)
			#tokens = [spreekbeurt for spreekbeurt in tokens if set(contains_word).issubset(spreekbeurt)]
		tokens = list(itertools.chain.from_iterable(tokens))
		li_tokens.append(tokens)

	# Return tokens per year in a list if a list of years is provided
	elif isinstance(years, list) and isinstance(years[0], int):
		
		for year in years:
			tokens = p.load(open('data/politiek/handelingen/tokens/tokens_handelingen_' + str(year) + str(year + 1) + '.p', 'rb'))
			# Filter on word if necessary
			if contains_word != '':
				match_tokens = []
				for spreekbeurt in tokens:
					if set(contains_word).issubset(spreekbeurt):
						#print(spreekbeurt, contains_word)
						match_tokens.append(spreekbeurt)
				tokens = match_tokens
				#tokens = [spreekbeurt for spreekbeurt in tokens if set(contains_word).issubset(spreekbeurt)]
			tokens = list(itertools.chain.from_iterable(tokens))
			li_tokens.append(tokens)

	# If a list of lists with years is provided,
	# merge the tokens from a single list and return tokens in a per range
	elif isinstance(years, list) and isinstance(years[0], list):
		for year_range in years:
			li_year_range = []
			for year in year_range:
				tokens = p.load(open('data/politiek/handelingen/tokens/tokens_handelingen_' + str(year) + str(year + 1) + '.p', 'rb'))
				# Filter on word if necessary
				if contains_word != '':
					match_tokens = []
					for spreekbeurt in tokens:
						if set(contains_word).issubset(spreekbeurt):
							#print(spreekbeurt, contains_word)
							match_tokens.append(spreekbeurt)
					tokens = match_tokens
					#print(contains_word, tokens)
					#tokens = [spreekbeurt for spreekbeurt in tokens if set(contains_word).issubset(spreekbeurt)]
				li_year_range.append(list(itertools.chain.from_iterable(tokens)))
			tokens = list(itertools.chain.from_iterable(li_year_range))
			li_tokens.append(tokens)

	else:
		print('Indicate which years to fetch with a single int (e.g. 2000) or a list of ints (e.g. [2000,2001,2002]')
		quit()

	return li_tokens

def getKrantTokens(file, filter_krant=False, years='all',):
	''' Returns the tokens from a newspapers.
	Accepts multiple ways of filtering on year: single int, 
	list of ints, list of list ints.
	Provide a newspaper in `filter_krant` to only get
	articles from that newspaper. '''

	df = pd.read_csv(file)
	li_tokens = []

	if 'tokens' not in df.columns:
		print('Tokenise the newspaper text first with getTokens.py!')
		quit()

	if filter_krant != False:
		if filter_krant == 'ad':
			filter_krant = 'dagblad'
		df = df[df['newspaper'].str.contains(filter_krant, case=False)]

	# Filter the DataFrame on whether it is in a year.
	if years != 'all':
		if isinstance(years, list):
			for years in years:
				if isinstance(years, list):
					df_year = df[df['date_formatted'].str.contains('|'.join([str(single_year) for single_year in years]))]
					tokens = [ast.literal_eval(tokens) for tokens in df_year['tokens'].tolist()]
					tokens = list(itertools.chain.from_iterable(tokens))
					li_tokens.append(tokens)
				elif isinstance(years, int):	
					df_year = df[df['date_formatted'].str.contains(str(years))]
					tokens = [ast.literal_eval(tokens) for tokens in df_year['tokens'].tolist()]
					tokens = list(itertools.chain.from_iterable(tokens))
					li_tokens.append(tokens)
		elif isinstance(years, int):	
					df_year = df[df['date_formatted'].str.contains(str(years))]
					tokens = [ast.literal_eval(tokens) for tokens in df_year['tokens'].tolist()]
					tokens = list(itertools.chain.from_iterable(tokens))
					li_tokens.append(tokens)
		else:
			print('Invalid year')
			print(type(years), years)
			quit()

	return li_tokens

def getFbTokens(years='all', contains_word=''):
	''' Returns a list of Facebook tokens.
	Returns everything by default, but can also
	return the tokens specific years, if provided
	with a list.
	Provide a word in `contains_word` to only get
	comments that contain that string. '''

	# Convert the querystring to a list of one element if it is a string
	if isinstance(contains_word, str):
		contains_word = [contains_word]

	df = getFbDf(querystring=contains_word)

	li_tokens = [ast.literal_eval(tokens) for tokens in df['tokens'].tolist()]
	li_tokens = list(itertools.chain.from_iterable(li_tokens))

	return li_tokens

def getStem(word):
	''' Checks if a stem is in the di_stems.p file.
	If it exists, it returns the word, and if not
	if shows wat similar words are in the file. '''

	di_stems = p.load(open('data/di_stems.p', 'rb'))
	if word not in di_stems:
		print(word + ' not in di_stems')
		print('Similarities:', [k for k, v in di_stems.items() if k.startswith(word[:4])])
		quit()
	else:
		return word

def rankVergaderingen(querystring):
	''' Prints out a ranked list of the vergaderingen where a 
	querystring was most often uttered. '''

	if isinstance(querystring, list):
		querystring = '|'.join(querystring)
	df = pd.read_csv('data/politiek/handelingen/all-handelingen-no-voorzitter.csv')
	df = df[df['tekst'].str.contains(querystring, case=False, na=False)]
	
	vergader_count = Counter(df['item-titel-full'].tolist()).most_common(10)
	return [(vergadering, (df.loc[df['item-titel-full'] == vergadering[0], 'datum'].iloc[0])) for vergadering in vergader_count]

def getSpreekbeurtCount():
	''' Returns a dict with the parties with most amount of
	spreekbeurten per year '''

	di_spreekbeurten = {}
	df = pd.read_csv('data/politiek/handelingen/all-handelingen.csv')
	for year in li_handelingen_year:
		df_year = df[df['datum'].str.contains(year)]
		#print(year, len(df_year))
		di_spreekbeurten[year] = len(df_year)
	return di_spreekbeurten

def getFbDf(querystring='', date=''):
	''' Returns a pandas DataFrame from the Facebook data.
	Can fetch data with a querystring. Can be one date,
	a range of dates, or a range of range of dates.
	Leave `querystring` empty for the full dataset.'''

	if querystring == '':
		df = pd.read_csv('data/social_media/fb/fb_nl_programmas_withtokens.csv')
	else:
		if len(querystring) == 1 and isinstance(querystring[0], list):
			querystring = querystring[0]
		if '|' in querystring:
			querystring = querystring.split('|')
		print(querystring)

		sql = 'SELECT * FROM page_comments WHERE '

		if isinstance(querystring, list):
			sql = sql + '1=2 '
			for string in querystring:
				sql = sql + 'OR lower(comment_message) LIKE "%' + string + '%" '
		else:
			sql = sql + 'lower(comment_message) LIKE "%' + querystring + '%"'

		print(sql)
		conn = sqlite3.connect("data/social_media/fb/fb_nl_programmas.db")
		df = pd.read_sql(sql, conn)

	# Filter on time
	if date != '':
		if isintance(date, int):
			df = df[df['comment_published'].str.contains(str(date))]
		elif isinstance(date, list):
			dates = '|'.join(date)
			df = df[df['comment_published'].str.contains(str(date))]

	return df