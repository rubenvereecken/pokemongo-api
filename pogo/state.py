from POGOProtos.Networking.Responses import (
    CheckAwardedBadgesResponse_pb2 as CheckAwardedBadgesResponse,
    DownloadSettingsResponse_pb2 as DownloadSettingsResponse,
    GetInventoryResponse_pb2 as GetInventoryResponse,
    GetHatchedEggsResponse_pb2 as GetHatchedEggsResponse,
    GetMapObjectsResponse_pb2 as GetMapObjectsResponse,
    GetPlayerResponse_pb2 as GetPlayerResponse,
    FortSearchResponse_pb2 as FortSearchResponse,
    FortDetailsResponse_pb2 as FortDetailsResponse,
    EncounterResponse_pb2 as EncounterResponse,
    CatchPokemonResponse_pb2 as CatchPokemonResponse,
    EvolvePokemonResponse_pb2 as EvolvePokemonResponse,
    ReleasePokemonResponse_pb2 as ReleasePokemonResponse,
    UseItemEggIncubatorResponse_pb2 as UseItemEggIncubatorResponse,
    RecycleInventoryItemResponse_pb2 as RecycleInventoryItemResponse,
    UseItemCaptureResponse_pb2 as UseItemCaptureResponse,
    NicknamePokemonResponse_pb2 as NicknamePokemonResponse,
    UseItemPotionResponse_pb2 as UseItemPotionResponse,
    UseItemReviveResponse_pb2 as UseItemReviveResponse,
    SetPlayerTeamResponse_pb2 as SetPlayerTeamResponse,
    SetFavoritePokemonResponse_pb2 as SetFavoritePokemonResponse,
    LevelUpRewardsResponse_pb2 as LevelUpRewardsResponse,
    UseItemXpBoostResponse_pb2 as UseItemXpBoostResponse,
    UpgradePokemonResponse_pb2 as UpgradePokemonResponse,
)


class State(object):
    """Class to wrap the current state of responses"""
    def __init__(self):
        self.profile = GetPlayerResponse.GetPlayerResponse()
        self.eggs = GetHatchedEggsResponse.GetHatchedEggsResponse()
        self.inventory = GetInventoryResponse.GetInventoryResponse()
        self.badges = CheckAwardedBadgesResponse.CheckAwardedBadgesResponse()
        self.settings = DownloadSettingsResponse.DownloadSettingsResponse()
        self.mapObjects = GetMapObjectsResponse.GetMapObjectsResponse()
        self.fortSearch = FortSearchResponse.FortSearchResponse()
        self.fortDetails = FortDetailsResponse.FortDetailsResponse()
        self.encounter = EncounterResponse.EncounterResponse()
        self.catch = CatchPokemonResponse.CatchPokemonResponse()
        self.itemCapture = UseItemCaptureResponse.UseItemCaptureResponse()
        self.itemPotion = UseItemPotionResponse.UseItemPotionResponse()
        self.itemRevive = UseItemReviveResponse.UseItemReviveResponse()
        self.evolve = EvolvePokemonResponse.EvolvePokemonResponse()
        self.release = ReleasePokemonResponse.ReleasePokemonResponse()
        self.recycle = RecycleInventoryItemResponse.RecycleInventoryItemResponse()
        self.incubator = UseItemEggIncubatorResponse.UseItemEggIncubatorResponse()
        self.nickname = NicknamePokemonResponse.NicknamePokemonResponse()
        self.playerTeam = SetPlayerTeamResponse.SetPlayerTeamResponse()
        self.favoritePokemon = SetFavoritePokemonResponse.SetFavoritePokemonResponse()
        self.levelUp = LevelUpRewardsResponse.LevelUpRewardsResponse()
        self.xpBoost = UseItemXpBoostResponse.UseItemXpBoostResponse()
        self.upgradePokemon = UpgradePokemonResponse.UpgradePokemonResponse()
