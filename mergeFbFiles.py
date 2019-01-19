import pandas as pd
import sqlite3
import os
from sqlalchemy import create_engine

def createSqliteDb(path_to_csv):
	''' Converts a csv file into a sqlite database '''

	#df = pd.read_csv(path_to_csv)
	# df = df[:10000]
	# df.to_csv('test.csv')
	# quit()
	fb_database = create_engine('sqlite:///fb_nl_programmas.db')

	chunksize = 100000
	i = 0
	j = 1
	
	for df in pd.read_csv(path_to_csv, engine='python', chunksize=chunksize, iterator=True):
		df.index += j
		i+=1
		df.to_sql('page_comments', fb_database, index=False, if_exists='append')
		j = df.index[-1] + 1
		print('Finished ' + str(i * chunksize) + '/' + str(len(df)) + ' rows')

def createCsvFromFb(path_to_files):
	''' Compile a bunch of netvizz .tab files into a big .csv file '''

	files = [file for file in os.listdir(path_to_files) if 'comments' in file]
	
	for file in files:
		print('Writing', file)
		name = file.split('_page')[0]
		df_page = pd.read_csv(path_to_files + file, sep='\t')
		df_page['page_name'] = [name] * len(df_page)

		# Write to csv
		df_page = df_page[['post_id','post_text','post_published','comment_id','comment_message','comment_published','comment_like_count','page_name']]

		if os.path.isfile(path_to_files + 'all-data.csv'):
			df_page.to_csv(path_to_files + 'all-data.csv', mode='a', header=False)
		else:
			df_page.to_csv(path_to_files + 'all-data.csv')

if __name__ == '__main__':
 	#createCsvFromFb('data/social_media/fb/tab_files/')
	createSqliteDb('data/social_media/fb/fb_nl_programmas_withtokens.csv')