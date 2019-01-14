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

def createHistogram(df, querystring='', time_column='datum', time_format='years', include_normalised=False):

	querystring = querystring.replace('|', ' OR ')

	df = df.sort_values(by=[time_column])

	# Set cut-off for yyyy-mm-dd format to filter on month or day
	endstring = 10
	if time_format == 'years':
		endstring = 4
	elif time_format == 'months':
		endstring = 7
	elif time_format == 'days':
		endstring = 10

	li_dates = [date[0:endstring] for date in df[time_column]]
	li_timeticks = []

	dateformat = '%d-%m-%y'

	df_histo = pd.DataFrame()
	df['date_histo'] = li_dates
	df = df.groupby(by=['date_histo']).agg(['count'])

	# Create new list of all dates between start and end date
	# Sometimes one date has zero counts, and gets skipped by matplotlib
	li_dates = []
	li_check_dates = []

	if time_format == 'years':
		d1 = datetime.strptime(df.index[0], "%Y").date()  			# start date
		d2 = datetime.strptime(df.index[len(df) - 1], "%Y").date()	# end date
		delta = d2 - d1													# timedelta
		for i in range(delta.days + 1):
			date = d1 + timedelta(days=i)
			date = str(date)[:endstring]
			if date not in li_dates:
				li_dates.append(date)
				li_check_dates.append(date)

	elif time_format == 'months':
		d1 = datetime.strptime(df.index[0], "%Y-%m").date()  			# start date
		d2 = datetime.strptime(df.index[len(df) - 1], "%Y-%m").date()	# end date
		delta = d2 - d1													# timedelta
		for i in range(delta.days + 1):
			date = d1 + timedelta(days=i)
			date = str(date)[:endstring]
			if date not in li_dates:
				li_dates.append(date)
				li_check_dates.append(date)
		
	if time_format == 'days':
		d1 = datetime.strptime(df.index[0], "%Y-%m-%d").date()			# start date
		d2 = datetime.strptime(df.index[len(df) - 1], "%Y-%m-%d").date()# end date
		# print(d1, d2)
		delta = d2 - d1         										# timedelta
		for i in range(delta.days + 1):
			date_object = d1 + timedelta(days=i)
			str_date = date_object.strftime('%Y-%m-%d')
			li_dates.append(date_object)
			li_check_dates.append(str_date)

	# Create list of counts. 0 if it does not appears in previous DataFrame
	li_counts = [0 for i in range(len(li_dates))]
	li_index_dates = df.index.values.tolist()
	for index, indate in enumerate(li_check_dates):
		# print(indate)
		if indate in li_index_dates and df.loc[indate][1] > 0:
			li_counts[index] = df.loc[indate][1]
		else:
			li_counts[index] = 0

	print(li_index_dates)
	
	df_histo['date'] = li_dates
	df_histo['count'] = li_counts

	#create list of average counts
	if include_normalised:
		li_av_count = []
		for i in range(len(df_histo)):
			av_count = (df_histo['count'][i] / di_spreekbeurten_year[df_histo['date'][i]]) * 100
			li_av_count.append(av_count)

		df_histo['av_count'] = li_av_count

	if not os.path.exists('data/'):
		os.makedirs('data/')

	print(df_histo.head())
	print('Writing raw data to "' + 'data/histogram_data_' + querystring + '.csv')
	# Safe the metadata
	df_histo.to_csv('data/histogram_data_' + querystring + '.csv', index=False)

	print('Making histogram...')

	quit()
	#df_stack = df_stack[['year', 'partij']]
	pivot_df = df_stack.pivot(index='year', columns='partij', values='Value')

	#Note: .loc[:,['Jan','Feb', 'Mar']] is used here to rearrange the layer ordering
	pivot_df.plot.bar(stacked=True, figsize=(10,7))
	plt.show()
	quit()

	# Plot the graph!
	fig, ax = plt.subplots(1,1)
	fig = plt.figure(figsize=(12, 8))
	fig.set_dpi(100)
	ax = fig.add_subplot(111)

	ax2 = ax.twinx()
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
	
	df_histo.plot(ax=ax, stacked=True, y='partij', kind='bar', legend=False, width=.9, color='#52b6dd');
	df_histo.plot(ax=ax2, y='av_count', legend=False, kind='line', linewidth=2, color='#d12d04');
	ax.set_axisbelow(True)
	# ax.set_xticks(xticks)
	ax.set_xticklabels(df_histo['date'], rotation='vertical')
	ax.grid(color='#e5e5e5',linestyle='dashed', linewidth=.6)
	ax.set_ylabel('Absoluut aantal', color='#52b6dd')
	ax2.set_ylabel('Percentage van totale spreekbeurten', color='#d12d04')
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

	# Reduce tick labels when there's more a lot of day dates:
	# if time_format == 'years' and len(set(li_dates)) > 50:
	# 	for index, label in enumerate(ax.xaxis.get_ticklabels()):
	# 		#print(label)
	# 		if label.get_text().endswith('-01'):
	# 			label.set_visible(True)
	# 		else:
	# 			label.set_visible(False)

	plt.title('Aantal spreekbeurten in Tweede Kamer met de woorden: "' + querystring + '"')

	print('Saving svg file as "img/histogram_' + querystring + '_' + time_format + '.svg"')
	plt.savefig('img/histogram_' + querystring + '_' + time_format + '.svg', dpi='figure',bbox_inches='tight')
	print('Saving png file as "img/histogram_' + querystring + '.png"')
	plt.savefig('img/histogram_' + querystring + '_' + time_format + '.png', dpi='figure',bbox_inches='tight')

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
	df = pd.read_csv('data/politiek/handelingen/all-handelingen-no-voorzitter.csv')
	df = df[df['tekst'].str.contains('crisis', na=False, case=False)]
	print('Mentions: ', len(df))

	print(df.head())

	# Rename parties that appear only < 10 times a year to 'anders'
	partij_count = Counter(df['partij'].tolist())
	li_formatted_partij = []
	for key, row in df.iterrows():
		if partij_count[row['partij']] < 500:
			li_formatted_partij.append('anders')
		else:
			if row['partij'] == 'geen':
				li_formatted_partij.append('kabinet')
			else:
				li_formatted_partij.append(row['partij'])
	print(set(li_formatted_partij))
	df['partij'] = li_formatted_partij
	
	# Add a year column
	df['year'] = [date[:4] for date in df['datum'].values.tolist()]
	df = df.groupby(['partij','year']).size().reset_index()
	#df = df.set_index('year')
	df.columns = ['partij', 'year', 'size']

	# li_formatted_partij = []
	# print(set(df['partij'].tolist()))
	# for key, row in df.iterrows():
	# 	if row['size'] < 10:
	# 		li_formatted_partij.append('anders')
	# 	else:
	# 		if row['partij'] == 'geen':
	# 			li_formatted_partij.append('kabinet')
	# 		else:
	# 			li_formatted_partij.append(row['partij'])
	# print(set(li_formatted_partij))
	# df['partij'] = li_formatted_partij

	print(df)
	df.to_csv('streamgraph-test.csv')
	df = df.reset_index()
	df_pivot = df.pivot(index='year', columns='partij', values='size')
	colors = ["#478f79","#853bce","#7de354","#d245bc","#5eaa3b","#5858ce","#d5d840","#5b2575","#60db9e","#d73d77","#c3dd85","#bc72c8","#538746","#747ed0","#d88b2e","#343c6f","#d44530","#67d3d6","#8a2d49","#afd4b5","#3f1d2d","#d4b774","#639dd1","#968a2d","#d693bf","#3f4e1e","#bbc0e0","#793c20","#517988","#d68562","#283831","#d06f7b","#867758","#836079","#d9b9ac"]
	df_pivot.plot.bar(stacked=True, figsize=(10,7), colors=colors)
	plt.show()
	quit()
	createHistogram(df, querystring='crisis', time_column='datum', time_format='years', include_normalised=True)