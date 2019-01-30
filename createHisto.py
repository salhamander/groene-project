import sys
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time
import re
import os
import pickle as p
from collections import OrderedDict, Counter
from matplotlib.ticker import ScalarFormatter, FormatStrFormatter
from helpers import *

# First, load some counts for calculating the averages in datasets
li_handelingen_year = p.load(open('data/li_handelingen_year.p', 'rb'))
di_spreekbeurten_year = p.load(open('data/di_spreekbeurten_year.p', 'rb'))
di_spreekbeurten_month = p.load(open('data/di_spreekbeurten_month.p', 'rb'))
di_tv_counts = p.load(open('data/di_tv_counts.p', 'rb'))
di_fb_months = p.load(open('data/di_fb_months.p', 'rb'))


def createHistogram(querystring='', domain='', file='', show_kranten=False, show_partij=False, program='all', include_normalised=False, normalise_fb=True, time_format='years', normalise_filecount=False):
	''' Creates frequency histograms from a range of different csvs:
	Politiek, Kranten, TV, Facebook, Twitter.
	Can make stacked bar charts and a normalised line.
	Works but should be cleaned up later :) '''

	# Domain (politics, newspapers, tweets) needs to be set to asses the data.
	# Use this to read specified csvs and set some column headers.
	filename = domain + '-'
	if domain.startswith('krant') or domain.startswith('newspaper'):
		df = pd.read_csv('data/media/kranten/' + file)
		time_col = 'date_formatted'
		text_col = 'full_text'
	elif domain == 'politiek':
		df = pd.read_csv('data/politiek/handelingen/all-handelingen-no-voorzitter.csv')
		time_col = 'datum'
		text_col = 'tekst'
	elif domain == 'facebook' or domain == 'fb':
		time_col = 'comment_published'
		text_col = 'comment_message'
	elif domain.startswith('tele'):
		time_col = 'datestamp'
		text_col = 'text'

		# Load program text file if string, concatenate if it's all or a list
		if program == 'all':
			df = pd.read_csv('data/media/televisie/all-transcripts.csv')
		elif isinstance(program, str):
			df = pd.read_csv('data/media/televisie/transcripts/TV_full_' + program  + '.csv')
		elif isinstance(program, list):
			li_dfs = []
			for single_program in program:
				df_program = pd.read_csv('data/media/televisie/transcripts/TV_full_' + program + '.csv')
				li_dfs.append(df_program)
			df = pd.concat(li_dfs, axis=0)

		# Convert dd-mm-yyyy format to yyyy-mm-dd if needed
		if (df[time_col].tolist())[1][2] == '-':
			df[time_col] = [time[6:] + '-' + time[3:6:] + '-' + time[:3] for time in df[time_col].tolist()]
	else:
		print('Please provide a correct domain (politiek, kranten, facebook, twitter). Current input: ', domain)
		quit()

	if isinstance(querystring, list):
		querystring = '|'.join(querystring)
		filename = filename + '-' + querystring.replace('|','OR')
		if show_partij != False:
			if isinstance(show_partij, int):
				filename = filename + '_top-' + str(show_partij) + '-partijen'
			else:
				filename = filename + show_partij
	else:
		filename = filename + querystring

	# Filter on text
	print('Filtering data: ' + filename)
	if domain == 'facebook':
		df = getFbDf(querystring)
	else:
		if normalise_filecount:
			df_full = df
		df = df[df[text_col].str.contains(querystring, case=False, na=False)]
	df = df.sort_values(by=[time_col])

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
	# Necessary since sometimes one date has zero counts, and gets skipped by matplotlib
	startdate = df_dates.index[0]
	enddate = df_dates.index[len(df_dates) - 1]
	li_dates = getDateRange(startdate, enddate, time_format=time_format)

	# Create list of counts. 0 if it does not appears in previous DataFrame
	li_counts = [0 for i in range(len(li_dates))]
	li_index_dates = df_dates.index.values.tolist()
	for index, indate in enumerate(li_dates):
		# print(indate)
		if indate in li_index_dates and df_dates.loc[indate][1] > 0:
			li_counts[index] = df_dates.loc[indate][1]
		else:
			li_counts[index] = 0

	#print(li_index_dates)
	
	df_histo['date'] = li_dates
	df_histo['count'] = li_counts
	print(li_dates)

	#create list of average counts
	if include_normalised:
		if domain == 'politiek':
			if time_format == 'years':
				di_av_counts = di_spreekbeurten_year
			elif time_format == 'months':
				di_av_counts = di_spreekbeurten_month
		elif domain == 'televisie':
			di_av_counts = di_tv_counts

		li_av_count = []
		for i in range(len(df_histo)):
			av_count = (df_histo['count'][i] / di_av_counts[df_histo['date'][i]]) * 100
			li_av_count.append(av_count)

		df_histo['av_count'] = li_av_count

	# Make a colunn with 
	if normalise_filecount and domain == 'kranten':
		li_av_count = []
		# Divide the counts of the subquery with those of the original file
		for i, date in enumerate(li_dates):
			av_count = (df_histo['count'][i] / len(df_full[df_full[time_col].str.contains(date, case=False, na=False)])) * 100
			li_av_count.append(av_count)
		df_histo['av_count'] = li_av_count
		print(li_av_count)

	# If indicated, show only some partijen as a stacked bar graph.
	if domain == 'politiek':
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

		# Add a year column
		df['date'] = [date[:endstring] for date in df['datum'].values.tolist()]
		df = df.groupby(['partij','date']).size().reset_index()
		df.columns = ['partij', 'date', 'size']

		df.to_csv('data/politiek/streamgraph-data-' + filename + '-' + time_format + '.csv')

		df = df.reset_index()
		df = df.pivot(index='date', columns='partij', values='size')

	# Indicate newspapers in stacked bar graph
	if show_kranten:
		df['time'] = [date[:endstring] for date in df[time_col].values.tolist()]
		df = df.groupby(['newspaper','time']).size().reset_index()
		#df = df.set_index('time')
		df.columns = ['newspaper', 'time', 'size']
		df.to_csv('data/politiek/streamgraph-data-' + filename + '.csv')
		df = df.reset_index()
		df = df.pivot(index='time', columns='newspaper', values='size')

	if domain == 'facebook':
		df['time'] = [date[:endstring] for date in df[time_col].values.tolist()]
		df = df.groupby(['page_name','time']).size().reset_index()
		df.columns = ['page_name','time','size']

		# Divide the values by the total amount of FB posts captured from the page that year
		if normalise_fb:
			#print(df['page_name'][i],[df.index[i]])
			li_av_size = []
			for i, row in df.iterrows():
				#print(float(row['size']) / float(di_fb_months[row['page_name']][row['time']]) * 100.0)
				li_av_size.append(float(row['size']) / float(di_fb_months[row['page_name']][row['time']]) * 100.0)
				print(float(row['size']), float(di_fb_months[row['page_name']][row['time']]))
			df['size'] = li_av_size
			print(df['size'])

		df = df.set_index('time')
		df.to_csv('data/politiek/streamgraph-data-' + filename + '.csv')
		df = df.reset_index()
		df = df.pivot(index='time', columns='page_name', values='size')

	if domain == 'televisie':
		if time_format == 'months' or time_format == 'days':
			df = df_histo
			df = df.set_index('date')
		else:
			df['time'] = [date[:endstring] for date in df[time_col].values.tolist()]
			df = df.groupby(['time']).size().reset_index()
			df = df.set_index('time')
			df.columns = ['size']
			df.to_csv('data/media/televisie/streamgraph-data-' + filename + '.csv')
			df = df.reset_index()
			print(df.columns)
			df = df.pivot(index='time', columns='program', values='size')

	# Check if there's no dates with zero occurances missing
	# If that's the case, append a row with zeroes and the
	# missing date as the index. (bit hacky for now, but works)
	for single_date in li_dates:
		if single_date not in df.index:
			df.loc[single_date] = [None] * len(df.columns)

	df = df.sort_index()

	# Save the metadata
	print('Writing raw data to "' + 'data/histogram-' + filename + '.csv')
	df.to_csv('data/histograms/histogram-' + filename + '.csv', index=False)
	print('Making histogram...')

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

	colors = ["#478f79","#853bce","#7de354","#d245bc","#5eaa3b","#5858ce","#d5d840","#5b2575","#60db9e","#d73d77","#c3dd85","#bc72c8","#538746","#747ed0","#d88b2e","#343c6f","#d44530","#67d3d6","#8a2d49","#afd4b5","#3f1d2d","#d4b774","#639dd1","#968a2d","#d693bf","#3f4e1e","#bbc0e0","#793c20","#517988","#d68562","#283831","#d06f7b","#867758","#836079","#d9b9ac"]
	#colors = ["#9a963f","#9968c9","#61ad4e","#c77f3a","#3fadaf"]

	if show_kranten != False or show_partij != False or domain == 'facebook':
		df.plot(ax=ax, stacked=True, kind='bar', width=.9, figsize=(10,7), color=colors)
	else:
		df.plot(ax=ax, y='count', kind='bar', width=.9, figsize=(10,7), color=colors[0])

	if include_normalised or normalise_filecount:
		ax2 = ax.twinx()
		df_histo.plot(ax=ax2, y='av_count', legend=False, kind='line', linewidth=2, color='#d12d04');
	#df_histo.plot(ax=ax, stacked=True, y='partij', kind='bar', legend=False, width=.9, color='#52b6dd');
	#df_histo.plot(ax=ax2, y='av_count', legend=False, kind='line', linewidth=2, color='#d12d04');
	
	ax.set_axisbelow(True)
	#ax.set_xticks(li_dates)
	ax.set_xticklabels(df.index, rotation='vertical')
	ax.grid(color='#e5e5e5',linestyle='dashed', linewidth=.6)
	ax.set_ylabel('Absoluut aantal', color=colors[0])
	
	# Do dome formatting if there's normalised data
	if domain == 'facebook' and normalise_fb:
		ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
		ax.set_ylabel('Percentage van totaal', color=colors[0])
		filename = filename + '-normalised'
	if  domain == 'kranten' and normalise_filecount:
		filename = filename + '-normalised'
	if include_normalised or normalise_filecount:
		if domain == 'politiek':
			ylabel = '% van totaal aantal spreekbeurten in TK'
		elif domain == 'televisie':
			ylabel = '% van totaal aantal verzamelde uitzendingen'
		elif domain == 'kranten':
			ylabel = '% van totaal aantal gearchiveerde krantenartikelen met \'islam\' of \'moslim\''
		ax2.set_ylabel(ylabel, color='#d12d04')
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
			if label.get_text().endswith('-01') or label.get_text().endswith('-07'):
				label.set_visible(True)
			else:
				label.set_visible(False)

	if domain == 'politiek':
		histo_title = 'Aantal spreekbeurten in Tweede Kamer met "' + querystring.replace('|', '" of "') + '"'
	elif domain.startswith('krant'):
		histo_title = 'Aantal gearchiveerde artikelen in Nederlandse kranten met "' + querystring.replace('|', '" of "') + '"'
	elif domain == 'facebook':
		if normalise_fb:
			histo_title = 'Genormaliseerd aantal comments op de Facebook pagina\'s van Nederlandse actualiteitenprogramma\'s met "' + querystring.replace('|', '" of "') + '"'
		else:
			histo_title = 'Aantal comments op de Facebook pagina\'s van Nederlandse actualiteitenprogramma\'s met "' + querystring.replace('|', '" of "') + '"'
	elif domain == 'televisie':
		if isinstance(program, list):
			program = ', '.join(program)
		elif program == 'all':
			program = 'Nieuwsuur, Brandpunt en EenVandaag'
		histo_title = 'Aantal ' + program + ' uitzendingen met "' + querystring.replace('|', '" of "') + '"'		
	plt.title(histo_title)

	print('Saving svg file as "img/histo/histogram_' + filename + '_' + time_format + '.svg"')
	plt.savefig('img/histo/histogram_' + filename + '_' + time_format + '.svg', dpi='figure',bbox_inches='tight')
	print('Saving png file as "img/histo/histogram_' + filename + '.png"')
	plt.savefig('img/histo/histogram_' + filename + '_' + time_format + '.png', dpi='figure',bbox_inches='tight')

	print('Done! Saved .csv of data and .png & .svg in folder \'img/\'')

