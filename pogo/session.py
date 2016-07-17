import requests
import logging
import sys

from proto import request_pb2

API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'

class PogoSession(object):
    def __init__(self, session, authProvider, accessToken, location=None):
        self.session = session
        self.authProvider = authProvider
        self.accessToken = accessToken
        self.location = location
        self.endpoint = createApiEndpoint()


    def __str__(self):
        s = 'Access Token: {}\nEndpoint: {}\nLocation: {}'.format(self.accessToken,
                self.endpoint, self.location)
        return s

    def setLocation(self, loc):
        self.location = loc
        
    def createApiEndpoint(self):
        messages = []
        messages.append(request_pb2.Message().type = request_pb2.Message.Type.REQUEST_ENDPOINT)
        req = self.wrapInRequest(messages);
        res = self.request(req)
        if res is None:
            logging.critical('Servers seem to be busy. Exiting.')
            sys.exit(-1)
        return res.api_url
        

    def wrapInRequest(self, messages):
        req = request_pb2.Request()
        req.messages.extend(messages)
        req.type = request_pb2.Request.Type.TWO
        req.rpc_id = getRPCId()

        req.latitude, req.longitude, req.altitude = encodeLocation(location)

        req.unknown12 = 18446744073709551615

        req.auth.provider = self.authProvider
        req.auth.token.contents = self.accessToken
        req.auth.token.unknown13 = 59

        return req

    def request(req):
        try:
            rawResponse = self.session.post(API_URL, data=req.SerializeToString())
            response = pokemon_pb2.Response()
            response.ParseFromString(rawResponse.content)
            return response
        except Exception, e:
            logging.error(e)
            return None
