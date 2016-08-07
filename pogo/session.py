from POGOProtos.Networking.Requests import Request_pb2
from POGOProtos.Networking.Requests import RequestType_pb2

from POGOProtos.Networking.Requests.Messages import EncounterMessage_pb2
from POGOProtos.Networking.Requests.Messages import FortSearchMessage_pb2
from POGOProtos.Networking.Requests.Messages import FortDetailsMessage_pb2
from POGOProtos.Networking.Requests.Messages import CatchPokemonMessage_pb2
from POGOProtos.Networking.Requests.Messages import GetMapObjectsMessage_pb2
from POGOProtos.Networking.Requests.Messages import EvolvePokemonMessage_pb2
from POGOProtos.Networking.Requests.Messages import ReleasePokemonMessage_pb2
from POGOProtos.Networking.Requests.Messages import UseItemCaptureMessage_pb2
from POGOProtos.Networking.Requests.Messages import UseItemEggIncubatorMessage_pb2
from POGOProtos.Networking.Requests.Messages import RecycleInventoryItemMessage_pb2
from POGOProtos.Networking.Requests.Messages import NicknamePokemonMessage_pb2
from POGOProtos.Networking.Requests.Messages import UseItemPotionMessage_pb2
from POGOProtos.Networking.Requests.Messages import UseItemReviveMessage_pb2
from POGOProtos.Networking.Requests.Messages import SetPlayerTeamMessage_pb2
from POGOProtos.Networking.Requests.Messages import SetFavoritePokemonMessage_pb2
from POGOProtos.Networking.Requests.Messages import LevelUpRewardsMessage_pb2
from POGOProtos.Networking.Requests.Messages import UseItemXpBoostMessage_pb2
from POGOProtos.Networking.Requests.Messages import UpgradePokemonMessage_pb2

from inventory import items
from location import Location
from session_bare import PogoSessionBare
from custom_exceptions import GeneralPogoException

import logging
import time


