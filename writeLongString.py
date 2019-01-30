import pandas as pd
import pickle as p
import re
from helpers import getFbDf

li_years = [1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018]

def writeLongString(querystring='', domain='', file='', text_col='tekst', date_col='datum', filter_newspaper='', timespan=False):
	''' Writes a long text file based on a df.
	Useful for Word Trees.
	Can also detect to donwload for a specific or ranges of date/year.'''

	filename = 'longstring_' + domain + '_'

	# Kranten
	if domain == 'kranten':
		if file == '':
			print('Please specify a specific file for newspaper data with `file`')
			quit()
		else:
			df = pd.read_csv('data/media/kranten/' + file)
		text_col = 'full_tekst'
		date_col = 'date_formatted'
	# Politiek
	elif domain == 'politiek':
		df = pd.read_csv('data/politiek/handelingen/all-handelingen-no-voorzitter.csv')
		text_col = 'tekst'
		date_col = 'datum'
	# Facebook
	elif domain == 'facebook':
		df = getFbDf(querystring=querystring)
		text_col = 'comment_message'
		date_col = 'comment_published'
	elif domain == 'twitter':
		if file == '':
			print('Please specify a specific file for newspaper data with `file`')
			quit()
		else:
			df = pd.read_csv('data/social_media/twitter/' +file)
			text_col = 'text'
	else:
		print('Please specify a domain! (kranten, politiek, facebook, twitter)')
		quit()

	# Filter df on querystring
	if querystring != '':
		if isinstance(querystring, list):
			querystring = '|'.join(querystring)
		print('Filtering data on whether it contains "' + querystring + '"')
		df = df[df[text_col].str.contains(querystring, case=False, na=False)]
		filename = filename + '' + querystring.replace('|','OR')

	# Filter df on newspaper (if applicable)
	if filter_newspaper != '':
		print('Filtering newspaper on "' + filter_newspaper + '"')
		df = df[df['newspaper'].str.contains(filter_newspaper, case=False, na=False)]
		filename = filename + '' + filter_newspaper

	# Filter df on timespan
	if timespan != False:
		print('Filtering data on time')
		if isinstance(timespan, int):
			df = df[df[date_col].str.contains(str(timespan))]
			filename = filename + '-' + str(timespan)
		elif isinstance(timespan, list):
			timespans = '|'.join(timespan)
			df = df[df[date_col].str.contains(str(timespans))]
			filename = filename + '-' + timespans.replace('|','-')

	txtfile_full = open('data/longstrings/' + filename + '.txt', 'w', encoding='utf-8')
	li_input = df[text_col].tolist()

	# Work with a list of list if it's kranten
	if domain == 'kranten':
		raw_text = []
		for single_text in li_input:
			single_text = re.split('\"\, \'|\'\, \'|\"\, \"|\'\, \"', single_text)
			single_text = '\n'.join(single_text)
			single_text = single_text.replace('[\'','')
			raw_text.append(single_text)
		li_input = raw_text

	for item in li_input:
		if item != 'nan':
			item = str(item).lower()
			txtfile_full.write('%s' % item)

	print('Done! Written text file: data/longstrings/' + filename + '.txt')

if __name__ == '__main__':
	
	writeLongString(querystring=['racist'], domain='facebook')