import re
import pickle as p
import pandas as pd
import ast
import os
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer

def getTokens(li_strings, stemming=False, lemmatizing=False):
	"""
	Self-made tokenizer Tweede Kamer text.
	Accepts input as a list of strings and a list of list of strings (paragraphs) 

	"""
	# Get a dict to save the stems of the words for retrieval later
	if stemming:
		global di_stems
		if os.path.isfile('data/di_stems.p'):
			di_stems = p.load(open('data/di_stems.p', 'rb'))
		else:
			di_stems = {}
	# Do some cleanup: only alphabetic characters, no stopwords
	# Create separate stemmed tokens, to which the full strings will be compared to:
	li_texts_stemmed = []
	len_text = len(li_strings)
	
	print(len(li_strings))
	
	for index, text in enumerate(li_strings):
		
		# Create list of list for comments and tokens
		if isinstance(text, str):
			li_text_stemmed = []
			li_text_stemmed = getFilteredText(text, stemming=stemming, lemmatizing=lemmatizing)
			li_texts_stemmed.append(li_text_stemmed)
		
		elif isinstance(text, list):
			li_text_stemmed = []
			for single_text in text:
				single_text = getFilteredText(single_text, stemming=stemming, lemmatizing=lemmatizing)
				li_text_stemmed.append(single_text)
			li_texts_stemmed.append(li_text_stemmed)

		if index % 100 == 0:
			print('Tokenising finished for string ' + str(index) + '/' + str(len_text))
	
	print(len(li_texts_stemmed))

	if stemming:
		p.dump(di_stems, open('data/di_stems.p', 'wb'))
		df_stems = pd.DataFrame.from_dict(di_stems, orient='index')
		df_stems.to_csv('di_stems_dataframe.csv')

	return li_texts_stemmed

def getFilteredText(string, stemming=False, lemmatizing=False):
	
	#first, remove urls
	# if 'http' in string:
	# 	string = re.sub(r'https?:\/\/.*[\r\n]*', ' ', string)
	# if 'www.' in string:
	# 	string = re.sub(r'www.*[\r\n]*', ' ', string)

	# get a list of words
	string = string.replace('\n', ' ')
	tokens = re.findall("[a-zA-Z]{3,50}", string)

	stemmer = SnowballStemmer('dutch')
	lemmatizer = WordNetLemmatizer()

	#list with tokens further processed
	li_filtered_tokens = []
	
	# filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
	for token in tokens:
		token = token.lower()
		
		# only alphabetic characters, keep '(' and ')' symbols for echo brackets, only tokens with three or more characters
		if re.match('[a-zA-Z\-\)\(]{3,50}', token) is not None:
			# no stopwords
			if token not in stopwords.words('dutch'):
				token = token.lower()

				# stem if indicated it should be stemmed
				if stemming:
					token_stemmed = stemmer.stem(token)
					li_filtered_tokens.append(token_stemmed)

					# update lookup dict with token and stemmed token
					# lookup dict is dict of stemmed words as keys and lists as full tokens
					if token_stemmed in di_stems:
						if token not in di_stems[token_stemmed]:
							di_stems[token_stemmed].append(token)
					else:
						di_stems[token_stemmed] = []
						di_stems[token_stemmed].append(token)
				
				#if lemmatizing is used instead
				elif lemmatizing:
					token = lemmatizer.lemmatize(token)
					li_filtered_tokens.append(token)
				
				else:
					li_filtered_tokens.append(token)

	return li_filtered_tokens

def getNewspaperTokens(path_to_file):
	''' Prepares the text in a compiled csv of newspaper data
	as to retrieve tokens '''
	df = pd.read_csv(path_to_file)
	df = df
	li_text = df['full_text'].tolist()
	
	all_tokens = []

	for i in range(len(df)):
		#print(df.loc[i])
		#print(len(li_text[i]))
		try:
			if li_text[i].startswith('['):
				raw_text = ast.literal_eval(li_text[i])
			else:
				raw_text = re.split('\"\, \'|\"\, \"|\'\, \"', li_text[i])
		except:
			raw_text = ''
		all_tokens.append(raw_text)
	
	all_tokens = getTokens(all_tokens, stemming=True)
	df['tokens'] = all_tokens
	df.to_csv(path_to_file[:-4] + '-withtokens.csv')
	df.to_csv('C:\\Users\\hagen\\Dropbox\\Universiteit van Amsterdam\\all-allochtoon-allochtoons-allochtoonse-allochtone-allochtonen-withtokens.csv')
	return all_tokens

if __name__ == '__main__':

	tokens = getNewspaperTokens('data/media/kranten/all-allochtoon-allochtoons-allochtoonse-allochtone-allochtonen.csv')
	#p.dump(tokens, open('data/media/kranten/tokens/tokens-allochtoon-allochtoons-allochtoonse-allochtone-allochtonen.p', 'wb'))

	# df = pd.read_csv('data/media/kranten/islam-moslim-moslims-atleast5-allpapers.csv')

	# years = years = ['1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018']
	# print(set(df['date_formatted'].tolist()))
	# quit()
	# for year in years:

	# 	df_date = df[df['date_formatted'].str.contains(year, NaN=False)]
	# 	tokens = df_date['tekst'].tolist()
	# 	print(len(tokens))
	# 	tokens = getTokens(tokens, stemming=True, lemmatizing=False)
	# 	p.dump(tokens, open('data/media/kranten/tokens_' + year + '-islam-moslim-moslims-atleast5-allpapers.p', 'wb'))
