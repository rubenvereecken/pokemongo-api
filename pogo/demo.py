#!/usr/bin/python
import argparse
import logging
import sys

import api
import location


def setupLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('Line %(lineno)d,%(filename)s  - %(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


if __name__ == '__main__':
    setupLogger()
    logging.debug('Logger set up')

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--auth", help="Auth Service",
        required=True)
    parser.add_argument("-u", "--username", help="Username", required=True)
    parser.add_argument("-p", "--password", help="Password", required=True)
    parser.add_argument("-l", "--location", help="Location", required=True)
    parser.add_argument("-s", "--client_secret", help="PTC Client Secret")
    args = parser.parse_args()

    if args.auth not in ['ptc', 'google']:
        logging.error('Invalid auth service {}'.format(args.auth))
        sys.exit(-1)

    if args.auth == 'ptc':
        session = api.createPTCSession(args.username, args.password, args.location)
    elif args.auth == 'google':
        session = api.createGoogleSession(args.username, args.password, args.location)

    if session: # do stuff
        profile = session.getProfile()
        logging.info(profile)
    else:
        logging.critical('Session not created successfully')
