import logging
import time

from api import PokeAuthSession
from location import Location

from pokedex import pokedex
from inventory import items

class Trainer(object):
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
            # Heap in pokemon protos where we have long + lat
            pokemons = [p for p in cell.wild_pokemons] + [p for p in cell.catchable_pokemons]
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

        # Grab needed data from proto
        chances = encounter.capture_probability.capture_probability
        balls = encounter.capture_probability.pokeball_type
        bag = self.session.checkInventory().bag

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
            for i in range(len(balls)):
                if balls[i] in bag:
                    altBall = balls[i]
                    if chances[i] > thresholdP:
                        bestBall = balls[i]
                        break

            # If we can't determine a ball, try a berry
            # or use a lower class ball
            if bestBall == items.UNKNOWN:
                if not berried and items.RAZZ_BERRY in bag and bag[items.RAZZ_BERRY]:
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
                logging.info("Possible soft ban.")
                return attempt

            # Only try up to x attempts
            count += 1
            if count >= limit:
                logging.info("Over catch limit")
                return None


    # Catch a pokemon at a given point
    def walkAndCatch(self, pokemon):
        if pokemon:
            logging.info("Catching %s:" % pokedex[pokemon.pokemon_data.pokemon_id])
            self.session.walkTo(pokemon.latitude, pokemon.longitude, step=3.2)
            logging.info(self.encounterAndCatch(pokemon))


    # Do Inventory stuff
    def getInventory(self):
        logging.info("Get Inventory:")
        logging.info(self.session.getInventory())


    # Basic solution to spinning all forts.
    # Since traveling salesman problem, not
    # true solution. But at least you get
    # those step in
    def sortCloseForts(self):
        # Sort nearest forts (pokestop)
        logging.info("Sorting Nearest Forts:")
        cells = self.session.getMapObjects()
        latitude, longitude, _ = self.session.getCoordinates()
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
    def findClosestFort(self):
        # Find nearest fort (pokestop)
        logging.info("Finding Nearest Fort:")
        return self.sortCloseForts()[0]


    # Walk to fort and spin
    def walkAndSpin(self, fort):
        # No fort, demo == over
        if fort:
            details = self.session.getFortDetails(fort)
            logging.info("Spinning the Fort \"%s\":" % details.name)

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
        for pokemon in inventory.party:
            logging.info(self.session.evolvePokemon(pokemon))
            time.sleep(1)


    # You probably don't want to run this
    def releaseAllPokemon(self):
        inventory = self.session.checkInventory()
        for pokemon in inventory.party:
            self.session.releasePokemon(pokemon)
            time.sleep(1)


    # Just incase you didn't want any revives
    def tossRevives(self):
        bag = self.session.checkInventory().bag
        return self.session.recycleItem(items.REVIVE, bag[items.REVIVE])


    # Set an egg to an incubator
    def setEgg(self):
        inventory = self.session.checkInventory()

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
        party = self.session.checkInventory().party
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

        # Evolve those we want
        for evolve in evolables:
            candies = self.session.checkInventory().candies[evolve]
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
        bag = self.session.checkInventory().bag

        # Clear out all of a crtain type
        tossable = [items.POTION, items.SUPER_POTION, items.REVIVE]
        for toss in tossable:
            if toss in bag and bag[toss]:
                self.session.recycleItem(toss, bag[toss])

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


    # Basic bot
    def simpleBot(self):
        # Trying not to flood the servers
        cooldown = 1

        # Run the bot
        while True:
            forts = self.sortCloseForts()
            self.cleanPokemon(thresholdCP=300)
            self.cleanInventory()
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
                self.session = poko_session.reauthenticate(self.session)
                time.sleep(cooldown)
                cooldown *= 2

            except Exception as e:
                logging.critical('Exception raised: %s', e)
                self.session = poko_session.reauthenticate(self.session)
                time.sleep(cooldown)
                cooldown *= 2
