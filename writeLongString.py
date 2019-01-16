import pandas as pd
import pickle as p
import re

li_years = [1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018]

def writeLongString(df, querystring='', domain='undefined', text_col='tekst', date_col='datum', filter_newspaper='', timespan=False):
	''' Writes a long text file based on a df.
	Useful for Word Trees.
	Can also detect to donwload for a specific or ranges of date/year.'''

	filename = 'longstring_' + domain + '_'

	# Filter df on querystring
	if querystring != '':
		print('Filtering data on whether it contains "' + querystring + '"')
		df = df[df[text_col].str.contains(querystring, case=False, na=False)]
		filename = filename + '' + querystring

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
	df = pd.read_csv('data/politiek/handelingen/all-handelingen.csv')
	writeLongString(df, querystring='multiculturele', domain='politiek',text_col='tekst')