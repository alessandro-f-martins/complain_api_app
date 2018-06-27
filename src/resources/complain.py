'''
--- Complain API microservice application ---
Author: Alessandro Martins
Module: complain
Description: module for the Complain classes and related routines. Complain
documents are passed as JSON objects.
'''
import re
import json
from flask_restful import abort, Resource, reqparse
from pymongo import ReturnDocument
from api_util import api_log, http_codes
from api_util.geocode import insert_geoloc_info, nearby_complains_query
from api_main import api_db


# Valid fields that may come from the API HTTP request
_VALID_FIELDS = ('title', 'description', 'locale', 'company')
_VALID_LOCALE_FIELDS = ('address', 'complement', 'vicinity',
                        'zip', 'city', 'state', 'country')


# Adding fields to the request parser
parser = reqparse.RequestParser()
parser.add_argument('complain')
parser.add_argument('id')
parser.add_argument('within_radius')


# '<attribute>_like' fields are also added for regex-based queries
for field in _VALID_FIELDS:
    if field != 'locale':
        parser.add_argument(field)
        parser.add_argument(field + '_like')

for field in _VALID_LOCALE_FIELDS:
    if field != 'complement':
        parser.add_argument(field)
        parser.add_argument(field + '_like')


# Initializing HTTP code and Log objects
log = api_log.Log()
HTTP_CODES = http_codes.HTTP_CODES


def _validate_fields(obj, complete=False):
    # Internal field validation function. 'complete=True' forces exactness
    # of document fields, including internal validation of 2nd-level 'locale'
    # attributes.
    error_msg = None

    for field in obj:
        if field not in _VALID_FIELDS:
            error_msg = 'Field "%s" is incorrect' % field
            break

    if complete:
        if len(obj) != len(_VALID_FIELDS):
            error_msg = 'Field list length is incorrect: %d' % len(obj)
        elif not isinstance(obj['locale'], dict):
            error_msg = 'Locale field is not a list'
        elif len(obj['locale']) != len(_VALID_LOCALE_FIELDS):
            error_msg = 'Locale field list length is incorrect: %d' % \
                len(obj['locale'])
        else:
            for locale_field in obj['locale']:
                if locale_field not in _VALID_LOCALE_FIELDS:
                    error_msg = 'Locale field "%s" is incorrect' % locale_field
                    break

        # In case of any of the errors above, aborts with 'Bad Request' HTTP
        # code and issues the proper message to the requesting client.
        if error_msg:
            abort(HTTP_CODES['Bad Request'], message=error_msg)


class Complain(Resource):
    ''' Complain: complaint class for object-referencing URIs (GET obj_id,
        PUT obj_id, PATCH obj_id)
    '''
    def get(self, complain_id):
        ''' get(complain_id): returns the complaint document of id=<complain_id>
        '''
        # Attribute 'locale.geo_location' is left out of the returning object,
        # as it is not part of the original document
        ret = api_db.db.complains.find_one(
            {'complain_id': complain_id},
            projection={'_id': False, 'locale.geo_location': False})
        if not ret:
            abort(HTTP_CODES['Not Found'],
                  message='Complaint %s not found' % complain_id)

        log.log_msg('Reclamacao obtida: %s' % ret)
        return ret

    def put(self, complain_id):
        ''' put(complain_id): replaces content of complaint document of
            id=<complain_id>.
        '''
        complain_args = json.loads(parser.parse_args()['complain'])
        _validate_fields(complain_args, True)
        insert_geoloc_info(complain_args)
        complain_to_replace = {'complain_id': complain_id}
        complain_to_replace.update(complain_args)
        # Performs an 'upsert', i.e., inserts a new complaint document if it's
        # not already present with the given <complain_id>
        result = api_db.db.complains.replace_one(
            {'complain_id': complain_id},
            complain_to_replace,
            upsert=True)

        ins_or_cr = ('updated', 'alterada')

        # If an insert was performed (no documents were matched), adjusts
        # complaint sequence numbering accordingly.
        if not result.matched_count:
            api_db.db.complains_seq.update_one({'_id': 'complain_id'},
                                               {'$set': {'seq_value':
                                                         complain_id + 1}})
            ins_or_cr = ('created', 'criada')

        log.log_msg('Reclamacao %s: id# %d' % (ins_or_cr[1], complain_id))
        return 'Complaint id# %d %s' % (complain_id, ins_or_cr[0]), \
            HTTP_CODES['Created']

    def patch(self, complain_id):
        ''' patch(complain_id): patches (updates) content of complaint
            document of id=<complain_id>.
        '''
        complain_patches = json.loads(parser.parse_args()['complain'])
        _validate_fields(complain_patches)
        # NOTE: at the moment, 'locale' fields should be fully complete to be
        # patched/updated, even if only one of its subfields are modified
        if 'locale' in complain_patches:
            insert_geoloc_info(complain_patches)
        result = api_db.db.complains.update_one(
            {'complain_id': complain_id},
            {'$set': complain_patches})
        # Differently from put(), an error is issued if no matching documents
        # were found.
        if not result.matched_count:
            abort(HTTP_CODES['Not Found'],
                  message='Complaint %d not found' % complain_id)

        log.log_msg('Reclamacao alterada: id# %d' % complain_id)
        return 'Complaint id# %d patched' % complain_id, HTTP_CODES['Created']

    def delete(self, complain_id):
        ''' delete(complain_id): deletes complaint document of
            id=<complain_id>.
        '''
        result = api_db.db.complains.delete_one(
            {'complain_id': complain_id})

        # An error is issued if no matching documents were found.
        if not result.deleted_count:
            abort(HTTP_CODES['Not Found'],
                  message='Complain %s not found' % complain_id)

        log.log_msg('Reclamacao removida: id# %s' % complain_id)
        return 'Complaint id# %s deleted' % complain_id


