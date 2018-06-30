'''
--- Complain API microservice application ---
Author: Alessandro Martins
Module: api_routes
Description: routing module for the application. Adds the resource-related
classes to the REST API listener and performs initialization routines.
'''
from api_main import application, api, api_db
from resources.complain import Complain, ComplainList
from pymongo import GEOSPHERE

# Adding resource classes to the listener

api.add_resource(ComplainList, '/complain')
api.add_resource(Complain, '/complain/<int:complain_id>')


# Performing pre-first request tasks
@application.before_first_request
def before_first_request():
    ''' function before_first_request: called once per application activation,
        before the first request
    '''
    # Initializing id sequence, if needed
    if not api_db.db.complains_seq.find_one({'_id': 'complain_id'}):
        api_db.db.complains_seq.insert_one({'_id': 'complain_id',
                                            'seq_value': 1})
    # Creating geolocalization index
    api_db.db.complains.create_index([('locale.geo_location', GEOSPHERE)])


if __name__ == '__main__':
    application.run()
