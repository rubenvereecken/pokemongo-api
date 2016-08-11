import logging
import json
import requests
import re

from pogo.session import PogoSession
from pogo.location import Location

from gpsoauth import perform_master_login
from gpsoauth import perform_oauth

# Callbacks and Constants
LOGIN_OAUTH = 'https://sso.pokemon.com/sso/oauth2.0/accessToken'
API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'
CLIENT_SIG = '321187995bc7cdc2b5fc91b11a96e2baa8602c62'
APP = 'com.nianticlabs.pokemongo'
ANDROID_ID = '9774d56d682e549c'
LOGIN_URL = (
    'https://sso.pokemon.com/sso/login'
    '?service=https%3A%2F%2Fsso.pokemon.com'
    '%2Fsso%2Foauth2.0%2FcallbackAuthorize'
)
PTC_CLIENT_SECRET = (
    'w8ScCUXJQc6kXKw8FiOhd8Fixzht18Dq'
    '3PEVkUCP5ZPxtgyWsbTvWHFLm2wNY0JR'
)
SERVICE = (
    'audience:server:client_id:848232511240-7so421jotr'
    '2609rmqakceuu1luuq0ptb.apps.googleusercontent.com'
)


class PokeAuthSession(object):
    """Wrapper for initial Authentication"""

    _proxies = {}

    def __init__(
        self, username, password,
        provider='google', encrypt_lib=None, geo_key=None
    ):

        self.requestSession = self.createRequestsSession()
        self.provider = provider
        self.encryptLib = encrypt_lib

        # User credentials
        self.username = username
        self.password = password
        self.accessToken = ''

        self.geo_key = geo_key

    @staticmethod
    def setProxy(proxy):
        PokeAuthSession._proxies = {
            "http": proxy,
            "https": proxy
        }

    @staticmethod
    def createRequestsSession():
        requestSession = requests.session()
        requestSession.headers = {
            'User-Agent': 'Niantic App',
        }
        if PokeAuthSession._proxies:
            requestSession.proxies.update(PokeAuthSession._proxies)
        requestSession.verify = False
        return requestSession

    @staticmethod
    def parseToken(response):
        token = re.sub('&expires.*', '', response.content.decode('utf-8'))
        return re.sub('.*access_token=', '', token)

    @property
    def proxies(self):
        return self._proxies

    def createPogoSession(
        self, provider=None, locationLookup='',
        session=None, noop=False
    ):
        if self.provider:
            self.provider = provider

        # determine location
        location = None
        if noop:
            location = Location.noop()
        elif session:
            location = session.location
        elif locationLookup:
            location = Location(locationLookup, self.geo_key)
            logging.info(location)

        if self.accessToken and location:
            return PogoSession(self, location, old=session)

        # else something has gone wrong
        elif location is None:
            logging.critical('Location not found')
        elif self.accessToken is None:
            logging.critical('Access token not generated')
        return None

    def createGoogleSession(
        self, locationLookup=None, session=None, noop=False
    ):

        logging.info('Creating Google session for %s', self.username)

        r1 = perform_master_login(self.username, self.password, ANDROID_ID)
        r2 = perform_oauth(
            self.username,
            r1.get('Token', ''),
            ANDROID_ID,
            SERVICE,
            APP,
            CLIENT_SIG
        )

        self.accessToken = r2.get('Auth')  # access token
        return self.createPogoSession(
            provider='google',
            locationLookup=locationLookup,
            session=session,
            noop=noop
        )

    def createPTCSession(self, locationLookup=None, session=None, noop=False):
        instance = self.createRequestsSession()
        logging.info('Creating PTC session for %s', self.username)
        r = instance.get(LOGIN_URL)
        jdata = json.loads(r.content.decode())
        data = {
            'lt': jdata['lt'],
            'execution': jdata['execution'],
            '_eventId': 'submit',
            'username': self.username,
            'password': self.password,
        }
        authResponse = instance.post(LOGIN_URL, data=data)

        ticket = None
        try:
            ticket = re.sub(
                '.*ticket=',
                '',
                authResponse.history[0].headers['Location']
            )
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
        r2 = instance.post(LOGIN_OAUTH, data=data1)

        # Parse and format token
        self.accessToken = self.parseToken(r2)

        return self.createPogoSession(
            provider='ptc',
            locationLookup=locationLookup,
            session=session,
            noop=noop
        )

    def authenticate(self, locationLookup=None):
        """We already have all information, authenticate"""
        noop = locationLookup is None
        return {
            "google": self.createGoogleSession,
            "ptc": self.createPTCSession
        }[self.provider](locationLookup=locationLookup, noop=noop)

    def reauthenticate(self, session):
        """Reauthenticate from an old session"""
        return {
            "google": self.createGoogleSession,
            "ptc": self.createPTCSession
        }[self.provider](session=session)
