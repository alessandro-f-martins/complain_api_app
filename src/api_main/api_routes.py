from api_main import app, api, api_db
from resources.complain import Complain, ComplainList

api.add_resource(ComplainList, '/complain')
api.add_resource(Complain, '/complain/<int:complain_id>')


@app.before_first_request
def before_first_request():
    ''' Preparacao da base de dados, antes do primeiro request
    '''
    if not api_db.db.complains_seq.find_one({'_id': 'complain_id'}):
        api_db.db.complains_seq.insert_one({'_id': 'complain_id',
                                            'seq_value': 1})


if __name__ == '__main__':
    app.run()
