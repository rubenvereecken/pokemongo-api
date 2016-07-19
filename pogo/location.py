from google.protobuf.internal import encoder
from geopy.geocoders import GoogleV3
from s2sphere import CellId, LatLng
import logging

import util

geolocator = GoogleV3()

def getLocation(search):
    loc = geolocator.geocode(search)
    return loc

def encodeLocation(loc):
    return (util.f2i(loc.latitude), util.f2i(loc.longitude), util.f2i(loc.altitude))


def getCells(loc, radius = 10):
    origin = CellId.from_lat_lng(LatLng.from_degrees(loc.latitude, loc.longitude)).parent(15)
    walk = [origin.id()]
    right = origin.next()
    left = origin.prev()

    # Search around provided radius
    for i in range(radius):
        walk.append(right.id())
        walk.append(left.id())
        next = right.next()
        prev = left.prev()

    # Return everything
    return sorted(walk)