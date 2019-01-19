import pandas as pd
import ast

def filterKrant(file, year, word):
	''' Filters a newspaper dataset on year/string'''

	df = pd.read_csv(file)
	df = df[df['full_text'].str.contains(word, na=False, case=False)]

	if isinstance(year, list):
		year = '|'.join(str(single_year) for single_year in year)
	elif isinstance(year, int):
		year = str(year)

	df = df[df['date_formatted'].str.contains(year)]
	return(df)

def deduplicateKrant(file):
	''' Deduplicates the rows from a newspaper csv.
	Writes a new file (original name + -deduplicated)'''

	df = pd.read_csv(file)

	li_dropindex = []

	for index, row in df.iterrows():
		if index == 0:
			prev_row = row
		elif index > 0:
			if str(row['author']) == str(prev_row['author']) and str(row['pagina']) == str(prev_row['pagina']) and row['date'] == prev_row['date']:
				if len(ast.literal_eval(row['tokens'])) > 4 and len(ast.literal_eval(prev_row['tokens'])) > 4:
					if (ast.literal_eval(row['tokens'])[2][:10] == ast.literal_eval(prev_row['tokens'])[2][:10]) and (ast.literal_eval(row['tokens'])[4][:10] == ast.literal_eval(prev_row['tokens'])[4][:10]):
						print('equals')
						print(str(row['title'])[:10], str(prev_row['title'])[:10])
						print(ast.literal_eval(row['tokens'])[2][:10], ast.literal_eval(prev_row['tokens'])[2][:10])
						print(ast.literal_eval(row['tokens'])[4][:10], ast.literal_eval(prev_row['tokens'])[4][:10])
						li_dropindex.append(index)
			prev_row = row

	df = df.drop(df.index[li_dropindex])
	df.to_csv(file[:-4] + '-deduplicated.csv')

if __name__ == '__main__':
	deduplicateKrant('data/media/kranten/all-multicultureel-multiculturele-multiculturalisme-withtokens.csv')
