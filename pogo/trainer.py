import logging
import time

from pogo.custom_exceptions import GeneralPogoException
from pogo.location import Location
from pogo.pokedex import pokedex
from pogo.inventory import items


class Trainer(object):
    """Trainer is a general purpose class meant to encapsulate basic functons.
    We recommend that you inherit from this class to provide your specific
    usecase.
    """

    def __init__(self, auth, session):
        self._auth = auth
        self._session = session

    @property
    def auth(self):
        return self._auth

    @property
    def session(self):
        return self._session

    # Get profile
    def getProfile(self):
        logging.info("Printing Profile:")
        profile = self.session.getProfile()
        logging.info(profile)

    # Do Inventory stuff
    def checkInventory(self):
        logging.info("Checking Inventory:")
        logging.info(self.session.inventory)

    # Grab the nearest pokemon details
    def findBestPokemon(self):
        # Get Map details and print pokemon
        logging.info("Finding Nearby Pokemon:")
        cells = self.session.getMapObjects(bothDirections=False)
        closest = float("Inf")
        best = -1
        pokemonBest = None
        latitude, longitude, _ = self.session.getCoordinates()
        logging.info("Current pos: %f, %f" % (latitude, longitude))
        for cell in cells.map_cells:
            # Heap in pokemon protos where we have long + lat
            pokemons = [p for p in cell.wild_pokemons]
            pokemons += [p for p in cell.catchable_pokemons]
            for pokemon in pokemons:
                # Normalize the ID from different protos
                pokemonId = getattr(pokemon, "pokemon_id", None)
                if not pokemonId:
                    pokemonId = pokemon.pokemon_data.pokemon_id

                # Find distance to pokemon
                dist = Location.getDistance(
                    latitude,
                    longitude,
                    pokemon.latitude,
                    pokemon.longitude
                )

                # Log the pokemon found
                logging.info("%s, %f meters away" % (
                    pokedex[pokemonId],
                    dist
                ))

                rarity = pokedex.getRarityById(pokemonId)
                # Greedy for rarest
                if rarity > best:
                    pokemonBest = pokemon
                    best = rarity
                    closest = dist
                # Greedy for closest of same rarity
                elif rarity == best and dist < closest:
                    pokemonBest = pokemon
                    closest = dist
        return pokemonBest

    # Wrap both for ease
    def encounterAndCatch(self, pokemon, thresholdP=0.5, limit=5, delay=2):
        # Start encounter
        encounter = self.session.encounterPokemon(pokemon)

        # If party full
        if encounter.status == encounter.POKEMON_INVENTORY_FULL:
            logging.error("Can't catch! Party is full!")
            return None

        # Grab needed data from proto
        chances = encounter.capture_probability.capture_probability
        balls = encounter.capture_probability.pokeball_type
        balls = balls or [items.POKE_BALL, items.GREAT_BALL, items.ULTRA_BALL]
        bag = self.session.inventory.bag

        # Have we used a razz berry yet?
        berried = False

        # Make sure we aren't oer limit
        count = 0

        # Attempt catch
        while True:
            bestBall = items.UNKNOWN
            altBall = items.UNKNOWN

            # Check for balls and see if we pass
            # wanted threshold
            for i, ball in enumerate(balls):
                if bag.get(ball, 0) > 0:
                    altBall = ball
                    if chances[i] > thresholdP:
                        bestBall = ball
                        break

            # If we can't determine a ball, try a berry
            # or use a lower class ball
            if bestBall == items.UNKNOWN:
                if not berried and bag.get(items.RAZZ_BERRY, 0) > 0:
                    logging.info("Using a RAZZ_BERRY")
                    self.session.useItemCapture(items.RAZZ_BERRY, pokemon)
                    berried = True
                    time.sleep(delay)
                    continue

                # if no alt ball, there are no balls
                elif altBall == items.UNKNOWN:
                    raise GeneralPogoException("Out of usable balls")
                else:
                    bestBall = altBall

            # Try to catch it!!
            logging.info("Using a %s" % items[bestBall])
            attempt = self.session.catchPokemon(pokemon, bestBall)
            time.sleep(delay)

            # Success or run away
            if attempt.status == 1:
                return attempt

            # CATCH_FLEE is bad news
            if attempt.status == 3:
                if count == 0:
                    logging.info("Possible soft ban.")
                else:
                    logging.info("Pokemon fleed at %dth attempt" % (count + 1))
                return attempt

            # Only try up to x attempts
            count += 1
            if count >= limit:
                logging.info("Over catch limit")
                return None

    # Walk over to position in meters
    def walkTo(self, olatitude, olongitude, epsilon=10, step=7.5, delay=10):
        if step >= epsilon:
            raise GeneralPogoException("Walk may never converge")

        if self.session.location.noop:
            raise GeneralPogoException("Location not set")

        # Calculate distance to position
        latitude, longitude, _ = self.session.getCoordinates()
        dist = closest = Location.getDistance(
            latitude,
            longitude,
            olatitude,
            olongitude
        )

        # Run walk
        divisions = closest / step
        dLat = (latitude - olatitude) / divisions
        dLon = (longitude - olongitude) / divisions

        logging.info(
            "Walking %f meters. This will take ~%f seconds..." % (
                dist,
                dist / step
            )
        )

        # Approach at supplied rate
        steps = 1
        while dist > epsilon:
            logging.debug("%f m -> %f m away", closest - dist, closest)
            latitude -= dLat
            longitude -= dLon
            steps %= delay
            if steps == 0:
                self.session.setCoordinates(
                    latitude,
                    longitude
                )
            time.sleep(1)
            dist = Location.getDistance(
                latitude,
                longitude,
                olatitude,
                olongitude
            )
            steps += 1

        # Finalize walk
        steps -= 1
        if steps % delay > 0:
            time.sleep(delay - steps)
            self.session.setCoordinates(
                latitude,
                longitude
            )

    # Catch a pokemon at a given point
    def walkAndCatch(self, pokemon):
        if pokemon:
            logging.info(
                "Catching %s:" % pokedex[pokemon.pokemon_data.pokemon_id]
            )
            self.walkTo(pokemon.latitude, pokemon.longitude, step=3.2)
            logging.info(self.encounterAndCatch(pokemon))

    # We sort forts using Hilbert indices generated by their
    # coordinates. To avoid the long walk to the first point,
    # we make sure we look up forts only one way on the Hilbert
    # path.
    def sortCloseForts(self):
        # Sort nearest forts (pokestop)
        logging.info("Sorting Nearest Forts:")
        cells = self.session.getMapObjects(bothDirections=False)
        latitude, longitude, _ = self.session.getCoordinates()
        ordered_forts = []
        for cell in cells.map_cells:
            for fort in cell.forts:
                if fort.type == 1:
                    ordered_forts.append({
                        'hilbert': Location.getLatLongIndex(
                            fort.latitude, fort.longitude
                        ),
                        'fort': fort
                    })

        ordered_forts = sorted(ordered_forts, key=lambda k: k['hilbert'])

        return [instance['fort'] for instance in ordered_forts]

    # Find the fort closest to user
    def findClosestFort(self):
        # Find nearest fort (pokestop)
        logging.info("Finding Nearest Fort:")
        forts = self.sortCloseForts()
        if forts:
            return forts[0]
        logging.info("No forts found..")
        return None

    # Walk to fort and spin
    def walkAndSpin(self, fort):
        # No fort, demo == over
        if fort:
            details = self.session.getFortDetails(fort)
            logging.info("Spinning the Fort \"%s\":" % details.name)

            # Walk over
            self.walkTo(fort.latitude, fort.longitude, step=3.2)
            # Give it a spin
            fortResponse = self.session.getFortSearch(fort)
            logging.info(fortResponse)

    # Walk and spin everywhere
    def walkAndSpinMany(self, forts):
        for fort in forts:
            self.walkAndSpin(self.session, fort)

    # A very brute force approach to evolving
    def evolveAllPokemon(self):
        inventory = self.session.inventory
        for pokemon in inventory.party:
            logging.info(self.session.evolvePokemon(pokemon))
            time.sleep(1)

    # You probably don't want to run this
    def releaseAllPokemon(self):
        inventory = self.session.inventory
        for pokemon in inventory.party:
            self.session.releasePokemon(pokemon)
            time.sleep(1)

    # Set an egg to an incubator
    def setEggs(self):
        inventory = self.session.inventory

        # If no eggs, nothing we can do
        if len(inventory.eggs) == 0:
            return None

        egg = inventory.eggs[0]
        incubator = inventory.incubators[0]
        return self.session.setEgg(incubator, egg)

    # Understand this function before you run it.
    # Otherwise you may flush pokemon you wanted.
    def cleanPokemon(self, thresholdCP=50):
        logging.info("Cleaning out Pokemon...")
        party = self.session.inventory.party
        evolables = [pokedex.PIDGEY, pokedex.RATTATA, pokedex.ZUBAT]
        toEvolve = {evolve: [] for evolve in evolables}
        for pokemon in party:
            # If low cp, throw away
            if pokemon.cp < thresholdCP:
                # It makes more sense to evolve some,
                # than throw away
                if pokemon.pokemon_id in evolables:
                    toEvolve[pokemon.pokemon_id].append(pokemon)
                    continue

                # Get rid of low CP, low evolve value
                logging.info("Releasing %s" % pokedex[pokemon.pokemon_id])
                self.session.releasePokemon(pokemon)
                time.sleep(2)

        # Evolve those we want
        for evolve in evolables:
            # if we don't have any candies of that type
            # e.g. not caught that pokemon yet
            if evolve not in self.session.inventory.candies:
                continue
            candies = self.session.inventory.candies[evolve]
            pokemons = toEvolve[evolve]
            # release for optimal candies
            while candies // pokedex.evolves[evolve] < len(pokemons):
                pokemon = pokemons.pop()
                logging.info("Releasing %s" % pokedex[pokemon.pokemon_id])
                self.session.releasePokemon(pokemon)
                time.sleep(1)
                candies += 1

            # evolve remainder
            for pokemon in pokemons:
                logging.info("Evolving %s" % pokedex[pokemon.pokemon_id])
                logging.info(self.session.evolvePokemon(pokemon))
                time.sleep(1)
                self.session.releasePokemon(pokemon)
                time.sleep(1)

    def cleanInventory(self):
        logging.info("Cleaning out Inventory...")
        bag = self.session.inventory.bag

        # Clear out all of a certain type
        tossable = [items.POTION, items.SUPER_POTION, items.REVIVE]
        for toss in tossable:
            if toss in bag and bag[toss]:
                self.session.recycleItem(toss, bag[toss])
                time.sleep(1)

        # Limit a certain type
        limited = {
            items.POKE_BALL: 50,
            items.GREAT_BALL: 100,
            items.ULTRA_BALL: 150,
            items.RAZZ_BERRY: 25
        }
        for limit in limited:
            if limit in bag and bag[limit] > limited[limit]:
                self.session.recycleItem(limit, bag[limit] - limited[limit])
                time.sleep(1)

    # Basic bot
    def simpleBot(self):
        # Trying not to flood the servers
        cooldown = 1

        # Run the bot
        while True:
            forts = self.sortCloseForts()
            self.cleanPokemon()
            self.cleanInventory()
            time.sleep(1)
            try:
                for fort in forts:
                    pokemon = self.findBestPokemon()
                    self.walkAndCatch(pokemon)
                    self.walkAndSpin(fort)
                    cooldown = 1
                    time.sleep(1)

            # Catch problems and reauthenticate
            except GeneralPogoException as e:
                logging.critical('GeneralPogoException raised: %s', e)
                self._session = self.auth.reauthenticate(self.session)
                time.sleep(cooldown)
                cooldown *= 2

            except Exception as e:
                logging.critical('Exception raised: %s', e)
                self._session = self.auth.reauthenticate(self.session)
                time.sleep(cooldown)
                cooldown *= 2
