from geopy.geocoders import GoogleV3
from s2sphere import CellId, LatLng
from custom_exceptions import GeneralPogoException
import gpxpy.geo

# Wrapper for location
class Location(object):
    def __init__(self, locationLookup, geo_key):
        self.geo_key = geo_key
        self.locator = GoogleV3()
        if geo_key:
            self.locator = GoogleV3(api_key=geo_key)

        self.latitude, self.longitude, self.altitude = self.setLocation(locationLookup)

    def __str__(self):
        s = 'Coordinates: {} {} {}'.format(
            self.latitude,
            self.longitude,
            self.altitude
        )
        return s

    @staticmethod
    def getDistance(*coords):
        return gpxpy.geo.haversine_distance(*coords)

    @staticmethod
    def getRadianVector(latitude, longitude, olatitude, olongitude):
        # this is imprecise, but i need a vector, not a dumb haversine distance
        r = 6373e3
        dlon = olongitude - longitude 
        dlat = latitude - olatitude

        x = dlon * r * 100
        y = dlat * r * 100
        return (x, y)

    @staticmethod
    def getDistanceVector(*coords):
        return Location.getRadianVector(*[radians(coord) for coord in coords])

    def setLocation(self, search):
        try:
            geo = self.locator.geocode(search)
        except:
            raise GeneralPogoException('Error in Geo Request')
        return geo.latitude, geo.longitude, geo.altitude

    def setCoordinates(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def getCoordinates(self):
        return self.latitude, self.longitude, self.altitude

    def getCells(self, radius=10):
        origin = CellId.from_lat_lng(
            LatLng.from_degrees(
                self.latitude,
                self.longitude
            )
        ).parent(15)

        # Create walk around area
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
