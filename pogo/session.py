import requests
import logging
import sys

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import proto
from proto import LocalPlayer_pb2
from Networking import Envelopes_pb2
from Networking.Requests import Request_pb2
from Networking.Requests import RequestType_pb2
from Networking.Requests.Messages import DownloadSettingsMessage_pb2
from Networking.Requests.Messages import GetInventoryMessage_pb2
from Networking.Requests.Messages import FortSearchMessage_pb2
from Networking.Requests.Messages import GetMapObjectsMessage_pb2
from Networking.Responses import CheckAwardedBadgesResponse_pb2
from Networking.Responses import DownloadSettingsResponse_pb2
from Networking.Responses import GetHatchedEggsResponse_pb2
from Networking.Responses import GetMapObjectsResponse_pb2
from Networking.Responses import GetPlayerResponse_pb2

import api
import location
from util import getMs

API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'

class PogoSession(object):

    def __init__(self, session, authProvider, accessToken, loc):
        self.session = session
        self.authProvider = authProvider
        self.accessToken = accessToken
        self.location = loc
        self.authTicket = None
        self.endpoint = None
        self.endpoint = 'https://' + self.createApiEndpoint() + '/rpc'

    def __str__(self):
        s = 'Access Token: {}\nEndpoint: {}\nLocation: {}'.format(self.accessToken,
                self.endpoint, self.location)
        return s

    def setLocation(self, loc):
        self.location = loc
        
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
            sys.exit(-1)

        return res.api_url

    def wrapInRequest(self, payload):

        # If we haven't authenticated before
        info = None
        if(not self.authTicket):
            info = Envelopes_pb2.Envelopes.RequestEnvelope.AuthInfo(
                provider = self.authProvider,
                token = Envelopes_pb2.Envelopes.RequestEnvelope.AuthInfo.JWT(
                    contents = self.accessToken,
                    unknown2 = 59
                )
            )

        # Build Envelope
        latitude, longitude, altitude = location.encodeLocation(self.location)
        req = Envelopes_pb2.Envelopes.RequestEnvelope(
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
        req.requests.extend(payload)

        print(req)
        return req

    def requestOrThrow(self, req, url=None):
        if url is None:
            url = self.endpoint

        rawResponse = self.session.post(url, data=req.SerializeToString())

        # Parse it out
        res = Envelopes_pb2.Envelopes.ResponseEnvelope()
        res.ParseFromString(rawResponse.content)

        # Update Auth ticket if it exists
        if(res.auth_ticket.start):
            self.authTicket = res.auth_ticket

        return res

    def request(self, req, url=None):
        try:
            return self.requestOrThrow(req, url)
        except Exception, e:
            logging.error(e)
            return None
        
    def wrapAndRequest(self, payload):
        res = self.request(self.wrapInRequest(payload))
        if res is None:
            logging.critical('Servers seem to be busy. Exiting.')
            sys.exit(-1)
        # logging.debug('{} payloads'.format(len(res.payload)))
        # logging.debug('payload has data?  {}'.format(res.payload[0].HasField('data')))
        return res

    # Returns profile
    def getProfile(self):
        payload = []
        msg = Request_pb2.Request(
            request_type = RequestType_pb2.GET_PLAYER
        )
        payload.append(msg)
        res = self.wrapAndRequest(payload)
        data = GetPlayerResponse_pb2.GetPlayerResponse()
        data.ParseFromString(res.returns[0])
        return data

    # Returns egg query
    def getEggs(self):
        payload = []
        msg = Request_pb2.Request(
            request_type=RequestType_pb2.GET_HATCHED_EGGS
        )
        payload.append(msg)
        res = self.wrapAndRequest(payload)
        data = GetHatchedEggsResponse_pb2.GetHatchedEggsResponse()
        data.ParseFromString(res.returns[0])
        return data
    
    #Returns inventory query
    def getInventory(self):
        payload = []
        msg = Request_pb2.Request(
            request_type = RequestType_pb2.GET_INVENTORY,
            request_message = GetInventoryMessage_pb2.GetInventoryMessage(
                timestamp_ms = getMs()
            ).SerializeToString()
        )
        payload.append(msg)
        res = self.wrapAndRequest(payload)
        data = GetHatchedEggsResponse_pb2.GetHatchedEggsResponse()
        data.ParseFromString(res.returns[0])
        return data

    # Returns Badge Query
    def getBadges(self):
        payload = []
        msg = Request_pb2.Request(
            request_type = RequestType_pb2.CHECK_AWARDED_BADGES
        )
        payload.append(msg)
        res = self.wrapAndRequest(payload)
        data = GetHatchedEggsResponse_pb2.GetHatchedEggsResponse()
        data.ParseFromString(res.returns[0])
        return data

    # Returns Settings Query
    def getDownloadSettings(self):
        payload = []
        msg = Request_pb2.Request(
            request_type = RequestType_pb2.DOWNLOAD_SETTINGS,
            request_message = DownloadSettingsMessage_pb2.DownloadSettingsMessage(
                hash = "4a2e9bc330dae60e7b74fc85b98868ab4700802e"
            ).SerializeToString()
        )
        payload.append(msg)
        res = self.wrapAndRequest(payload)
        data = DownloadSettingsResponse_pb2.DownloadSettingsResponse()
        data.ParseFromString(res.returns[0])
        return data

    # Get Location
    def getLocation(self, radius = 10):
        payload = []
        cells = location.getCells(self.location, radius)
        latitude, longitude, altitude = location.encodeLocation(self.location)
        timestamps = [0,] * len(cells)
        msg = Request_pb2.Request(
            request_type = RequestType_pb2.GET_MAP_OBJECTS,
            request_message = GetMapObjectsMessage_pb2.GetMapObjectsMessage(
                cell_id = cells,
                since_timestamp_ms = timestamps,
                latitude = latitude,
                longitude = longitude
            ).SerializeToString()
        )
        payload.append(msg)
        res = self.wrapAndRequest(payload)
        data = GetMapObjectsResponse_pb2.GetMapObjectsResponse()
        data.ParseFromString(res.returns[0])
        return data