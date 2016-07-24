#!/usr/bin/python
import argparse
import logging
import time
import sys
from custom_exceptions import GeneralPogoException

from api import PokeAuthSession
from location import Location

from pokedex import pokedex

def setupLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('Line %(lineno)d,%(filename)s - %(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


# Example functions
# Get profile
def getProfile(session):
        logging.info("Printing Profile:")
        profile = session.getProfile()
        logging.info(profile)


# Grab the nearest pokemon details
def findBestPokemon(session):
    # Get Map details and print pokemon
    logging.info("Finding Nearby Pokemon:")
    cells = session.getMapObjects()
    closest = float("Inf")
    best = -1
    pokemonBest = None
    latitude, longitude, _ = session.getCoordinates()
    logging.info("Current pos: %f, %f" % (latitude, longitude))
    for cell in cells.map_cells:
        for pokemon in cell.wild_pokemons:
            # Find distance to pokemon
            dist = Location.getDistance(
                latitude,
                longitude,
                pokemon.latitude,
                pokemon.longitude
            )

            # Log the pokemon found
            logging.info("%s, %f meters away" % (
                pokedex.Pokemons[pokemon.pokemon_data.pokemon_id],
                dist
            ))

            rarity = pokedex.RarityByNumber(pokemon.pokemon_data.pokemon_id)
            #Greedy for rarest
            if rarity > best:
                pokemonBest = pokemon
                closest = dist
            # Greedy for closest
            elif dist < closest:
                pokemonBest = pokemon
                closest = dist
    return pokemonBest


# Catch a pokemon at a given point
def walkAndCatch(session, pokemon):
    if pokemon:
        logging.info("Catching %s:" % pokedex.Pokemons[pokemon.pokemon_data.pokemon_id])
        session.walkTo(pokemon.latitude, pokemon.longitude, step=3.2)
        logging.info(session.encounterAndCatch(pokemon))


# Do Inventory stuff
def getInventory(session):
    logging.info("Get Inventory:")
    logging.info(session.getInventory())


# Basic solution to spinning all forts.
# Since traveling salesman problem, not
# true solution. But at least you get
# those step in
def sortCloseForts(session):
    # Sort nearest forts (pokestop)
    logging.info("Sorting Nearest Forts:")
    cells = session.getMapObjects()
    latitude, longitude, _ = session.getCoordinates()
    ordered_forts = []
    for cell in cells.map_cells:
        for fort in cell.forts:
            dist = Location.getDistance(
                latitude,
                longitude,
                fort.latitude,
                fort.longitude
            )
            if fort.type == 1:
                ordered_forts.append({'distance': dist, 'fort': fort})

    ordered_forts = sorted(ordered_forts, key=lambda k: k['distance'])
    return [instance['fort'] for instance in ordered_forts]


# Find the fort closest to user
def findClosestFort(session):
    # Find nearest fort (pokestop)
    logging.info("Finding Nearest Fort:")
    return sortCloseForts(session)[0]


# Walk to fort and spin
def walkAndSpin(session, fort):
    # No fort, demo == over
    if fort:
        logging.info("Spinning a Fort:")
        # Walk over
        session.walkTo(fort.latitude, fort.longitude, step=3.2)
        # Give it a spin
        fortResponse = session.getFortSearch(fort)
        logging.info(fortResponse)


# Walk and spin everywhere
def walkAndSpinMany(session, forts):
    for fort in forts:
        walkAndSpin(session, fort)


# A very brute force approach to evolving
def evolveAllPokemon(session):
    inventory = session.checkInventory()
    for pokemon in inventory["party"]:
        logging.info(session.evolvePokemon(pokemon))
        time.sleep(1)


# You probably don't want to run this
def releaseAllPokemon(session):
    inventory = session.checkInventory()
    for pokemon in inventory["party"]:
        session.releasePokemon(pokemon)
        time.sleep(1)


# Just incase you didn't want any revives
def tossRevives(session):
    bag = session.checkInventory()["bag"]

    # 201 are revives.
    # TODO: We should have a reverse lookup here
    return session.recycleItem(201, bag[201])


# Set an egg to an incubator
def setEgg(session):
    inventory = session.checkInventory()

    # If no eggs, nothing we can do
    if len(inventory["eggs"]) == 0:
        return None

    egg = inventory["eggs"][0]
    incubator = inventory["incubators"][0]
    return session.setEgg(incubator, egg)


# Basic bot
def simpleBot(session):
    # Trying not to flood the servers
    cooldown = 1

    # Run the bot
    while True:
        try:
            forts = sortCloseForts(session)
            for fort in forts:
                pokemon = findBestPokemon(session)
                walkAndCatch(session, pokemon)
                walkAndSpin(session, fort)
                cooldown = 1
                time.sleep(1)

        # Catch problems and reauthenticate
        except GeneralPogoException as e:
            logging.critical('GeneralPogoException raised: %s', e)
            session = poko_session.reauthenticate(session)
            time.sleep(cooldown)
            cooldown *= 2

        except Exception as e:
            logging.critical('Exception raised: %s', e)
            session = poko_session.reauthenticate(session)
            time.sleep(cooldown)
            cooldown *= 2

# Entry point
# Start off authentication and demo
if __name__ == '__main__':
    setupLogger()
    logging.debug('Logger set up')

    # Read in args
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--auth", help="Auth Service", required=True)
    parser.add_argument("-u", "--username", help="Username", required=True)
    parser.add_argument("-p", "--password", help="Password", required=True)
    parser.add_argument("-l", "--location", help="Location", required=True)
    parser.add_argument("-g", "--geo_key", help="GEO API Secret")
    args = parser.parse_args()

    # Check service
    if args.auth not in ['ptc', 'google']:
        logging.error('Invalid auth service {}'.format(args.auth))
        sys.exit(-1)

    # Create PokoAuthObject
    poko_session = PokeAuthSession(
        args.username,
        args.password,
        args.auth,
        geo_key=args.geo_key
    )

    # Authenticate with a given location
    # Location is not inherent in authentication
    # But is important to session
    session = poko_session.authenticate(args.location)

    # Time to show off what we can do
    if session:

        # General
        getProfile(session)
        getInventory(session)

        # Pokemon related
        # 
        simpleBot(session)
        

    else:
        logging.critical('Session not created successfully')
