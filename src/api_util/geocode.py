from googlemaps import Client
from api_util.config import Config
from api_main import api_db


_GMAPS = Client(key=Config.GKEY)
_EARTH_RADIUS = 6378137.0


def __get_geolocation(address):
    return _GMAPS.geocode(address)[0]['geometry']['location']


def insert_geoloc_info(complain):
    if Config.USE_GEOLOC:
        geo_location = __get_geolocation(
            ', '.join((complain['locale'].get('address'),
                       complain['locale'].get('city'),
                       complain['locale'].get('state'),
                       complain['locale'].get('country'))))
        complain['locale']['geo_location'] = \
            {'type': 'Point', 'coordinates': [geo_location['lng'],
                                              geo_location['lat']]}


def nearby_complains_query(complain_id, radius):
    if Config.USE_GEOLOC:
        complain_geoloc = api_db.db.complains.find_one(
            {'complain_id': int(complain_id)},
            projection={'_id': False, 'locale.geo_location': True})
        return {'locale.geo_location':
                {'$geoWithin':
                 {'$centerSphere':
                  [complain_geoloc['locale']['geo_location']['coordinates'],
                   float(radius)/_EARTH_RADIUS]}}}
    return {}
