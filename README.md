# Pokemon Go API for Python

This was originally based on
[this API](https://github.com/tejado/pokemongo-api-demo),
you can view this as an advanced
and cleaned up version
based on object-oriented principles.

Additions welcome.

# Current implementation
Our current implementaion covers most of the basics of gameplay. The following methods are availible:

```
# Get profile
def getProfile(self):

# Get Location
def getMapObjects(self, radius=10):

# Spin a pokestop
def getFortSearch(self, fort):

# Get encounter
def encounterPokemon(self, pokemon):

# Upon Encounter, try and catch
def catchPokemon(self, pokemon, pokeball=1):

# Evolve Pokemon
def evolvePokemon(self, pokemon):

# Transfer Pokemon
def releasePokemon(self, pokemon):

# Throw away items
def recycleItem(self, item_id, count):

# set an Egg into an incubator
def setEgg(self, item, pokemon):

# Get Eggs
def getEggs(self):

# Get Inventory
def getInventory(self):

# Get Badges
def getBadges(self):

# Get Settings
def getDownloadSettings(self):
```
Every method has been tested. Pull requests are encouraged.

## Demo
`demo.py` includes a demo of the API.

```
➜  python demo.py -a "google" -u "email@gmail.com" -p "thepassword" -l "The Atlantic Ocean"

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
