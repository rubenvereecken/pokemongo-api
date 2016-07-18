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
from Networking.Requests.Messages import GetInventoryMessage_pb2
from Networking.Requests.Messages import FortSearchMessage_pb2
from Networking.Requests.Messages import DownloadSettingsMessage_pb2
from Networking.Responses import CheckAwardedBadgesResponse_pb2
from Networking.Responses import DownloadSettingsResponse_pb2
from Networking.Responses import GetHatchedEggsResponse_pb2
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
        req = Envelopes_pb2.Envelopes.RequestEnvelope(
            auth_info = Envelopes_pb2.Envelopes.RequestEnvelope.AuthInfo(
                provider = self.authProvider,
                token = Envelopes_pb2.Envelopes.RequestEnvelope.AuthInfo.JWT(
                    contents = self.accessToken,
                    unknown2 = 59
                )
            )
        )

        # Build Envelope
        req.status_code = 2
        req.request_id = api.getRPCId()
        req.latitude, req.longitude, req.altitude = location.encodeLocation(self.location)
        req.unknown12 = 18446744071615
        req.requests.extend(payload)

        return req

    def requestOrThrow(self, req, url=None):
        if url is None:
            url = self.endpoint

        rawResponse = self.session.post(url, data=req.SerializeToString())

        res = Envelopes_pb2.Envelopes.ResponseEnvelope()
        res.ParseFromString(rawResponse.content)

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
        msg = Request_pb2.Request(
            request_type = RequestType_pb2.CHECK_AWARDED_BADGES
        )
        payload.append(msg)
        res = self.wrapAndRequest(payload)
        data = GetHatchedEggsResponse_pb2.GetHatchedEggsResponse()
        data.ParseFromString(res.res.returns[0])
        return data

    # Returns Settings Query
    def getDownloadSettings(self):
        msg = Request_pb2.Request(
            request_type = RequestType_pb2.DOWNLOAD_SETTINGS,
            request_message = DownloadSettingsMessage_pb2.DownloadSettingsMessage(
                hash = "4a2e9bc330dae60e7b74fc85b98868ab4700802e"
            ).SerializeToString()
        )
        payload.append(msg)
        res = self.wrapAndRequest(payload)
        data = DownloadSettingsResponse_pb2.DownloadSettingsResponse()
        data.ParseFromString(res.res.returns[0])
        return data
