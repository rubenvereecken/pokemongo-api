class Inventory(dict):

    # Split from inventory since everything is bundled
    def __init__(self, items):
        # Reset inventory
        # Assuming sincetimestamp = 0
        # Otherwise have to associate time state,
        # and that's a pain
        self["incubators"] = []
        self["pokedex"] = {}
        self["candies"] = {}
        self["stats"] = {}
        self["party"] = []
        self["eggs"] = []
        self["bag"] = {}
        for item in items:
            data = item.inventory_item_data

            if data.HasField("player_stats"):
                self["stats"] = data.player_stats
                continue

            pokedexEntry = getattr(data, "pokedex_entry", None)
            if data.HasField("pokedex_entry"):
                self["pokedex"][pokedexEntry.pokemon_id] = data.pokedex_entry
                continue

            pokemonFamily = getattr(data, "pokemon_family", None)
            if data.HasField("pokemon_family"):
                self["candies"][pokemonFamily.family_id] = pokemonFamily.candy
                continue

            pokemonData = getattr(data, "pokemon_data", None)
            if data.HasField("pokemon_data"):
                if pokemonData.is_egg:
                    self["eggs"].append(pokemonData)
                else:
                    self["party"].append(pokemonData)
                continue

            incubators = getattr(data, "egg_incubators", None)
            if data.HasField("egg_incubators"):
                self["incubators"] = incubators.egg_incubator
                continue

            bagItem = getattr(data, "item", None)
            if data.HasField("item"):
                self["bag"][bagItem.item_id] = bagItem.count
                continue

    def __str__(self):
        s = "Inventory:"

        s += "\n-- Stats: {0}".format(str(self["stats"]).replace("\n", "\n\t"))

        s += "\n-- Pokedex:"
        for pokemon in self["pokedex"]:
            s += "\n\t{0}: {1}".format(pokemon, str(self["pokedex"][pokemon]).replace("\n", "\n\t"))

        s += "\n-- Candies:"
        for key in self["candies"]:
            s += "\n\t{0}: {1}".format(key, self["candies"][key])

        s += "\n-- Party:"
        for pokemon in self["party"]:
            s += "\n\t{0}".format(str(pokemon).replace("\n", "\n\t"))

        s += "\n-- Eggs:"
        for egg in self["eggs"]:
            s += "\n\t{0}".format(str(egg).replace("\n", "\n\t"))

        s += "\n-- Bag:"
        for key in self["bag"]:
            s += "\n\t{0}: {1}".format(key, self["bag"][key])

        s += "\n-- Incubators:"
        for incubator in self["incubators"]:
            s += "\n\t{0}".format(str(incubator).replace("\n", "\n\t"))

        return s
