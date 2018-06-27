'''
--- Complain API microservice application ---
Author: Alessandro Martins
Module: geocode
Description: provides geolocation capabilities for the system. Based upon
Google Maps API.
'''
from googlemaps import Client
from api_util.config import Config
from api_main import api_db


_GMAPS = Client(key=Config.GKEY)
# Earth's radius in meters
_EARTH_RADIUS = 6378137.0


def __get_geolocation(address):
    # Uses Google Maps API to provide geographic coordinates for a given
    # <address>
    return _GMAPS.geocode(address)[0]['geometry']['location']


def insert_geoloc_info(complain):
    ''' function insert_geoloc_info(complain): for a given <complain>, updates
       its locale sub-document with the GeoJSON-formatted geographical
       coordinates
    '''
    if Config.USE_GEOLOC:
        # Concatenates together <complain>'s full adddress components to
        # obtain its geolocation
        geo_location = __get_geolocation(
            ', '.join((complain['locale'].get('address'),
                       complain['locale'].get('city'),
                       complain['locale'].get('state'),
                       complain['locale'].get('country'))))
        # Coordinates are attached to a new "geo_location" attribute
        complain['locale']['geo_location'] = \
            {'type': 'Point', 'coordinates': [geo_location['lng'],
                                              geo_location['lat']]}


def nearby_complains_query(complain_id, radius):
    ''' function nearby_complains_query(complain_id, radius): returns a MongoDB
        query document which, once executed, returns the complaints which are
        situated within <radius> meters from where a complaint with
        <complain_id> was issued.
    '''
    if Config.USE_GEOLOC:
        complain_geoloc = api_db.db.complains.find_one(
            {'complain_id': int(complain_id)},
            projection={'_id': False, 'locale.geo_location': True})
        # Uses MongoDB native geolocation $geoWithin function to evaluate
        # complaints located within a sphered-surface circle of radius <radius>
        # centered on the querying complaint geographic location. As the
        # measurement radius must be given in radians, convertion to meters is
        # needed, dividing search radius by the Earth's radius.
        if complain_geoloc:
            return {'locale.geo_location':
                    {'$geoWithin':
                     {'$centerSphere':
                      [complain_geoloc['locale']['geo_location']
                       ['coordinates'], float(radius)/_EARTH_RADIUS]}}}
    return {}
