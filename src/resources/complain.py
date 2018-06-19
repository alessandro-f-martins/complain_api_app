import json
from flask_restful import abort, Resource, reqparse
from api_util.api_log import Log
from api_main import mongo_db as db
from pymongo import ReturnDocument


parser = reqparse.RequestParser()
parser.add_argument('complain')

log = Log()


class Complain(Resource):
    ''' Complain: classe principal de dados de reclamacoes
    '''
    def get(self, complain_id):
        ret = db.complain_db.complains.find_one(
            {'complain_id': complain_id})
        if not ret:
            abort(404, message="Complain %s not found" % complain_id)

        log.log_msg('Reclamacao obtida: %s' % ret)
        return ret

    def put(self, complain_id):
        complain_to_update = json.loads(parser.parse_args()['complain'])
        result = db.complain_db.complains.replace_one(
                                        {'complain_id': complain_id},
                                        complain_to_update, upsert=True)
        log.log_msg('Reclamacao alterada: id# %s' % complain_id)
        return 'Complain id# %s updated' % complain_id, 201

    def patch(self, complain_id):
        complain_patches = json.loads(parser.parse_args()['complain'])
        result = db.complain_db.complains.update_one(
                                        {'complain_id': complain_id},
                                        complain_patches)
        if not result.matched_count:
            abort(404, message="Complain %s not found" % complain_id)

        log.log_msg('Reclamacao alterada: id# %s' % complain_id)
        return 'Complain id# %s patched' % complain_id, 201

    def delete(self, complain_id):
        result = db.complain_db.complains.delete_one(
                                        {'complain_id': complain_id})
        if not result.deleted_count:
            abort(404, message="Complain %s not found" % complain_id)

        log.log_msg('Reclamacao removida: id# %s' % complain_id)
        return 'Complain id# %s deleted' % complain_id, 204


class ComplainList(Resource):
    ''' ComplainList: classe de lista de reclamacoes
    '''
    def get(self):
        ret = db.complain_db.complains.find({})
        log.log_msg('Reclamacoes obtidas: %s' % ret)
        return ret

    def post(self):
        args = parser.parse_args()
        new_complain_id = db.complains_seq.find_one_and_update(
            filter={'_id': 'complain_id'},
            update={'$inc': {'seq_value': 1}},
            return_document=ReturnDocument.AFTER,
        ).get('seq_value')
        new_complain = {'complain_id': new_complain_id}
        new_complain.update(json.loads(args['complain']))

        db.complain_db.complains.insert_one(new_complain)
        log.log_msg('Reclamacao criada: id# %s' % new_complain_id)

        return 'Complain id# %s created' % new_complain_id, 201
