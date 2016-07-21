from Networking.Responses import CheckAwardedBadgesResponse_pb2
from Networking.Responses import DownloadSettingsResponse_pb2
from Networking.Responses import GetInventoryResponse_pb2
from Networking.Responses import GetHatchedEggsResponse_pb2
from Networking.Responses import GetMapObjectsResponse_pb2
from Networking.Responses import GetPlayerResponse_pb2
from Networking.Responses import FortSearchResponse_pb2
from Networking.Responses import EncounterResponse_pb2
from Networking.Responses import CatchPokemonResponse_pb2

class State(object):

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