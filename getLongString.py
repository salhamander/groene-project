import pandas as pd


getLongString

df = pd.read_csv('handelingen-v1.csv')
print(df.columns)

li_years = [1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]

# Write a txt file with all the strings
df_year = df[df['datum'].str.contains('2010|2011|2012|2013|2014')]
# df_year.to_csv('data/politiek/handelingen/handelingen_' + str(year) + '.csv')

txtfile_full = open('data/politiek/handelingen/longstring_handelingen_20102014.txt', 'w', encoding='utf-8')
li_input = df_year['tekst'].tolist()

for item in li_input:
	if item != 'nan':
		item = str(item).lower()
		txtfile_full.write('%s' % item)