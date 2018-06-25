from api_main import application, api, api_db
from resources.complain import Complain, ComplainList
from pymongo import GEOSPHERE


api.add_resource(ComplainList, '/complain')
api.add_resource(Complain, '/complain/<int:complain_id>')


@application.before_first_request
def before_first_request():
    ''' Preparacao da base de dados, antes do primeiro request
    '''
    if not api_db.db.complains_seq.find_one({'_id': 'complain_id'}):
        api_db.db.complains_seq.insert_one({'_id': 'complain_id',
                                            'seq_value': 1})

    api_db.db.complains.create_index([('locale.geo_location', GEOSPHERE)])


if __name__ == '__main__':
    application.run()
