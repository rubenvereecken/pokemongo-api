from pokedex import pokedex
from util import ConstReflect


# Not quiet an enum
class Items(ConstReflect):
    """Items class for static item reference"""

    # Static Lookups
    UNKNOWN = 0
    POKE_BALL = 1
    GREAT_BALL = 2
    ULTRA_BALL = 3
    MASTER_BALL = 4
    POTION = 101
    SUPER_POTION = 102
    HYPER_POTION = 103
    MAX_POTION = 104
    REVIVE = 201
    MAX_REVIVE = 202
    LUCKY_EGG = 301
    INCENSE_ORDINARY = 401
    INCENSE_SPICY = 402
    INCENSE_COOL = 403
    INCENSE_FLORAL = 404
    TROY_DISK = 501
    X_ATTACK = 602
    X_DEFENSE = 603
    X_MIRACLE = 604
    RAZZ_BERRY = 701
    BLUK_BERRY = 702
    NANAB_BERRY = 703
    WEPAR_BERRY = 704
    PINAP_BERRY = 705
    SPECIAL_CAMERA = 801
    INCUBATOR_BASIC_UNLIMITED = 901
    INCUBATOR_BASIC = 902
    POKEMON_STORAGE_UPGRADE = 1001
    ITEM_STORAGE_UPGRADE = 1002

items = Items()


class Inventory(object):
    """ Inventory class to hold response from inventory"""

    # Split from inventory since everything is bundled
    def __init__(self, items):
        # Reset inventory
        # Assuming sincetimestamp = 0
        # Otherwise have to associate time state,
        # and that's a pain
        self.incubators = []
        self.pokedex = {}
        self.candies = {}
        self.stats = {}
        self.party = []
        self.eggs = []
        self.bag = {}
        for item in items:
            data = item.inventory_item_data

            if data.HasField("player_stats"):
                self.stats = data.player_stats
                continue

            pokedexEntry = getattr(data, "pokedex_entry", None)
            if data.HasField("pokedex_entry"):
                self.pokedex[pokedexEntry.pokemon_id] = data.pokedex_entry
                continue

            pokemonFamily = getattr(data, "candy", None)
            if data.HasField("candy"):
                self.candies[pokemonFamily.family_id] = pokemonFamily.candy
                continue

            pokemonData = getattr(data, "pokemon_data", None)
            if data.HasField("pokemon_data"):
                if pokemonData.is_egg:
                    self.eggs.append(pokemonData)
                else:
                    self.party.append(pokemonData)
                continue

            incubators = getattr(data, "egg_incubators", None)
            if data.HasField("egg_incubators"):
                self.incubators = incubators.egg_incubator
                continue

            bagItem = getattr(data, "item", None)
            if data.HasField("item"):
                self.bag[bagItem.item_id] = bagItem.count
                continue

    def __getitem__(self, lookup):
        if lookup in self.bag:
            return self.bag[lookup]
        else:
            return 0

    def __str__(self):
        def clean(proto):
            return str(proto).replace("\n", "\n\t")

        s = "Inventory:"

        s += "\n-- Stats: {0}".format(clean(self.stats))

        s += "\n-- Pokedex:"
        for pokemon in self.pokedex:
            s += "\n\t{0}: {1}".format(pokemon, clean(self.pokedex[pokemon]))

        s += "\n-- Candies:"
        for key in self.candies:
            s += "\n\t{0}: {1}".format(pokedex[key], self.candies[key])

        s += "\n-- Party:"
        for pokemon in self.party:
            s += "\n\t{0}".format(clean(pokemon))

        s += "\n-- Eggs:"
        for egg in self.eggs:
            s += "\n\t{0}".format(clean(egg))

        s += "\n-- Bag:"
        for key in self.bag:
            s += "\n\t{0}: {1}".format(items[key], self.bag[key])

        s += "\n-- Incubators:"
        for incubator in self.incubators:
            s += "\n\t{0}".format(clean(incubator))

        return s
