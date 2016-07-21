import requests
import logging
import time

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from POGOProtos.Networking.Envelopes import ResponseEnvelope_pb2
from POGOProtos.Networking.Envelopes import RequestEnvelope_pb2
from POGOProtos.Networking.Requests import Request_pb2
from POGOProtos.Networking.Requests import RequestType_pb2
from POGOProtos.Networking.Requests.Messages import DownloadSettingsMessage_pb2
from POGOProtos.Networking.Requests.Messages import GetInventoryMessage_pb2
from POGOProtos.Networking.Requests.Messages import GetMapObjectsMessage_pb2
from POGOProtos.Networking.Requests.Messages import FortSearchMessage_pb2
from POGOProtos.Networking.Requests.Messages import EncounterMessage_pb2
from POGOProtos.Networking.Requests.Messages import CatchPokemonMessage_pb2


import api
import location
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
        self.getMapObjects(radius=1)

    def setCoords(self, latitude, longitude):
        self.location = location.getCoords(latitude, longitude)
        self.getMapObjects(radius=1)

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

    def wrapInRequest(self, payload, defaults=True):

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
            request_id = api.getRPCId(),
            longitude = longitude,
            latitude = latitude,
            altitude = altitude,
            auth_ticket = self.authTicket,
            unknown12 = 989,
            auth_info = info
        )

        # Add requests
        if defaults:
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
            logging.critical('Probably server fires.')
            logging.error(e)
            raise

    def wrapAndRequest(self, payload, defaults=True):
        res = self.request(self.wrapInRequest(payload, defaults=defaults))
        if(defaults): self.parseDefault(res)
        if res is None:
            logging.critical(res)
            logging.critical('Servers seem to be busy. Exiting.')
            raise Exception('No Valid Response.')

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
                last_timestamp_ms = 0
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
    def parseDefault(self, res):
        self.state.eggs.ParseFromString(res.returns[1])
        self.state.inventory.ParseFromString(res.returns[2])
        self.state.badges.ParseFromString(res.returns[3])
        self.state.settings.ParseFromString(res.returns[4])

    # Walk over to position in meters
    def walkTo(self, olatitude, olongitude, epsilon=10, step=7.5):
        if step >= epsilon:
            raise Exception("Walk may never converge")

        # Calculate distance to position
        latitude, longitude, _ = self.getLocation()
        dist = closest = location.getDistance(latitude, longitude, olatitude, olongitude)

        # Run walk
        divisions = closest/step
        dLat = (latitude - olatitude)/divisions
        dLon = (longitude - olongitude)/divisions
        while dist > epsilon:
            logging.info("%f m -> %f m away" % (closest - dist, closest))
            latitude  -= dLat
            longitude -= dLon
            self.setCoords(
                latitude,
                longitude
            )
            time.sleep(1)
            dist = location.getDistance(latitude, longitude, olatitude, olongitude)


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

    def getInventory(self):
        self.getProfile()
        return self.state.inventory

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
        self.state.mapObjects.ParseFromString(res.returns[0])

        # Return everything
        return self.state.mapObjects

    # Get Location
    def getFortSearch(self, fort):

        # Create request
        payload = [Request_pb2.Request(
            request_type = RequestType_pb2.FORT_SEARCH,
            request_message = FortSearchMessage_pb2.FortSearchMessage(
                fort_id = fort.id,
                player_latitude = self.location.latitude,
                player_longitude = self.location.longitude,
                fort_latitude = fort.latitude,
                fort_longitude = fort.longitude
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self.state.fortSearch.ParseFromString(res.returns[0])

        # Return everything
        return self.state.fortSearch

    # Get encounter
    def encounterPokemon(self, pokemon):

        # Create request
        payload = [Request_pb2.Request(
            request_type = RequestType_pb2.ENCOUNTER,
            request_message = EncounterMessage_pb2.EncounterMessage(
                encounter_id = pokemon.encounter_id,
                spawn_point_id = pokemon.spawn_point_id,
                player_latitude = self.location.latitude,
                player_longitude = self.location.longitude
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self.state.encounter.ParseFromString(res.returns[0])

        # Return everything
        return self.state.encounter

    def catchPokemon(self, pokemon, pokeball=1):

        # Create request
        payload = [Request_pb2.Request(
            request_type = RequestType_pb2.CATCH_POKEMON,
            request_message = CatchPokemonMessage_pb2.CatchPokemonMessage(
                encounter_id = pokemon.encounter_id,
                pokeball = pokeball,
                normalized_reticle_size = 1.950,
                spawn_point_guid = pokemon.spawn_point_id,
                hit_pokemon = True,
                spin_modifier = 0.850,
                normalized_hit_position = 1.0
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self.state.catch.ParseFromString(res.returns[0])

        # Return everything
        return self.state.catch