class ComplainList(Resource):
    ''' ComplainList: complaint class for non-object-referencing URIs
        (GET, GET <query>, POST)
    '''
    def __retrieve_valid_get_fields(self):
        # Helper private method for constructing validation structures for
        # GET queries, to match with request fields as returned by request
        # and reqparse objects
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
        valid_get_args.append('id')
        valid_get_args.append('within_radius')

        return like_fields, locale_fields, valid_get_args

    def get(self):
        ''' get(): returns a list of all the complaint documents, or the ones
            which match the given query criteria if they are provided via the
            GET query string. Provides functionality for exact matches, "_like"
            matches (partial arguments, case insensitive) and matches within a
            distance range (radius).
        '''
        ret = []
        args = parser.parse_args()
        query_dict = {'$and': []}
        like_fields, locale_fields, valid_get_args = \
            self.__retrieve_valid_get_fields()

        # Checks request for malformed query strings
        for req_arg in reqparse.request.args:
            if req_arg not in valid_get_args:
                abort(HTTP_CODES['Bad Request'],
                      message='Invalid query string.')

        radius = args['within_radius']
        id = args['id']

        if radius and id:
            # Performs distance range query. Retrieves a MongoDB query that
            # matches all complaint documents within the provided radius. In
            # this case, if no matches were found, returns an empty list
            query_dict = nearby_complains_query(id, radius)
            if not query_dict:
                return []
        else:
            # Performs attribute-related queries
            for arg in args:
                if args[arg]:
                    query_key = arg.split('_')[0]
                    if arg in locale_fields:
                        # Builds locale field-related query parameters
                        query_key = 'locale.' + query_key
                    if arg in like_fields:
                        # Builds partial argument, case insensitive query
                        # parameters ('like' parameters)
                        query_condition = re.compile(args[arg], re.IGNORECASE)
                    else:
                        # Builds exact match query parameters
                        query_condition = args[arg]

                    # Concatenates all query parameters for combined parameter
                    # search
                    query_dict['$and'].append({query_key: query_condition})

            if not query_dict['$and']:
                # if query string is empty, retrieves all complaint documents
                query_dict = {}

        # Assembles together the list of results. Attribute
        # 'locale.geo_location' is left out of the returning object, as it is
        # not part of the original document
        complain_results = api_db.db.complains.find(
                query_dict, projection={'_id': False,
                                        'locale.geo_location': False})
        if complain_results is None:
            abort(HTTP_CODES['Bad Request'],
                  message='There was a problem with your request. Please check.')

        for result in complain_results:
            if not id:
                # Non-range query (exact or partial match)
                ret.append(result)
            elif result['complain_id'] != int(id):
                # In a distance range query, excludes the given complaint
                # document itself from the list, as it is already given as
                # the center of the search
                ret.append(result)

        log.log_msg('Reclamacoes obtidas: %s' % ret)
        return ret

    def post(self):
        ''' post(): inserts a new complaint document.
        '''
        new_complain_args = json.loads(parser.parse_args()['complain'])
        _validate_fields(new_complain_args, True)
        insert_geoloc_info(new_complain_args)
        # Gets the highest available complaint sequenced id and increments
        # its value
        new_complain_id = api_db.db.complains_seq.find_one_and_update(
            filter={'_id': 'complain_id'},
            update={'$inc': {'seq_value': 1}},
            return_document=ReturnDocument.BEFORE).get('seq_value')
        new_complain = {'complain_id': new_complain_id}
        new_complain.update(new_complain_args)

        # Inserts the new complaint document in the database
        api_db.db.complains.insert_one(new_complain)
        log.log_msg('Reclamacao criada: id# %s' % new_complain_id)

        return 'Complaint id# %d created' % new_complain_id, \
            HTTP_CODES['Created']
