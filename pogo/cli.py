import argparse
import logging
import sys

import api
import location


def setupLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


if __name__ == '__main__':
    setupLogger()
    logging.debug('ola')

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--auth", help="Auth Service",
        required=True)
    parser.add_argument("-u", "--username", help="Username", required=True)
    parser.add_argument("-p", "--password", help="Password", required=True)
    parser.add_argument("-l", "--location", help="Location", required=True)
    # parser.add_argument("-d", "--debug", help="Debug Mode", action='store_true')
    parser.add_argument("-s", "--client_secret", help="PTC Client Secret")
    # parser.set_defaults(DEBUG=True)
    args = parser.parse_args()

    if args.auth not in ['ptc', 'google']:
        logging.error('Invalid auth service {}'.format(args.auth))
        sys.exit(-1)

    if args.auth == 'ptc':
        session = api.createPTCSession(args.username, args.password)
    elif args.auth == 'google':
        session = api.createGoogleSession(args.username, args.password)

    loc = location.getLocation(args.location)
    if loc:
        logging.info('Location: {}'.format(loc.address))
        logging.info('Coordinates: {} {} {}'.format(loc.latitude, log.longitude,
            log.altitude))
    else:
        logging.critical('Location not found')
        sys.exit(-1)
    session.setLocation(loc)


    print(session)

