import re
from math import radians
import json
from flask_restful import abort, Resource, reqparse
from api_util import Log, HTTP_CODES, get_geolocation
from api_main import api_db
from pymongo import ReturnDocument

_VALID_FIELDS = ('title', 'description', 'locale', 'company')
_VALID_LOCALE_FIELDS = ('address', 'complement', 'vicinity',
                        'zip', 'city', 'state', 'country')
_USE_GEOLOC = True

parser = reqparse.RequestParser()
parser.add_argument('complain')

for field in _VALID_FIELDS:
    if field != 'locale':
        parser.add_argument(field)
        parser.add_argument(field + '_like')

for field in _VALID_LOCALE_FIELDS:
    if field != 'complement':
        parser.add_argument(field)
        parser.add_argument(field + '_like')


log = Log()


def _validate_fields(obj, complete=False):
    error_msg = None

    for field in obj:
        if field not in _VALID_FIELDS:
            error_msg = 'Field "%s" is incorrect' % field
            break

    if complete:
        if len(obj) != len(_VALID_FIELDS):
            error_msg = 'Field list is incomplete: %d' % len(obj)
        elif not isinstance(obj['locale'], dict):
            error_msg = 'Locale field is not a list'
        elif len(obj['locale']) != len(_VALID_LOCALE_FIELDS):
            error_msg = 'Locale field list is incomplete: %d' % \
                len(obj['locale'])
        else:
            for locale_field in obj['locale']:
                if locale_field not in _VALID_LOCALE_FIELDS:
                    error_msg = 'Locale field "%s" is incorrect' % locale_field
                    break

        if error_msg:
            abort(HTTP_CODES['Bad Request'], message=error_msg)

# TODO: refatorar para o modulo api_util.geoloc
def _insert_geoloc_info(complain_obj):
    if _USE_GEOLOC:
            geo_location = get_geolocation(
                ', '.join((complain_obj['locale'].get('address'),
                           complain_obj['locale'].get('city'),
                           complain_obj['locale'].get('state'),
                           complain_obj['locale'].get('country'))
                          ))
            geoJSON = {'type': 'Point',
                       'coordinates': [radians(geo_location['lng']),
                                       radians(geo_location['lat'])]}
            complain_obj['locale']['geo_location'] = geoJSON


class Complain(Resource):
    ''' Complain: classe principal de dados de reclamacoes
    '''
    def get(self, complain_id):
        ret = api_db.db.complains.find_one(
            {'complain_id': complain_id}, projection={'_id': False})
        if not ret:
            abort(HTTP_CODES['Not Found'],
                  message='Complain %s not found' % complain_id)

        log.log_msg('Reclamacao obtida: %s' % ret)
        return ret

    def put(self, complain_id):
        complain_args = json.loads(parser.parse_args()['complain'])
        _validate_fields(complain_args, True)
        _insert_geoloc_info(complain_args)
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
        if 'locale' in complain_patches:
            _insert_geoloc_info(complain_patches)
        result = api_db.db.complains.update_one(
            {'complain_id': complain_id},
            {'$set': complain_patches})
        if not result.matched_count:
            abort(HTTP_CODES['Not Found'],
                  message='Complain %d not found' % complain_id)

        log.log_msg('Reclamacao alterada: id# %d' % complain_id)
        return 'Complain id# %d patched' % complain_id, HTTP_CODES['Created']

    def delete(self, complain_id):
        result = api_db.db.complains.delete_one(
            {'complain_id': complain_id})
        if not result.deleted_count:
            abort(HTTP_CODES['Not Found'],
                  message='Complain %s not found' % complain_id)

        log.log_msg('Reclamacao removida: id# %s' % complain_id)
        return 'Complain id# %s deleted' % complain_id


class ComplainList(Resource):
    ''' ComplainList: classe de lista de reclamacoes
    '''

    def __retrieve_valid_get_fields(self):
        _like_locale_fields = list(map(lambda x: x + '_like',
                                       _VALID_LOCALE_FIELDS))
        like_fields = list(map(lambda x: x + '_like',
                               _VALID_FIELDS)) + _like_locale_fields
        locale_fields = list(_VALID_LOCALE_FIELDS) + _like_locale_fields
        valid_get_args = list(_VALID_FIELDS) + list(_VALID_LOCALE_FIELDS) \
            + like_fields
        valid_get_args.remove('complement')
        valid_get_args.remove('locale')
        valid_get_args.remove('complement_like')
        valid_get_args.remove('locale_like')

        return like_fields, locale_fields, valid_get_args

    def get(self):
        ret = []
        args = parser.parse_args()
        query_dict = {'$and': []}
        like_fields, locale_fields, valid_get_args = \
            self.__retrieve_valid_get_fields()

        for req_arg in reqparse.request.args:
            if req_arg not in valid_get_args:
                abort(HTTP_CODES['Bad Request'],
                      message='Invalid query string.')

        for arg in args:
            if args[arg]:
                query_key = arg.split('_')[0]
                if arg in locale_fields:
                    query_key = 'locale.' + query_key
                if arg in like_fields:
                    query_condition = re.compile(args[arg], re.IGNORECASE)
                else:
                    query_condition = args[arg]

                query_dict['$and'].append({query_key: query_condition})

        if not query_dict['$and']:
            query_dict = {}

        for result in api_db.db.complains.find(query_dict,
                                               projection={'_id': False}):
            ret.append(result)

        log.log_msg('Reclamacoes obtidas: %s' % ret)
        return ret

    def post(self):
        new_complain_args = json.loads(parser.parse_args()['complain'])
        _validate_fields(new_complain_args, True)
        _insert_geoloc_info(new_complain_args)
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
