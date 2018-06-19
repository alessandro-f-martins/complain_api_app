from api_main import app, api
from resources.complain import Complain, ComplainList

api.add_resource(ComplainList, '/complain')
api.add_resource(Complain, '/complain/<string:complain_id>')

if __name__ == '__main__':
    app.run()
