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
from helpers import getFbDf

# Some counts for calculating the averages in parliamentary data per year and months
li_handelingen_year = ['1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018']
di_spreekbeurten_year = {'1995': 15307, '1996': 29962, '1997': 35065, '1998': 31306, '1999': 27441, '2000': 30259, '2001': 28454, '2002': 27759, '2003': 27340, '2004': 26221, '2005': 29306, '2006': 26912, '2007': 30040, '2008': 39179, '2009': 29565, '2010': 30557, '2011': 56205, '2012': 58427, '2013': 70284, '2014': 67304, '2015': 71281, '2016': 76531, '2017': 60142, '2018': 83588}
di_spreekbeurten_month = {'1995-09':2099,'1995-10':4559,'1995-11':6167,'1995-12':2482,'1996-01':2039,'1996-02':2180,'1996-03':2422,'1996-04':2688,'1996-05':3429,'1996-06':3598,'1996-07':0,'1996-08':530,'1996-09':1953,'1996-10':7198,'1996-11':3925,'1996-12':0,'1997-01':0,'1997-02':912,'1997-03':2210,'1997-04':2987,'1997-05':3713,'1997-06':5283,'1997-07':0,'1997-08':1326,'1997-09':4483,'1997-10':5093,'1997-11':4805,'1997-12':4253,'1998-01':2985,'1998-02':3514,'1998-03':3377,'1998-04':2773,'1998-05':484,'1998-06':1730,'1998-07':0,'1998-08':939,'1998-09':2263,'1998-10':3757,'1998-11':5886,'1998-12':3598,'1999-01':1663,'1999-02':1064,'1999-03':2881,'1999-04':2565,'1999-05':1509,'1999-06':3669,'1999-07':119,'1999-08':179,'1999-09':3469,'1999-10':2997,'1999-11':4380,'1999-12':2946,'2000-01':2378,'2000-02':2678,'2000-03':2449,'2000-04':1505,'2000-05':2089,'2000-06':3650,'2000-07':0,'2000-08':858,'2000-09':3298,'2000-10':3350,'2000-11':6371,'2000-12':1633,'2001-01':2408,'2001-02':2222,'2001-03':1579,'2001-04':2436,'2001-05':1872,'2001-06':2571,'2001-07':624,'2001-08':0,'2001-09':2394,'2001-10':3948,'2001-11':5709,'2001-12':2691,'2002-01':1887,'2002-02':1489,'2002-03':3134,'2002-04':1907,'2002-05':202,'2002-06':1485,'2002-07':1362,'2002-08':0,'2002-09':3906,'2002-10':3195,'2002-11':5659,'2002-12':3533,'2003-01':237,'2003-02':1910,'2003-03':1926,'2003-04':2638,'2003-05':1159,'2003-06':3036,'2003-07':0,'2003-08':1312,'2003-09':2824,'2003-10':4669,'2003-11':4605,'2003-12':3024,'2004-01':1276,'2004-02':2617,'2004-03':1858,'2004-04':3430,'2004-05':1210,'2004-06':2694,'2004-07':135,'2004-08':249,'2004-09':3610,'2004-10':3080,'2004-11':4113,'2004-12':1949,'2005-01':1304,'2005-02':3760,'2005-03':4080,'2005-04':2038,'2005-05':1344,'2005-06':2890,'2005-07':0,'2005-08':231,'2005-09':3951,'2005-10':2212,'2005-11':5352,'2005-12':2144,'2006-01':1522,'2006-02':3188,'2006-03':3033,'2006-04':2887,'2006-05':1718,'2006-06':3876,'2006-07':211,'2006-08':807,'2006-09':3116,'2006-10':4581,'2006-11':272,'2006-12':1698,'2007-01':1463,'2007-02':1048,'2007-03':2845,'2007-04':2392,'2007-05':1612,'2007-06':4513,'2007-07':552,'2007-08':0,'2007-09':3663,'2007-10':3630,'2007-11':5328,'2007-12':2994,'2008-01':2925,'2008-02':2482,'2008-03':3871,'2008-04':3613,'2008-05':2880,'2008-06':3720,'2008-07':846,'2008-08':0,'2008-09':4794,'2008-10':5160,'2008-11':4864,'2008-12':4024,'2009-01':3220,'2009-02':2541,'2009-03':4015,'2009-04':1253,'2009-05':3089,'2009-06':3657,'2009-07':0,'2009-08':0,'2009-09':0,'2009-10':3128,'2009-11':5361,'2009-12':3301,'2010-01':3547,'2010-02':2956,'2010-03':3862,'2010-04':2415,'2010-05':1592,'2010-06':1351,'2010-07':145,'2010-08':73,'2010-09':2300,'2010-10':2304,'2010-11':6060,'2010-12':3950,'2011-01':2654,'2011-02':2738,'2011-03':4448,'2011-04':3644,'2011-05':2104,'2011-06':4303,'2011-07':0,'2011-08':255,'2011-09':4936,'2011-10':5938,'2011-11':9212,'2011-12':4983,'2012-01':3058,'2012-02':4572,'2012-03':6264,'2012-04':5854,'2012-05':3460,'2012-06':5306,'2012-07':1503,'2012-08':0,'2012-09':987,'2012-10':3860,'2012-11':5073,'2012-12':5988,'2013-01':4595,'2013-02':4783,'2013-03':5493,'2013-04':5790,'2013-05':4468,'2013-06':5918,'2013-07':1355,'2013-08':0,'2013-09':4981,'2013-10':5790,'2013-11':6851,'2013-12':3587,'2014-01':3517,'2014-02':5182,'2014-03':4056,'2014-04':5067,'2014-05':2841,'2014-06':4971,'2014-07':1775,'2014-08':0,'2014-09':6006,'2014-10':5575,'2014-11':7989,'2014-12':3666,'2015-01':3635,'2015-02':4330,'2015-03':4921,'2015-04':6375,'2015-05':2235,'2015-06':6314,'2015-07':1193,'2015-08':301,'2015-09':6831,'2015-10':5884,'2015-11':6488,'2015-12':4816,'2016-01':3939,'2016-02':4534,'2016-03':6961,'2016-04':4662,'2016-05':3892,'2016-06':6832,'2016-07':2040,'2016-08':0,'2016-09':5612,'2016-10':4662,'2016-11':7723,'2016-12':5348,'2017-01':2404,'2017-02':5189,'2017-03':838,'2017-04':2811,'2017-05':3327,'2017-06':4468,'2017-07':1430,'2017-08':0,'2017-09':4294,'2017-10':2300,'2017-11':9858,'2017-12':5217,'2018-01':3922,'2018-02':5667,'2018-03':5298,'2018-04':6392,'2018-05':4478,'2018-06':6844,'2018-07':1974,'2018-08':0,'2018-09':5760,'2018-10':7839,'2018-11':7358}

