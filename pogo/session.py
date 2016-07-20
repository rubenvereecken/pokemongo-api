import requests
import logging
import sys

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import proto
from Networking.Envelopes import ResponseEnvelope_pb2
from Networking.Envelopes import RequestEnvelope_pb2
from Networking.Requests import Request_pb2
from Networking.Requests import RequestType_pb2
from Networking.Requests.Messages import DownloadSettingsMessage_pb2
from Networking.Requests.Messages import GetInventoryMessage_pb2
from Networking.Requests.Messages import GetMapObjectsMessage_pb2

import location
from util import getMs
from state import State

API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'

class PogoSession(object):

    def __init__(self, session, authProvider, accessToken, loc):
        self.session = session
        self.authProvider = authProvider
        self.accessToken = accessToken
        self.location = loc
        self.state = State()

        self.authTicket = None
        self.endpoint = None
        self.endpoint = 'https://' + self.createApiEndpoint() + '/rpc'

    def __str__(self):
        s = 'Access Token: {}\nEndpoint: {}\nLocation: {}'.format(self.accessToken,
                self.endpoint, self.location)
        return s

    def setLocation(self, loc):
        self.location = loc

    def getLocation(self):
        return self.location.latitude, self.location.longitude, self.location.altitude

    def createApiEndpoint(self):
        payload = []
        msg = Request_pb2.Request(
            request_type = RequestType_pb2.GET_PLAYER
        )
        payload.append(msg)
        req = self.wrapInRequest(payload)
        res = self.request(req, API_URL)
        if res is None:
            logging.critical('Servers seem to be busy. Exiting.')
            raise Exception('Could not connect to servers')

        return res.api_url

    def wrapInRequest(self, payload):

        # If we haven't authenticated before
        info = None
        if(not self.authTicket):
            info = RequestEnvelope_pb2.RequestEnvelope.AuthInfo(
                provider = self.authProvider,
                token = RequestEnvelope_pb2.RequestEnvelope.AuthInfo.JWT(
                    contents = self.accessToken,
                    unknown2 = 59
                )
            )

        # Build Envelope
        latitude, longitude, altitude = self.getLocation()
        req = RequestEnvelope_pb2.RequestEnvelope(
            status_code = 2,
            request_id = 1469378659230941192,#api.getRPCId(),
            longitude = longitude,
            latitude = latitude,
            altitude = altitude,
            auth_ticket = self.authTicket,
            unknown12 = 989,
            auth_info = info
        )

        # Add requests
        payload += self.getDefaults()
        req.requests.extend(payload)

        return req

    def requestOrThrow(self, req, url=None):
        if url is None:
            url = self.endpoint

        rawResponse = self.session.post(url, data=req.SerializeToString())

        # Parse it out
        res = ResponseEnvelope_pb2.ResponseEnvelope()
        res.ParseFromString(rawResponse.content)

        # Update Auth ticket if it exists
        if(res.auth_ticket.start):
            self.authTicket = res.auth_ticket

        return res

    def request(self, req, url=None):
        try:
            return self.requestOrThrow(req, url)
        except Exception as e:
            logging.error(e)
            raise

    def wrapAndRequest(self, payload):
        res = self.request(self.wrapInRequest(payload))
        self.parseDefault(res)
        if res is None:
            logging.critical('Servers seem to be busy. Exiting.')
            sys.exit(-1)
        # logging.debug('{} payloads'.format(len(res.payload)))
        # logging.debug('payload has data?  {}'.format(res.payload[0].HasField('data')))
        return res

    def getDefaults(self):
        # Allocate for 4 default requests
        data = [None,] * 4

        # Create Egg request
        data[0] = Request_pb2.Request(
            request_type=RequestType_pb2.GET_HATCHED_EGGS
        )

        # Create Inventory Request
        data[1] = Request_pb2.Request(
            request_type = RequestType_pb2.GET_INVENTORY,
            request_message = GetInventoryMessage_pb2.GetInventoryMessage(
                last_timestamp_ms = getMs()
            ).SerializeToString()
        )

        # Create Badge request
        data[2] = Request_pb2.Request(
            request_type = RequestType_pb2.CHECK_AWARDED_BADGES
        )

        # Create Settings request
        data[3] = Request_pb2.Request(
            request_type = RequestType_pb2.DOWNLOAD_SETTINGS,
            request_message = DownloadSettingsMessage_pb2.DownloadSettingsMessage(
                hash = "4a2e9bc330dae60e7b74fc85b98868ab4700802e"
            ).SerializeToString()
        )

        return data

    # Parse the default responses
    def parseDefault(self, res, isGeneral=False):
        self.state.eggs.ParseFromString(res.returns[0])
        self.state.inventory.ParseFromString(res.returns[1])
        self.state.badges.ParseFromString(res.returns[2])
        self.state.settings.ParseFromString(res.returns[3])

    # Get profile
    def getProfile(self):
        # Create profile request
        payload = [Request_pb2.Request(
            request_type = RequestType_pb2.GET_PLAYER
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self.state.profile.ParseFromString(res.returns[0])

        # Return everything
        return self.state.profile

    # Get Location
    def getMapObjects(self, radius = 10):
        # Work out location details
        cells = location.getCells(self.location, radius)
        latitude, longitude, altitude = self.getLocation()
        timestamps = [0,] * len(cells)

        # Create request
        payload = [Request_pb2.Request(
            request_type = RequestType_pb2.GET_MAP_OBJECTS,
            request_message = GetMapObjectsMessage_pb2.GetMapObjectsMessage(
                cell_id = cells,
                since_timestamp_ms = timestamps,
                latitude = latitude,
                longitude = longitude
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self.state.location.ParseFromString(res.returns[0])

        # Return everything
        return self.state.location
