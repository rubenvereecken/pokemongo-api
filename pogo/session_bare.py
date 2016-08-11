# Load Generated Protobuf
from POGOProtos.Networking.Envelopes import (
    Unknown6_pb2 as Unknown6,
    Signature_pb2 as Signature,
    ResponseEnvelope_pb2 as ResponseEnvelope,
    RequestEnvelope_pb2 as RequestEnvelope
)
from POGOProtos.Networking.Requests import (
    RequestType_pb2 as RequestType,
    Request_pb2 as Request
)
from POGOProtos.Networking.Requests.Messages import (
    GetInventoryMessage_pb2 as GetInventoryMessage,
    DownloadSettingsMessage_pb2 as DownloadSettingsMessage
)

# Load local
from pogo.state import State
from pogo.inventory import Inventory

# Exceptions
from pogo.custom_exceptions import (
    PogoServerException,
    PogoResponseException,
    PogoInventoryException,
    PogoRateException
)
from google.protobuf.message import DecodeError

# Utils
from pogo.util import hashLocation, hashRequests, hashSignature, getMs

# Pacakges
import os
import requests
import logging
import random

# Hide errors (Yes this is terrible, but prettier)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Constants
API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'
RPC_ID = int(random.random() * 10 ** 12)

# Error messages
ERROR_CONNECT = 'Could not connect to servers'
ERROR_RESPONSE = 'Malformed Response Evelope'
ERROR_SERVER = 'Probably server fires.'
ERROR_VALID = 'No Valid Response.'
ERROR_RETURN = 'Error parsing response. Malformed response'
ERROR_PROTO = 'Expected response not returned'
ERROR_INVENTORY = 'Please initialize Inventory before access.'
ERROR_RATE = 'Request frequency exceeds rate limit.'

# Notices
NO_ENCRYPTION_NOTICE = (
    "NOTICE:\n"
    "You have not specified a path for the Encryption Library\n"
    "As such, your functionality will be limited- requests may\n"
    "return blank or all together fail. To provide a library from\n"
    "demo.py, specify the -e flag e.g. -e'encrpyt.dll'"
)
NO_LOCATION_NOTICE = "Limited functionality. No location provided"


