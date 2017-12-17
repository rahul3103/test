import os
import requests,zipfile, io
from bs4 import BeautifulSoup as bs

def get_todays_filename():
	r = requests.get("http://www.bseindia.com/markets/equity/EQReports/Equitydebcopy.aspx")
	html = r.content
	soup = bs(html, 'html.parser')
	find_url = soup.find('li',{'id':'liZip'})
	url = find_url.find('a')['href']
	filename = find_url.text
	filename = filename[10:].replace('/','')
	filename = filename.replace('20','')
	csv_filename = 'EQ'+filename+'.CSV'
	return { 'filename': csv_filename, 'url': url }

def check_file_exists(filename):
	return os.path.isfile(filename)

def get_todays_csv_file():
	data = get_todays_filename()
	if not check_file_exists(data['filename']):
		try:
			r = requests.get(data['url'])
			z = zipfile.ZipFile(io.BytesIO(r.content))
			z.extractall()
		except PermissionError:
			print("you already have this file")
	return data['filename']
