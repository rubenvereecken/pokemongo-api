import requests
import re
import json
import random
import logging

from session import PogoSession
import location

from gpsoauth import perform_master_login, perform_oauth

API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'
LOGIN_URL = 'https://sso.pokemon.com/sso/login?service=https%3A%2F%2Fsso.pokemon.com%2Fsso%2Foauth2.0%2FcallbackAuthorize'
LOGIN_OAUTH = 'https://sso.pokemon.com/sso/oauth2.0/accessToken'
PTC_CLIENT_SECRET = 'w8ScCUXJQc6kXKw8FiOhd8Fixzht18Dq3PEVkUCP5ZPxtgyWsbTvWHFLm2wNY0JR'

ANDROID_ID = '9774d56d682e549c'
SERVICE= 'audience:server:client_id:848232511240-7so421jotr2609rmqakceuu1luuq0ptb.apps.googleusercontent.com'
APP = 'com.nianticlabs.pokemongo'
CLIENT_SIG = '321187995bc7cdc2b5fc91b11a96e2baa8602c62'

RPC_ID = int(random.random() * 10 ** 12)

def getRPCId():
    global RPC_ID
    RPC_ID = RPC_ID + 1
    return RPC_ID

def createRequestsSession():
    session = requests.session()
    session.headers = {
        'User-Agent': 'Niantic App',
    }
    session.verify = False
    return session

def createPogoSession(session, provider, access_token, loc):
    loc = location.getLocation(loc)
    if loc:
        logging.info('Location: {}'.format(loc.address))
        logging.info('Coordinates: {} {} {}'.format(loc.latitude, loc.longitude,
            loc.altitude))

    if access_token and loc:
        return PogoSession(session, provider, access_token, loc)
    elif loc is None:
        logging.critical('Location not found')
    elif access_token is None:
        logging.critical('Access token not generated')
    return None

def createGoogleSession(username, pw, startLocation):
    session = createRequestsSession()
    logging.info('Creating Google session for {}'.format(username))

    r1 = perform_master_login(username, pw, ANDROID_ID)
    r2 = perform_oauth(username, r1.get('Token', ''), ANDROID_ID, SERVICE, APP,
        CLIENT_SIG)

    access_token = r2.get('Auth') # access token
    return createPogoSession(session, 'google', access_token, startLocation)

def createPTCSession(username, pw, startLocation):
    session = createRequestsSession()
    logging.info('Creating PTC session for {}'.format(username))
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
    except:
        logging.error(authResponse.json()['errors'][0])
        raise

    data1 = {
        'client_id': 'mobile-app_pokemon-go',
        'redirect_uri': 'https://www.nianticlabs.com/pokemongo/error',
        'client_secret': PTC_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'code': ticket,
    }
    r2 = session.post(LOGIN_OAUTH, data=data1)
    access_token = re.sub('&expires.*', '', r2.content.decode('utf-8'))
    access_token = re.sub('.*access_token=', '', access_token)

    return createPogoSession(session, 'ptc', access_token, startLocation)

        