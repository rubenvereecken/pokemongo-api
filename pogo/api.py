import requests
import re
import struct
import json
import argparse
import random
import logging

from proto import request_pb2

from session import PogoSession


API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'
LOGIN_URL = 'https://sso.pokemon.com/sso/login?service=https%3A%2F%2Fsso.pokemon.com%2Fsso%2Foauth2.0%2FcallbackAuthorize'
LOGIN_OAUTH = 'https://sso.pokemon.com/sso/oauth2.0/accessToken'
PTC_CLIENT_SECRET = 'w8ScCUXJQc6kXKw8FiOhd8Fixzht18Dq3PEVkUCP5ZPxtgyWsbTvWHFLm2wNY0JR'

RPC_ID = int(random.random() * 10 ** 15)

def getRPCId():
    global RPC_ID
    RPC_ID = RPC_ID + 1
    return RPC_ID

def createSession():
    session = requests.session()
    session.headers = {
        'User-Agent': 'Niantic App',
    }
    session.verify = False
    return session

def createGoogleSession(username, pw):
    logging.info('Creating Google session for {}'.format(username))
    raise NotImplemented()


def createPTCSession(username, pw, startLocation):
    session = createSession()
    r = session.get(LOGIN_URL)
    jdata = json.loads(r.content)
    data = {
        'lt': jdata['lt'],
        'execution': jdata['execution'],
        '_eventId': 'submit',
        'username': username,
        'password': pw,
    }
    authResponse = session.post(LOGIN_URL, data=data)

    ticket = None
    try:
        ticket = re.sub('.*ticket=', '', authResponse.history[0].headers['Location'])
    except Exception as e:
        if DEBUG:
            print(authResponse.json()['errors'][0])
        return None

    data1 = {
        'client_id': 'mobile-app_pokemon-go',
        'redirect_uri': 'https://www.nianticlabs.com/pokemongo/error',
        'client_secret': PTC_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'code': ticket,
    }
    r2 = session.post(LOGIN_OAUTH, data=data1)
    access_token = re.sub('&expires.*', '', r2.content)
    access_token = re.sub('.*access_token=', '', access_token)

    loc = location.getLocation(startLocation)

    if access_token:
        return PogoSession(session, access_token, loc)
    else:
        return None
