# Pokemon Go API for Python
[![Code Health](https://landscape.io/github/dmadisetti/pokemongo-api/master/landscape.svg?style=flat)](https://landscape.io/github/dmadisetti/pokemongo-api/master)
[![Build Status](https://travis-ci.org/dmadisetti/pokemongo-api.svg?branch=master)](https://travis-ci.org/dmadisetti/pokemongo-api)
## Why use this API?

This is arguably one of the cleanest python API's out there. It is our hope that this codebase is easily understood and very readable. We actively stay away from reflection, because actively managed calls provide a nicer experience than digging through protobufs. Development is currently active, so feel free to contribute any requests or functionality you think is missing.

*Important note*: `libencrypt.so` or `encrypt.dll` is needed in order for complete functionality. Minor calls such as getProfile will still work without this. We do not provide this library due to copyright issues. However, if you know where to look, you should be able to be able to find either the binaries or the source. 

## Installation

Install this package via pip i.e
`pip install git+git://github.com/rubenvereecken/pokemongo-api@master`
Alternatively, clone this and use `pip install .`

To get newest, run `pip install git+git://github.com/rubenvereecken/pokemongo-api@master --upgrade`

## Implementation

Trainer is a general purpose class meant to encapsulate basic functons. We recommend that you inherit from this class to provide your specific usecase. We understand that `Trainer` is not as fully flushed out as it could be- it is meant to be a stub for building more complex logic. e.g.
```
class Map(Trainer):
    """My beautiful map implementation"""

    def fillWebSocketsForRealtimeStuffOrSomethingLikeThat(self):
        """Fill websockets with profile data or something.
        I don't know. The world is your oyster."""
        profile = self.session.getProfile()
        ...
```

or

```
class Bot(Trainer):
    """Such bot, much cheat."""

    def catchAllThePokemonOrSomething(self):
        """Whatever it is botters do"""
        ...
```

Feel free to also ignore trainer and call session functions directly.

## Features

Our current implementaion covers most of the basics of gameplay. The following methods are availible:


| Description                                      | function      |
| ------------------                               | -------------:|
| Get Profile (Avatar, team etc..)                 | getProfile() |
| Get Eggs                                         | getEggs() |
| Get Inventory                                    | getInventory() |
| Get Badges                                       | getBadges() |
| Get Settings                                     | getDownloadSettings() |
| Get Location                                     | getMapObjects(radius=10, bothDirections=True) |
| Get Location                                     | getFortSearch(fort) |
| Get details about fort (image, text etc..)       | getFortDetails(fort) |
| Get encounter (akin to tapping a pokemon)        | encounterPokemon(pokemon) |
| Upon Encounter, try and catch                    | catchPokemon(pokemon, pokeball=items.POKE_BALL, normalized_reticle_size=1.950, hit_pokemon=True, spin_modifier=0.850, normalized_hit_position=1.0)|
| Use a razz berry or the like                     | useItemCapture(item_id, pokemon) |
| Use a Potion (Hyper potion, super, etc..)        | useItemPotion(item_id, pokemon) |
| Use a Revive (Max revive etc as well)            | useItemRevive(item_id, pokemon) |
| Evolve Pokemon (check for candies first)         | evolvePokemon(pokemon) |
| 'Transfers' a pokemon.                           | releasePokemon(pokemon) |
| Check for level up and apply                     | getLevelUp(newLevel) |
| Use a lucky egg                                  | useXpBoost() |
| Throw away items                                 | recycleItem(item_id, count) |
| set an Egg into an incubator                     | setEgg(item, pokemon) |
| Set the name of a given pokemon                  | nicknamePokemon(pokemon, nickname) |
| Set Pokemon as favorite                          | setFavoritePokemon(pokemon, is_favorite) |
| Upgrade a Pokemon's CP                           | upgradePokemon(pokemon) |
| Choose player's team - `BLUE`,`RED`, or `YELLOW`.| setPlayerTeam(team) |

Every method has been tested locally. Automated units tests are needed, and are currently in the works. Pull requests are encouraged.

## Demo
`demo.py` includes a demo of the API.

```
➜  python demo.py -a "google" -u "email@gmail.com" -p "thepassword" -l "The Atlantic Ocean" -e"libencrypt.so"

2016-07-17 16:26:59,947 - INFO - Creating Google session for email@gmail.com
2016-07-17 16:26:59,953 - INFO - Starting new HTTPS connection (1): android.clients.google.com
2016-07-17 16:27:00,362 - INFO - Starting new HTTPS connection (1): android.clients.google.com
2016-07-17 16:27:00,789 - INFO - Location: The Atlantic Ocean
2016-07-17 16:27:00,789 - INFO - Coordinates: 51.01 7.12 0.0
2016-07-17 16:27:00,793 - INFO - Starting new HTTPS connection (1): pgorelease.nianticlabs.com
2016-07-17 16:27:01,633 - INFO - creation_time: 3341800000
team: 3
avatar {
  hair: 1
  shirt: 1
  pants: 1
  hat: 1
  shoes: 1
  eyes: 1
  backpack: 1
}
max_pokemon_storage: 250
max_item_storage: 400
daily_bonus {
  next_defender_bonus_collect_timestamp_ms: 4106877052
}
currency {
  type: "STARDUST"
  quantity: 9001
}
```

This is achieved with minimal coding effort on the client's part
(extract from `demo.py`):

```
  # ... Blabla define the parser
  if args.auth == 'ptc':
      session = api.createPTCSession(args.username, args.password, args.location)
  elif args.auth == 'google':
      session = api.createGoogleSession(args.username, args.password, args.location)

  if session: # do stuff
      profile = session.getProfile()
      logging.info(profile)
```

## Contribution
Hell yeah!
I'm on [Slack](https://pkre.slack.com) too
(want an [invite](https://shielded-earth-81203.herokuapp.com)?)
if you want to have a quick chat.

I welcome all PRs but for big changes it'd be best
to open an issue so I have some idea of what's going on.
This thing is under heavy development after all.

## Protocol
We currently use [AeonLucid's Pokemon Go Protobuf protocol](https://github.com/AeonLucid/POGOProtos).

## Contributors
Thanks @dmadisetti for keeping this baby up and giving it the love it deserves,
along with everybody else who took the time to set up a PR!
