import sys
import os
import pandas as pd
import pickle as p
import numpy as np
import itertools
from helpers import getPolitiekTokens, getKrantTokens, getStem
from sklearn.feature_extraction.text import TfidfVectorizer

def no_tokenizer(doc):
	return doc

def getTfidf(li_tokens, li_filenames, filename, min_df=0, max_df=0, top_n=25, ngram_range=1):
	'''
	Creates a csv with the top n highest scoring tf-idf words.

	:param input,		list of tokens. Should be unpickled first
	:param filename,	the name of the output folder, based on the input
	:param max_df,		filter out words that appear in more than length of token list - max_df
	:param min_df,		filter out words that appear in less than min_df
	:param ngram_range, the amount of words to extract
	'''

	if min_df != 0:
		min_df = len(li_tokens) - min_df
		print('Terms must appear in at least ' + str(min_df) + ' of the total ' + str(len(li_tokens)) + ' files.')
	if max_df == 0:
		max_df = len(li_tokens)
	else:
		max_df = len(li_tokens) - max_df
		print('Terms may only appear in max ' + str(max_df) + ' of the total ' + str(len(li_tokens)) + ' files.')

	output = 'data/tfidf/' + filename + '_tfidf.csv'

	print('Vectorizing!')
	print(min_df, max_df)
	tfidf_vectorizer = TfidfVectorizer(min_df=min_df, max_df=max_df, ngram_range=(ngram_range,ngram_range), analyzer='word', token_pattern=None, tokenizer=lambda i:i, lowercase=False)
	tfidf_matrix = tfidf_vectorizer.fit_transform(li_tokens)
	#print(tfidf_matrix[:10])

	feature_array = np.array(tfidf_vectorizer.get_feature_names())
	tfidf_sorting = np.argsort(tfidf_matrix.toarray()).flatten()[::-1]
	
	# Print and store top n highest scoring tf-idf scores
	top_words = feature_array[tfidf_sorting][:top_n]
	print(top_words)

	weights = np.asarray(tfidf_matrix.mean(axis=0)).ravel().tolist()
	df_weights = pd.DataFrame({'term': tfidf_vectorizer.get_feature_names(), 'weight': weights})
	df_weights = df_weights.sort_values(by='weight', ascending=False).head(100)
	#df_weights.to_csv(output[:-4] + '_top100_terms.csv')
	#print(df_weights.head())

	df_matrix = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_vectorizer.get_feature_names())
	
	# Turn the dataframe 90 degrees
	df_matrix = df_matrix.transpose()
	#print('Amount of words: ' + str(len(df_matrix)))
	
	print('Writing tf-idf vector to csv')

	# Do some editing of the dataframe
	df_matrix.columns = li_filenames
	cols = df_matrix.columns.tolist()
	cols = li_filenames

	df_matrix = df_matrix[cols]
	#df_matrix.to_csv(output[:-4] + '_matrix.csv')
	
	df_full = pd.DataFrame()

	print('Writing top ' + str(top_n) + ' terms per token file to "' + output[:-4] + '_full.csv"')
	# Store top terms per doc in a csv
	for index, doc in enumerate(df_matrix):
		df_tim = (df_matrix.sort_values(by=[doc], ascending=False))[:top_n]
		df_timesep = pd.DataFrame()
		df_timesep[doc] = df_tim.index.values[:top_n]
		df_timesep['tfidf_score_' + str(index + 1)] = df_tim[doc].values[:top_n]
		df_full = pd.concat([df_full, df_timesep], axis=1)

	df_full.to_csv(output[:-4] + '_full.csv')

	print('Writing a Rankflow-proof csv to "' + output[:-4] + '_rankflow.csv"')
	df_rankflow = df_full
	#df_rankflow = df_rankflow.drop(df_rankflow.columns[0], axis=1)
	
	cols = df_rankflow.columns
	for index, col in enumerate(cols):
		#print(col)
		if 'tfidf' in col:
			li_scores = df_rankflow[col].tolist()
			vals = [int(tfidf * 100) for tfidf in li_scores]
			df_rankflow[col] = vals

	df_rankflow.to_csv(output[:-4] + '_rankflow.csv', encoding='utf-8', index=False)

	print('Done!')

if __name__ == '__main__':

	li_years = [1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018]
	
	#li_years = [[1995,1996,1997,1998,1999],[2000,2001,2002,2003,2004],[2005,2006,2007,2008,2009],[2010,2011,2012,2013,2014],[2015,2016,2017,2018]]
	
	filterword = getStem('moslim')
	tokens = getPolitiekTokens(years=li_years, contains_word=filterword)
	li_filenames = [str(year) for year in li_years]
	getTfidf(tokens, li_filenames,filterword, ngram_range=2)