class PogoSession(PogoSessionBare):
    # Hooks for those bundled in default
    # Getters
    def getEggs(self):
        self.getProfile()
        return self._state.eggs

    def getInventory(self):
        self.getProfile()
        return self.inventory

    def getBadges(self):
        self.getProfile()
        return self._state.badges

    def getDownloadSettings(self):
        self.getProfile()
        return self._state.settings

    # Check, so we don't have to start another request
    def checkEggs(self):
        return self._state.eggs

    def checkInventory(self):
        return self.inventory

    def checkBadges(self):
        return self._state.badges

    def checkDownloadSettings(self):
        return self._state.settings

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
        self._state.profile.ParseFromString(res.returns[0])

        # Return everything
        return self._state.profile

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
        self._state.mapObjects.ParseFromString(res.returns[0])

        # Return everything
        return self._state.mapObjects

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
        self._state.fortSearch.ParseFromString(res.returns[0])

        # Return everything
        return self._state.fortSearch

    # set an Egg into an incubator
    def getFortDetails(self, fort):

        # Create request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.FORT_DETAILS,
            request_message=FortDetailsMessage_pb2.FortDetailsMessage(
                fort_id=fort.id,
                latitude=fort.latitude,
                longitude=fort.longitude,
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self._state.fortDetails.ParseFromString(res.returns[0])

        # Return everything
        return self._state.fortDetails

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
        self._state.encounter.ParseFromString(res.returns[0])

        # Return everything
        return self._state.encounter

    # Upon Encounter, try and catch
    def catchPokemon(
        self, pokemon, pokeball=items.POKE_BALL,
        normalized_reticle_size=1.950, hit_pokemon=True,
        spin_modifier=0.850, normalized_hit_position=1.0
    ):

        # Create request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.CATCH_POKEMON,
            request_message=CatchPokemonMessage_pb2.CatchPokemonMessage(
                encounter_id=pokemon.encounter_id,
                pokeball=pokeball,
                normalized_reticle_size=normalized_reticle_size,
                spawn_point_id=pokemon.spawn_point_id,
                hit_pokemon=hit_pokemon,
                spin_modifier=spin_modifier,
                normalized_hit_position=normalized_hit_position
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self._state.catch.ParseFromString(res.returns[0])

        # Return everything
        return self._state.catch

    # Use a razz berry or the like
    def useItemCapture(self, item_id, pokemon):

        # Create request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.USE_ITEM_CAPTURE,
            request_message=UseItemCaptureMessage_pb2.UseItemCaptureMessage(
                item_id=item_id,
                encounter_id=pokemon.encounter_id
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload, defaults=False)

        # Parse
        self._state.itemCapture.ParseFromString(res.returns[0])

        # Return everything
        return self._state.itemCapture

    # Use a Potion
    def useItemPotion(self, item_id, pokemon):

        # Create Request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.USE_ITEM_POTION,
            request_message=UseItemPotionMessage_pb2.UseItemPotionMessage(
                item_id=item_id,
                pokemon_id=pokemon.id
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload, defaults=False)

        # Parse
        self._state.itemPotion.ParseFromString(res.returns[0])

        # Return everything
        return self._state.itemPotion

    # Use a Revive
    def useItemRevive(self, item_id, pokemon):

        # Create request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.USE_ITEM_REVIVE,
            request_message=UseItemReviveMessage_pb2.UseItemReviveMessage(
                item_id=item_id,
                pokemon_id=pokemon.id
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload, defaults=False)

        # Parse
        self._state.itemRevive.ParseFromString(res.returns[0])

        # Return everything
        return self._state.itemRevive

    # Evolve Pokemon
    def evolvePokemon(self, pokemon):

        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.EVOLVE_POKEMON,
            request_message=EvolvePokemonMessage_pb2.EvolvePokemonMessage(
                pokemon_id=pokemon.id
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self._state.evolve.ParseFromString(res.returns[0])

        # Return everything
        return self._state.evolve

    def releasePokemon(self, pokemon):

        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.RELEASE_POKEMON,
            request_message=ReleasePokemonMessage_pb2.ReleasePokemonMessage(
                pokemon_id=pokemon.id
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload, defaults=False)

        # Parse
        self._state.release.ParseFromString(res.returns[0])

        # Return everything
        return self._state.release

    def getLevelUp(self, newLevel):

        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.LEVEL_UP_REWARDS,
            request_message=LevelUpRewardsMessage_pb2.LevelUpRewardsMessage(
                level=newLevel
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload, defaults=False)

        # Parse
        self._state.levelUp.ParseFromString(res.returns[0])

        # Return everything
        return self._state.levelUp

    def useXpBoost(self):

        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.USE_ITEM_XP_BOOST,
            request_message=UseItemXpBoostMessage_pb2.UseItemXpBoostMessage(
                item_id=items.LUCKY_EGG
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload, defaults=False)

        # Parse
        self._state.xpBoost.ParseFromString(res.returns[0])

        # Return everything
        return self._state.xpBoost

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
        self._state.recycle.ParseFromString(res.returns[0])

        # Return everything
        return self._state.recycle

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
        self._state.incubator.ParseFromString(res.returns[0])

        # Return everything
        return self._state.incubator

    def nicknamePokemon(self, pokemon, nickname):
        # Create request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.NICKNAME_POKEMON,
            request_message=NicknamePokemonMessage_pb2.NicknamePokemonMessage(
                pokemon_id=pokemon.id,
                nickname=nickname
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self._state.nickname.ParseFromString(res.returns[0])

        # Return everything
        return self._state.nickname

    # Set Pokemon as favorite
    def setFavoritePokemon(self, pokemon, is_favorite):

        # Create Request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.SET_FAVORITE_POKEMON,
            request_message=SetFavoritePokemonMessage_pb2.SetFavoritePokemonMessage(
                pokemon_id=pokemon.id,
                is_favorite=is_favorite
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload, defaults=False)

        # Parse
        self._state.favoritePokemon.ParseFromString(res.returns[0])

        # Return Everything
        return self._state.favoritePokemon

    # Upgrade a Pokemon's CP
    def upgradePokemon(self, pokemon):

        # Create request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.UPGRADE_POKEMON,
            request_message=UpgradePokemonMessage_pb2.UpgradePokemonMessage(
                pokemon_id=pokemon.id
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload, defaults=False)

        # Parse
        self._state.upgradePokemon.ParseFromString(res.returns[0])

        # Return everything
        return self._state.upgradePokemon

    # Choose player's team: "BLUE","RED", or "YELLOW".
    def setPlayerTeam(self, team):

        # Create request
        payload = [Request_pb2.Request(
            request_type=RequestType_pb2.SET_PLAYER_TEAM,
            request_message=SetPlayerTeamMessage_pb2.SetPlayerTeamMessage(
                team=team
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload, defaults=False)

        # Parse
        self._state.playerTeam.ParseFromString(res.returns[0])

        # Return everything
        return self._state.playerTeam

    # These act as more logical functions.
    # Might be better to break out seperately
    # Walk over to position in meters
    def walkTo(self, olatitude, olongitude, epsilon=10, step=7.5):
        if step >= epsilon:
            raise GeneralPogoException("Walk may never converge")

        if self.location.noop:
            raise GeneralPogoException("Location not set")

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

        logging.info("Walking %f meters. This will take %f seconds..." % (dist, dist / step))
        while dist > epsilon:
            logging.debug("%f m -> %f m away", closest - dist, closest)
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
