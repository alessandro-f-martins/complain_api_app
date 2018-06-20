import json
from flask_restful import abort, Resource, reqparse
from api_util.api_log import Log
from api_util.http_codes import HTTP_CODES
from api_main import api_db
from pymongo import ReturnDocument


parser = reqparse.RequestParser()
parser.add_argument('complain')

log = Log()


def _validate_fields(obj, complete=False):
    # VALID_FIELDS = ['title', 'description', 'locale', 'address',
    # 'complement', 'zip', 'city', 'state', 'country', 'company']
    VALID_FIELDS = ['title', 'description', 'locale', 'company']

    for field in obj:
        if field not in VALID_FIELDS:
            abort(HTTP_CODES['Bad Request'],
                  message="Field '%s' is incorrect" % field)

    if complete and len(obj) != len(VALID_FIELDS):
        abort(HTTP_CODES['Bad Request'],
              message="Field list is incomplete: %d" % len(obj))


class Complain(Resource):
    ''' Complain: classe principal de dados de reclamacoes
    '''
    def get(self, complain_id):
        ret = api_db.db.complains.find_one(
            {'complain_id': complain_id}, projection={'_id': False})
        if not ret:
            abort(HTTP_CODES['Not Found'],
                  message="Complain %s not found" % complain_id)

        log.log_msg('Reclamacao obtida: %s' % ret)
        return ret

    def put(self, complain_id):
        complain_args = json.loads(parser.parse_args()['complain'])
        _validate_fields(complain_args, True)
        complain_to_replace = {'complain_id': complain_id}
        complain_to_replace.update(complain_args)
        result = api_db.db.complains.replace_one(
            {'complain_id': complain_id},
            complain_to_replace,
            upsert=True)

        ins_or_cr = ('updated', 'alterada')

        if not result.matched_count:
            api_db.db.complains_seq.update_one({'_id': 'complain_id'},
                                               {'$set': {'seq_value':
                                                         complain_id + 1}})
            ins_or_cr = ('created', 'criada')

        log.log_msg('Reclamacao %s: id# %d' % (ins_or_cr[1], complain_id))
        return 'Complain id# %d %s' % (complain_id, ins_or_cr[0]), \
            HTTP_CODES['Created']

    def patch(self, complain_id):
        complain_patches = json.loads(parser.parse_args()['complain'])
        _validate_fields(complain_patches)
        result = api_db.db.complains.update_one(
            {'complain_id': complain_id},
            {'$set': complain_patches})
        if not result.matched_count:
            abort(HTTP_CODES['Not Found'],
                  message="Complain %d not found" % complain_id)

        log.log_msg('Reclamacao alterada: id# %d' % complain_id)
        return 'Complain id# %d patched' % complain_id, HTTP_CODES['Created']

    def delete(self, complain_id):
        result = api_db.db.complains.delete_one(
            {'complain_id': complain_id})
        if not result.deleted_count:
            abort(HTTP_CODES['Not Found'],
                  message="Complain %s not found" % complain_id)

        log.log_msg('Reclamacao removida: id# %s' % complain_id)
        return 'Complain id# %s deleted' % complain_id


class ComplainList(Resource):
    ''' ComplainList: classe de lista de reclamacoes
    '''
    def get(self):
        ret = []
        for result in api_db.db.complains.find({}, projection={'_id': False}):
            ret.append(result)
        log.log_msg('Reclamacoes obtidas: %s' % ret)
        return ret

    def post(self):
        new_complain_args = json.loads(parser.parse_args()['complain'])
        _validate_fields(new_complain_args, True)
        new_complain_id = api_db.db.complains_seq.find_one_and_update(
            filter={'_id': 'complain_id'},
            update={'$inc': {'seq_value': 1}},
            return_document=ReturnDocument.BEFORE).get('seq_value')
        new_complain = {'complain_id': new_complain_id}
        new_complain.update(new_complain_args)

        api_db.db.complains.insert_one(new_complain)
        log.log_msg('Reclamacao criada: id# %s' % new_complain_id)

        return 'Complain id# %d created' % new_complain_id, \
            HTTP_CODES['Created']
