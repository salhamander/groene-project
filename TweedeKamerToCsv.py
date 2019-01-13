import pandas as pd
import pickle as p
import pprint
import collections
import os
import xmltodict
from sqlalchemy import create_engine

def TweedeKamerToCsv():
	'''
	Cycles through all the handelingen and kamervragen and puts them in a csv.
	This can be filtered afterwards.
	Saving columns:
	type,	Type of document (e.g. kamervraag or vergadering)
	title,	Title of document
	date, 	Date of document
	name, 	Name of speaker
	party, 	Party of speaker. 'geen' if voorzitter
	text,	Text
	'''

	global jaar
	global datum
	global title
	global clean_al
	clean_al = ''

	df = pd.DataFrame()
	
	is_handeling = True

	if is_handeling:
		for handeling in os.listdir('data/politiek/handelingen/xml/'):

			#if handeling.startswith('h-tk-19951996-1'):
			if handeling.endswith('.p') and handeling.startswith('h-tk-'):

				# DEBUGGING
				# handeling = 'h-tk-20102011-100-1.p'
				# https://zoek.officielebekendmakingen.nl/handelingen/h-tk-20132014-104-2.xml
				# pprint.pprint(di_handeling)

				print('Getting values for ' + handeling)
				# Get all the relvant data from the xml->dict files
				di_handeling = p.load(open('data/politiek/handelingen/xml/' + handeling, 'rb'))

				# Load metadata for date
				#if os.path.isfile('data/politiek/handelingen/metadata/metadata-' + handeling):
				di_metadata = p.load(open('data/politiek/handelingen/metadata/metadata-' + handeling, 'rb'))
				di_metadata = xmltodict.parse(di_metadata)
				#print(di_metadata)
				#pprint.pprint(di_metadata)

				# Get some metadata for in the csv (type of document and date)
				for di_info in di_metadata['metadata_gegevens']['metadata']:
					#print(di_info)
					for k, v in di_info.items():
						if v == 'OVERHEID.Informatietype':
							informatietype = di_info['@content']
							#print(informatietype)
						if v == 'OVERHEIDop.datumVergadering':
							datum = di_info['@content']
							#print(datum)
						if v == 'DC.title':
							title_full = di_info['@content']
							#print(title_full)
				# else:
				# 	informatietype = 'onbekend'
				# 	datum = 'onbekend'
				# 	title_full = 'onbekend'

				# Vergaderjaren are like school years, so the exact date of meeting should be checked
				jaar = int(datum[0:4])

				# Values to get
				global title
				global li_data
				global li_tekst
				global li_partijen
				global li_sprekers
				global li_aanhef

				li_tekst = []
				li_data = []
				li_partijen = []
				li_sprekers = []
				li_aanhef = []

				#pprint.pprint(di_handeling)
				getValues(di_handeling)

				di_results = {}
				di_results['datum'] = [datum for i in range(len(li_tekst))]
				di_results['aanhef'] = li_aanhef
				di_results['spreker'] = li_sprekers
				di_results['partij'] = li_partijen
				di_results['tekst'] = li_tekst
				di_results['item-titel'] = [title for i in range(len(li_tekst))]
				di_results['item-titel-full'] = [title_full for i in range(len(li_tekst))]
				di_results['informatietype'] = [informatietype for i in range(len(li_tekst))]
				di_results['document_no'] = [handeling[:-2] for i in range(len(li_tekst))]
				
				df_single = pd.DataFrame.from_dict(di_results)

				#print(df_single.head())

				df = pd.concat([df, df_single])
				#
	# Write to csv!
	print('Writing to csv...')
	df.to_csv('handelingen-v2.csv')
	# Write to sqlite!
	print('Writing sqlite database...')
	engine = create_engine('sqlite://', echo=False)
	df.to_sql('users', con=engine)

