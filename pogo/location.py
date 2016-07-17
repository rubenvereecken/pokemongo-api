import logging
from geopy.geocoders import GoogleV3

geolocator = GoogleV3()

def getLocation(search):
    loc = geolocator.geocode(search)
    return loc
