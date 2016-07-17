import requests
import logging
import sys

from proto import request_pb2, response_pb2
import api
import location

API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'

class PogoSession(object):
    def __init__(self, session, authProvider, accessToken, loc):
        self.session = session
        self.authProvider = authProvider
        self.accessToken = accessToken
        self.location = loc
        self.endpoint = self.createApiEndpoint()


    def __str__(self):
        s = 'Access Token: {}\nEndpoint: {}\nLocation: {}'.format(self.accessToken,
                self.endpoint, self.location)
        return s

    def setLocation(self, loc):
        self.location = loc
        
    def createApiEndpoint(self):
        payload = []
        msg = request_pb2.Request.Payload()
        msg.type = request_pb2.Request.Payload.Type.Value('REQUEST_ENDPOINT')
        payload.append(msg)
        req = self.wrapInRequest(payload);
        res = self.request(req)
        if res is None:
            logging.critical('Servers seem to be busy. Exiting.')
            sys.exit(-1)
        return res.endpoint
        

    def wrapInRequest(self, payload):
        req = request_pb2.Request()
        req.payload.extend(payload)
        req.type = request_pb2.Request.Type.Value('TWO')
        req.rpc_id = api.getRPCId()

        req.latitude, req.longitude, req.altitude = location.encodeLocation(self.location)

        req.unknown12 = 18446744071615

        req.auth.provider = self.authProvider
        req.auth.token.contents = self.accessToken
        req.auth.token.unknown13 = 59

        return req

    def request(self, req):
        try:
            rawResponse = self.session.post(API_URL, data=req.SerializeToString())
            response = response_pb2.Response()
            response.ParseFromString(rawResponse.content)
            return response
        except Exception, e:
            logging.error(e)
            return None
