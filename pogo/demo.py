#!/usr/bin/python
import argparse
import logging
import time
import sys

import api
import location


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
def findClosetPokemon(session):
    # Get Map details and print pokemon
    logging.info("Printing Nearby Pokemon:")
    cells = session.getMapObjects()
    closest = float("Inf")
    pokemonBest = None
    latitude, longitude, _ = session.getLocation()
    for cell in cells.map_cells:
        for pokemon in cell.wild_pokemons:
            # Log the pokemon found
            logging.info("%i at %f,%f" % (
                pokemon.pokemon_data.pokemon_id,
                pokemon.latitude,
                pokemon.longitude
            ))

            # Fins distance to pokemon
            dist = location.getDistance(
                latitude,
                longitude,
                pokemon.latitude,
                pokemon.longitude
            )

            # Greedy for closest
            if dist < closest:
                pokemonBest = pokemon
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


def sortCloseForts(session):
    # Sort nearest forts (pokestop)
    logging.info("Sorting Nearest Forts:")
    cells = session.getMapObjects()
    latitude, longitude, _ = session.getLocation()
    ordered_forts = []
    for cell in cells.map_cells:
        for fort in cell.forts:
            dist = location.getDistance(
                latitude,
                longitude,
                fort.latitude,
                fort.longitude
            )
            if fort.type == 1:
                ordered_forts.append({'distance': dist, 'fort': fort})

    ordered_forts = sorted(ordered_forts, key=lambda k: k['distance'])
    return [instance['fort'] for instance in ordered_forts]


def findClosestPokemon(session):
    # Find nearest fort (pokestop)
    logging.info("Finding Nearest Fort:")
    cells = session.getMapObjects()
    closest = float("Inf")
    fortBest = None
    latitude, longitude, _ = session.getLocation()
    for cell in cells.map_cells:
        for fort in cell.forts:
            dist = location.getDistance(
                latitude,
                longitude,
                fort.latitude,
                fort.longitude
            )
            if dist < closest and fort.type == 1:
                closest = dist
                fortBest = fort
    return fortBest


def walkAndSpin(session, forts):
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
        walkAndSpin(fort)


# A very brute force approach to evolving
def evolveAllPokemon(session):
    inventory = session.checkInventory()
    for pokemon in inventory["party"]:
        session.evolvePokemon(pokemon)
        time.sleep(1)


# You probably don't want to run this
def releaseAllPokemon(session):
    inventory = session.checkInventory()
    for pokemon in inventory["party"]:
        session.releasePokemon(pokemon)
        time.sleep(1)


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
    while True:
        forts = sortCloseForts(session)
        for fort in forts:
            pokemon = findClosestPokemon(session)
            walkAndCatch(session, pokemon)
            walkAndSpin(session, fort)

# Entry point
# Start off authentication and demo
if __name__ == '__main__':
    setupLogger()
    logging.debug('Logger set up')

    # Read in args
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--auth", help="Auth Service",
                        required=True)
    parser.add_argument("-u", "--username", help="Username", required=True)
    parser.add_argument("-p", "--password", help="Password", required=True)
    parser.add_argument("-l", "--location", help="Location", required=True)
    parser.add_argument("-s", "--client_secret", help="PTC Client Secret")
    args = parser.parse_args()

    # Check service
    if args.auth not in ['ptc', 'google']:
        logging.error('Invalid auth service {}'.format(args.auth))
        sys.exit(-1)

    # Authenticate
    if args.auth == 'ptc':
        session = api.createPTCSession(
            args.username,
            args.password,
            args.location
        )
    elif args.auth == 'google':
        session = api.createGoogleSession(
            args.username,
            args.password,
            args.location
        )

    # Time to show off what we can do
    if session:

        # General
        getProfile(session)
        getInventory(session)

        # Pokemon related
        pokemon = findClosetPokemon(session)
        walkAndCatch(session, pokemon)

        # Pokestop related
        fort = findClosestFort(session)
        walkAndSpin(session, fort)

    else:
        logging.critical('Session not created successfully')
