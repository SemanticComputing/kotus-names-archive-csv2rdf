#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Mapping of CSV columns to RDF properties
"""

from namespaces import *
from converters import convert_int, validate_wgs84_lat, validate_wgs84_long

KOTUS_MAPPING = {
    'Paikannimi':
        {
            'uri': SKOS.prefLabel
        },
    'Paikanlaji':
        {
            'uri': SCHEMA_NS['type'],
            'name_fi': 'Paikkatyyppi',
            'name_en': 'Place type',
        },
    'Kartan numero':
        {
            'uri': SCHEMA_NS['collection_map_code'],
            'name_fi': 'Kartan numero',
            'name_en': 'Map code',
        },
    'Kerääjän karttanumero':
        {
            'uri': SCHEMA_NS['collection_map_number'],
            'name_fi': 'Kartan numero',
            'name_en': 'Map code',
        },
    'X':
        {
            'uri': SCHEMA_NS['collection_map_tile_x'],
            'name_fi': 'Keruulipussa oleva X-merkintä',
            'name_en': 'Collection slip map tile x',
        },
    'Y':
        {
            'uri': SCHEMA_NS['collection_map_tile_y'],
            'name_fi': 'Keruulipussa oleva X-merkintä',
            'name_en': 'Collection slip map tile y',
        },
    'Pistesij.viite':
        {
            'uri': SCHEMA_NS['collection_map_point'],
            'name_fi': 'Keruulipussa oleva pistesijaintimerkintä',
            'name_en': 'Collection slip map point',
        },
    'Pitäjä':
        {
            'uri': SCHEMA_NS['municipality'],
            'name_fi': 'Pitäjä (n. 1938 pitäjäjaon mukaan)',
            'name_en': 'Municipality (in ca 1938)',
        },
    'Kerääjä':
        {
            'uri': SCHEMA_NS['collector'],
            'name_fi': 'Kerääjän nimi',
            'name_en': 'Collector',
        },
    'Vuosi':
        {
            'uri': SCHEMA_NS['collection_year'],
            'name_fi': 'Leimausvuosi',
            'name_en': 'Collection year',
            'converter': convert_int
        },
    'Aakkonen':
        {
            'uri': SCHEMA_NS['initial_letter'],
            'name_fi': 'Nimen alkukirjain',
            'name_en': 'Initial letter',
        },
    'Jatko':
        {
            'uri': SCHEMA_NS['extended_collection_slip'],
            'name_fi': 'Jatkolippu (J = jatkolippu, ks. Emolippu)',
            'name_en': 'Extended collectoin slip',
        },
    'PEX':
        {
            'uri': SCHEMA_NS['pex'],
            'name_fi': 'PEX (koodeja)',
            'name_en': 'PEX (codes)',
        },
    'Muut nimet':
        {
            'uri': SCHEMA_NS['other_names'],
            'name_fi': 'Muut nimet (X = lipussa tietoja muistakin nimistä)',
            'name_en': 'X = other names in the collection slip',
        },
    'Todellinen pitäjä':
        {
            'uri': SCHEMA_NS['actual_municipality'],
            'name_fi': 'Todellinen pitäjä (esim. Joensuun liput Kontiolahden kokoelmassa)',
            'name_en': 'Actual municipality',
        },
    'KarttaID':
        {
            'uri': SCHEMA_NS['collection_map_file_id'],
            'name_fi': 'KarttaID (keruukarttatiedoston tunniste)',
            'name_en': 'Collection map file id',
        },
    'wgs84_lat':
        {
            'uri': WGS84['lat'],
            'converter': validate_wgs84_lat
        },
    'wgs84_long':
        {
            'uri': WGS84['long'],
            'converter': validate_wgs84_long
        },
    'Kokoelma':
        {
            'uri': SCHEMA_NS['collection'],
            'name_fi': 'Kokoelma (KotusNA1 tai SLS)',
            'name_en': 'Collection',
        },
    # 'Kuvalinkki':
    #     {
    #         'uri': SCHEMA_NS['collection_map_image_file'],
    #         'name_fi': 'Kuvalinkki (linkin loppuosa merityksellinen, alkuosa Kotuksen sisäinen)',
    #         'name_en': 'Collection map image filename',
    #     },
    'Emolippu':
        {
            'uri': SCHEMA_NS['parent_collection_slip'],
            'name_fi': 'Emolippu (jatkolipuissa viittaus aloittavaan lippuun)',
            'name_en': 'Extended collection slips parent slip',
        },

}
