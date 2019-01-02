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
        globalVars['fixtures_filename']     = "./data/india_fixtures_data.json"
    except KeyError as e:
        logger.error("Unable to set Global Environment variables. Exiting")
        logger.error('ERROR: {0}'.format( str(e) ) )
        exit
    return globalVars


def read_from_file(filename):
    with open(filename) as json_file:
        data = json.load(json_file, parse_float = Decimal)
    return data

def getNextMatch(fixtures):
    nowDate = datetime.datetime.now()
    #pdb.set_trace()

    nextMatchData = {'status':'',
                     'match_details':{},
                     'error_message':''
        }

    try:
        for i in fixtures:
            if i.get('host_team'):
                matchDate = str (i.get('day')) + '/' + str (i.get('month')) + '/' + str (i.get('year') )
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

def findNextMatchAgainstTeam(fixtures, needleData):
    nextMatchData = {'status':'',
                     'match_details':{},
                     'error_message':''
        }
    try:
        for i in fixtures:
            if ( ( i.get('host_team') == needleData.get('country') or i.get('opposition_team') == needleData.get('country') ) and (not i.get('is_ongoing_match')) ):
                nextMatchData['match_details'] = i
                nextMatchData['status'] = True
                break
        if not nextMatchData['match_details']:
            nextMatchData['status'] = False

    except Exception as e:
        nextMatchData['status'] = False
        nextMatchData['error_message'] = str(e)
    
    return nextMatchData


def lambda_handler(event, context):
    setGlobalVars()
    india_fixtures = read_from_file(globalVars['fixtures_filename'])

    needleData = { 'country' : 'New Zealand',
                    'at_home': True }

    print ( findNextMatchAgainstTeam(india_fixtures, needleData) )
    return getNextMatch(india_fixtures)

if __name__ == '__main__':
    lambda_handler({}, {})