def createHorizontalHisto(li_values, li_counts, histo_title='Veelvoorkomende woordcombinaties', file_name=''):
	''' Creates a horizontal histogram with counts of values.
	Requires a list of values and a list of counts. '''

	fig, ax = plt.subplots(1,1)
	fig = plt.figure(figsize=(12, 8))
	fig.set_dpi(100)
	ax = fig.add_subplot(111)

	rects = ax.barh(li_values, li_counts, align='center', color='green')
	ax.set_yticks(li_values)
	ax.invert_yaxis()
	ax.set_xlabel('Aantal')
	ax.set_title(histo_title)

	rect_labels = []
	# Write in the ranking inside each bar
	for i, rect in enumerate(rects):
		width = rect.get_width()
		labels = li_values[i] + ' (' + str(li_counts[i]) + ')'

		# The bars aren't wide enough to print the ranking inside
		if width < 0:
			# Shift the text to the right side of the right edge
			xloc = width + 0.5
			clr = 'black'
			align = 'left'
		else:
			# Shift the text to the left side of the right edge
			xloc = 0.98 * width
			clr = 'white'
			align = 'right'

		# Center the text vertically in the bar
		yloc = rect.get_y() + rect.get_height()/2.0
		label = ax.text(xloc, yloc, labels, horizontalalignment=align,
						verticalalignment='center', color=clr,
						clip_on=True)
		rect_labels.append(label)

	# Hide y axis labels
	ax.get_yaxis().set_visible(False)

	print('Saving svg file as "img/histo/histogram_' + file_name + '.svg"')
	plt.savefig('img/histo/histogram_' + file_name + '.svg', dpi='figure',bbox_inches='tight')
	print('Saving png file as "img/histo/histogram_' + file_name + '.png"')
	plt.savefig('img/histo/histogram_' + file_name + '.png', dpi='figure',bbox_inches='tight')

	print('Done! Saved .csv of data and .png & .svg in folder \'img/\'')

