import pickle as p
import pandas as pd
import itertools
import ast
from getTokens import getNewspaperTokens

# Helper functions for the rest of the code

def getPolitiekTokens(years='all', contains_word=''):
	''' Returns a list of Tweede Kamer tokens.
	Returns everything by default, but can also
	return the tokens specific years, if provided
	with a list.
	Provide a word in `contains_word` to only get
	spreekbeurten that contain that string. '''

	if years == 'all':
		for i in range(23):
			year = 1995 + i
			li_tokens = p.load(open('data/politiek/handelingen/tokens/tokens_handelingen_' + str(year) + str(year + 1) + '.p', 'rb'))
			if contains_word != '':
				li_tokens = [spreekbeurt for spreekbeurt in li_tokens if contains_word in spreekbeurt]
	
	elif not isinstance(years, list) and not isinstance(years, int):
		print('Indicate which years to fetch with a single int (e.g. 2000) or a list of ints (e.g. [2000,2001,2002]')
		quit()
	else:
		li_tokens = []

		# Simply return the tokens of one year if `years` is a single int
		if isinstance(years, int):
			tokens = p.load(open('data/politiek/handelingen/tokens/tokens_handelingen_' + str(years) + str(years + 1) + '.p', 'rb'))
			# Filter on word if nessecary
			if contains_word != '':
				tokens = [spreekbeurt for spreekbeurt in tokens if contains_word in spreekbeurt]
			tokens = list(itertools.chain.from_iterable(tokens))
			li_tokens.append(tokens)

		# Return tokens per year in a list if a list of years is provided
		elif isinstance(years[0], int):
			for year in years:
				tokens = p.load(open('data/politiek/handelingen/tokens/tokens_handelingen_' + str(year) + str(year + 1) + '.p', 'rb'))
				# Filter on word if necessary
				if contains_word != '':
					tokens = [spreekbeurt for spreekbeurt in tokens if contains_word in spreekbeurt]
				tokens = list(itertools.chain.from_iterable(tokens))
				li_tokens.append(tokens)

		# If a list of lists with years is provided,
		# merge the tokens from a single list and return tokens in a per range
		elif isinstance(years[0], list):
			for year_range in years:
				li_year_range = []
				for year in year_range:
					tokens = p.load(open('data/politiek/handelingen/tokens/tokens_handelingen_' + str(year) + str(year + 1) + '.p', 'rb'))
					# Filter on word if necessary
					if contains_word != '':
						tokens = [spreekbeurt for spreekbeurt in tokens if contains_word in spreekbeurt]
					li_year_range.append(list(itertools.chain.from_iterable(tokens)))
				tokens = list(itertools.chain.from_iterable(li_year_range))
				li_tokens.append(tokens)

	return li_tokens

def getKrantTokens(file, filter_krant=False, years='all',):
	''' Returns the tokens from a newspapers. '''

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
			if isinstance(years[0], list):
				for li_years in years:
					df_year = df[df['date_formatted'].str.contains('|'.join([str(year) for year in li_years]))]
					tokens = [ast.literal_eval(tokens) for tokens in df_year['tokens'].tolist()]
					tokens = list(itertools.chain.from_iterable(tokens))
					li_tokens.append(tokens)
			elif isinstance(years[0], int):
				for year in years:
					df_year = df[df['date_formatted'].str.contains(str(year))]
					tokens = [ast.literal_eval(tokens) for tokens in df_year['tokens'].tolist()]
					tokens = list(itertools.chain.from_iterable(tokens))
					li_tokens.append(tokens)

			else:
				print('Invalid year')
				print(type(year), year)
				quit()

	return li_tokens

def getStem(word):
	''' Checks if a stem is in the di_stems.p file.
	If it exists, it returns the word, and if not
	if shows wat similar words are in the file.'''

	di_stems = p.load(open('data/di_stems.p', 'rb'))
	if word not in di_stems:
		print(word + ' not in di_stems')
		print('Similarities:', [k for k, v in di_stems.items() if k.startswith(word[:4])])
		quit()
	else:
		return word