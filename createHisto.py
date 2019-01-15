import sys
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time
import re
import os
from datetime import date, datetime, timedelta
from collections import OrderedDict, Counter
from matplotlib.ticker import ScalarFormatter

li_handelingen_year = ['1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018']
di_spreekbeurten_year = {'1995': 15307, '1996': 29962, '1997': 35065, '1998': 31306, '1999': 27441, '2000': 30259, '2001': 28454, '2002': 27759, '2003': 27340, '2004': 26221, '2005': 29306, '2006': 26912, '2007': 30040, '2008': 39179, '2009': 29565, '2010': 30557, '2011': 56205, '2012': 58427, '2013': 70284, '2014': 67304, '2015': 71281, '2016': 76531, '2017': 60142, '2018': 83588}

def createHistogram(df, querystring='', time_format='years', domain='', show_kranten=False, show_partij=False, include_normalised=False):

	# Set some column headers
	if domain == 'kranten':
		time_col = 'date_formatted'
		text_col = 'full_text'
	elif domain == 'politiek':
		time_col = 'datum'
		text_col = 'tekst'

	# Domain (politcs, newspapers, tweets) needs to be set to asses the data
	if domain == '':
		print('Please provide a domain (politcs, newspapers, tweets). Current input: ', domain)
		quit()
	else:
		filename = domain

	if isinstance(querystring, list):
		querystring = '|'.join(querystring)
		filename = querystring.replace('|','OR')
		if show_partij != False:
			if isinstance(show_partij, int):
				filename = filename + '_top-' + str(show_partij) + '-partijen'
			else:
				filename = filename + show_partij
	else:
		filename = querystring

	# Filter the datasets on whether a specific words appears
	if querystring != '':
		print('Filtering data on whether it contains ' + filename)
		df = df.sort_values(by=[time_col])
		df = df[df[text_col].str.contains(querystring, case=False, na=False)]

	print('Setting time values correctly for the histogram')
	# Set cut-off for yyyy-mm-dd format to filter on month or day
	endstring = 10
	if time_format == 'years':
		endstring = 4
	elif time_format == 'months':
		endstring = 7
	elif time_format == 'days':
		endstring = 10

	li_dates = [date[0:endstring] for date in df[time_col]]
	li_timeticks = []

	dateformat = '%d-%m-%y'

	df_histo = pd.DataFrame()
	df['date_histo'] = li_dates
	df_dates = df.groupby(by=['date_histo']).agg(['count'])

	# Create new list of all dates between start and end date
	# Sometimes one date has zero counts, and gets skipped by matplotlib
	li_dates = []
	li_check_dates = []

	if time_format == 'years':
		d1 = datetime.strptime(df_dates.index[0], "%Y").date()  			# start date
		d2 = datetime.strptime(df_dates.index[len(df_dates) - 1], "%Y").date()	# end date
		delta = d2 - d1													# timedelta
		for i in range(delta.days + 1):
			date = d1 + timedelta(days=i)
			date = str(date)[:endstring]
			if date not in li_dates:
				li_dates.append(date)
				li_check_dates.append(date)

	elif time_format == 'months':
		d1 = datetime.strptime(df_dates.index[0], "%Y-%m").date()  			# start date
		d2 = datetime.strptime(df_dates.index[len(df_dates) - 1], "%Y-%m").date()	# end date
		delta = d2 - d1													# timedelta
		for i in range(delta.days + 1):
			date = d1 + timedelta(days=i)
			date = str(date)[:endstring]
			if date not in li_dates:
				li_dates.append(date)
				li_check_dates.append(date)
		
	if time_format == 'days':
		d1 = datetime.strptime(df_dates.index[0], "%Y-%m-%d").date()			# start date
		d2 = datetime.strptime(df_dates.index[len(df) - 1], "%Y-%m-%d").date()	# end date
		# print(d1, d2)
		delta = d2 - d1         												# timedelta
		for i in range(delta.days + 1):
			date_object = d1 + timedelta(days=i)
			str_date = date_object.strftime('%Y-%m-%d')
			li_dates.append(date_object)
			li_check_dates.append(str_date)

	# Create list of counts. 0 if it does not appears in previous DataFrame
	li_counts = [0 for i in range(len(li_dates))]
	li_index_dates = df_dates.index.values.tolist()
	for index, indate in enumerate(li_check_dates):
		# print(indate)
		if indate in li_index_dates and df_dates.loc[indate][1] > 0:
			li_counts[index] = df_dates.loc[indate][1]
		else:
			li_counts[index] = 0

	#print(li_index_dates)
	
	df_histo['date'] = li_dates
	df_histo['count'] = li_counts
	#print(li_counts)

	#create list of average counts
	if include_normalised:
		li_av_count = []
		for i in range(len(df_histo)):
			av_count = (df_histo['count'][i] / di_spreekbeurten_year[df_histo['date'][i]]) * 100
			li_av_count.append(av_count)

		df_histo['av_count'] = li_av_count

	if not os.path.exists('data/'):
		os.makedirs('data/')

	#print(df_histo.head())
	print('Writing raw data to "' + 'data/histogram_data_' + filename + '.csv')
	# Safe the metadata
	df_histo.to_csv('data/histogram_data_' + filename + '.csv', index=False)

	print('Making histogram...')

	# If indicated, show only some partijen as a stacked bar graph.
	if show_partij != False:
		li_formatted_partij = []
		if isinstance(show_partij, int):
			partij_count = Counter(df['partij'].tolist())
			li_common_partijen = [tpl[0] for tpl in partij_count.most_common(show_partij)]

		for key, row in df.iterrows():
			# If only one partij should be highlighted (str)
			if isinstance(show_partij, str):
				if show_partij.lower() == (row['partij'].lower()):
					li_formatted_partij.append(row['partij'])
				else:
					li_formatted_partij.append('overig')
			# If a range of partijen should be highlighted (list)
			elif isinstance(show_partij, list):
				if row['partij'] in show_partij:
					li_formatted_partij.append(row['partij'])
				else:
					li_formatted_partij.append('overig')
			# If only the top n partijen should be highlighted (int)
			elif isinstance(show_partij, int):
				if row['partij'] in li_common_partijen:
					if row['partij'] == 'geen':
						li_formatted_partij.append('kabinet')
					else:
						li_formatted_partij.append(row['partij'])
				else:
					li_formatted_partij.append('overig')
			else:
				print('Invalid show_partij: ' + str(show_partij))
				quit()

		df['partij'] = li_formatted_partij
		# print(set(li_formatted_partij))
		# print(df)
		# print(li_av_count)

		# Add a year column
		df['year'] = [date[:4] for date in df['datum'].values.tolist()]
		df = df.groupby(['partij','year']).size().reset_index()
		#df = df.set_index('year')
		df.columns = ['partij', 'year', 'size']

		df.to_csv('data/politiek/streamgraph-data-' + filename + '.csv')

		df = df.reset_index()
		df = df.pivot(index='year', columns='partij', values='size')

	# Indicate newspapers in stacked bar graph
	if show_kranten:
		df['year'] = [date[:4] for date in df[time_col].values.tolist()]
		df = df.groupby(['newspaper','year']).size().reset_index()
		#df = df.set_index('year')
		df.columns = ['newspaper', 'year', 'size']
		df.to_csv('data/politiek/streamgraph-data-' + filename + '.csv')
		df = df.reset_index()
		df = df.pivot(index='year', columns='newspaper', values='size')

	fig, ax = plt.subplots(1,1)
	fig = plt.figure(figsize=(12, 8))
	fig.set_dpi(100)
	ax = fig.add_subplot(111)
	
	if time_format == 'years':
		ax.xaxis.set_major_locator(matplotlib.dates.YearLocator())
		ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(dateformat))
	elif time_format == 'days':
		ax.xaxis.set_major_locator(matplotlib.dates.DayLocator())
		ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(dateformat))
	elif time_format == 'months':
		ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
		ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(dateformat))
	ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

	#colors = ["#478f79","#853bce","#7de354","#d245bc","#5eaa3b","#5858ce","#d5d840","#5b2575","#60db9e","#d73d77","#c3dd85","#bc72c8","#538746","#747ed0","#d88b2e","#343c6f","#d44530","#67d3d6","#8a2d49","#afd4b5","#3f1d2d","#d4b774","#639dd1","#968a2d","#d693bf","#3f4e1e","#bbc0e0","#793c20","#517988","#d68562","#283831","#d06f7b","#867758","#836079","#d9b9ac"]
	colors = ["#9a963f","#9968c9","#61ad4e","#c77f3a","#3fadaf"]

	if show_kranten != False or show_partij != False:
		df.plot(ax=ax, stacked=True, kind='bar', width=.9, figsize=(10,7), color=colors)
	
	if include_normalised:
		ax2 = ax.twinx()
		df_histo.plot(ax=ax2, y='av_count', legend=False, kind='line', linewidth=2, color='#d12d04');
	
	#df_histo.plot(ax=ax, stacked=True, y='partij', kind='bar', legend=False, width=.9, color='#52b6dd');
	#df_histo.plot(ax=ax2, y='av_count', legend=False, kind='line', linewidth=2, color='#d12d04');
	
	ax.set_axisbelow(True)
	# ax.set_xticks(xticks)
	ax.set_xticklabels(df_histo['date'], rotation='vertical')
	ax.grid(color='#e5e5e5',linestyle='dashed', linewidth=.6)
	ax.set_ylabel('Absoluut aantal', color=colors[0])
	
	if include_normalised:
		ax2.set_ylabel('% van totaal aantal spreekbeurten in TK', color='#d12d04')
		ax2.set_ylim(bottom=0)

	# Reduce tick labels when there's more a lot of day dates:
	if time_format == 'days' and len(set(li_dates)) > 50:
		for index, label in enumerate(ax.xaxis.get_ticklabels()):
			#print(label)
			if label.get_text().endswith('-01'):
				label.set_visible(True)
			else:
				label.set_visible(False)

	if time_format == 'months' and len(set(li_dates)) > 50:
		for index, label in enumerate(ax.xaxis.get_ticklabels()):
			#print(label)
			if label.get_text().endswith('-01'):
				label.set_visible(True)
			else:
				label.set_visible(False)

	if domain == 'politiek':
		histo_title = 'Aantal spreekbeurten in Tweede Kamer met "' + querystring.replace('|', '" of "') + '"'
	elif domain == 'kranten':
		histo_title = 'Aantal gearchiveerde artikelen in Nederlandse kranten met "' + querystring.replace('|', '" of "') + '"'
	plt.title(histo_title)

	print('Saving svg file as "img/histo/histogram_' + filename + '_' + time_format + '.svg"')
	plt.savefig('img/histo/histogram_' + filename + '_' + time_format + '.svg', dpi='figure',bbox_inches='tight')
	print('Saving png file as "img/histo/histogram_' + filename + '.png"')
	plt.savefig('img/histo/histogram_' + filename + '_' + time_format + '.png', dpi='figure',bbox_inches='tight')

	print('Done! Saved .csv of data and .png & .svg in folder \'img/\'')

def getSpreekbeurtCount():
	''' Returns a dict with the amount of spreekbeurten per year '''
	di_spreekbeurten = {}
	df = pd.read_csv('data/politiek/handelingen/all-handelingen.csv')
	for year in li_handelingen_year:
		df_year = df[df['datum'].str.contains(year)]
		#print(year, len(df_year))
		di_spreekbeurten[year] = len(df_year)
	return di_spreekbeurten

if __name__ == '__main__':
	
	# di_spreekbeurten = getSpreekbeurtCount()
	# print(di_spreekbeurten)
	# quit()
	df = pd.read_csv('data/media/kranten/all-islam-moslim-moslims-atleast5.csv')
	#df = df[df['tekst'].str.contains('islam', na=False, case=False)]

	#querystrings = [['nederlandse identiteit','nederlandse waarden'], 'gewone nederlander']
	#for querystring in querystrings:
	createHistogram(df, querystring=['moslim','islam'], time_format='years', domain='kranten', show_kranten=True)