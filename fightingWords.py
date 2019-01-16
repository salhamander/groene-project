import numpy as np
import pickle as p
import string
import itertools
from sklearn.feature_extraction.text import CountVectorizer as CV
exclude = set(string.punctuation)

def basic_sanitize(in_string):
	'''Returns a very roughly sanitized version of the input string.'''
	#return_string = ' '.join(in_string.encode('ascii', 'ignore').strip().split())
	#return_string = ''.join(ch for ch in return_string if ch not in exclude)
	#return_string = return_string.lower()
	#return_string = ' '.join(return_string.split())
	return ' '.join(in_string.lower().split())

def bayes_compare_language(l1, l2, ngram = 1, prior=.01, cv = None):
	'''
	Arguments:
	- l1, l2; a list of strings from each language sample
	- ngram; an int describing up to what n gram you want to consider (1 is unigrams,
	2 is bigrams + unigrams, etc). Ignored if a custom CountVectorizer is passed.
	- prior; either a float describing a uniform prior, or a vector describing a prior
	over vocabulary items. If you're using a predefined vocabulary, make sure to specify that
	when you make your CountVectorizer object.
	- cv; a sklearn.feature_extraction.text.CountVectorizer object, if desired.
	Returns:
	- A list of length |Vocab| where each entry is a (n-gram, zscore) tuple.'''
	if cv is None and type(prior) is not float:
		print("If using a non-uniform prior:")
		print("Please also pass a count vectorizer with the vocabulary parameter set.")
		quit()

	if isinstance(l1, str):
		l1 = [basic_sanitize(l) for l in l1]
	if isinstance(l2, str):
		l2 = [basic_sanitize(l) for l in l2]
	if cv is None:
		cv = CV(decode_error = 'ignore', min_df = 10, max_df = .5, ngram_range=(1,ngram),
				binary = False,
				max_features = 15000)
	counts_mat = cv.fit_transform(l1+l2).toarray()
	# Now sum over languages...
	vocab_size = len(cv.vocabulary_)
	print("Vocab size is {}".format(vocab_size))
	if type(prior) is float:
		priors = np.array([prior for i in range(vocab_size)])
	else:
		priors = prior
	z_scores = np.empty(priors.shape[0])
	count_matrix = np.empty([2, vocab_size], dtype=np.float32)
	count_matrix[0, :] = np.sum(counts_mat[:len(l1), :], axis = 0)
	count_matrix[1, :] = np.sum(counts_mat[len(l1):, :], axis = 0)
	a0 = np.sum(priors)
	n1 = 1.*np.sum(count_matrix[0,:])
	n2 = 1.*np.sum(count_matrix[1,:])
	print("Comparing language...")
	for i in range(vocab_size):
		#compute delta
		term1 = np.log((count_matrix[0,i] + priors[i])/(n1 + a0 - count_matrix[0,i] - priors[i]))
		term2 = np.log((count_matrix[1,i] + priors[i])/(n2 + a0 - count_matrix[1,i] - priors[i]))        
		delta = term1 - term2
		#compute variance on delta
		var = 1./(count_matrix[0,i] + priors[i]) + 1./(count_matrix[1,i] + priors[i])
		#store final score
		z_scores[i] = delta/np.sqrt(var)
	index_to_term = {v:k for k,v in cv.vocabulary_.items()}
	sorted_indices = np.argsort(z_scores)
	return_list = []
	for i in sorted_indices:
		return_list.append((index_to_term[i], z_scores[i]))
	return return_list

if __name__ == '__main__':
	# for spreekbeurt in inputtokens:
	# 		if any(i in querystring for i in spreekbeurt):
	# 			tokens.append(spreekbeurt)

	querystring = 'islam'

	li_years = [[1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006],[2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018]]
	tokens1 = []
	tokens2 = []
	for i, years in enumerate(li_years):
		for year in years:
			tokens = p.load(open('data/politiek/handelingen/tokens/tokens_handelingen_' + str(year) + str(year + 1) + '.p', 'rb'))
			if i == 0:
				tokens1.append(tokens)
			else:
				tokens2.append(tokens)

	# Filter out querystrings
	tokens1 = [token for token in tokens1 if querystring in token]
	tokens2 = [token for token in tokens2 if querystring in token]

	tokens = list(itertools.chain.from_iterable(tokens))
	tokens2 = list(itertools.chain.from_iterable(tokens2))
	
	fighting_words = bayes_compare_language(tokens, tokens2, ngram=2)
	print(fighting_words)