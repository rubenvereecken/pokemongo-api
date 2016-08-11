#!/usr/bin/python
import argparse
import logging
import time

import pogo.util as util
from pogo.api import PokeAuthSession
from pogo.custom_exceptions import GeneralPogoException
import pogo.Trainer as Trainer


# Example functions
# Get profile
def getProfile(session):
    logging.info("Printing Profile:")
    profile = session.getProfile()
    logging.info(profile)


def setNickname(session):
    pokemon = session.inventory.party[0]
    session.nicknamePokemon(pokemon, "Testing")


# Do Inventory stuff
def checkInventory(session):
    logging.info("Checking Inventory:")
    logging.info(session.inventory)


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
    parser.add_argument("-e", "--encrypt_lib", help="Encryption Library")
    parser.add_argument("-g", "--geo_key", help="GEO API Secret")
    parser.add_argument("-l", "--location", help="Location")
    parser.add_argument("-proxy", "--proxy", help="Full Path to Proxy")
    args = parser.parse_args()

    # Check service
    if args.auth not in ['ptc', 'google']:
        raise GeneralPogoException('Invalid auth service {}'.format(args.auth))

    # Set proxy
    if args.proxy:
        PokeAuthSession.setProxy(args.proxy)

    # Create PokoAuthObject
    auth_session = PokeAuthSession(
        args.username,
        args.password,
        args.auth,
        args.encrypt_lib,
        geo_key=args.geo_key,
    )

    # Authenticate with a given location
    # Location is not inherent in authentication
    # But is important to session
    if args.location:
        session = auth_session.authenticate(locationLookup=args.location)
    else:
        session = auth_session.authenticate()

    # Time to show off what we can do
    if session:
        trainer = Trainer(auth_session, session)

        # Wait for a second to prevent GeneralPogoException
        # Goodnight moon. Goodnight moon.
        time.sleep(1)

        # General
        trainer.getProfile()
        trainer.checkInventory()

        # Things we need GPS for
        if args.location:
            # We need a solid sleep to get over rate limting
            # Goodnight cow jumping over the moon.
            time.sleep(10)

            # Pokemon related
            pokemon = trainer.findBestPokemon()
            trainer.walkAndCatch(pokemon)

            # Goodnight light and the red balloon.
            time.sleep(5)

            # Pokestop related
            fort = trainer.findClosestFort()
            trainer.walkAndSpin(fort)

            # see simpleBot() for logical usecases
            # simpleBot(session)

    else:
        logging.critical('Session not created successfully')
