#!/usr/bin/python
import argparse
import logging
import time
import sys

import util
from api import PokeAuthSession
from trainer import Trainer

# Entry point
# Start off authentication and demo
if __name__ == '__main__':
    util.setupLogger()
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
        trainer = Trainer(session)
        # General
        trainer.getProfile()
        trainer.getInventory()

        # Pokemon related
        pokemon = trainer.findBestPokemon()
        trainer.walkAndCatch(pokemon)

        # Pokestop related
        fort = trainer.findClosestFort()
        trainer.walkAndSpin(fort)

        # see simpleBot() for logical usecases
        # eg. simpleBot(session)

    else:
        logging.critical('Session not created successfully')
