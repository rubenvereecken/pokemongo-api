class Pokedex(dict):
    def __init__(self):
    	super(dict, self).__init__(self)
        self.Pokemons = dict()
        self.Pokemons[0] = "MISSINGNO"
        self.Pokemons[1] = "BULBASAUR"
        self.Pokemons[2] = "IVYSAUR"
        self.Pokemons[3] = "VENUSAUR"
        self.Pokemons[4] = "CHARMANDER"
        self.Pokemons[5] = "CHARMELEON"
        self.Pokemons[6] = "CHARIZARD"
        self.Pokemons[7] = "SQUIRTLE"
        self.Pokemons[8] = "WARTORTLE"
        self.Pokemons[9] = "BLASTOISE"
        self.Pokemons[10] = "CATERPIE"
        self.Pokemons[11] = "METAPOD"
        self.Pokemons[12] = "BUTTERFREE"
        self.Pokemons[13] = "WEEDLE"
        self.Pokemons[14] = "KAKUNA"
        self.Pokemons[15] = "BEEDRILL"
        self.Pokemons[16] = "PIDGEY"
        self.Pokemons[17] = "PIDGEOTTO"
        self.Pokemons[18] = "PIDGEOT"
        self.Pokemons[19] = "RATTATA"
        self.Pokemons[20] = "RATICATE"
        self.Pokemons[21] = "SPEAROW"
        self.Pokemons[22] = "FEAROW"
        self.Pokemons[23] = "EKANS"
        self.Pokemons[24] = "ARBOK"
        self.Pokemons[25] = "PIKACHU"
        self.Pokemons[26] = "RAICHU"
        self.Pokemons[27] = "SANDSHREW"
        self.Pokemons[28] = "SANDSLASH"
        self.Pokemons[29] = "NIDORAN_FEMALE"
        self.Pokemons[30] = "NIDORINA"
        self.Pokemons[31] = "NIDOQUEEN"
        self.Pokemons[32] = "NIDORAN_MALE"
        self.Pokemons[33] = "NIDORINO"
        self.Pokemons[34] = "NIDOKING"
        self.Pokemons[35] = "CLEFAIRY"
        self.Pokemons[36] = "CLEFABLE"
        self.Pokemons[37] = "VULPIX"
        self.Pokemons[38] = "NINETALES"
        self.Pokemons[39] = "JIGGLYPUFF"
        self.Pokemons[40] = "WIGGLYTUFF"
        self.Pokemons[41] = "ZUBAT"
        self.Pokemons[42] = "GOLBAT"
        self.Pokemons[43] = "ODDISH"
        self.Pokemons[44] = "GLOOM"
        self.Pokemons[45] = "VILEPLUME"
        self.Pokemons[46] = "PARAS"
        self.Pokemons[47] = "PARASECT"
        self.Pokemons[48] = "VENONAT"
        self.Pokemons[49] = "VENOMOTH"
        self.Pokemons[50] = "DIGLETT"
        self.Pokemons[51] = "DUGTRIO"
        self.Pokemons[52] = "MEOWTH"
        self.Pokemons[53] = "PERSIAN"
        self.Pokemons[54] = "PSYDUCK"
        self.Pokemons[55] = "GOLDUCK"
        self.Pokemons[56] = "MANKEY"
        self.Pokemons[57] = "PRIMEAPE"
        self.Pokemons[58] = "GROWLITHE"
        self.Pokemons[59] = "ARCANINE"
        self.Pokemons[60] = "POLIWAG"
        self.Pokemons[61] = "POLIWHIRL"
        self.Pokemons[62] = "POLIWRATH"
        self.Pokemons[63] = "ABRA"
        self.Pokemons[64] = "KADABRA"
        self.Pokemons[65] = "ALAKAZAM"
        self.Pokemons[66] = "MACHOP"
        self.Pokemons[67] = "MACHOKE"
        self.Pokemons[68] = "MACHAMP"
        self.Pokemons[69] = "BELLSPROUT"
        self.Pokemons[70] = "WEEPINBELL"
        self.Pokemons[71] = "VICTREEBEL"
        self.Pokemons[72] = "TENTACOOL"
        self.Pokemons[73] = "TENTACRUEL"
        self.Pokemons[74] = "GEODUDE"
        self.Pokemons[75] = "GRAVELER"
        self.Pokemons[76] = "GOLEM"
        self.Pokemons[77] = "PONYTA"
        self.Pokemons[78] = "RAPIDASH"
        self.Pokemons[79] = "SLOWPOKE"
        self.Pokemons[80] = "SLOWBRO"
        self.Pokemons[81] = "MAGNEMITE"
        self.Pokemons[82] = "MAGNETON"
        self.Pokemons[83] = "FARFETCHD"
        self.Pokemons[84] = "DODUO"
        self.Pokemons[85] = "DODRIO"
        self.Pokemons[86] = "SEEL"
        self.Pokemons[87] = "DEWGONG"
        self.Pokemons[88] = "GRIMER"
        self.Pokemons[89] = "MUK"
        self.Pokemons[90] = "SHELLDER"
        self.Pokemons[91] = "CLOYSTER"
        self.Pokemons[92] = "GASTLY"
        self.Pokemons[93] = "HAUNTER"
        self.Pokemons[94] = "GENGAR"
        self.Pokemons[95] = "ONIX"
        self.Pokemons[96] = "DROWZEE"
        self.Pokemons[97] = "HYPNO"
        self.Pokemons[98] = "KRABBY"
        self.Pokemons[99] = "KINGLER"
        self.Pokemons[100] = "VOLTORB"
        self.Pokemons[101] = "ELECTRODE"
        self.Pokemons[102] = "EXEGGCUTE"
        self.Pokemons[103] = "EXEGGUTOR"
        self.Pokemons[104] = "CUBONE"
        self.Pokemons[105] = "MAROWAK"
        self.Pokemons[106] = "HITMONLEE"
        self.Pokemons[107] = "HITMONCHAN"
        self.Pokemons[108] = "LICKITUNG"
        self.Pokemons[109] = "KOFFING"
        self.Pokemons[110] = "WEEZING"
        self.Pokemons[111] = "RHYHORN"
        self.Pokemons[112] = "RHYDON"
        self.Pokemons[113] = "CHANSEY"
        self.Pokemons[114] = "TANGELA"
        self.Pokemons[115] = "KANGASKHAN"
        self.Pokemons[116] = "HORSEA"
        self.Pokemons[117] = "SEADRA"
        self.Pokemons[118] = "GOLDEEN"
        self.Pokemons[119] = "SEAKING"
        self.Pokemons[120] = "STARYU"
        self.Pokemons[121] = "STARMIE"
        self.Pokemons[122] = "MR_MIME"
        self.Pokemons[123] = "SCYTHER"
        self.Pokemons[124] = "JYNX"
        self.Pokemons[125] = "ELECTABUZZ"
        self.Pokemons[126] = "MAGMAR"
        self.Pokemons[127] = "PINSIR"
        self.Pokemons[128] = "TAUROS"
        self.Pokemons[129] = "MAGIKARP"
        self.Pokemons[130] = "GYARADOS"
        self.Pokemons[131] = "LAPRAS"
        self.Pokemons[132] = "DITTO"
        self.Pokemons[133] = "EEVEE"
        self.Pokemons[134] = "VAPOREON"
        self.Pokemons[135] = "JOLTEON"
        self.Pokemons[136] = "FLAREON"
        self.Pokemons[137] = "PORYGON"
        self.Pokemons[138] = "OMANYTE"
        self.Pokemons[139] = "OMASTAR"
        self.Pokemons[140] = "KABUTO"
        self.Pokemons[141] = "KABUTOPS"
        self.Pokemons[142] = "AERODACTYL"
        self.Pokemons[143] = "SNORLAX"
        self.Pokemons[144] = "ARTICUNO"
        self.Pokemons[145] = "ZAPDOS"
        self.Pokemons[146] = "MOLTRES"
        self.Pokemons[147] = "DRATINI"
        self.Pokemons[148] = "DRAGONAIR"
        self.Pokemons[149] = "DRAGONITE"
        self.Pokemons[150] = "MEWTWO"
        self.Pokemons[151] = "MEW"

        self[Rarity.MYTHIC] = ["MEW"]
        self[Rarity.LEGENDARY] = ["ZAPDOS", "MOLTRES", "MEWTWO", "ARTICUNO"]
        self[Rarity.EPIC] = ["DITTO", "VENUSAUR", "TAUROS", "DRAGONITE", "CLEFABLE", "CHARIZARD", "BLASTOISE"]
        self[Rarity.VERY_RARE] = [
            "WEEPINBELL", "WARTORTLE", "VILEPLUME", "VICTREEBEL", "VENOMOTH", "VAPOREON", "SLOWBRO", "RAICHU", 
            "POLIWRATH", "PINSIR", "PIDGEOT", "OMASTAR", "NIDOQUEEN", "NIDOKING", "MUK", "MAROWAK", "LAPRAS", 
            "KANGASKHAN", "KABUTOPS", "IVYSAUR", "GYARADOS", "GOLEM", "GENGAR", "EXEGGUTOR", "DRAGONAIR", "DEWGONG", 
            "CHARMELEON", "BEEDRILL", "ALAKAZAM"
        ]
        self[Rarity.RARE] = [
            "WIGGLYTUFF", "WEEZING", "TENTACRUEL", "TANGELA", "STARMIE", "SNORLAX", "SCYTHER", "SEAKING", "SEADRA", 
            "RHYDON", "RAPIDASH", "PRIMEAPE", "PORYGON", "POLIWHIRL", "PARASECT", "ONIX", "OMANYTE", "NINETALES", "NIDORINO", 
            "NIDORINA", "MR_MIME", "MAGMAR", "MACHOKE", "MACHAMP", "LICKITUNG", "KINGLER", "JOLTEON", "HYPNO", "HITMONCHAN", 
            "GLOOM", "GOLDUCK", "FLAREON", "FEAROW", "FARFETCHD", "ELECTABUZZ", "DUGTRIO", "DRATINI", "DODRIO", "CLOYSTER", "CHANSEY", 
            "BUTTERFREE", "ARCANINE", "AERODACTYL"
        ]
        self[Rarity.UNCOMMON] = [
            "VULPIX", "TENTACOOL", "STARYU", "SQUIRTLE", "SPEAROW", "SHELLDER", "SEEL", "SANDSLASH", "RHYHORN", "RATICATE", 
            "PSYDUCK", "PONYTA", "PIKACHU", "PIDGEOTTO", "PERSIAN", "METAPOD", "MAGNETON", "KOFFING", "KADABRA", "KABUTO", 
            "KAKUNA", "JYNX", "JIGGLYPUFF", "HORSEA", "HITMONLEE", "HAUNTER", "GROWLITHE", "GRIMER", "GRAVELER", "GOLBAT", 
            "EXEGGCUTE", "ELECTRODE", "CUBONE", "CLEFAIRY", "CHARMANDER", "BULBASAUR", "ARBOK", "ABRA"
        ]
        self[Rarity.COMMON] = [
            "WEEDLE", "VOLTORB", "VENONAT", "SLOWPOKE", "SANDSHREW", "POLIWAG", "PARAS", "ODDISH", 
            "NIDORAN_MALE", "NIDORAN_FEMALE", "MEOWTH", "MANKEY", "MAGNEMITE", "MAGIKARP", "MACHOP", "KRABBY", "GOLDEEN", 
            "GEODUDE", "GASTLY", "EEVEE", "EKANS", "DROWZEE", "DODUO", "DIGLETT", "CATERPIE", "BELLSPROUT"
        ]
        self[Rarity.CRITTER] = ["ZUBAT", "PIDGEY", "RATTATA"]
    
    def RarityByName(self, name):
        if (name in self[Rarity.CRITTER]): return Rarity.CRITTER
        elif (name in self[Rarity.COMMON]): return Rarity.COMMON
        elif (name in self[Rarity.UNCOMMON]): return Rarity.UNCOMMON
        elif (name in self[Rarity.RARE]): return Rarity.RARE
        elif (name in self[Rarity.VERY_RARE]): return Rarity.VERY_RARE
        elif (name in self[Rarity.EPIC]): return Rarity.EPIC
        elif (name in self[Rarity.LEGENDARY]): return Rarity.LEGENDARY
        elif (name in self[Rarity.MYTHIC]): return Rarity.MYTHIC

    def RarityByNumber(self, number):
        return self.RarityByName(self.Pokemons[number])

class Rarity(object):
    CRITTER = 0
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    VERY_RARE = 4
    EPIC = 5
    LEGENDARY = 6
    MYTHIC = 7

pokedex = Pokedex()