class PogoSessionBare(object):
    """ Core session class for creating requests"""

    def __init__(self, authSession, location, old=None):
        self._authSession = authSession
        self._location = location
        if self._location.noop:
            logging.warning(NO_LOCATION_NOTICE)

        # Set up Inventory
        if old is not None:
            self._inventory = old.inventory
            self._state = old._state

        # Start fresh
        else:
            self._inventory = None
            self._state = State()

        self._start = getMs()
        self._authTicket = None
        self._session = self._authSession.requestSession
        self._endpoint = self.formatEndpoint(self.createApiEndpoint())

        if self.encryptLib is None:
            logging.warning(NO_ENCRYPTION_NOTICE)

    def __str__(self):
        s = 'Access Token: {0}\nEndpoint: {1}\nLocation: {2}'.format(
            self.accessToken,
            self.endpoint,
            self.location
        )
        return s

    # Session related Properties
    @property
    def authSession(self):
        return self._authSession

    @property
    def location(self):
        return self._location

    @property
    def authTicket(self):
        return self._authTicket

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def encryptLib(self):
        return self._authSession.encryptLib

    @property
    def accessToken(self):
        return self._authSession.accessToken

    @property
    def authProvider(self):
        return self._authSession.provider

    # Properties for defaults
    # Check, so we don't have to start another request
    def _verifyInventory(self, attribute):
        if self._inventory is None:
            raise PogoInventoryException(ERROR_INVENTORY)
        return attribute

    @property
    def eggs(self):
        return self._verifyInventory(self._state.eggs)

    @property
    def inventory(self):
        return self._verifyInventory(self._inventory)

    @property
    def badges(self):
        return self._verifyInventory(self._state.badges)

    @property
    def downloadSettings(self):
        return self._verifyInventory(self._state.settings)

    # Statics
    @staticmethod
    def formatEndpoint(endpoint):
        return 'https://{0}/rpc'.format(
            endpoint
        )

    @staticmethod
    def getRPCId():
        global RPC_ID
        RPC_ID = RPC_ID + 1
        return RPC_ID

    def createApiEndpoint(self):
        payload = []
        msg = Request.Request(
            request_type=RequestType.GET_PLAYER
        )
        payload.append(msg)
        req = self.wrapInRequest(payload)
        res = self.request(req, API_URL)
        if res is None:
            logging.critical('Servers seem to be busy. Exiting.')
            raise Exception(ERROR_CONNECT)

        return res.api_url

    def setCoordinates(self, latitude, longitude):
        self.location.setCoordinates(latitude, longitude)
        self.getMapObjects(radius=1)

    def getCoordinates(self):
        return self.location.getCoordinates()

    def wrapInRequest(self, payload, defaults=True):

        # Grab coords
        latitude, longitude, altitude = self.getCoordinates()

        # Add requests
        if defaults:
            payload += self.getDefaults()

        # If we haven't authenticated before
        info = None
        signature = None
        if self.authTicket is None:
            info = RequestEnvelope.RequestEnvelope.AuthInfo(
                provider=self.authProvider,
                token=RequestEnvelope.RequestEnvelope.AuthInfo.JWT(
                    contents=self.accessToken,
                    unknown2=59
                )
            )

        # Otherwise build signature
        elif self.encryptLib and not self.location.noop:

            # Generate hashes
            hashA, hashB = hashLocation(
                self.authTicket,
                latitude,
                longitude,
                altitude
            )

            # Build and hash signature
            proto = Signature.Signature(
                location_hash1=hashA,
                location_hash2=hashB,
                unknown22=os.urandom(32),
                timestamp=getMs(),
                timestamp_since_start=getMs() - self._start,
                request_hash=hashRequests(self.authTicket, payload)
            )

            signature = hashSignature(proto, self.encryptLib)

        # Build Envelope
        req = RequestEnvelope.RequestEnvelope(
            status_code=2,
            request_id=PogoSessionBare.getRPCId(),
            unknown6=Unknown6.Unknown6(
                request_type=6,
                unknown2=Unknown6.Unknown6.Unknown2(
                    encrypted_signature=signature
                )
            ),
            longitude=longitude,
            latitude=latitude,
            altitude=altitude,
            auth_ticket=self.authTicket,
            unknown12=741,
            auth_info=info
        )

        req.requests.extend(payload)

        return req

    def requestOrThrow(self, req, url=None):
        if url is None:
            url = self.endpoint

        # Send request
        rawResponse = self._session.post(url, data=req.SerializeToString())

        # Parse it out
        res = ResponseEnvelope.ResponseEnvelope()
        res.ParseFromString(rawResponse.content)

        # Update Auth ticket if it exists
        if res.auth_ticket.start:
            self._authTicket = res.auth_ticket

        return res

    def request(self, req, url=None):
        try:
            return self.requestOrThrow(req, url)
        except DecodeError as e:
            raise PogoResponseException(ERROR_RESPONSE)
            logging.error(e)
        except Exception as e:
            raise PogoServerException(ERROR_SERVER)
            logging.error(e)

    def wrapAndRequest(self, payload, defaults=True):
        res = self.request(self.wrapInRequest(payload, defaults=defaults))
        if res is None:
            logging.critical(res)
            logging.critical('Servers seem to be busy. Exiting.')
            raise Exception(ERROR_CONNECT)

        # Try again.
        if res.status_code == 53:
            self.endpoint = self.formatEndpoint(res.api_url)
            logging.info('Using new endpoint...')
            # Does python somehow fanagle tail recursion optimization?
            # Hopefully won't result in a stack overflow
            return self.wrapAndRequest(payload, defaults=defaults)

        # Rate Limited
        if res.status_code == 52:
            raise PogoRateException(ERROR_RATE)

        if defaults:
            self.parseDefault(res)

        return res

    @staticmethod
    def getDefaults():
        # Allocate for 4 default requests
        data = [None, ] * 4

        # Create Egg request
        data[0] = Request.Request(
            request_type=RequestType.GET_HATCHED_EGGS
        )

        # Create Inventory Request
        data[1] = Request.Request(
            request_type=RequestType.GET_INVENTORY,
            request_message=GetInventoryMessage.GetInventoryMessage(
                last_timestamp_ms=0
            ).SerializeToString()
        )

        # Create Badge request
        data[2] = Request.Request(
            request_type=RequestType.CHECK_AWARDED_BADGES
        )

        # Create Settings request
        data[3] = Request.Request(
            request_type=RequestType.DOWNLOAD_SETTINGS,
            request_message=DownloadSettingsMessage.DownloadSettingsMessage(
                hash="4a2e9bc330dae60e7b74fc85b98868ab4700802e"
            ).SerializeToString()
        )

        return data

    # Parse the default responses
    def parseDefault(self, res):
        l = len(res.returns)
        if l < 5:
            logging.error(res)
            raise PogoResponseException(ERROR_PROTO)

        try:
            self._state.eggs.ParseFromString(res.returns[l - 4])
            self._state.inventory.ParseFromString(res.returns[l - 3])
            self._state.badges.ParseFromString(res.returns[l - 2])
            self._state.settings.ParseFromString(res.returns[l - 1])
        except Exception as e:
            logging.error(e)
            raise PogoResponseException(ERROR_RETURN)

        # Finally make inventory usable
        item = self._state.inventory.inventory_delta.inventory_items
        self._inventory = Inventory(item)
