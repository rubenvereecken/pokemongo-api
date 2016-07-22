# Load Generated Protobuf
from POGOProtos.Networking.Requests import Request_pb2
from POGOProtos.Networking.Requests import RequestType_pb2
from POGOProtos.Networking.Envelopes import ResponseEnvelope_pb2
from POGOProtos.Networking.Envelopes import RequestEnvelope_pb2
from POGOProtos.Networking.Requests.Messages import EncounterMessage_pb2
from POGOProtos.Networking.Requests.Messages import FortSearchMessage_pb2
from POGOProtos.Networking.Requests.Messages import CatchPokemonMessage_pb2
from POGOProtos.Networking.Requests.Messages import GetInventoryMessage_pb2
from POGOProtos.Networking.Requests.Messages import GetMapObjectsMessage_pb2
from POGOProtos.Networking.Requests.Messages import EvolvePokemonMessage_pb2
from POGOProtos.Networking.Requests.Messages import ReleasePokemonMessage_pb2
from POGOProtos.Networking.Requests.Messages import DownloadSettingsMessage_pb2
from POGOProtos.Networking.Requests.Messages import UseItemEggIncubatorMessage_pb2
from POGOProtos.Networking.Requests.Messages import RecycleInventoryItemMessage_pb2

# Load local
import api
from custom_exceptions import GeneralPogoException
from inventory import Inventory
from location import Location
from state import State

import requests
import logging
import time

# Hide errors (Yes this is terrible, but prettier)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'


