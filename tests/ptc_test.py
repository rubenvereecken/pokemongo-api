from httmock import all_requests, HTTMock
from pogo.api import PokeAuthSession
import unittest
import pickle


# TODO: Create for Session, Trainer, and Google
class PtcTest(unittest.TestCase):

    def setUp(self):
        self.__call = 0
        self.__CALLS = ['r', 'authResponse', 'r2', 'rpc']

    def attemptSession(self, auth, locationLookup=None):
        # Set up fake endpoint
        @all_requests
        def fake_ptc(url, request):
            file = open(
                "tests/pickles/%s.pickle" % self.__CALLS[self.__call],
                "rb"
            )
            response = pickle.load(file)
            self.__call += 1
            return response

        self.__call = 0
        with HTTMock(fake_ptc):
            auth.authenticate(locationLookup=locationLookup)

    def test_noLib_noLocation(self):
        # Create PokoAuthObject
        self.attemptSession(PokeAuthSession(
            "user",
            "password",
            "ptc",
            None,
        ))

    def test_Lib_noLocation(self):
        # Create PokoAuthObject
        self.attemptSession(PokeAuthSession(
            "user",
            "password",
            "ptc",
            "lib.so",
        ))

    def test_noLib_Location(self):
        # Create PokoAuthObject
        self.attemptSession(PokeAuthSession(
            "user",
            "password",
            "ptc",
            None,
        ), locationLookup="New York")

    def test_Lib_Location(self):
        # Create PokoAuthObject
        self.attemptSession(PokeAuthSession(
            "user",
            "password",
            "ptc",
            "lib.so",
        ), locationLookup="New York")
