#!/usr/bin/python
import argparse
import logging
import time
import sys
import const
from custom_exceptions import GeneralPogoException

from api import PokeAuthSession
from location import Location


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
def findClosestPokemon(session):
    # Get Map details and print pokemon
    logging.info("Printing Nearby Pokemon:")
    cells = session.getMapObjects()
    closest = float("Inf")
    pokemonBest = None
    latitude, longitude, _ = session.getCoordinates()
    for cell in cells.map_cells:
        for pokemon in cell.wild_pokemons:
            # Log the pokemon found
            logging.info("%i at %f,%f" % (
                pokemon.pokemon_data.pokemon_id,
                pokemon.latitude,
                pokemon.longitude
            ))

            # Fins distance to pokemon
            dist = Location.getDistance(
                latitude,
                longitude,
                pokemon.latitude,
                pokemon.longitude
            )

            # Greedy for closest
            if dist < closest:
                pokemonBest = pokemon
                closest = dist
    return pokemonBest


# Catch a pokemon at a given point
def walkAndCatch(session, pokemon):
    if pokemon:
        logging.info("Catching nearest pokemon:")
        session.walkTo(pokemon.latitude, pokemon.longitude)
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
        session.walkTo(fort.latitude, fort.longitude)
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


def cleanPokemon(session):
    party = session.checkInventory()["party"]
    pidgeys = []
    rats = []
    for pokemon in party:
        if pokemon.pokemon_id == 16:  # The pdigey id ccording to google
            pidgeys.append(pokemon)
            continue

        if pokemon.pokemon_id == 19:  # The ratatta id
            rats.append(pokemon)
            continue

        if pokemon.cp < 250 or pokemon.pokemon_id in [17, 20]:
            session.releasePokemon(pokemon)

    candies = session.checkInventory()["candies"][16]
    while candies // 12 < len(pidgeys) and len(pidgeys):
        session.releasePokemon(pidgeys.pop())
        time.sleep(1)
        candies += 1

    candies = session.checkInventory()["candies"][19]
    while candies // 12 < len(rats) and len(rats):
        session.releasePokemon(rats.pop())
        time.sleep(1)
        candies += 1

    for pidgey in pidgeys:
        logging.info(session.evolvePokemon(pidgey))
        time.sleep(1)
        session.releasePokemon(pidgey)
        time.sleep(1)

    for rat in rats:
        logging.info(session.evolvePokemon(rat))
        time.sleep(1)
        session.releasePokemon(rat)
        time.sleep(1)


def cleanInventory(session):
    bag = session.checkInventory()["bag"]
    print(bag)
    tossable = [101, 102, 103, 104, 201, 202]
    for toss in tossable:
        if toss in bag and bag[toss]:
            session.recycleItem(toss, bag[toss])

    balls = [1, 2, 3]
    for ball in balls:
        if ball in bag and bag[ball] > 100:
            session.recycleItem(ball, bag[ball] - 100)


# Basic bot
def simpleBot(session):
    # Trying not to flood the servers
    cooldown = 1

    # Run the bot
    while True:
        try:
            forts = sortCloseForts(session)
            cleanPokemon(session)
            cleanInventory(session)
            for fort in forts:
                pokemon = findClosestPokemon(session)
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
        pokemon = findClosestPokemon(session)
        walkAndCatch(session, pokemon)

        # Pokestop related
        fort = findClosestFort(session)
        walkAndSpin(session, fort)

        simpleBot(session)
    else:
        logging.critical('Session not created successfully')