def createCollectiveHisto(querystring, file_kranten='', file_twitter='', time_format='years'):
	''' Creates a multiple line plot of all the media data '''

	# Have different slices of yyyy-mm-dd dates depending on time format
	endstring = 10
	if time_format == 'years':
		endstring = 4
	elif time_format == 'months':
		endstring = 7
	elif time_format == 'days':
		endstring = 10

	# Load political data
	print('Grouping political data')
	df_politiek = pd.read_csv('data/politiek/handelingen/all-handelingen-no-voorzitter.csv')
	df_politiek = df_politiek[df_politiek['tekst'].str.contains(querystring, case=False, na=False)]
	df_politiek['date_col'] = [date[:endstring] for date in df_politiek['datum'].tolist()]
	df_politiek = df_politiek.groupby(['date_col']).count()
	df_politiek = df_politiek.rename(columns={'tekst':'politiek'})
	df_politiek = df_politiek[['politiek']]

	# Load TV data (incomplete)
	# print('Grouping TV data')
	# df_tv = pd.read_csv('data/media/televisie/all-transcripts.csv')
	# df_tv = df_tv[df_tv['text'].str.contains(querystring, case=False, na=False)]
	# if (df_tv['datestamp'].tolist())[1][2] == '-':
	# 	df_tv['datestamp'] = [time[6:] + '-' + time[3:6:] + '-' + time[:3] for time in df_tv['datestamp'].tolist()]
	# df_tv['date_col'] = [date[:endstring] for date in df_tv['datestamp'].tolist()]
	# df_tv = df_tv.groupby(['date_col']).count()
	# df_tv = df_tv.rename(columns={'text':'TV'})
	# df_tv = df_tv[['TV']]

	#print(df_tv.head())

	# Load kranten data
	print('Grouping newspaper data')
	df_krant = pd.read_csv('data/media/kranten/' + file_kranten)
	#only volkskrant & nrc
	df_krant = df_krant[df_krant['newspaper'].str.contains('volkskrant|nrc', case=False, na=False)]
	df_krant = df_krant[df_krant['full_text'].str.contains(querystring, case=False, na=False)]
	df_krant['date_col'] = [date[:endstring] for date in df_krant['date_formatted'].tolist()]
	df_krant = df_krant.groupby(['date_col']).count()
	df_krant = df_krant.rename(columns={'full_text':'krant'})
	df_krant = df_krant[['krant']]

	# Load Facebook data
	#print('Grouping Facebook data')
	#df_fb = getFbDf(querystring)
	#print(df_fb.head())
	#df_fb['date_col'] = [date[:endstring] for date in df_fb['comment_published'].tolist()]
	#df_fb = df_fb.groupby(['date_col']).count()
	#df_fb = df_fb.rename(columns={'comment_published':'Facebook'})
	#df_fb = df_fb[['Facebook']]

	df = pd.concat([df_krant,df_politiek], axis=1)
	df = df.drop(['2019'])
	df['politiek'] = df['politiek'].fillna(0)
	print(df)
	xtick_labels = df.index.values

	print('Grouping Twitter data')
	df_twitter = pd.read_csv('data/social_media/twitter/' + file_twitter)
	df_twitter['date_col'] = [date[:endstring] for date in df_twitter['created_at'].tolist()]
	df_twitter = df_twitter.groupby(['date_col']).count()
	df_twitter = df_twitter.rename(columns={'created_at':'Twitter'})
	df_twitter = df_twitter[['Twitter']]
	for date in df.index.values:
		if date not in df_twitter.index:
			df_twitter.loc[date] = [None] * len(df_twitter.columns)
	# 2013 is not complete
	df_twitter.at['2013','Twitter'] = None
	df_twitter = df_twitter.sort_index()
	print(df_twitter)

	df = df.reset_index()
	#li_dates = getDateRange(startdate, enddate, time_format)

	fig, ax = plt.subplots(1,1)
	fig = plt.figure(figsize=(12, 8))
	fig.set_dpi(100)
	ax = fig.add_subplot(111)
	ax.set_xticklabels(xtick_labels, rotation='vertical')

	df.plot(ax=ax, kind='line', xticks=df.index.values, figsize=(10,7), color='red')

	ax2 = ax.twinx()
	df_twitter.plot(ax=ax2, legend=False, kind='line', color='#1da1f2')
	ax.grid(color='#e5e5e5',linestyle='dashed', linewidth=.6)
	ax.set_ylim(bottom=0)
	ax2.set_ylim(bottom=0)
	ax.set_xticklabels(xtick_labels, rotation='vertical')

	#ax.xticks(df.index.values)
	#ax.set_xticklabels(df.index.values, rotation='vertical')
	#ax.grid(color='#e5e5e5',linestyle='dashed', linewidth=.6)
	#ax.set_ylabel('Absoluut aantal')
	
	plt.show()
	quit()

if __name__ == '__main__':

	#createCollectiveHisto('racisme', file_kranten='all-racisme-racistisch-racist-withtokens-deduplicated.csv', file_twitter='tcat_racism-20131119-20181220-racisme-nl.csv')
	#createHistogram(querystring=['zwarte piet'], domain='kranten', file='all-racisme-racistisch-racist-withtokens-deduplicated.csv', time_format='years', show_kranten=True, normalise_filecount=True)
	createHistogram(querystring=[''], domain='politiek', time_format='years', show_partij=8)
