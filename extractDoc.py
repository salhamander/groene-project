from glob import glob
import re
import os
import win32com.client as win32
import pandas as pd
from datetime import datetime
from docx import Document
from win32com.client import constants


def save_as_docx(folder):
	paths = glob('C:\\users\\hagen\\documents\\uva\\groene-project\\data\\media\\kranten\\moslims-moslim-islam-atleast5\\**\\*.doc', recursive=True)
	for file in paths:
		
			# Opening MS Word
			word = win32.gencache.EnsureDispatch('Word.Application')
			doc = word.Documents.Open(file)
			doc.Activate ()

			# Rename path with .docx
			new_file_abs = os.path.abspath(file)
			new_file_abs = re.sub(r'\.\w+$', '.docx', new_file_abs)

			# Save and Close
			word.ActiveDocument.SaveAs(
				new_file_abs, FileFormat=constants.wdFormatXMLDocument
			)
			doc.Close(False)


def getKrantenInfo(folder):
	li_files = [file for file in os.listdir(folder) if file.endswith('.docx')]
	print(li_files)

	weekdays = ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag']
	months_en = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
	months_nl = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']
	years = ['1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018']

	li_artikelen = []
	start_of_doc = False
	is_date = False
	is_title = False
	print_para = False
	
	for index, file in enumerate(li_files[14:]):
		print(file)

		# Debugging
		#if file != 'De_Volkskrant-2006-1-moslim-moslim-islam-atleast5.docx':
		if 1 == 2:
		 	print('')
		else:
			print('Reading file ' + str(index) + ' of ' + str(len(li_files)) + ': ' +  file)
			f = open(folder + file, 'rb')
			document = Document(f)

			article_no = -1

			# Variables to get
			# artikel_info = {}
			# artikel_info['newspaper'] = ''
			# artikel_info['title'] = ''
			# artikel_info['author'] = ''
			# artikel_info['date'] = ''
			# artikel_info['pagina'] = 0
			# artikel_info['length'] = 0
			# artikel_info['full_text'] = []

			# Loop through the paragraphs
			for i, para in enumerate(document.paragraphs):
				#print(i, len(document.paragraphs))
				para_full = para.text
				para = para.text.lower().rstrip().lstrip()

				#print(para)
				# New article
				# If a new '1 of XX DOCUMENTS' is reached, start storing article data
				if 'of' in para_full and 'DOCUMENTS' in para_full:
					article_no = article_no + 1
					li_artikelen.append({})
					li_artikelen[article_no]['full_text'] = []
					start_of_doc = True
					print('new doc')
					# if print_para:
					# 	quit()
					# if para == '38 of 199 documents':
					# 	print_para = True

				# Only store data after the start of a doc
				if start_of_doc:
					#print(para)
					# if para_full == 'Met dubbele tong':
					# 	print_para = True

					if len(para) > 0:
						#print(para)
						if print_para:
							print(para)
						# Only catch the first newspaper header. Sometimes newspaper names appear as in-text headers.
						# print('newspaper' in li_artikelen[article_no])
						if (para == 'de volkskrant' or para == 'de telegraaf' or para == 'nrc handelsblad' or para == 'ad/algemeen dagblad') and (not 'newspaper' in li_artikelen[article_no] and not 'title' in li_artikelen[article_no]):
							print(para_full + ' article')

							print('paper:', para_full)
							li_artikelen[article_no]['newspaper'] = para_full
							# Date (always?) comes after newspaper name
							is_date = True

						elif is_date:
							print('Published on ' + para_full)
							li_artikelen[article_no]['date'] = para
							date_formatted = para.replace(',','').rstrip()
							for year in years:
								if year in date_formatted:
									date_formatted = date_formatted.split(year)
									date_formatted = date_formatted[0] + year
							for z, day in enumerate(weekdays):
								if day in date_formatted:
									date_formatted = date_formatted.replace(' ' + day, '')
							for x, month in enumerate(months_nl):
								if month in date_formatted:
									date_formatted = date_formatted.replace(month, months_en[x])
							if date_formatted[0].isdigit():
								li_artikelen[article_no]['date_formatted'] = datetime.strptime(date_formatted.rstrip(), '%d %B %Y').strftime('%Y-%m-%d')
							else:
								li_artikelen[article_no]['date_formatted'] = datetime.strptime(date_formatted.rstrip(), '%B %d %Y').strftime('%Y-%m-%d')
							
							is_date = False

							# Title (always?) comes after date
							is_title = True

						elif 'SECTION: ' in para_full:
							li_artikelen[article_no]['pagina'] = para.lower().replace('section: ', '')
						elif 'LENGTH: ' in para_full:
							li_artikelen[article_no]['length'] = int(para.lower().replace('length: ', '').replace(' words', '').replace(' woorden', ''))
						elif 'BYLINE: ' in para_full:
							li_artikelen[article_no]['author'] = para.lower().replace('byline: ', '')

						elif is_title:
							if para_full in weekdays:
								is_title = True
							else:
								print('New article on paragraph ' + str(i) + '/' + str(len(document.paragraphs)) + ': "' + para_full + '"')
								li_artikelen[article_no]['title'] = para_full
								is_title = False
						
						elif len(para) > 0 and para != ' ' and not para_full.endswith(' DOCUMENTS') and 'Time Of Request' not in para_full and 'All Documents:' not in para_full and not para_full.startswith('SECTION: '):
							li_artikelen[article_no]['full_text'].append(para_full)
							# print('Regular text paragraph')
							# print(para_full)

					# End of doc
					if i == (len(document.paragraphs) - 1):
						print('End of doc')
						print('Writing results to csv')
						start_of_doc = True
						df = pd.DataFrame(li_artikelen)
						print(df.head())
						
						# Write to file
						if os.path.isfile('data/media/kranten/islam-moslim-moslims-atleast5-allpapers.csv'):
							df.to_csv('data/media/kranten/islam-moslim-moslims-atleast5-allpapers.csv', mode='a', header=False)
						else:
							df.to_csv('data/media/kranten/islam-moslim-moslims-atleast5-allpapers.csv')

						li_artikelen = []
						start_of_doc = False
						is_date = False
						is_title = False
						article_no = -1
						f.close()

			#print(li_artikelen)
			#print(document)
			

#save_as_docx('shit')
getKrantenInfo('data/media/kranten/moslims-moslim-islam-atleast5/')