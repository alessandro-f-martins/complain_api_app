from googlemaps import Client

key = 'AIzaSyDRnUVxmIT4uvWEUs_WNBeQBwnZZP5TV6U'

gmaps = Client(key=key)


def get_geolocation(address):
    return gmaps.geocode(address)[0]['geometry']['location']
