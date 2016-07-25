#!/usr/bin/python
import argparse
import getpass

import logging
import time
import sys
from custom_exceptions import GeneralPogoException

from api import PokeAuthSession
from location import Location

from pokedex import pokedex
from quadtree import Tree, Rect

def setupLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('Line %(lineno)d,%(filename)s - %(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class Obibot(object):
    def __init__(self, session):
        self.session = session
    # Example functions
    # Get profile
    def getProfile(self):
            logging.info("Printing Profile:")
            profile = self.session.getProfile()
            logging.info(profile)


    # Grab the nearest pokemon details
    def findBestPokemon(self):
        # Get Map details and print pokemon
        logging.info("Finding Nearby Pokemon:")
        cells = self.session.getMapObjects()
        closest = float("Inf")
        best = -1
        pokemonBest = None
        latitude, longitude, _ = self.session.getCoordinates()
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
                    best = rarity
                    closest = dist
                # Greedy for closest
                elif dist < closest:
                    pokemonBest = pokemon
                    closest = dist
        return pokemonBest


    # Catch a pokemon at a given point
    def walkAndCatch(self, pokemon):
        if pokemon:
            logging.info("Catching %s:" % pokedex.Pokemons[pokemon.pokemon_data.pokemon_id])
            self.session.walkTo(pokemon.latitude, pokemon.longitude, step=4.2)
            logging.info(self.session.encounterAndCatch(pokemon))


    # Do Inventory stuff
    def getInventory(self):
        logging.info("Get Inventory:")
        logging.info(self.session.getInventory())

    def sortCloseForts(self):
        # Sort nearest forts (pokestop)
        logging.info("Sorting Nearest Forts:")
        cells = self.session.getMapObjects()
        latitude, longitude, _ = self.session.getCoordinates()
        all_forts = []
        left = float("Inf")
        top = float("Inf")
        right = float("-Inf")
        bottom = float("-Inf")

        #determine out rectangle

        for cell in cells.map_cells:
            for fort in cell.forts:
                if fort.type == 1:
                    distX, distY = Location.getDistanceVector(latitude, longitude, fort.latitude, fort.longitude)

                    if distX < left:
                        left = fort.longitude
                    if distX > right:
                        right = fort.longitude
                    if distY < top:
                        top = fort.latitude 
                    if distY > bottom:
                        bottom = fort.latitude
                    all_forts.append({'x': distX, 'y': distY, 'fort':fort})

        #build our tree for sorting
        tree = Tree(Rect(left, top, right, bottom), 8)
        for fort in all_forts:
            tree.addObject(fort['x'], fort['y'], fort['fort'])
        return tree.getObjects()
        


    # Find the fort closest to user
    def findClosestFort(self):
        # Find nearest fort (pokestop)
        logging.info("Finding Nearest Fort:")
        return sortCloseForts(self.session)[0]


    # Walk to fort and spin
    def walkAndSpin(self, fort):
        # No fort, demo == over
        if fort:
            logging.info("Spinning a Fort:")
            # Walk over
            self.session.walkTo(fort.latitude, fort.longitude, step=3.2)
            # Give it a spin
            fortResponse = self.session.getFortSearch(fort)
            logging.info(fortResponse)


    # Walk and spin everywhere
    def walkAndSpinMany(self, forts):
        for fort in forts:
            self.walkAndSpin(self.session, fort)


    # A very brute force approach to evolving
    def evolveAllPokemon(self):
        inventory = self.session.checkInventory()
        for pokemon in inventory["party"]:
            logging.info(session.evolvePokemon(pokemon))
            time.sleep(1)


    # You probably don't want to run this
    def releaseAllPokemon(self):
        inventory = self.session.checkInventory()
        for pokemon in inventory["party"]:
            self.session.releasePokemon(pokemon)
            time.sleep(1)


    # Just incase you didn't want any revives
    def tossRevives(self):
        bag = self.session.checkInventory()["bag"]

        # 201 are revives.
        # TODO: We should have a reverse lookup here
        return self.session.recycleItem(201, bag[201])


    # Set an egg to an incubator
    def setEgg(self):
        inventory = self.session.checkInventory()

        # If no eggs, nothing we can do
        if len(inventory["eggs"]) == 0:
            return None

        egg = inventory["eggs"][0]
        incubator = inventory["incubators"][0]
        return self.session.setEgg(incubator, egg)


    # Basic bot
    def obiBot(self):
        # Trying not to flood the servers
        _baseCooldown = 30
        cooldown = _baseCooldown
        #self.getProfile()
        #self.getInventory()
        # Run the bot
        while True:
            try:
                forts = self.sortCloseForts()
                for fort in forts:
                    pokemon = self.findBestPokemon()
                    self.walkAndCatch(pokemon)
                    self.walkAndSpin(fort)
                    #no problem this iteration, reset cooldown
                    cooldown = _baseCooldown
                    time.sleep(1)
            # Catch problems and reauthenticate
            except Exception as e:
                logging.critical('%s raised: %s', e.__class__.__name__ , e)
                session = poko_session.reauthenticate(self.session)
                time.sleep(cooldown)
                #back down progressively
                cooldown *= 2

# Entry point
# Start off authentication and demo
if __name__ == '__main__':
    setupLogger()
    logging.debug('Logger set up')

    # Read in args
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--auth", help="Auth Service", required=True)
    parser.add_argument("-u", "--username", help="Username", required=False)
    parser.add_argument("-p", "--password", help="Password", required=False)
    parser.add_argument("-l", "--location", help="Location", required=True)
    parser.add_argument("-g", "--geo_key", help="GEO API Secret")
    args = parser.parse_args()

    # Check service
    if args.auth not in ['ptc', 'google']:
        logging.error('Invalid auth service {}'.format(args.auth))
        sys.exit(-1)

    #So you can do things like a video without broadcasting your gmail 
    #user/pass to everyone by accident
    if not args.username:
        args.username = getpass.getuser()
    if not args.password:
        args.password = getpass.getpass()

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
        Obibot(session).obiBot()
        

    else:
        logging.critical('Session not created successfully')
