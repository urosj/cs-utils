# Copyright 2016 Canonical Ltd
# Licensed under the AGPLv3, see copyright file for details.

import json
import requests
import logging
import sys

CHARMSTORE_URL = 'https://api.jujucharms.com/charmstore/v5'
CHANGES_URL = '/changes/published?'

def getCharmRevisionFromId(charmId):
    """ Parses the charm ID string and returns the revision if there is one.
    Returns the string of the revision if one exists, otherwise it returns
    None.
    """
    parts = charmId.split('-')
    revision = parts[-1]
    try:
        return int(revision)
    except Exception:
        return None


def checkIfPromulgated(charmId):
    """ Calls charm store /meta/promulgated endpoint and verifies if the
    charm is promulgated or not.
    """
    url = CHARMSTORE_URL + '/' + charmId + '/meta/promulgated'
    # logging.debug("fetching promulgated info for {}", url)
    print "fetching data from ", url
    response = requests.get(url)
    if response.status_code != 200:
        logging.debug('promulgated info for {} failed', url)
        return False

    data = json.loads(response.content)
    value = data['Promulgated']
    return value


def getCharmInfo(changesData):
    """  Returns all charm Ids mapped to the information about their revision
    and whether the charm is promulgated or not.
    """
    charms = {}
    for published in changesData:
        charmId = published['Id']
        charmId = charmId.replace('cs:', '')
        info = {}
        info['revision'] = getCharmRevisionFromId(charmId)
        info['promulgated'] = checkIfPromulgated(charmId)
        charms[charmId] = info
    # logging.debug('all content {}', charms)
    print charms
    return charms


def filterNew(charms, promulgated=True):
    """ Filters charms with revision 0.
    """
    filtered = []
    for charm in charms:
        info = charms[charm]
        if (info['revision'] == 0) and (info['promulgated'] == promulgated):
            filtered.append(charm)
    print filtered
    return filtered


def getNewPromulgated(charms):
    """ Filters all promulgated new charms.
    """
    return filterNew(charms)


def getNewCommunity(charms):
    """ Filters all new but not promulgated charms.
    """
    return filterNew(charms, False)


def filterUpdatedRevisions(charms, promulgated=True):
    """ Filters charms with revision not 0.
    """
    filtered = []
    for charm in charms:
        info = charms[charm]
        if (info['revision'] != 0) and (info['promulgated'] == promulgated):
            filtered.append(charm)
    print filtered
    return filtered


def getUpdatedPromulgated(charms):
    return filterUpdatedRevisions(charms)


def getUpdatedCommunity(charms):
    return filterUpdatedRevisions(charms, False)


def processHtmlRows(charms, numInRow=4):
	pos = 0
	str = '<table><tr>\n'
	for charm in charms:
		if pos % numInRow == 0:
			str += '</tr><tr>'
		str += '<td><div class="juju-card" data-id="' + charm + '"></div></td>\n'
		pos += 1
	str += '</tr></table>\n'
	return str


def generateHtml(newPromulgated, newCommunity, updatedPromulgated,
                 updatedCommunity, date):
    str = '<html><body>\n'
    str += '<script src="https://assets.ubuntu.com/v1/juju-cards-v1.3.0.js"></script>\n'
    str += '<h1>New charms on ' + date + '</h1>\n'
    str += '<h2>New recommeded charms</h2>\n'
    str += processHtmlRows(newPromulgated)

    str += '<h2>New community charms</h2>'
    str += processHtmlRows(newCommunity)

    str += '<h2>New revisions of recommeded charms</h2>\n'
    str += processHtmlRows(updatedPromulgated)

    str += '<h2>New revisions of community charms</h2>\n'
    str += processHtmlRows(updatedCommunity)

    str += '</html>'
    return str


def fetchChanges(date):
	""" Fetches the data about changes from charm store. Example of the
	url:
	https://api.jujucharms.com/charmstore/v5/changes/published?start=2016-08-05&stop=2016-08-05
	"""
	url = CHARMSTORE_URL + CHANGES_URL + 'start=' + date + '&stop=' + date
	print 'fetching changes from ', url
	response = requests.get(url)
	if response.status_code != 200:
		logging.debug('changes info at {} failed', url)
		return None
	return json.loads(response.content)

def main():
    logging.basicConfig(filename='cs-whats-new.log', level=logging.DEBUG)
    logging.info('Started')

    changesData = fetchChanges(sys.argv[1])
    info = getCharmInfo(changesData)
    newPromulgated = getNewPromulgated(info)
    newCommunity = getNewCommunity(info)
    updatedPromulgated = getUpdatedPromulgated(info)
    updatedCommunity = getUpdatedCommunity(info)

    html = generateHtml(newPromulgated, newCommunity, updatedPromulgated,
                 updatedCommunity, sys.argv[1])
    f = open(sys.argv[2] + '-' + sys.argv[1] + '.html', 'w')
    f.write(html)
    f.close()

    logging.info('Finished')

if __name__ == '__main__':
    main()
