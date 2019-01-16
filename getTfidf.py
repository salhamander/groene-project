import sys
import os
import pandas as pd
import pickle as p
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def no_tokenizer(doc):
	return doc

def getTfidf(li_tokens, li_filenames, filename, min_df=0, max_df=0, top_n=25):
	"""
	Creates a csv with the top n highest scoring tf-idf words.

	:param input,		list of tokens. Should be unpickled first
	:param filename,	the name of the output folder, based on the input
	:param max_df,		sklearn TfidfVectorizer function to filter words that appear in all token lists
	:

	"""

	# Create an output folder if it doesn't exist yet
	if not os.path.exists('output/'):
		os.makedirs('output/')
	if not os.path.exists('output/tfidf/'):
		os.makedirs('output/tfidf/')
	if min_df == 0:
		min_df = len(li_tokens)
	else:
		min_df = len(li_tokens) - min_df
		print('Terms must appear in at least ' + str(min_df) + ' of the total ' + str(len(li_tokens)) + ' files.')
	if max_df == 0:
		max_df = len(li_tokens)
	else:
		max_df = len(li_tokens) - max_df
		print('Terms may not appear in ' + str(max_df) + ' of the total ' + str(len(li_tokens)) + ' files.')

	output = 'output/tfidf/' + filename + '_tfidf.csv'

	print('Vectorizing!')
	tfidf_vectorizer = TfidfVectorizer(min_df=min_df, max_df=max_df, analyzer='word', token_pattern=None, tokenizer=lambda i:i, lowercase=False)
	tfidf_matrix = tfidf_vectorizer.fit_transform(li_tokens)
	#print(tfidf_matrix[:10])

	feature_array = np.array(tfidf_vectorizer.get_feature_names())
	tfidf_sorting = np.argsort(tfidf_matrix.toarray()).flatten()[::-1]
	
	# Print and store top n highest scoring tf-idf scores
	top_words = feature_array[tfidf_sorting][:top_n]
	#print(top_words)

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

# show manual if needed
if __name__ == '__main__':
	getTfidf(li_tokens, li_filenames, filename, min_df=min_df, max_df=max_df, top_n=top)