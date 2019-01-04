# -*- coding: utf-8 -*-
from __future__ import print_function # Python 2/3 compatibility
import json
import logging
import datetime
from decimal import Decimal
import pdb

# Initialize Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

globalVars  = {}

def setGlobalVars():
    """
    Set the Global Variables
    If User provides different values, override defaults
    """
    try:
        # Set the global variables
        globalVars['Owner']                 = "Miztiik"
        globalVars['Environment']           = "Production"
        globalVars['fixtures_filename']     = "./data/fixtures.json"
        globalVars['countries_filename']    = "./data/icc_test_countries.json"
        globalVars['flag_base_url']         = "https://raw.githubusercontent.com/miztiik/alexa-indian-cricket-matches/master/data/flags/"
    except KeyError as e:
        logger.error("Unable to set Global Environment variables. Exiting")
        logger.error('ERROR: {0}'.format( str(e) ) )
        exit
    return globalVars


def read_from_file(filename):
    with open(filename, 'r') as json_file:
        data = json.load(json_file, parse_float = Decimal)
    return data

def getNextMatch(fixtures):
    nextMatchData = {'status':'',
                     'match_details':{},
                     'error_message':''
        }

    try:
        for i in fixtures:
            if i.get('host_team'):
                # Only find matches that are in the future                
                nowDate = datetime.datetime.now()
                matchDate = str (i.get('month')) + '/' + str (i.get('day')) + '/' + str (i.get('year') )
                if datetime.datetime.strptime( matchDate ,"%m/%d/%Y") > nowDate:
                    nextMatchData['match_details'] = i
                    nextMatchData['status'] = True
                    break
        if not nextMatchData['match_details']:
            nextMatchData['status'] = False

    except Exception as e:
        nextMatchData['status'] = False
        nextMatchData['error_message'] = str(e)
    
    return nextMatchData

def findNextMatchAgainstTeam(fixtures, countriesData, needleData):
    nextMatchData = {'status':'',
                     'match_details': {},
                     'error_message':''
        }
    # Find the next fixture against the given country
    logger.info('Processing Fixtures')
    try:
        for i in fixtures:
            # Continue only if there are matches for that day
            if i.get('host_team'):
                # Only find matches that are in the future
                nowDate = datetime.datetime.now()
                matchDate = str (i.get('month')) + '/' + str (i.get('day')) + '/' + str (i.get('year') )
                if datetime.datetime.strptime( matchDate ,"%m/%d/%Y") > nowDate:
                    if ( i.get('host_team').lower() == needleData.get('country').lower() or i.get('opposition_team').lower() == needleData.get('country').lower() ):
                        nextMatchData['match_details'] = i
                        nextMatchData['status'] = True
                        nextMatchData['match_details']['matchMonth'] = datetime.datetime.strptime( matchDate ,"%m/%d/%Y").strftime("%B")
                        break

        if nextMatchData.get('match_details'):
            for i in countriesData:
                if i.get('name') == nextMatchData['match_details'].get('host_team'):
                    nextMatchData['match_details']['host_team_flag'] = globalVars['flag_base_url'] + i.get('code') + '.png'
                    break
            for i in countriesData:
                if i.get('name') == nextMatchData['match_details'].get('opposition_team'):
                    nextMatchData['match_details']['opposition_team_flag'] = globalVars['flag_base_url'] + i.get('code') + '.png'
                    break
        else:
            nextMatchData['status'] = False
            nextMatchData['match_details']['no_team_flag'] = globalVars['flag_base_url'] +'no_team' + '.png'

    except Exception as e:
        nextMatchData['status'] = False
        nextMatchData['error_message'] = str(e)
        logger.error('ERROR: {0}'.format( str(e) ) )
  
    return nextMatchData


def lambda_handler(event, context):
    setGlobalVars()
    fixtures = read_from_file(globalVars['fixtures_filename'])
    countriesData = read_from_file(globalVars['countries_filename'])

    # logger.info('Event: {0}'.format( event ) )
    # For Testing
    if not event.get('country'):
        event = { 'country' : 'Bangladesh'}

    resp = findNextMatchAgainstTeam(fixtures, countriesData, event)
    print ( resp )
    # logger.info(json.dumps(resp, indent=4, sort_keys=True) )
    return resp

if __name__ == '__main__':
    lambda_handler({}, {})