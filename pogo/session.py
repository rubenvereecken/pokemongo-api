# Load protobufs
from POGOProtos.Networking.Requests import(
    Request_pb2 as Request,
    RequestType_pb2 as RequestType
)
from POGOProtos.Networking.Requests.Messages import(
    EncounterMessage_pb2 as EncounterMessage,
    FortSearchMessage_pb2 as FortSearchMessage,
    FortDetailsMessage_pb2 as FortDetailsMessage,
    CatchPokemonMessage_pb2 as CatchPokemonMessage,
    GetMapObjectsMessage_pb2 as GetMapObjectsMessage,
    EvolvePokemonMessage_pb2 as EvolvePokemonMessage,
    ReleasePokemonMessage_pb2 as ReleasePokemonMessage,
    UseItemCaptureMessage_pb2 as UseItemCaptureMessage,
    UseItemEggIncubatorMessage_pb2 as UseItemEggIncubatorMessage,
    RecycleInventoryItemMessage_pb2 as RecycleInventoryItemMessage,
    NicknamePokemonMessage_pb2 as NicknamePokemonMessage,
    UseItemPotionMessage_pb2 as UseItemPotionMessage,
    UseItemReviveMessage_pb2 as UseItemReviveMessage,
    SetPlayerTeamMessage_pb2 as SetPlayerTeamMessage,
    SetFavoritePokemonMessage_pb2 as SetFavoritePokemonMessage,
    LevelUpRewardsMessage_pb2 as LevelUpRewardsMessage,
    UseItemXpBoostMessage_pb2 as UseItemXpBoostMessage,
    UpgradePokemonMessage_pb2 as UpgradePokemonMessage
)

# Load Local
from pogo.inventory import items
from pogo.session_bare import PogoSessionBare


class PogoSession(PogoSessionBare):
    """Session class with more robust calls"""

    # Core api calls
    # Get profile
    def getProfile(self):
        # Create profile request
        payload = [Request.Request(
            request_type=RequestType.GET_PLAYER
        )]

        # Send
        res = self.wrapAndRequest(payload)

        # Parse
        self._state.profile.ParseFromString(res.returns[0])

        # Return everything
        return self._state.profile

    # Hooks for those bundled in default
    def getEggs(self):
        self.getProfile()
        return self._state.eggs

    def getInventory(self):
        self.getProfile()
        return self._inventory

    def getBadges(self):
        self.getProfile()
        return self._state.badges

    def getDownloadSettings(self):
        self.getProfile()
        return self._state.settings

    # Get Location
    def getMapObjects(self, radius=10, bothDirections=True):
        # Work out location details
        cells = self.location.getCells(radius, bothDirections)
        latitude, longitude, _ = self.getCoordinates()
        timestamps = [0, ] * len(cells)

        # Create request
        payload = [Request.Request(
            request_type=RequestType.GET_MAP_OBJECTS,
            request_message=GetMapObjectsMessage.GetMapObjectsMessage(
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
        payload = [Request.Request(
            request_type=RequestType.FORT_SEARCH,
            request_message=FortSearchMessage.FortSearchMessage(
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
        payload = [Request.Request(
            request_type=RequestType.FORT_DETAILS,
            request_message=FortDetailsMessage.FortDetailsMessage(
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
        payload = [Request.Request(
            request_type=RequestType.ENCOUNTER,
            request_message=EncounterMessage.EncounterMessage(
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
        payload = [Request.Request(
            request_type=RequestType.CATCH_POKEMON,
            request_message=CatchPokemonMessage.CatchPokemonMessage(
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
        payload = [Request.Request(
            request_type=RequestType.USE_ITEM_CAPTURE,
            request_message=UseItemCaptureMessage.UseItemCaptureMessage(
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
        payload = [Request.Request(
            request_type=RequestType.USE_ITEM_POTION,
            request_message=UseItemPotionMessage.UseItemPotionMessage(
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
        payload = [Request.Request(
            request_type=RequestType.USE_ITEM_REVIVE,
            request_message=UseItemReviveMessage.UseItemReviveMessage(
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

        payload = [Request.Request(
            request_type=RequestType.EVOLVE_POKEMON,
            request_message=EvolvePokemonMessage.EvolvePokemonMessage(
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

        payload = [Request.Request(
            request_type=RequestType.RELEASE_POKEMON,
            request_message=ReleasePokemonMessage.ReleasePokemonMessage(
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

        payload = [Request.Request(
            request_type=RequestType.LEVEL_UP_REWARDS,
            request_message=LevelUpRewardsMessage.LevelUpRewardsMessage(
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

        payload = [Request.Request(
            request_type=RequestType.USE_ITEM_XP_BOOST,
            request_message=UseItemXpBoostMessage.UseItemXpBoostMessage(
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
        payload = [Request.Request(
            request_type=RequestType.RECYCLE_INVENTORY_ITEM,
            request_message=RecycleInventoryItemMessage.RecycleInventoryItemMessage(
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
        payload = [Request.Request(
            request_type=RequestType.USE_ITEM_EGG_INCUBATOR,
            request_message=UseItemEggIncubatorMessage.UseItemEggIncubatorMessage(
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

    # Set the name of a given pokemon
    def nicknamePokemon(self, pokemon, nickname):
        # Create request
        payload = [Request.Request(
            request_type=RequestType.NICKNAME_POKEMON,
            request_message=NicknamePokemonMessage.NicknamePokemonMessage(
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
        payload = [Request.Request(
            request_type=RequestType.SET_FAVORITE_POKEMON,
            request_message=SetFavoritePokemonMessage.SetFavoritePokemonMessage(
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
        payload = [Request.Request(
            request_type=RequestType.UPGRADE_POKEMON,
            request_message=UpgradePokemonMessage.UpgradePokemonMessage(
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
        payload = [Request.Request(
            request_type=RequestType.SET_PLAYER_TEAM,
            request_message=SetPlayerTeamMessage.SetPlayerTeamMessage(
                team=team
            ).SerializeToString()
        )]

        # Send
        res = self.wrapAndRequest(payload, defaults=False)

        # Parse
        self._state.playerTeam.ParseFromString(res.returns[0])

        # Return everything
        return self._state.playerTeam
