import json
import requests
import sys
import logging

CHARMSTORE_URL = 'https://api.jujucharms.com/charmstore/v5'

def setKPIs():
	KPI = {}
	KPI['curated'] = 0
	KPI['homepage'] = 0
	KPI['bugs-url'] = 0
	KPI['layers'] = 0
	KPI['resources'] = 0
	KPI['terms'] = 0
	return KPI

KPI = setKPIs()

def getData(url):
	log.debug("get data from %s", url)
	response = requests.get(url)
	#TBD handle errors
	if response.status_code != 200:
		log.error("url failed: %s", url)
		return {}
	data = json.loads(response.content)
	log.debug("resonse: %s", data)
	return data

def checkCommonInfo(url):
	cinfo = getData(url + '/meta/common-info')
	if cinfo != None and len(cinfo) > 0:
		if 'homepage' in cinfo:
			KPI['homepage'] += 1
		if 'bugs-url' in cinfo:
			KPI['bugs-url'] += 1

def checkResources(url):
	data = getData(url + '/meta/resources')
	if len(data) > 0:
		KPI['resources'] += 1

def checkTerms(url):
	data = getData(url + '/meta/terms')
	if len(data) > 0:
		KPI['terms'] += 1			

def checkLayers(url):
	log.debug("checking layers for %s", url)
	response = requests.get(url + '/archive/layer.yaml')
	if response.status_code != 200:
		response = None
	if response != None:
		KPI['layers'] += 1

def processSearchResults(searchData):
	results = []
	for id in searchData["Results"]:
		KPI['curated'] += 1
		result = {}
		charm = id['Id'].replace('cs:', '')
		result['id'] = charm
		# generate base URL for the entity
		url = CHARMSTORE_URL + '/' + charm
		checkCommonInfo(url)
		checkLayers(url)
		checkResources(url)
		res = checkTerms(url)
		# TBD: analyze readme
	return results


logging.basicConfig(filename="check-charm-urls.log", level=logging.DEBUG)
log = logging.getLogger("charm-urls")

# create the logging file handler
fh = logging.FileHandler("check-charm-urls.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add handler to logger object
log.addHandler(fh)


logging.info("Started")

data = getData(CHARMSTORE_URL + '/search?promulgated=1&limit=5')
results = processSearchResults(data)

print KPI

logging.info("Ended")