class PogoSession(object):

    def __init__(self, session, authProvider, accessToken, location):
        self.session = session
        self.authProvider = authProvider
        self.accessToken = accessToken
        self.location = location
        self.state = State()

        self.authTicket = None
        self.endpoint = None
        self.endpoint = 'https://{0}{1}'.format(
            self.createApiEndpoint(),
            '/rpc'
        )

        # Set up Inventory
        self.getInventory()

    def __str__(self):
        s = 'Access Token: {0}\nEndpoint: {1}\nLocation: {2}'.format(
            self.accessToken,
            self.endpoint,
            self.location
        )
        return s

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

        # If we haven't authenticated before
        info = None
        if not self.authTicket:
            info = RequestEnvelope_pb2.RequestEnvelope.AuthInfo(
                provider=self.authProvider,
                token=RequestEnvelope_pb2.RequestEnvelope.AuthInfo.JWT(
                    contents=self.accessToken,
                    unknown2=59
                )
            )

        # Build Envelope
        latitude, longitude, altitude = self.getCoordinates()
        req = RequestEnvelope_pb2.RequestEnvelope(
            status_code=2,
            request_id=api.getRPCId(),
            longitude=longitude,
            latitude=latitude,
            altitude=altitude,
            auth_ticket=self.authTicket,
            unknown12=989,
            auth_info=info
        )

        # Add requests
        if defaults:
            payload += self.getDefaults()
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
        except Exception as e:
            logging.error(e)
            raise GeneralPogoException('Probably server fires.')

    def wrapAndRequest(self, payload, defaults=True):
        res = self.request(self.wrapInRequest(payload, defaults=defaults))
        if defaults:
            self.parseDefault(res)
        if res is None:
            logging.critical(res)
            logging.critical('Servers seem to be busy. Exiting.')
            raise Exception('No Valid Response.')

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
        try:
            self.state.eggs.ParseFromString(res.returns[1])
            self.state.inventory.ParseFromString(res.returns[2])
            self.state.badges.ParseFromString(res.returns[3])
            self.state.settings.ParseFromString(res.returns[4])
        except Exception as e:
            logging.error(e)
            raise GeneralPogoException("Error parsing response. Malformed response")

        # Finally make inventory usable
        items = self.state.inventory.inventory_delta.inventory_items
        self.inventory = Inventory(items)

    # Hooks for those bundled in default
    # Getters
    def getEggs(self):
        self.getProfile()
        return self.state.eggs

    def getInventory(self):
        self.getProfile()
        return self.inventory

    def getBadges(self):
        self.getProfile()
        return self.state.badges

    def getDownloadSettings(self):
        self.getProfile()
        return self.state.settings

    # Check, so we don't have to start another request
    def checkEggs(self):
        return self.state.eggs

    def checkInventory(self):
        return self.inventory

    def checkBadges(self):
        return self.state.badges

    def checkDownloadSettings(self):
        return self.state.settings

    # Core api calls
    # Get profile
    def getProfile(self):
        # Create profile request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.GET_PLAYER
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self.state.profile.ParseFromString(res.returns[0])

        # Return everything
        return self.state.profile

    # Get Location
    def getMapObjects(self, radius=10):
        # Work out location details
        cells = self.location.getCells(radius)
        latitude, longitude, _ = self.getCoordinates()
        timestamps = [0, ] * len(cells)

        # Create request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.GET_MAP_OBJECTS,
            request_message=GetMapObjectsMessage_pb2.GetMapObjectsMessage(
                cell_id=cells,
                since_timestamp_ms=timestamps,
                latitude=latitude,
                longitude=longitude
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
            request_type=RequestType_pb2.FORT_SEARCH,
            request_message=FortSearchMessage_pb2.FortSearchMessage(
                fort_id=fort.id,
                player_latitude=self.location.latitude,
                player_longitude=self.location.longitude,
                fort_latitude=fort.latitude,
                fort_longitude=fort.longitude
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
            request_type=RequestType_pb2.ENCOUNTER,
            request_message=EncounterMessage_pb2.EncounterMessage(
                encounter_id=pokemon.encounter_id,
                spawn_point_id=pokemon.spawn_point_id,
                player_latitude=self.location.latitude,
                player_longitude=self.location.longitude
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self.state.encounter.ParseFromString(res.returns[0])

        # Return everything
        return self.state.encounter

    # Upon Encounter, try and catch
    def catchPokemon(self, pokemon, pokeball=1):

        # Create request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.CATCH_POKEMON,
            request_message=CatchPokemonMessage_pb2.CatchPokemonMessage(
                encounter_id=pokemon.encounter_id,
                pokeball=pokeball,
                normalized_reticle_size=1.950,
                spawn_point_guid=pokemon.spawn_point_id,
                hit_pokemon=True,
                spin_modifier=0.850,
                normalized_hit_position=1.0
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self.state.catch.ParseFromString(res.returns[0])

        # Return everything
        return self.state.catch

    # Evolve Pokemon
    def evolvePokemon(self, pokemon):

        # Create request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.EVOLVE_POKEMON,
            request_message=EvolvePokemonMessage_pb2.EvolvePokemonMessage(
                pokemon_id=pokemon.id
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self.state.evolve.ParseFromString(res.returns[0])

        # Return everything
        return self.state.evolve

    # Transfer Pokemon
    def releasePokemon(self, pokemon):

        # Create request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.RELEASE_POKEMON,
            request_message=ReleasePokemonMessage_pb2.ReleasePokemonMessage(
                pokemon_id=pokemon.id
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self.state.release.ParseFromString(res.returns[0])

        # Return everything
        return self.state.release

    # Throw away items
    def recycleItem(self, item_id, count):

        # Create request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.RECYCLE_INVENTORY_ITEM,
            request_message=RecycleInventoryItemMessage_pb2.RecycleInventoryItemMessage(
                item_id=item_id,
                count=count
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self.state.recycle.ParseFromString(res.returns[0])

        # Return everything
        return self.state.recycle

    # set an Egg into an incubator
    def setEgg(self, item, pokemon):

        # Create request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.USE_ITEM_EGG_INCUBATOR,
            request_message=UseItemEggIncubatorMessage_pb2.UseItemEggIncubatorMessage(
                item_id=item.id,
                pokemon_id=pokemon.id
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self.state.incubator.ParseFromString(res.returns[0])

        # Return everything
        return self.state.incubator

    # These act as more logical functions.
    # Might be better to break out seperately
    # Walk over to position in meters
    def walkTo(self, olatitude, olongitude, epsilon=10, step=7.5):
        if step >= epsilon:
            raise Exception("Walk may never converge")

        # Calculate distance to position
        latitude, longitude, _ = self.getCoordinates()
        dist = closest = Location.getDistance(
            latitude,
            longitude,
            olatitude,
            olongitude
        )

        # Run walk
        divisions = closest / step
        dLat = (latitude - olatitude) / divisions
        dLon = (longitude - olongitude) / divisions
        while dist > epsilon:
            logging.info("%f m -> %f m away", closest - dist, closest)
            latitude -= dLat
            longitude -= dLon
            self.setCoordinates(
                latitude,
                longitude
            )
            time.sleep(1)
            dist = Location.getDistance(
                latitude,
                longitude,
                olatitude,
                olongitude
            )

    # Wrap both for ease
    # TODO: Should probably check for success
    def encounterAndCatch(self, pokemon, pokeball=1, delay=2):
        self.encounterPokemon(pokemon)
        time.sleep(delay)
        return self.catchPokemon(pokemon, pokeball)
