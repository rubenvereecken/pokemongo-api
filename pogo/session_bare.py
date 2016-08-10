# Load Generated Protobuf
from POGOProtos.Networking.Requests import Request_pb2
from POGOProtos.Networking.Envelopes import Unknown6_pb2
from POGOProtos.Networking.Envelopes import Signature_pb2
from POGOProtos.Networking.Requests import RequestType_pb2
from POGOProtos.Networking.Envelopes import ResponseEnvelope_pb2
from POGOProtos.Networking.Envelopes import RequestEnvelope_pb2
from POGOProtos.Networking.Requests.Messages import GetInventoryMessage_pb2
from POGOProtos.Networking.Requests.Messages import DownloadSettingsMessage_pb2

# Load local
import api
from state import State
from inventory import Inventory

# Exceptions
from custom_exceptions import PogoServerException
from custom_exceptions import PogoResponseException
from custom_exceptions import PogoInventoryException
from custom_exceptions import PogoRateException
from google.protobuf.message import DecodeError

# Utils
from util import hashLocation, hashRequests, hashSignature, getMs

# Pacakges
import os
import requests
import logging

# Hide errors (Yes this is terrible, but prettier)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'


class PogoSessionBare(object):

    def __init__(
        self, session, authProvider,
        accessToken, location, encrypt_lib,
        old=None
    ):
        self.session = session
        self.authProvider = authProvider
        self.accessToken = accessToken
        self.location = location
        if self.location.noop:
            logging.info("Limited functionality. No location provided")

        # Set up Inventory
        if old is None:
            self._inventory = old.inventory
            self._state = old._state

        # Start fresh
        else:
            self._inventory = None
            self._state = State()

        self._start = getMs()
        self._encryptLib = encrypt_lib

        self.authTicket = None
        self.endpoint = None
        self.endpoint = self.formatEndpoint(self.createApiEndpoint())

    def __str__(self):
        s = 'Access Token: {0}\nEndpoint: {1}\nLocation: {2}'.format(
            self.accessToken,
            self.endpoint,
            self.location
        )
        return s

    @staticmethod
    def formatEndpoint(endpoint):
        return 'https://{0}/rpc'.format(
            endpoint
        )

    def setCoordinates(self, latitude, longitude):
        self.location.setCoordinates(latitude, longitude)
        self.getMapObjects(radius=1)

    def getCoordinates(self):
        return self.location.getCoordinates()

    def createApiEndpoint(self):
        payload = []
        msg = Request_pb2.Request(
            request_type=RequestType_pb2.GET_PLAYER
        )
        payload.append(msg)
        req = self.wrapInRequest(payload)
        res = self.request(req, API_URL)
        if res is None:
            logging.critical('Servers seem to be busy. Exiting.')
            raise Exception('Could not connect to servers')

        return res.api_url

    def wrapInRequest(self, payload, defaults=True):

        # Grab coords
        latitude, longitude, altitude = self.getCoordinates()

        # Add requests
        if defaults:
            payload += self.getDefaults()

        # If we haven't authenticated before
        info = None
        signature = None
        if not self.authTicket:
            info = RequestEnvelope_pb2.RequestEnvelope.AuthInfo(
                provider=self.authProvider,
                token=RequestEnvelope_pb2.RequestEnvelope.AuthInfo.JWT(
                    contents=self.accessToken,
                    unknown2=59
                )
            )

        # Otherwise build signature
        elif self._encryptLib:

            # Generate hashes
            hashA, hashB = hashLocation(
                self.authTicket,
                latitude,
                longitude,
                altitude
            )

            # Build and hash signature
            proto = Signature_pb2.Signature(
                location_hash1=hashA,
                location_hash2=hashB,
                unknown22=os.urandom(32),
                timestamp=getMs(),
                timestamp_since_start=getMs() - self._start,
                request_hash=hashRequests(self.authTicket, payload)
            )

            signature = hashSignature(proto, self._encryptLib)

        # Build Envelope
        req = RequestEnvelope_pb2.RequestEnvelope(
            status_code=2,
            request_id=api.getRPCId(),
            unknown6=Unknown6_pb2.Unknown6(
                request_type=6,
                unknown2=Unknown6_pb2.Unknown6.Unknown2(
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
        rawResponse = self.session.post(url, data=req.SerializeToString())

        # Parse it out
        res = ResponseEnvelope_pb2.ResponseEnvelope()
        res.ParseFromString(rawResponse.content)

        # Update Auth ticket if it exists
        if res.auth_ticket.start:
            self.authTicket = res.auth_ticket

        return res

    def request(self, req, url=None):
        try:
            return self.requestOrThrow(req, url)
        except DecodeError as e:
            raise PogoResponseException("Malformed Response Evelope")
        except Exception as e:
            logging.error(e)
            raise PogoServerException('Probably server fires.')

    def wrapAndRequest(self, payload, defaults=True):
        res = self.request(self.wrapInRequest(payload, defaults=defaults))
        if res is None:
            logging.critical(res)
            logging.critical('Servers seem to be busy. Exiting.')
            raise Exception('No Valid Response.')

        # Try again.
        if res.status_code == 53:
            self.endpoint = self.formatEndpoint(res.api_url)
            logging.info('Using new endpoint...')
            # Does python somehow fanagle tail recursion optimization?
            # Hopefully won't result in a stack overflow
            return self.wrapAndRequest(payload, defaults=defaults)

        # Rate Limited
        if res.status_code == 52:
            raise PogoRateException('Request frequency exceeds rate limit.')

        if defaults:
            self.parseDefault(res)

        return res

    @staticmethod
    def getDefaults():
        # Allocate for 4 default requests
        data = [None, ] * 4

        # Create Egg request
        data[0] = Request_pb2.Request(
            request_type=RequestType_pb2.GET_HATCHED_EGGS
        )

        # Create Inventory Request
        data[1] = Request_pb2.Request(
            request_type=RequestType_pb2.GET_INVENTORY,
            request_message=GetInventoryMessage_pb2.GetInventoryMessage(
                last_timestamp_ms=0
            ).SerializeToString()
        )

        # Create Badge request
        data[2] = Request_pb2.Request(
            request_type=RequestType_pb2.CHECK_AWARDED_BADGES
        )

        # Create Settings request
        data[3] = Request_pb2.Request(
            request_type=RequestType_pb2.DOWNLOAD_SETTINGS,
            request_message=DownloadSettingsMessage_pb2.DownloadSettingsMessage(
                hash="4a2e9bc330dae60e7b74fc85b98868ab4700802e"
            ).SerializeToString()
        )

        return data

    # Parse the default responses
    def parseDefault(self, res):
        l = len(res.returns)
        if l < 5:
            logging.error(res)
            raise PogoResponseException("Expected response not returned")

        try:
            self._state.eggs.ParseFromString(res.returns[l - 4])
            self._state.inventory.ParseFromString(res.returns[l - 3])
            self._state.badges.ParseFromString(res.returns[l - 2])
            self._state.settings.ParseFromString(res.returns[l - 1])
        except Exception as e:
            logging.error(e)
            raise PogoResponseException("Error parsing response. Malformed response")

        # Finally make inventory usable
        item = self._state.inventory.inventory_delta.inventory_items
        self._inventory = Inventory(item)

    # Check, so we don't have to start another request
    def _verifyInventory(self, attribute):
        if self._inventory is None:
            raise PogoInventoryException("Please initialize Inventory before access.")
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
