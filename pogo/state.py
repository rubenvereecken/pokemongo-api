from Networking.Responses import CheckAwardedBadgesResponse_pb2
from Networking.Responses import DownloadSettingsResponse_pb2
from Networking.Responses import GetInventoryResponse_pb2
from Networking.Responses import GetHatchedEggsResponse_pb2
from Networking.Responses import GetMapObjectsResponse_pb2
from Networking.Responses import GetPlayerResponse_pb2
from Networking.Responses import FortSearchResponse_pb2
from Networking.Responses import EncounterResponse_pb2
from Networking.Responses import CatchPokemonResponse_pb2
from Networking.Responses import EvolvePokemonResponse_pb2
from Networking.Responses import ReleasePokemonResponse_pb2
from Networking.Responses import UseItemEggIncubatorResponse_pb2
from Networking.Responses import RecycleInventoryItemResponse_pb2


class State(object):
    """Class to wrap the current state of responses"""
    def __init__(self):
        self.profile = GetPlayerResponse_pb2.GetPlayerResponse()
        self.eggs = GetHatchedEggsResponse_pb2.GetHatchedEggsResponse()
        self.inventory = GetInventoryResponse_pb2.GetInventoryResponse()
        self.badges = CheckAwardedBadgesResponse_pb2.CheckAwardedBadgesResponse()
        self.settings = DownloadSettingsResponse_pb2.DownloadSettingsResponse()
        self.mapObjects =  GetMapObjectsResponse_pb2.GetMapObjectsResponse()
        self.fortSearch = FortSearchResponse_pb2.FortSearchResponse()
        self.encounter = EncounterResponse_pb2.EncounterResponse()
        self.catch = CatchPokemonResponse_pb2.CatchPokemonResponse()
        self.evolve = EvolvePokemonResponse_pb2.EvolvePokemonResponse()
        self.release = ReleasePokemonResponse_pb2.ReleasePokemonResponse()
        self.recycle = RecycleInventoryItemResponse_pb2.RecycleInventoryItemResponse()
        self.incubator = UseItemEggIncubatorResponse_pb2.UseItemEggIncubatorResponse()
