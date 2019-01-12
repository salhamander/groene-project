import sqlite3
import pandas as pd
import io
import os
import urllib.request, json
import untangle
import time
import ssl
import xmltodict
import pickle as p
from TweedeKamerToCsv import TweedeKamerToCsv
from xml.parsers.expat import ExpatError
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
   'Accept-Encoding': 'none',
   'Accept-Language': 'en-US,en;q=0.8',
   'Connection': 'keep-alive'}

def scrapeTweedeKamer():
	#getHandelingen()
	#li_input = [file for file in os.listdir('data/politiek/handelingen/xml/')]
	#print(li_input)
	#li_input = [file for file in li_input if file.startswith('h-tk-2015') or file.startswith('h-tk-2016') or file.startswith('h-tk-2017') or file.startswith('h-tk-2018')]
	#getMetaData(li_input)
	getHandelingen()
	#TweedeKamerToCsv()
	# li_input = [file for file in os.listdir('data/politiek/kamervragen/') if file.endswith('.p')]
	# print(li_input)
	# getMetaData(li_input)
	
	
def getHandelingen(year = 2014, vol = 1):
	"""
	Collects all the Tweede Kamer handelingen from officielebekendmakingen.nl
	year: the starting year of the loop
	coutner: the starting document in the respective year

	"""

	years_left = True
	docs_left = True
	first_fail = False

	doc = 1

	# Starting dossier number
	dossier_no = 1
	dossiers = True

	# loop through all pages listing 30 documents	
	while years_left:

		# docname = 'h-tk-' + str(year) + str(year + 1) + '-' + str(vol) + '-' + str(doc) + '.p'
		# if os.path.isfile('data/politiek/handelingen/xml/' + docname) and (vol != 1 and doc != 1):
		# 	print('Document ' + docname + ' already exists')
		# else:

		# Document numbers are different before 2011, as they rely on page numbers

		if year < 2011:


			# For loop through the dossier numbers for the year
			dossier_url = 'https://zoek.officielebekendmakingen.nl/handelingen/TK/' + str(year) + '-' + str(year + 1) + '/' + str(dossier_no)

			print('Requesting:', dossier_url)

			request = urllib.request.Request(dossier_url, headers=headers)

			# Bypass SSL - not a problem since we're only requesting one site
			gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
			
			# check if the page exists
			try:
				response = urllib.request.urlopen(request, context=gcontext)

			# if there's a HTTP error
			except ConnectionResetError as e:
				print('HTTP error when requesting dossier page')
				print('Reason:', e)
				print('Sleeping for a minute')
				time.sleep(60)
				pass
			except urllib.error.HTTPError as httperror:
				print('HTTP error when requesting dossier page')
				print('Reason:', httperror.code)
				pass
			else:

				# Get a list of the links for the documents
				html = response.read()
				soup = BeautifulSoup(html, features="lxml")
				anchors = soup.find('div', {'class': 'lijst'})
	
				# Check if it's not a 404 HTML page
				if not anchors:
					year = year + 1
					dossier_no = 1
					print('No dossiers found for this year. Continuing to ' + str(year))
				
				# If the dossier exists and has documents, get the xml urls and save them as pickled dictonaries
				else:

					anchors = anchors.find_all('a')
					li_documents = []

					for a in anchors:
						doc_name = a['href'].split('?')[0]
						print(doc_name)

						if 'h-tk' not in doc_name:
							doc_name = 'h-' + doc_name.split('h-')[1]
						else:
							doc_name = 'h-tk' + doc_name.split('h-tk')[1]
						#print(doc_name)
						li_documents.append(doc_name)

					print(li_documents)

					for document_name in li_documents:
						url = 'https://zoek.officielebekendmakingen.nl/' + document_name + '.xml'
						print(url)
						# check if the page exists
						try:
							response = urllib.request.urlopen(url, context=gcontext)

						# if there's a HTTP error
						except ConnectionResetError as e:
							print('HTTP error when requesting thread')
							print('Reason:', e)
							print('Sleeping for a minute')
							time.sleep(60)
							pass
						except urllib.error.HTTPError as httperror:
							print('HTTP error when requesting thread')
							print('Reason:', httperror.code)
							pass
						else:

							file = response.read()
							
							if not os.path.exists('data/politiek/handelingen/xml/'):
								os.makedirs('data/politiek/handelingen/xml/')
							
							di_handelingen = xmltodict.parse(file)
							#print(di_handelingen)
							print('data/politiek/handelingen/xml/' + document_name + '.p')
							p.dump(di_handelingen, open('data/politiek/handelingen/xml/' + document_name + '.p', 'wb'))

					dossier_no = dossier_no + 1
					print('Dossier no:', dossier_no)
		
		else:	
			# Handelingen have a volume (vol) and document number (doc),
			# so we'll have to loop through both
			document_name = 'h-tk-' + str(year) + str(year + 1) + '-' + str(vol) + '-' + str(doc)

			url = 'https://zoek.officielebekendmakingen.nl/' + document_name + '.xml'
			print('Requesting:')
			print(url)
			request = urllib.request.Request(url, headers=headers)

			# Bypass SSL - not a problem since we're only requesting one site
			gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
			
			# check if the page exists
			try:
				response = urllib.request.urlopen(request, context=gcontext)

			# if there's a HTTP error
			except ConnectionResetError as e:
				print('HTTP error when requesting thread')
				print('Reason:', e)
				print('Sleeping for a minute')
				time.sleep(60)
				pass
			except urllib.error.HTTPError as httperror:
				print('HTTP error when requesting thread')
				print('Reason:', httperror.code)
				pass
			else:

				info = response.info()

				print(info.get_content_subtype())   # -> html
				
				# Check if the response is a 404 handle page or a XML file
				if info.get_content_subtype() != 'xml':
					
					print('No doc left this volume')

					# If fetching already failed after increasing the volume number, proceed to the next year instead
					if first_fail:
						year = year + 1
					else:
						vol = vol + 1
						doc = 1
						first_fail = True
					
				else:
					
					file = response.read()
					
					if not os.path.exists('data/politiek/handelingen/xml/'):
						os.makedirs('data/politiek/handelingen/xml/')
					
					try:
						di_handelingen = xmltodict.parse(file)
						p.dump(di_handelingen, open('data/politiek/handelingen/xml/' + document_name + '.p', 'wb'))
						print(di_handelingen)

					except ExpatError as e:
						print('Couldn\'t parse')

					else:
						print('Continuing')
						first_fail = False
						doc = doc + 1

		# End if the year to check is 2019
		if year == 2019:
			years_left = False