def getValues(di_input, is_text_dict=False):
	"""
	Recursive function that loops through the handelingen dicts
	Returns a clean dictionary with all the results.

	"""
	global title
	global partij
	global clean_al
	
	# Markup is different for years before 2011
	if jaar < 2011:
		for key, value in di_input.items():

			# Get the title
			#print(key)
			if key == 'itemnaam':
				if len(value) > 0:
					title = value

			if key == 'spreker':
				#print(value['spreker'])
				#print(type(value))

				if not isinstance(value, list):
					value = [value]

				for beurt in value:
					#print(beurt)
					# Get the spreker
					#print(beurt)
					if 'wie' in beurt.keys():
						spreker = beurt['wie']
					else:
						spreker = beurt

					#print(beurt)
					#print(spreker)
					if 'naam' in spreker.keys():
						if 'aanspr' in spreker:
							aanhef = spreker['aanspr']
						else:
							aanhef = ''
						naam = spreker['naam']
					elif 'naam' in spreker.keys():
						naam = spreker['naam']
					else:
						naam = 'onbekend'

					li_sprekers.append(naam)
					li_aanhef.append(aanhef)
					
					# Get the partij
					#print(beurt['spreker'].keys())
					if 'partij' in spreker.keys():
						partij = spreker['partij']
					else:
						partij = 'geen'
					li_partijen.append(partij)

					#print(beurt)
					#print(beurt.keys())

					# Get the text
					text = ''
					# Some spreekbeurten consists of multiple paragraphs.
					# In this case, they are 'al-groep's. Loop and join as string:
					#print(beurt)
					if 'al-groep' in beurt.keys():
						#print(beurt['al-groep'])

						# al-groep are sometimes dicts, sometimes lists
						if isinstance(text[0]['al-groep'], list):
							text = [text for text in text[0]['al-groep']]
							text = [al['al'] for al in text]

						else:
							#print(text[0].keys())
							if 'al' in text[0]['al-groep'].keys():
								one_text = text[0]['al-groep']
								text = [one_text['al']][0]
								print(text)
							else:
								text = [text for text in text[0]['al-groep'].items()]
								text = '\n'.join(text[0][1])
							
					#print(text)
					# Single paragraph spreekbeurt (just 'al')
					else:
						#print(beurt)
						# Clean up the text
						if 'al' in beurt.keys():
							if isinstance(beurt['al'], str):
								text = [beurt['al']]
							else:
								text = beurt['al']
							#print(text)

							# Check if there's dicts in the text list
							# This happens then a 'lijst' occurs
							text_formatted = []

							for sent in text:
								
								if isinstance(sent, collections.OrderedDict):
									sent_concat = ''

									if 'lijst' in sent.keys():
										sent = sent['lijst']
										#print(sent)
										for k, v in sent.items():
											if k == 'li':
												#print(sent['li'])
												for val in sent['li']:
													if isinstance(val, collections.OrderedDict):
														if 'li' in val.keys():
															for key, li in val.items():
																if isinstance(li, collections.OrderedDict):
																	sent_concat = sent_concat + ' ' + ' '.join(li.values())
																elif isinstance(li, str):
																	sent_concat = sent_concat + ' ' + li
													elif isinstance(val, str):
														sent_concat = sent_concat + ' ' + val
											else:
												sent_concat = sent_concat + ' ' + v

									else:
										#print(sent)

										for k, v in sent.items():
											if isinstance(v, collections.OrderedDict):
												sent[k] = ' '.join(v.values())

										# Some redundant markup (mostly numbers) should be deleted
										if 'inf' in sent.keys():
											del sent['inf']
										if 'sup' in sent.keys():
											del sent['sup']

										#print(sent)
										sent = ' '.join(sent.values())

									sent = sent_concat

								# If the text is a list
								elif isinstance(sent, list):
									sent = [v for v in sent]

								# If not list or dict, sent is a string, and does not need to be processed
								
								sent.replace('\n', ' ')
								text_formatted.append(sent)

							#print(text_formatted)
							text = '\n'.join(text_formatted)
							#print(text)

							# Some checking
							if type(sent) != str:
								#print(sent)
								quit()

					li_tekst.append(text)

			# Recursive funciton to loop through the entire dict
			elif isinstance(value, dict) or isinstance(value, tuple):
				getValues(value)

	# Documents from >= 2011
	else:
		for key, value in di_input.items():

			# Get the title
			if key == 'item-titel' or key == 'vergadering-nummer':
				if len(value) > 0:
					title = value

			if key == 'spreekbeurt':
				# if isinstance(value, list):
				# 	getValues(value, is_text_dict)
				# else:

				# A single spreekbeurt won't appear as a list. Cast to list if this is the case.
				if isinstance(value, collections.OrderedDict):
					value = [value]

				for di_text in value:

					# get the spreker
					spreker = di_text['spreker']
					#print(spreker)
					if isinstance(spreker['naam'], collections.OrderedDict):
						naam = spreker['naam']['achternaam']
					elif isinstance(spreker['naam'], list):
						naam = spreker['naam'][0]['achternaam']
					else:
						print('Invalid name format',spreker)
					if 'voorvoegsels' in spreker:
						aanhef = spreker['voorvoegsels']
					li_sprekers.append(naam)
					li_aanhef.append(aanhef)

					# Get the partij
					if 'politiek' in di_text['spreker'].keys():
						partij = di_text['spreker']['politiek']
					else:
						partij = 'geen'
					li_partijen.append(partij)

					# Get the text
					text = [di_text[i] for i in di_text if i == 'tekst']

					# Some spreekbeurten consists of multiple paragraphs.
					# In this case, they are 'al-groep's. Loop and join as string:
					if 'al-groep' in text[0]:
						# Clean the al-groep lists and dicts
						clean_al = ''
						cleanAlGroep(text[0])

						text = clean_al
					else:
						text = text[0]['al']

					# Some further parsing for stemmingen and moties
					if isinstance(text, list):
						#print(text)
						li_formatted_text = []
						for item in text:
							if isinstance(item, collections.OrderedDict):
								# Extref signals a motie
								if 'extref' in item.keys():
									print(item)
									li_formatted_text.append(item['#text'])
							elif isinstance(text, str):
								li_formatted_text.append(text)
						text = '\n'.join(li_formatted_text)

					#print(text)
					li_tekst.append(text)

			# Recursive function to loop through the entire dict
			elif isinstance(value, dict) or isinstance(value, tuple):
				getValues(value)

def cleanAlGroep(text_input):
	"""
	Recursive function that attempts to fetch as much spoken text from
	'al-groep' xml branches
	"""

	global clean_al
	if isinstance(text_input, str) and text_input != 'goed':
		clean_al = clean_al + ' ' + text_input
	elif isinstance(text_input, tuple) and text_input[0] == 'al':
		#print('al found', text_input)
		clean_al = clean_al + ' ' + text_input[1]
	elif isinstance(text_input, collections.OrderedDict):
		#print('al is dict', text_input)
		for k, v in text_input.items():
			cleanAlGroep(v)
	elif isinstance(text_input, list):
		#print('al is list', text_input)
		for v in text_input:
			cleanAlGroep(v)


def countHandelingenPerYear():
	start_year = 1995

	while start_year <= 2019:
		i = [file for file in os.listdir('data/politiek/handelingen/xml/') if (str(start_year) + str(start_year + 1)) in file]
		i = len(i)
		print(str(i) + ' handelingen in ' + (str(start_year) + str(start_year + 1)))
		start_year = start_year + 1

if __name__ == "__main__":
	countHandelingenPerYear()
	TweedeKamerToCsv()