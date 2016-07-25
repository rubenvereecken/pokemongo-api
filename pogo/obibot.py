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
from trainer import Trainer

def setupLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('Line %(lineno)d,%(filename)s - %(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class Obibot(Trainer):
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
        
    # Basic bot with quadtree sorting
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