def getKamerVragen(year = 1995, counter = 0):
	"""
	Collects all the Tweede Kamer kamervragen from officielebekendmakingen.nl
	year: the starting year of the loop
	coutner: the starting document in the respective year

	"""
	
	documents_left = True

	while documents_left:

		document_name = 'ah-tk-' + str(year) + str(year + 1) + '-' + str(counter)
		url = 'https://zoek.officielebekendmakingen.nl/' + document_name + '.xml'
		print('Requesting:')
		print(url)
		request = urllib.request.Request(url, headers=headers)

		# Bypass SSL - not a problem since we're only requesting one site
		gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
		
		# check if the page exists
		try:
			response = urllib.request.urlopen(request, context=gcontext)

		# if there's a HTTP error
		except ConnectionResetError as e:
			print('HTTP error when requesting thread')
			print('Reason:', e)
			print('Sleeping for a minute')
			time.sleep(60)
			pass
		except urllib.error.HTTPError as httperror:
			print('HTTP error when requesting thread')
			print('Reason:', httperror.code)
			pass
		else:

			info = response.info()

			print(info.get_content_subtype())   # -> html
			
			# Check if the response is a 404 handle page or a XML file
			if info.get_content_subtype() != 'xml':
				print('No file left this year')
				year = year + 1
				counter = 0

			else:
				
				file = response.read()
				
				if not os.path.exists('data/politiek/kamervragen/'):
					os.makedirs('data/politiek/kamervragen/')
				
				p.dump(file, open('data/politiek/kamervragen/' + document_name + '.p', 'wb'))

				try:
					di_kamervragen = xmltodict.parse(file)
					print(di_kamervragen)
				except ExpatError as e:
					print('No file left', e)
					year = year + 1
					counter = 0

				else:
					print('continue')

		#time.sleep(4)
		counter = counter + 1

		# End if the year to check is 2019
		if year == 2019:
			documents_left = False

def getMetaData(li_input):
	"""
	Gets the metadata from Officiële Bekendmakingen documents
	Input: a list of document names
	
	"""

	for doc in li_input:

		if ('metadata-' + doc) not in os.listdir('data/politiek/handelingen/metadata/'):
			url = 'https://zoek.officielebekendmakingen.nl/' + doc[:-2] + '/metadata.xml'
			print('Requesting:')
			print(url)
			request = urllib.request.Request(url, headers=headers)

			# Bypass SSL - not a problem since we're only requesting one site
			gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
			
			# check if the page exists
			try:
				response = urllib.request.urlopen(request, context=gcontext)

			# if there's a HTTP error
			except ConnectionResetError as e:
				print('HTTP error when requesting thread')
				print('Reason:', e)
				print('Sleeping for a minute')
				time.sleep(60)
				pass
			except urllib.error.HTTPError as httperror:
				print('HTTP error when requesting thread')
				print('Reason:', httperror.code)
				pass
			else:

				info = response.info()

				print(info.get_content_subtype())   # -> html
				
				# Check if the response is a 404 handle page or a XML file
				if info.get_content_subtype() != 'xml':
					print('Error... xml file not found.')
					quit()

				else:
					
					file = response.read()
					
					if not os.path.exists('data/politiek/metadata/'):
						os.makedirs('data/politiek/handelingen/metadata/')
					
					p.dump(file, open('data/politiek/handelingen/metadata/metadata-' + doc, 'wb'))

					di_kamervragen = xmltodict.parse(file)
					print(di_kamervragen)
	

scrapeTweedeKamer()