# Some counts for calculating the averages in TV data per year
di_tv_counts = {'2013-05':31, '2013-06':51, '2013-07':47, '2013-08':48, '2013-09':53, '2013-10':56, '2013-11':55, '2013-12':49, '2014-01':58, '2014-02':40, '2014-03':56, '2014-04':55, '2014-05':61, '2014-06':39, '2014-07':47, '2014-08':50, '2014-09':58, '2014-10':59, '2014-11':58, '2014-12':50, '2015-01':51, '2015-02':54, '2015-03':58, '2015-04':55, '2015-05':54, '2015-06':57, '2015-07':56, '2015-08':44, '2015-09':60, '2015-10':53, '2015-11':57, '2015-12':53, '2016-01':54, '2016-02':56, '2016-03':60, '2016-04':56, '2016-05':59, '2016-06':50, '2016-07':51, '2016-08':49, '2016-09':57, '2016-10':56, '2016-11':59, '2016-12':56, '2017-01':57, '2017-02':54, '2017-03':59, '2017-04':57, '2017-05':60, '2017-06':55, '2017-07':53, '2017-08':45, '2017-09':54, '2017-10':58, '2017-11':56, '2017-12':51, '2018-01':48}

def createHistogram(querystring='', domain='', path_to_file='', show_kranten=False, show_partij=False, program='all', include_normalised=False, time_format='years'):

	# Domain (politcs, newspapers, tweets) needs to be set to asses the data
	# Set some column headers
	filename = domain + '-'
	if domain.startswith('krant') or domain.startswith('newspaper'):
		df = pd.read_csv(path_to_file)
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

		# Convert dd-mm-yyyy format to yyyy-mm-dd
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
	#if querystring != '':
	print('Filtering data: ' + filename)
	if domain == 'facebook':
		print(querystring)
		df = getFbDf(querystring)
		print(df)
		# df[time_col] = [time[:10] for time in df[time_col].tolist()]
		# print(df[time_col])
	else:
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
	print(df_dates)
	# Create new list of all dates between start and end date
	# Sometimes one date has zero counts, and gets skipped by matplotlib
	li_dates = []
	li_check_dates = []

	if time_format == 'years':
		d1 = datetime.strptime(df_dates.index[0], "%Y").date()  				# start date
		d2 = datetime.strptime(df_dates.index[len(df_dates) - 1], "%Y").date()	# end date
		delta = d2 - d1															# timedelta
		for i in range(delta.days + 1):
			date = d1 + timedelta(days=i)
			date = str(date)[:endstring]
			if date not in li_dates:
				li_dates.append(date)
				li_check_dates.append(date)

	elif time_format == 'months':
		print(df_dates)
		d1 = datetime.strptime(df_dates.index[0], "%Y-%m").date()  					# start date
		d2 = datetime.strptime(df_dates.index[len(df_dates) - 1], "%Y-%m").date()	# end date
		delta = d2 - d1																# timedelta
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
	print(li_dates)

	#create list of average counts
	li_empty_dates = []
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
			#print(df_histo['count'][i], di_av_counts[df_histo['date'][i]])
			av_count = (df_histo['count'][i] / di_av_counts[df_histo['date'][i]]) * 100
			li_av_count.append(av_count)

		df_histo['av_count'] = li_av_count


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
		df = df.set_index('time')
		df.columns = ['page_name','size']
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
			df = df.pivot(index='time', columns='page_name', values='size')

	# Check if there's no dates with zero occurances missing
	# If that's the case, append a row with zeroes and the
	# missing date as the index.
	for single_date in li_dates:
		if single_date not in df.index:
			df.loc[single_date] = [None] * len(df.columns)
			# print('Date not in index', single_date)
			# series = pd.Series([None] * len(df.columns))
			# series.name = single_date
			# df.append(series)
			# print(series)
	df = df.sort_index()
	print(df.head(10))
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

	if include_normalised:
		ax2 = ax.twinx()
		df_histo.plot(ax=ax2, y='av_count', legend=False, kind='line', linewidth=2, color='#d12d04');
	
	#df_histo.plot(ax=ax, stacked=True, y='partij', kind='bar', legend=False, width=.9, color='#52b6dd');
	#df_histo.plot(ax=ax2, y='av_count', legend=False, kind='line', linewidth=2, color='#d12d04');
	
	ax.set_axisbelow(True)
	#ax.set_xticks(li_dates)
	ax.set_xticklabels(df.index, rotation='vertical')
	ax.grid(color='#e5e5e5',linestyle='dashed', linewidth=.6)
	ax.set_ylabel('Absoluut aantal', color=colors[0])
	ax.set_xlabel('Jaren')
	
	if include_normalised:
		if domain == 'politiek':
			ylabel = '% van totaal aantal spreekbeurten in TK'
		elif domain == 'televisie':
			ylabel = '% van totaal aantal verzamelde uitzendingen'
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

if __name__ == '__main__':
	
	createHistogram(querystring=['racis'], domain='politiek', time_format='years', show_partij=6, include_normalised=True)