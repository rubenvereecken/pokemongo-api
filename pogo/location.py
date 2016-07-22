from math import sin, cos, sqrt, atan2, radians
from geopy.geocoders import GoogleV3
from s2sphere import CellId, LatLng

geolocator = GoogleV3()


def getLocation(search):
    loc = geolocator.geocode(search)
    return loc


def getCoords(latitude, longitude):
    try:
        loc = geolocator.reverse((latitude, longitude))
    except IOError:
        return False
    return loc[0]


def getRadianDistance(latitude, longitude, olatitude, olongitude):
    # approximate radius of earth in km
    R = 6373e3

    # delta angles
    dLat = olatitude - latitude
    dLon = olongitude - longitude

    # do the math
    # stackoverflow/questions/19412462/
    a = sin(dLat / 2)**2 + cos(latitude) * cos(olatitude) * sin(dLon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def getDistance(*coords):
    return getRadianDistance(*[radians(coord) for coord in coords])


def getCells(loc, radius=10):
    origin = CellId.from_lat_lng(LatLng.from_degrees(loc.latitude, loc.longitude)).parent(15)
    walk = [origin.id()]
    right = origin.next()
    left = origin.prev()

    # Search around provided radius
    for _ in range(radius):
        walk.append(right.id())
        walk.append(left.id())
        right = right.next()
        left = left.prev()

    # Return everything
    return sorted(walk)
