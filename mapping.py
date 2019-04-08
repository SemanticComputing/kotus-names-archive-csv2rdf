#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Mapping of CSV columns to RDF properties
"""

from namespaces import *
from converters import convert_int

KOTUS_MAPPING = {
    'wiki_id': {
            'uri': OWL['sameAs']
        },
    'place_name':
        {
            'uri': SKOS.prefLabel
        },
    'place_type':
        {
            'uri': RDF['type'],
        },
    'name_type':
        {
            'uri': NA_SCHEMA_NS['name_type'],
            'name_fi': 'Nimenlaji',
            'name_en': 'Name type',
        },
    'parish':
        {
            'uri': NA_SCHEMA_NS['parish'],
            'name_fi': 'Pitäjänkokoelma (vuoden 1938 pitäjä, jonka alueella kerätty kohde on)',
            'name_en': 'Collection parish (in ca 1938)',
        },
    'lat':
        {
            'uri': WGS84['lat'],
        },
    'long':
        {
            'uri': WGS84['long'],
        },
    'precision':
        {
            'uri': NA_SCHEMA_NS['positioning_accuracy'],
            'name_fi': 'Paikannustarkkuus',
            'name_en': 'Positioning accuracy',
        },
    'collector':
        {
            'uri': NA_SCHEMA_NS['collector'],
            'name_fi': 'Kerääjä',
            'name_en': 'Collector',
        },
    'collection_year':
        {
            'uri': NA_SCHEMA_NS['stamp_date'],
            'name_fi': 'Leimausvuosi',
            'name_en': 'Stamp date',
            'converter': convert_int
        },
    'collection':
        {
            'uri': NA_SCHEMA_NS['collection'],
            'name_fi': 'Kokoelma, johon tieto kuuluu',
            'name_en': 'Collection',
        }
}
