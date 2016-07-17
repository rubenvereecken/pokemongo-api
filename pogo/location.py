import logging
from geopy.geocoders import GoogleV3

import util

geolocator = GoogleV3()

def getLocation(search):
    loc = geolocator.geocode(search)
    return loc

def encodeLocation(loc):
    return (util.f2i(loc.latitude), util.f2i(loc.longitude), util.f2i(loc.altitude))
